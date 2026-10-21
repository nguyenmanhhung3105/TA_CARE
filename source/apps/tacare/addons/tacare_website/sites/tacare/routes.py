"""Server-rendered local first experience backed by Odoo records."""
import math
from urllib.parse import urlsplit

from markupsafe import escape
from werkzeug.exceptions import BadRequest, Forbidden, NotFound

from odoo import http, fields
from odoo.http import request

from ...models.hr_job import SECTORS, TYPES, MODES, preferred_currency
from ...controllers.site_context import site_context


class HubControllers(http.Controller):
    def _connection(self, connection_id):
        item = request.env['tacare.connection'].sudo().browse(connection_id).exists()
        business_access = (item and self._is_business() and item.job_id.company_id == request.env.company
                           and item.organization_id in self._authorized_organizations('handle'))
        candidate_access = item and self._is_candidate() and item.profile_id.user_id == self._user()
        if not item or self._role() != 'admin' and not business_access and not candidate_access:
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
        role = self._role()
        if role == 'candidate':
            profile = self._my_profile()
            if not profile:
                return request.redirect(self._urls()['tuhoso'] + 'tuhoso/profiles?kind=recruitment')
            jobs = request.env['hr.job'].sudo().search(
                self._job_domain() + [('care_matching_enabled', '=', True),
                    ('care_opportunity_kind', '=', 'recruitment' if profile.care_recruitment_enabled else 'flexible')]) if self._current_consent(profile, 'matching') else request.env['hr.job']
            matches = sorted([(job, self._match(job, profile)) for job in jobs],
                             key=lambda pair: pair[1]['rank'], reverse=True)
            matches = [pair for pair in matches if pair[1].get('eligible', True)]
            return self._render('live_matching', matches=matches, kind='jobs', profile=profile,
                                matching_enabled=bool(self._current_consent(profile, 'matching')))
        self._require_business()
        organizations = self._authorized_organizations('handle')
        if not organizations and role != 'admin':
            raise Forbidden('Bạn chưa được cấp quyền xử lý ứng viên.')
        domain = [('tacare_owner_partner_id', '!=', False)]
        if role == 'admin':
            domain.append(('company_id', 'in', self._user().company_ids.ids))
        if role != 'admin':
            domain.extend([('company_id', '=', request.env.company.id),
                           ('tacare_owner_partner_id', 'in', organizations.ids)])
        jobs = request.env['hr.job'].sudo().search(domain + [
            ('tacare_status', '=', 'published'), ('care_matching_enabled', '=', True)])
        try:
            selected_id = int(kw.get('job') or 0)
        except ValueError:
            raise BadRequest('ID tin không hợp lệ.')
        selected = jobs.filtered(lambda item: item.id == selected_id)[:1] if selected_id else jobs[:1]
        if selected_id and not selected:
            raise NotFound()
        profiles = self._visible_profiles(selected.tacare_owner_partner_id).filtered(lambda item: bool(self._current_consent(item, 'matching', selected.tacare_owner_partner_id, 'skills') and self._current_consent(item, 'matching', selected.tacare_owner_partner_id, 'profile'))) if selected else request.env['tacare.profile']
        matches = sorted([(profile, self._match(selected, profile)) for profile in profiles],
                         key=lambda pair: pair[1]['rank'], reverse=True) if selected else []
        matches = [pair for pair in matches if pair[1].get('eligible', True)]
        return self._render('live_matching', matches=matches, kind='profiles', jobs=jobs,
                            selected=selected, editable_org_ids=organizations.ids)

    @http.route('/tacare/request/send', type='http', auth='user', methods=['POST'], website=True)
    def request_send(self, **kw):
        kind = kw.get('type')
        if kind not in ('application', 'invitation'):
            raise BadRequest('Loại đề nghị không hợp lệ.')
        try:
            job_id, profile_id = int(kw.get('job_id') or 0), int(kw.get('profile_id') or 0)
        except ValueError:
            raise BadRequest('ID không hợp lệ.')
        job = request.env['hr.job'].sudo().browse(job_id).exists()
        profile = request.env['tacare.profile'].sudo().browse(profile_id).exists()
        if not job or not profile or profile.status != 'active' or not profile.user_id.active:
            raise BadRequest('Tin hoặc hồ sơ không tồn tại.')
        request.env.cr.execute('SELECT id FROM hr_job WHERE id = %s FOR UPDATE', [job.id])
        job.invalidate_recordset(['tacare_status', 'is_published'])
        if job.tacare_status != 'published' or not job.is_published or (job.tacare_deadline and job.tacare_deadline < fields.Date.today()):
            raise BadRequest('Tin hoặc hồ sơ không còn sẵn sàng.')
        if kind == 'application':
            self._require_candidate()
            if profile.user_id != self._user():
                raise Forbidden('Chỉ chủ hồ sơ được ứng tuyển.')
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
        elif not profile.care_recruitment_enabled:
            raise BadRequest('Chọn hồ sơ tuyển dụng cho tin tuyển dụng.')
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
        if kind == 'application' and job.care_opportunity_kind == 'recruitment':
            applicant = request.env['hr.applicant'].sudo().create({
                'partner_name': profile.name,
                'email_from': False,
                'job_id': job.id, 'company_id': job.company_id.id,
                'applicant_notes': vals['message'],
            })
            vals['applicant_id'] = applicant.id
        connection = request.env['tacare.connection'].sudo().create(vals)
        self._audit('connection.' + kind + '.sent', connection)
        self._notify(receiver, ('Có đề nghị ứng tuyển mới: ' if kind == 'application' else 'Có lời mời trao đổi mới: ') + job.name, connection)
        if kind == 'application':
            members = request.env['care.org.member'].sudo().search([
                ('organization_id', '=', job.tacare_owner_partner_id.id),
                ('company_id', '=', job.company_id.id), ('state', '=', 'active')])
            for member in members.filtered(lambda item: item.role in ('owner', 'recruiter') or item.can_handle_candidates):
                if member.user_id != receiver and member.user_id.active:
                    self._notify(member.user_id, 'Có đề nghị ứng tuyển mới: ' + job.name, connection)
        return request.redirect(f'/tacare/connection/{connection.id}?notice=sent')

    @http.route('/tacare/connections', type='http', auth='user', website=True)
    def connections(self, **kw):
        if self._role() == 'admin':
            domain = []
        elif self._is_business():
            domain = [('job_id.company_id', '=', request.env.company.id),
                      ('organization_id', 'in', self._authorized_organizations('handle').ids)]
        else:
            domain = [('profile_id.user_id', '=', self._user().id)]
        if kw.get('type') in ('application', 'invitation'):
            domain.append(('type', '=', kw['type']))
        items = request.env['tacare.connection'].sudo().search(domain, limit=100)
        return self._render('live_connections', items=items)

    @http.route('/tacare/connection/<int:connection_id>', type='http', auth='user', website=True)
    def connection_detail(self, connection_id, **kw):
        item = self._connection(connection_id)
        show_contact = (item.status == 'accepted' and item.contact_consent_id and
                        item.contact_consent_id.is_current('contact', item.organization_id, 'email'))
        can_respond = (item.status == 'pending' and (self._role() == 'admin' or
            item.type == 'application' and self._is_business() and
            item.organization_id in self._authorized_organizations('handle') or
            item.type == 'invitation' and self._is_candidate() and item.profile_id.user_id == self._user()))
        can_cancel = (item.status == 'pending' and (self._role() == 'admin' or
            item.sender_id == self._user() and (self._is_candidate() or
            item.organization_id in self._authorized_organizations('handle'))))
        return self._render('live_connection_detail', item=item, show_contact=show_contact,
                            can_respond=can_respond, can_cancel=can_cancel)

    @http.route('/tacare/connection/<int:connection_id>/contact', type='http', auth='user', methods=['POST'], website=True)
    def connection_contact(self, connection_id, **kw):
        item = self._connection(connection_id)
        if self._role() != 'candidate' or item.profile_id.user_id != self._user() or item.status != 'accepted':
            raise Forbidden('Chỉ ứng viên trong kết nối đã đồng ý được thay đổi quyền liên hệ.')
        action = kw.get('action')
        if action not in ('grant', 'revoke'):
            raise BadRequest('Thao tác chia sẻ không hợp lệ.')
        consent = item.contact_consent_id
        if action == 'revoke':
            if consent and consent.state == 'granted':
                consent.write({'state': 'revoked', 'revoked_at': fields.Datetime.now(),
                               'revoke_reason': 'Ứng viên thu hồi'})
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
        business_receiver = (item.type == 'application' and self._is_business() and
                             item.organization_id in self._authorized_organizations('handle'))
        candidate_receiver = item.type == 'invitation' and self._is_candidate() and item.profile_id.user_id == self._user()
        if not (self._role() == 'admin' or business_receiver or candidate_receiver) or item.status != 'pending':
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
        business_sender = (item.type == 'invitation' and item.sender_id == self._user() and
                           item.organization_id in self._authorized_organizations('handle'))
        candidate_sender = item.type == 'application' and self._is_candidate() and item.profile_id.user_id == self._user()
        if not (self._role() == 'admin' or business_sender or candidate_sender) or item.status != 'pending':
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
