"""Server-rendered local first experience backed by Odoo records."""
import math
from urllib.parse import urlsplit

from markupsafe import escape
from werkzeug.exceptions import BadRequest, Forbidden, NotFound

from odoo import http, fields
from odoo.http import request

from ...models.hr_job import SECTORS, TYPES, MODES, preferred_currency
from ..site_context import site_context


class SharedControllers(http.Controller):
    def _user(self):
        return request.env.user

    def _role(self):
        user = self._user()
        return 'admin' if user.has_group('base.group_system') else (user.sudo().tacare_account_role or 'pending')

    def _is_business(self):
        return self._role() in ('business', 'admin')

    def _is_candidate(self):
        return self._role() == 'candidate'

    def _require_business(self):
        if not self._is_business():
            raise Forbidden('Chỉ tài khoản doanh nghiệp hoặc quản trị được thực hiện.')

    def _require_candidate(self):
        if not self._is_candidate():
            raise Forbidden('Chỉ tài khoản cá nhân được thực hiện.')

    def _organizations(self):
        user = self._user().sudo()
        memberships = user.care_org_member_ids
        if memberships:
            return memberships.filtered(lambda item: item.state == 'active' and
                                        item.company_id == request.env.company).mapped('organization_id')
        if user.tacare_account_role == 'business' and user.company_id == request.env.company:
            return user.partner_id.commercial_partner_id
        return request.env['res.partner']

    def _editable_organizations(self):
        return self._authorized_organizations('manage')

    def _authorized_organizations(self, capability):
        user = self._user().sudo()
        memberships = user.care_org_member_ids.filtered(lambda item: item.company_id == request.env.company)
        if memberships:
            return memberships.filtered(lambda item: item.state == 'active' and
                (item.role == 'owner' or capability == 'handle' and item.role == 'recruiter' or
                 (item.can_manage_jobs if capability == 'manage' else item.can_handle_candidates))).mapped('organization_id')
        return self._organizations()

    def _organization(self, value=None):
        organizations = self._editable_organizations()
        if not organizations:
            raise Forbidden('Tài khoản chưa thuộc tổ chức đang hoạt động.')
        if value:
            try:
                organization = organizations.filtered(lambda item: item.id == int(value))
            except ValueError:
                raise BadRequest('Tổ chức không hợp lệ.')
            if not organization:
                raise Forbidden('Bạn không thuộc tổ chức này.')
            return organization[:1]
        if len(organizations) != 1:
            raise BadRequest('Cần chọn tổ chức đăng tin.')
        return organizations[:1]

    def _current_consent(self, profile, purpose, recipient=None, field=None):
        for consent in request.env['care.consent'].sudo().search([
            ('profile_id', '=', profile.id), ('purpose', '=', purpose), ('state', '=', 'granted')]):
            if self._user()._is_public() and consent.recipient_kind != 'public':
                continue
            if consent.is_current(purpose, recipient, field):
                return consent
        return False

    def _website(self, site):
        return request.env['website'].sudo().search([('domain', 'ilike', site)], limit=1)

    def _urls(self):
        host = (urlsplit('//' + request.httprequest.host).hostname or '').lower()
        local = host.endswith('.localhost') or host in ('localhost', '127.0.0.1')
        if local:
            return {key: f'http://{key}.localhost:8069/' for key in ('khovieclam', 'tuhoso', 'tacare')}
        return {'khovieclam': 'https://khovieclam.vn/', 'tuhoso': 'https://tuhoso.com/',
                'tacare': 'https://tacare.vn/'}

    def _render(self, template, site='tacare', **values):
        if template in ('live_connections', 'live_connection_detail', 'live_notifications') and \
                (urlsplit('//' + request.httprequest.host).hostname or '').startswith('khovieclam.'):
            site = 'khovieclam'
        from ..seasonal import marketplace_context
        if site in ('khovieclam', 'tuhoso') or template in ('profile_workspace', 'live_matching', 'matching_examples'):
            values.update(marketplace_context(request.env))
        sector_records = request.env['care.job.sector'].sudo().search([])
        values.setdefault('child_form', '')
        values.setdefault('child_id', 0)
        values.setdefault('child_values', {})
        values.update(site=site, role=self._role(), account_name=self._user().name,
                      is_guest=self._user()._is_public(), urls=self._urls(),
                      sectors=SECTORS, job_sectors=sector_records, types=TYPES, modes=MODES,
                      positions=request.env['care.job.position'].sudo().search([]),
                      regions=request.env['res.country.state'].sudo().search([('country_id.code', '=', 'VN')]),
                      currencies=request.env['res.currency'].sudo().search([('active', '=', True)]),
                      notice=request.params.get('notice'))
        values.update(site_context(site, values['urls']))
        response = request.render('tacare_website.' + template, values)
        response.headers['Cache-Control'] = 'private, no-store'
        return response

    def _job_domain(self):
        website = self._website('khovieclam')
        return [('care_opportunity_kind', '=', 'flexible'), ('tacare_status', '=', 'published'), ('is_published', '=', True),
                ('website_id', '=', website.id), ('company_id', '=', website.company_id.id), '|', ('tacare_deadline', '=', False),
                ('tacare_deadline', '>=', fields.Date.today())]

    def _visible_profiles(self, recipient=None):
        # Kho owns needs, Tu owns provider profiles. Crossing that product
        # boundary is discovery only: current purpose/recipient consent still
        # gates every returned profile; this grants no private-library access.
        company_ids = self._user().company_ids.ids if self._role() == 'admin' else self._website('tuhoso').company_id.ids
        profiles = request.env['tacare.profile'].sudo().search([
            ('company_id', 'in', company_ids), ('care_recruitment_enabled', '=', False), ('visible', '=', True), ('status', '=', 'active'), ('scope', '!=', 'private')])
        if self._user()._is_public():
            profiles = profiles.filtered(lambda item: item.scope == 'public')
        return profiles.filtered(lambda item: bool(self._current_consent(item, 'discovery', recipient, 'profile')))

    def _skills(self, text):
        return [item.strip() for item in (text or '').split(',') if item.strip()]

    def _catalog_skill(self, name):
        skills = request.env['hr.skill'].sudo()
        skill = skills.search([('name', '=ilike', name)], limit=1)
        if not skill:
            types = request.env['hr.skill.type'].sudo()
            skill_type = types.search([('name', '=', 'TA.CARE')], limit=1)
            if not skill_type:
                skill_type = types.create({'name': 'TA.CARE'})
            skill = skills.create({'name': name, 'skill_type_id': skill_type.id})
        return skill

    def _audit(self, action, record, reason='', changes=None):
        request.env['care.audit.event'].sudo().create({
            'company_id': request.env.company.id, 'actor_user_id': self._user().id,
            'action': action, 'target_model': record._name, 'target_res_id': record.id,
            'reason': reason[:250], 'changes': changes or {},
        })
