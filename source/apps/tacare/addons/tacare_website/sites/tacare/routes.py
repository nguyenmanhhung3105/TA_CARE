"""Server-rendered local first experience backed by Odoo records."""
import math
from urllib.parse import urlsplit

from markupsafe import escape
from werkzeug.exceptions import BadRequest, Forbidden, NotFound

from odoo import http, fields
from odoo.http import request

from ...models.jobs.hr_job import SECTORS, TYPES, MODES, preferred_currency
from ...controllers.site_context import site_context


class HubControllers(http.Controller):
    def _connection(self, connection_id):
        item = request.env['tacare.connection'].sudo().browse(connection_id).exists()
        company_ids = self._user().company_ids.ids
        if not item or item.company_id.id not in company_ids or item.job_id.care_opportunity_kind != 'flexible':
            raise Forbidden('Kết nối không thuộc phạm vi của bạn.')
        organization_access = self._role() == 'business' and item.organization_id in self._authorized_organizations('handle')
        participant = self._role() == 'candidate' and (self._user() in (item.sender_id | item.receiver_id) or item.profile_id.user_id == self._user() or item.job_id.tacare_owner_user_id == self._user())
        if self._role() != 'admin' and not participant and not organization_access:
            raise Forbidden('Kết nối không thuộc tài khoản này.')
        return item

    def _match(self, job, profile):
        own = profile.user_id == self._user()
        organization = job.tacare_owner_partner_id
        return job._care_compare_profile(profile,
            allow_profile=own or bool(self._current_consent(profile, 'matching', organization, 'profile')),
            allow_skills=own or bool(self._current_consent(profile, 'matching', organization, 'skills')))

    def _notify(self, user, text, connection=None):
        request.env['tacare.notification'].sudo().create({
            'user_id': user.id, 'message': text,
            'connection_id': connection.id if connection else False,
        })

    @http.route('/tacare/matching', type='http', auth='user', website=True)
    def matching(self, **kw):
        self._flex_user()
        role = self._role()
        view = kw.get('view') or ('receive' if role == 'candidate' else 'hire')
        if view not in ('receive','hire'):
            raise BadRequest('Chọn phía cần người hoặc nhận việc.')
        if view == 'receive' and role == 'business':
            raise Forbidden('Tài khoản doanh nghiệp dùng phía tìm người làm; hồ sơ nhận việc thuộc tài khoản cá nhân.')
        if view == 'receive':
            profile = self._my_profile()
            if not kw.get('profile_id'):
                own_profiles = request.env['tacare.profile'].sudo().search([
                    ('user_id', '=', self._user().id), ('status', '=', 'active'),
                    ('company_id', 'in', self._user().company_ids.ids)], order='id desc', limit=100)
                # Read-only default selection; every form write still requires
                # an explicit owner-checked profile_id.
                profile = next((p for p in own_profiles if self._receive_matching_data(p)), profile)
            if not profile:
                return request.redirect(self._urls()['tuhoso'] + 'tuhoso/profiles/new?kind=flexible')
            matches = self._receive_matching_data(profile)
            return self._render('live_matching',matches=matches,kind='jobs',profile=profile,
                matching_enabled=self._matching_is_enabled(profile),seasonal_view=view)
        try:
            selected_id = int(kw.get('job') or 0)
        except ValueError:
            raise BadRequest('Tin không hợp lệ.')
        jobs, selected, matches = self._hire_matching_data(selected_id)
        if not selected_id and not matches:
            # The marketing entry opens the account's own suggestions, including
            # those attached to an older need. Explicit selections stay intact.
            for job in jobs - selected:
                _, candidate, candidate_matches = self._hire_matching_data(job.id)
                if candidate_matches:
                    selected, matches = candidate, candidate_matches
                    break
        return self._render('live_matching', matches=matches, kind='profiles', jobs=jobs, selected=selected,
            editable_org_ids=jobs.mapped('tacare_owner_partner_id').ids, seasonal_view=view)

    def _hire_matching_data(self, selected_id=0):
        role = self._role()
        company_ids = self._user().company_ids.ids
        domain = self._job_domain() + [('company_id', 'in', company_ids), ('care_matching_enabled', '=', True)]
        if role == 'business':
            domain.append(('tacare_owner_partner_id', 'in', self._authorized_organizations('handle').ids))
        elif role != 'admin':
            domain.append(('tacare_owner_user_id', '=', self._user().id))
        jobs = request.env['hr.job'].sudo().search(domain, order='write_date desc, id desc')
        selected = jobs.filtered(lambda j: j.id == selected_id)[:1] if selected_id else jobs[:1]
        if selected_id and not selected:
            raise NotFound()
        profiles = self._visible_profiles(selected.tacare_owner_partner_id).filtered(lambda p:
            p.user_id != self._user() and p.user_id.active and
            self._current_consent(p, 'matching', selected.tacare_owner_partner_id, 'profile') and
            self._current_consent(p, 'matching', selected.tacare_owner_partner_id, 'skills')) if selected else request.env['tacare.profile']
        matches = [(p, self._match(selected, p)) for p in profiles] if selected else []
        matches = sorted([p for p in matches if p[1].get('eligible', False)], key=lambda p: p[1]['rank'], reverse=True)
        return jobs, selected, matches

    def _receive_matching_data(self, profile):
        jobs = request.env['hr.job'].sudo().search(self._job_domain() + [
            ('care_matching_enabled', '=', True), ('tacare_owner_user_id', '!=', self._user().id)])
        jobs = jobs.filtered(lambda j: self._current_consent(profile, 'matching', j.tacare_owner_partner_id, 'profile') and
            self._current_consent(profile, 'matching', j.tacare_owner_partner_id, 'skills'))
        matches = [(job, self._match(job, profile)) for job in jobs]
        return sorted([p for p in matches if p[1].get('eligible', False)], key=lambda p: p[1]['rank'], reverse=True)

    def _matching_is_enabled(self, profile):
        # Display state only; this never grants discovery to an unspecified
        # recipient. Each job above still checks the exact organization.
        grants = request.env['care.consent'].sudo().search([
            ('profile_id', '=', profile.id), ('purpose', '=', 'matching'), ('state', '=', 'granted')])
        return any(c.is_current('matching', c.recipient_partner_id, 'profile') and
                   c.is_current('matching', c.recipient_partner_id, 'skills') for c in grants)

    @http.route('/tacare/matching/<int:job_id>/profile/<int:profile_id>',
                type='http', auth='user', website=True, methods=['GET'])
    def matching_profile_detail(self, job_id, profile_id, **kw):
        """Seasonal profile details, scoped to a live need and current consent."""
        self._flex_user()
        job = self._own_job(job_id, 'handle')
        if not job.care_matching_enabled or not request.env['hr.job'].sudo().search_count(
                self._job_domain() + [('id', '=', job.id)]):
            raise NotFound()
        recipient = job.tacare_owner_partner_id
        profile = self._visible_profiles(recipient).filtered(lambda p: p.id == profile_id)[:1]
        if not profile or not self._current_consent(profile, 'matching', recipient, 'profile') or not \
                self._current_consent(profile, 'matching', recipient, 'skills'):
            raise NotFound()
        evidence = profile.evidence_ids.filtered(lambda e: e.visibility in ('public', 'members'))
        if not self._current_consent(profile, 'discovery', recipient, 'evidence'):
            evidence = request.env['tacare.profile.evidence']
        reason = self._match(job, profile)
        if not reason.get('eligible'):
            raise NotFound('Cặp này không còn gợi ý phù hợp để xem chi tiết.')
        return self._render('kvl_candidate_detail', site='tacare', job=job, profile=profile,
                            evidence=evidence, comparisons=reason['comparisons'],
                            can_invite=bool(reason.get('eligible')))

    @http.route('/tacare/request/send', type='http', auth='user', methods=['POST'], website=True)
    def request_send(self, **kw):
        self._flex_user()
        kind = kw.get('type')
        if kind not in ('application', 'invitation'):
            raise BadRequest('Loại đề nghị không hợp lệ.')
        try:
            job_id, profile_id = int(kw.get('job_id') or 0), int(kw.get('profile_id') or 0)
        except ValueError:
            raise BadRequest('ID không hợp lệ.')
        job = request.env['hr.job'].sudo().browse(job_id).exists()
        profile = request.env['tacare.profile'].sudo().browse(profile_id).exists()
        if not job or job.care_opportunity_kind != 'flexible' or not profile or profile.care_recruitment_enabled or profile.status != 'active' or not profile.user_id.active:
            raise BadRequest('Tin hoặc hồ sơ không tồn tại.')
        company_ids = self._user().company_ids.ids
        profile_companies = company_ids if kind == 'application' or self._role() == 'admin' else self._website('tuhoso').company_id.ids
        if job.company_id.id not in company_ids or profile.company_id.id not in profile_companies:
            raise Forbidden('Tin hoặc hồ sơ ngoài phạm vi tài khoản.')
        request.env.cr.execute('SELECT id FROM hr_job WHERE id = %s FOR UPDATE', [job.id])
        job.invalidate_recordset(['tacare_status', 'is_published', 'care_remaining_slots'])
        if job.tacare_status != 'published' or not job.is_published or job.care_remaining_slots <= 0 or (job.tacare_deadline and job.tacare_deadline < fields.Date.today()):
            raise BadRequest('Tin hoặc hồ sơ không còn sẵn sàng.')
        if kind == 'application':
            self._require_candidate()
            if profile.user_id != self._user():
                raise Forbidden('Chỉ chủ hồ sơ được đề nghị nhận việc.')
            receiver = job.tacare_owner_user_id
        else:
            self._own_job(job.id, 'handle')
            if not job.care_matching_enabled:
                raise BadRequest('Tin đã tắt gợi ý kết nối.')
            if profile not in self._visible_profiles(job.tacare_owner_partner_id) or not self._current_consent(profile, 'matching', job.tacare_owner_partner_id, 'skills'):
                raise BadRequest('Hồ sơ không nhận lời mời mới.')
            receiver = profile.user_id
        if job.care_opportunity_kind == 'flexible':
            if not job.care_matching_enabled or not self._current_consent(profile, 'matching', job.tacare_owner_partner_id, 'profile') or not self._current_consent(profile, 'matching', job.tacare_owner_partner_id, 'skills'):
                raise BadRequest('Cần quyền đối chiếu hiện hành cho hồ sơ này.')
            if not self._match(job, profile).get('eligible', False):
                raise BadRequest('Tin và công việc nhận làm chưa có căn cứ phù hợp hoặc có điều kiện xung đột.')
        if receiver == self._user():
            raise BadRequest('Không thể tự gửi đề nghị cho chính mình.')
        if not receiver:
            raise BadRequest('Chưa có tài khoản nhận đề nghị.')
        message = (kw.get('message') or '').strip()[:2000]
        if kind == 'invitation' and not message:
            raise BadRequest('Lời mời cần có nội dung.')
        existing = request.env['tacare.connection'].sudo().search([
            ('job_id', '=', job.id), ('profile_id', '=', profile.id),
            ('type', '=', kind), ('status', '=', 'pending')], limit=1)
        if existing:
            raise BadRequest('Đã có đề nghị hoặc lời mời cùng loại đang chờ.')
        vals = {
            'type': kind, 'job_id': job.id, 'profile_id': profile.id,
            'sender_id': self._user().id, 'receiver_id': receiver.id,
            'message': message,
            'share_contact': False,
            'snapshot_name': profile.name, 'snapshot_headline': profile.headline,
            'snapshot_skills': ', '.join(profile.skill_ids.mapped('name')),
        }
        connection = request.env['tacare.connection'].sudo().create(vals)
        self._audit('connection.' + kind + '.sent', connection)
        self._notify(receiver, ('Có đề nghị nhận việc mới: ' if kind == 'application' else 'Có lời mời trao đổi mới: ') + job.name, connection)
        if kind == 'application':
            members = request.env['care.org.member'].sudo().search([
                ('organization_id', '=', job.tacare_owner_partner_id.id),
                ('company_id', '=', job.company_id.id), ('state', '=', 'active')])
            for member in members.filtered(lambda item: item.role in ('owner', 'recruiter') or item.can_handle_candidates):
                if member.user_id != receiver and member.user_id.active:
                    self._notify(member.user_id, 'Có đề nghị nhận việc mới: ' + job.name, connection)
        return request.redirect(f'/tacare/connection/{connection.id}?notice=sent')

    @http.route('/tacare/connections', type='http', auth='user', website=True)
    def connections(self, **kw):
        self._flex_user()
        company_ids = self._user().company_ids.ids
        domain = [('company_id','in',company_ids),('job_id.care_opportunity_kind','=','flexible')]
        if self._role() == 'business':
            domain.append(('organization_id','in',self._authorized_organizations('handle').ids))
        elif self._role() != 'admin':
            domain += ['|','|','|',('sender_id','=',self._user().id),('receiver_id','=',self._user().id),
                ('profile_id.user_id','=',self._user().id),('job_id.tacare_owner_user_id','=',self._user().id)]
        if kw.get('type') in ('application', 'invitation'):
            domain.append(('type', '=', kw['type']))
        items = request.env['tacare.connection'].sudo().search(domain, limit=100)
        return self._render('live_connections', items=items)

    def _can_respond_connection(self, item):
        return self._role() == 'admin' or item.receiver_id == self._user() or (
            self._role() == 'business' and item.type == 'application' and
            item.organization_id in self._authorized_organizations('handle'))

    @http.route('/tacare/connection/<int:connection_id>', type='http', auth='user', website=True)
    def connection_detail(self, connection_id, **kw):
        item = self._connection(connection_id)
        show_contact = (item.status == 'accepted' and item.contact_consent_id and
                        item.contact_consent_id.is_current('contact', item.organization_id, 'email'))
        can_respond = item.status == 'pending' and self._can_respond_connection(item)
        can_cancel = item.status == 'pending' and (self._role() == 'admin' or item.sender_id == self._user())
        return self._render('live_connection_detail', item=item, show_contact=show_contact,
                            can_respond=can_respond, can_cancel=can_cancel)

    @http.route('/tacare/connection/<int:connection_id>/contact', type='http', auth='user', methods=['POST'], website=True)
    def connection_contact(self, connection_id, **kw):
        item = self._connection(connection_id)
        if self._role() != 'candidate' or item.profile_id.user_id != self._user() or item.status != 'accepted':
            raise Forbidden('Chỉ người nhận việc trong kết nối đã đồng ý được thay đổi quyền liên hệ.')
        action = kw.get('action')
        if action not in ('grant', 'revoke'):
            raise BadRequest('Thao tác chia sẻ không hợp lệ.')
        consent = item.contact_consent_id
        if action == 'revoke':
            if consent and consent.state == 'granted':
                consent.write({'state': 'revoked', 'revoked_at': fields.Datetime.now(),
                               'revoke_reason': 'Người nhận việc thu hồi'})
            item.write({'contact_consent_id': False})
        elif not consent or not consent.is_current('contact', item.organization_id, 'email'):
            consent = request.env['care.consent'].sudo().create({
                'profile_id': item.profile_id.id, 'purpose': 'contact',
                'recipient_kind': 'organization', 'recipient_partner_id': item.organization_id.id,
                'field_scope': ['email'], 'state': 'granted',
                'granted_by': self._user().id, 'valid_from': fields.Datetime.now()})
            item.write({'contact_consent_id': consent.id})
        return request.redirect(f'/tacare/connection/{item.id}?notice=contact')

    @http.route('/tacare/connection/<int:connection_id>/respond', type='http', auth='user', methods=['POST'], website=True)
    def connection_respond(self, connection_id, **kw):
        item = self._connection(connection_id)
        request.env.cr.execute('SELECT id FROM tacare_connection WHERE id = %s FOR UPDATE', [item.id])
        item.invalidate_recordset(['status'])
        if item.status != 'pending' or not self._can_respond_connection(item):
            raise Forbidden('Chỉ bên nhận phản hồi đề nghị đang chờ.')
        status = kw.get('status')
        if status not in ('accepted', 'declined'):
            raise BadRequest('Trạng thái không hợp lệ.')
        item.write({'status': status, 'decided_at': fields.Datetime.now()})
        self._audit('connection.' + status, item)
        self._notify(item.sender_id, ('Đã đồng ý trao đổi: ' if status == 'accepted' else 'Đã từ chối: ') + item.job_id.name, item)
        return request.redirect(f'/tacare/connection/{item.id}?notice=responded')

    @http.route('/tacare/connection/<int:connection_id>/cancel', type='http', auth='user', methods=['POST'], website=True)
    def connection_cancel(self, connection_id, **kw):
        item = self._connection(connection_id)
        request.env.cr.execute('SELECT id FROM tacare_connection WHERE id = %s FOR UPDATE', [item.id])
        item.invalidate_recordset(['status'])
        if item.status != 'pending' or not (self._role() == 'admin' or item.sender_id == self._user()):
            raise Forbidden('Chỉ bên gửi hủy đề nghị đang chờ.')
        item.write({'status': 'cancelled', 'decided_at': fields.Datetime.now()})
        self._audit('connection.cancelled', item)
        self._notify(item.receiver_id, 'Đề nghị đã được hủy: ' + item.job_id.name, item)
        return request.redirect(f'/tacare/connection/{item.id}?notice=cancelled')

    @http.route('/tacare/connection/<int:connection_id>/result', type='http', auth='user', methods=['POST'], website=True)
    def connection_result(self, connection_id, **kw):
        item = self._connection(connection_id)
        if item.status != 'accepted':
            raise Forbidden('Chỉ kết nối đã đồng ý trao đổi mới nhận kết quả.')
        result = kw.get('result')
        if result not in dict(request.env['tacare.connection']._fields['result'].selection):
            raise BadRequest('Kết quả không hợp lệ.')
        item.write({'result': result, 'result_note': (kw.get('note') or '').strip()[:2000],
                    'result_user_id': self._user().id})
        other = item.receiver_id if item.sender_id == self._user() else item.sender_id
        self._notify(other, 'Kết quả trao đổi đã cập nhật: ' + item.job_id.name, item)
        return request.redirect(f'/tacare/connection/{item.id}?notice=result')

    @http.route('/tacare/notifications', type='http', auth='user', website=True)
    def notifications(self, **kw):
        items = request.env['tacare.notification'].sudo().search([('user_id', '=', self._user().id)], limit=100)
        return self._render('live_notifications', items=items)

    @http.route('/tacare/notification/<int:notification_id>/read', type='http', auth='user', methods=['POST'], website=True)
    def notification_read(self, notification_id, **kw):
        item = request.env['tacare.notification'].sudo().browse(notification_id).exists()
        if not item or item.user_id != self._user():
            raise Forbidden('Thông báo không thuộc tài khoản này.')
        item.write({'is_read': True})
        return request.redirect('/tacare/notifications')
