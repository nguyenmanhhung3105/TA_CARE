"""Work lifecycle and two-way reviews within an authorized connection."""
from odoo import http
from odoo.http import request
from odoo.exceptions import AccessError, ValidationError
from werkzeug.exceptions import BadRequest, Forbidden
from .examples import TacareExamples


class WorkReviews(TacareExamples):
    def _render(self, template, site='tacare', **values):
        values.setdefault('source_job', False)
        feedback = request.env['care.feedback'].sudo()
        if template == 'work_detail':
            record = values['record']
            values['review_summary'] = feedback._summary(profile=record.profile_id) if values.get('is_service') else \
                feedback._summary(buyer=record.tacare_owner_partner_id)
        if template in ('profile_overview', 'kvl_candidate_detail') and values.get('profile'):
            values['review_summary'] = feedback._summary(profile=values['profile'])
            grants = request.env['care.consent'].sudo().search([
                ('profile_id', '=', values['profile'].id), ('purpose', '=', 'matching'),
                ('recipient_kind', '=', 'organization'), ('state', '=', 'granted')])
            values['scoped_matching_orgs'] = grants.filtered(lambda c: c.is_current(
                'matching', c.recipient_partner_id, 'profile')).mapped('recipient_partner_id')
        return super()._render(template, site=site, **values)

    def _work_values_for_page(self, connection):
        participation = request.env['care.work.participation'].sudo().search([
            ('connection_id', '=', connection.id)], limit=1)
        side = False
        if participation:
            try:
                side = participation._side(self._user())
            except AccessError:
                pass
        else:
            if self._user() == connection.profile_id.user_id:
                side = 'provider'
            elif self._user() == connection.job_id.tacare_owner_user_id or (
                self._role() == 'business' and connection.organization_id in self._authorized_organizations('handle')):
                side = 'buyer'
        reviews = participation.feedback_ids.filtered(lambda r: r.published or r.author_side == side or self._role() == 'admin') if participation else \
            request.env['care.feedback'].sudo().browse()
        can_read_offers = (side == 'provider' or self._role() == 'admin' or
            side == 'buyer' and self._current_consent(connection.profile_id, 'matching', connection.organization_id, 'skills'))
        return dict(participation=participation, work_side=side, work_reviews=reviews,
            own_review=reviews.filtered(lambda r: r.author_side == side), work_error=False, work_vals={},
            offer_options=connection.profile_id.capability_ids.filtered(lambda s: s.active and
                s.flex_state == 'available' and s.category_id == connection.job_id.flex_category_id) if can_read_offers else [])

    @http.route()
    def connection_detail(self, connection_id, **kw):
        item = self._connection(connection_id)
        return self._work_page(item)

    def _work_page(self, item, error=False, vals=None):
        data = self._work_values_for_page(item)
        data.update(work_error=error, work_vals=vals or {})
        return self._render('live_connection_detail', item=item,
            show_contact=bool(item.status == 'accepted' and item.contact_consent_id and
                item.contact_consent_id.is_current('contact', item.organization_id, 'email')),
            can_respond=item.status == 'pending' and self._can_respond_connection(item),
            can_cancel=item.status == 'pending' and (self._role() == 'admin' or item.sender_id == self._user()), **data)

    @http.route('/tacare/connection/<int:connection_id>/work', auth='user', website=True, methods=['POST'])
    def propose_work(self, connection_id, **kw):
        item = self._connection(connection_id)
        if set(kw) - {'csrf_token', 'capability_id', 'terms'}:
            raise BadRequest('Biểu mẫu có trường không được phép sửa.')
        actor = self._user()
        if not self._work_values_for_page(item)['work_side']:
            raise Forbidden('Chỉ hai bên tham gia được chốt việc.')
        try:
            with request.env.cr.savepoint():
                request.env.cr.execute('SELECT id FROM hr_job WHERE id=%s FOR UPDATE', [item.job_id.id])
                item.invalidate_recordset()
                job = item.job_id
                job.invalidate_recordset()
                if item.status != 'accepted' or item.profile_id.status != 'active' or not item.profile_id.user_id.active or not request.env['hr.job'].sudo().search_count(
                        self._job_domain() + [('id', '=', job.id)]):
                    raise ValidationError('Cần kết nối đã đồng ý trao đổi và tin đang mở.')
                if request.env['care.work.participation'].sudo().search_count([('connection_id', '=', item.id)]):
                    raise ValidationError('Kết nối đã có lượt thực hiện.')
                offer = request.env['care.profile.capability'].sudo().search([
                    ('id', '=', int(kw.get('capability_id') or 0)), ('profile_id', '=', item.profile_id.id),
                    ('active', '=', True), ('flex_state', '=', 'available'), ('category_id', '=', job.flex_category_id.id)], limit=1)
                terms = (kw.get('terms') or '').strip()
                if not offer or not 20 <= len(terms) <= 4000:
                    raise ValidationError('Chọn đúng việc nhận làm và ghi thỏa thuận từ 20 đến 4.000 ký tự.')
                if actor != item.profile_id.user_id and not self._current_consent(
                        item.profile_id, 'matching', item.organization_id, 'skills'):
                    raise ValidationError('Chủ hồ sơ cần cho phép chia sẻ việc nhận làm hoặc chủ động gửi thỏa thuận.')
                orders = request.env['care.work.order'].sudo()
                order = orders.search([('job_id', '=', job.id)], limit=1) or orders.create({'job_id': job.id})
                if request.env['care.work.participation'].sudo().search_count([
                        ('work_order_id', '=', order.id), ('provider_user_id', '=', item.profile_id.user_id.id)]):
                    raise ValidationError('Người nhận việc đã có lượt thực hiện cho đầu việc này.')
                participation = request.env['care.work.participation'].sudo().create(dict(
                    work_order_id=order.id, connection_id=item.id, profile_id=item.profile_id.id,
                    capability_id=offer.id, buyer_partner_id=item.organization_id.id,
                    provider_user_id=item.profile_id.user_id.id, terms=terms))
                participation._act(actor, 'confirm')
                self._notify(item.receiver_id if actor == item.sender_id else item.sender_id,
                    'Có thỏa thuận công việc cần xác nhận: ' + job.name, item)
        except AccessError as exc:
            raise Forbidden(str(exc))
        except (ValidationError, ValueError, TypeError) as exc:
            return self._work_page(item, str(exc) if isinstance(exc, ValidationError) else 'Chọn việc nhận làm hợp lệ.', kw)
        return request.redirect('/tacare/connection/%s?notice=work' % item.id)

    @http.route('/tacare/connection/<int:connection_id>/work/action', auth='user', website=True, methods=['POST'])
    def work_action(self, connection_id, **kw):
        item = self._connection(connection_id)
        if set(kw) - {'csrf_token', 'action', 'note'}:
            raise BadRequest('Biểu mẫu có trường không được phép sửa.')
        p = request.env['care.work.participation'].sudo().search([('connection_id', '=', item.id)], limit=1)
        if not p:
            raise BadRequest('Chưa có thỏa thuận công việc.')
        try:
            with request.env.cr.savepoint():
                p._act(self._user(), kw.get('action'), kw.get('note') or '')
                for user in item.sender_id | item.receiver_id:
                    if user != self._user():
                        self._notify(user, 'Cập nhật thực hiện: ' + dict(p._fields['state'].selection)[p.state], item)
        except AccessError as exc:
            raise Forbidden(str(exc))
        except ValidationError as exc:
            return self._work_page(item, str(exc), kw)
        return request.redirect('/tacare/connection/%s?notice=work' % item.id)

    @http.route('/tacare/connection/<int:connection_id>/review', auth='user', website=True, methods=['POST'])
    def submit_review(self, connection_id, **kw):
        item = self._connection(connection_id)
        if set(kw) - {'csrf_token', 'rating', 'comment'}:
            raise BadRequest('Biểu mẫu có trường không được phép sửa.')
        p = request.env['care.work.participation'].sudo().search([('connection_id', '=', item.id)], limit=1)
        if not p:
            raise BadRequest('Chưa có lượt thực hiện công việc.')
        try:
            with request.env.cr.savepoint():
                p._review(self._user(), int(kw.get('rating') or 0), kw.get('comment') or '')
        except AccessError as exc:
            raise Forbidden(str(exc))
        except (ValidationError, TypeError, ValueError) as exc:
            return self._work_page(item, str(exc) if isinstance(exc, ValidationError) else 'Chọn từ 1 đến 5 sao.', kw)
        return request.redirect('/tacare/connection/%s?notice=review' % item.id)

    @http.route('/tacare/review/<int:review_id>/moderate', auth='user', website=True, methods=['POST'])
    def moderate_review(self, review_id, **kw):
        if self._role() != 'admin':
            raise Forbidden('Chỉ quản trị được kiểm duyệt đánh giá.')
        if set(kw) - {'csrf_token', 'moderation', 'reason'} or kw.get('moderation') not in ('visible', 'hidden'):
            raise BadRequest('Thao tác kiểm duyệt không hợp lệ.')
        review = request.env['care.feedback'].sudo().search([
            ('id', '=', review_id), ('company_id', 'in', self._user().company_ids.ids),
            ('participation_id', '!=', False)], limit=1)
        if not review:
            raise Forbidden()
        review.with_user(self._user()).write({'moderation': kw['moderation'],
            'moderation_reason': (kw.get('reason') or '').strip()[:1000]})
        return request.redirect('/tacare/connection/%s' % review.connection_id.id)
