"""Personal profile library: multiple profiles, explicit IDs, and an admin-only all tab."""
from odoo import http
from odoo.exceptions import ValidationError
from odoo.http import request
from werkzeug.exceptions import BadRequest, Forbidden, NotFound

from .flexible_work import TacareFlexible


class TacareProfiles(TacareFlexible):
    def _render(self, template, site='tacare', **values):
        if template == 'kvl_job_detail' and request.httprequest.path.startswith('/tacare/job/'):
            site = 'tacare'
        if template in ('work_form', 'live_profile', 'live_matching', 'kvl_job_detail') and not self._user()._is_public():
            values['own_profiles'] = request.env['tacare.profile'].sudo().search([
                ('user_id', '=', self._user().id), ('company_id', '=', request.env.company.id)], order='id desc')
        return super()._render(template, site=site, **values)

    @http.route('/tacare/job/<int:job_id>', auth='user', website=True, methods=['GET'])
    def matching_job(self, job_id, **kw):
        # Reuse published-job lookup, explicit owner profile selection and current
        # matching consent. Candidates keep the application flow inside TA.CARE.
        self._flex_user()
        if not request.env['hr.job'].sudo().search_count(self._job_domain() + [
                ('id', '=', job_id), ('care_opportunity_kind', '=', 'recruitment')]):
            raise NotFound()
        return self.job_detail(job_id, **kw)

    def _flex_profile(self, create=False):
        self._flex_user()
        if request.params.get('profile_id'):
            return self._my_profile()
        profiles = request.env['tacare.profile'].sudo()
        profile = profiles.search([('user_id', '=', self._user().id),
            ('company_id', '=', request.env.company.id), ('care_recruitment_enabled', '=', False)], order='id', limit=1)
        if not profile and create:
            profile = profiles.create({'user_id': self._user().id, 'name': self._user().name,
                'profile_title': 'Hồ sơ nhận việc', 'care_recruitment_enabled': False,
                'scope': 'private', 'visible': False})
        return profile

    @http.route()
    def profile_library(self, **kw):
        self._flex_user()
        kind = kw.get('kind') or 'all'
        scope = kw.get('scope') or ('all' if self._role() == 'admin' else 'mine')
        if kind not in ('all', 'recruitment', 'flexible') or scope not in ('mine', 'all'):
            raise BadRequest('Bộ lọc hồ sơ không hợp lệ.')
        if scope == 'all' and self._role() != 'admin':
            raise Forbidden('Chỉ quản trị được xem toàn bộ hồ sơ.')
        company_ids = self._user().company_ids.ids if self._role() == 'admin' else [request.env.company.id]
        domain = [('company_id', 'in', company_ids)]
        if scope == 'mine':
            domain.append(('user_id', '=', self._user().id))
        all_profiles = request.env['tacare.profile'].sudo().search(domain, order='write_date desc, id desc')
        counts = {'all': len(all_profiles),
            'recruitment': len(all_profiles.filtered('care_recruitment_enabled')),
            'flexible': len(all_profiles.filtered(lambda p: not p.care_recruitment_enabled or p.capability_ids))}
        profiles = all_profiles
        if kind == 'recruitment':
            profiles = profiles.filtered('care_recruitment_enabled')
        elif kind == 'flexible':
            profiles = profiles.filtered(lambda p: not p.care_recruitment_enabled or p.capability_ids)
        q = (kw.get('q') or '').strip().casefold()
        if q:
            profiles = profiles.filtered(lambda p: q in ' '.join([
                p.profile_title or '', p.name or '', p.headline or '', ', '.join(p.capability_ids.mapped('title'))]).casefold())
        if kind == 'recruitment' and kw.get('sector'):
            profiles = profiles.filtered(lambda p: p.sector == kw['sector'])
        if kind == 'flexible':
            for key, attr in [('category', 'category_id'), ('region', 'flex_region_id')]:
                if kw.get(key) and not kw[key].isdigit():
                    raise BadRequest('Bộ lọc không hợp lệ.')
            def selected(p):
                services = p.capability_ids
                for key, attr in [('category', 'category_id'), ('region', 'flex_region_id')]:
                    if kw.get(key):
                        services = services.filtered(lambda s: s[attr].id == int(kw[key]))
                for key, attr in [('mode', 'flex_mode'), ('unit', 'flex_pay_unit'), ('state', 'flex_state')]:
                    if kw.get(key):
                        services = services.filtered(lambda s: s[attr] == kw[key])
                return bool(services) if any(kw.get(k) for k in ('category','region','mode','unit','state')) else True
            profiles = profiles.filtered(selected)
        home = bool(kw.get('_home'))
        return self._render('profile_workspace', site='tuhoso', profiles=profiles,
            kind=kind, scope=scope, query=kw, counts=counts, home_page=home,
            workspace_base='/' if home else '/tuhoso/profiles')

    @http.route('/tuhoso/profiles/new', auth='user', website=True, methods=['GET'])
    def new_profile(self, **kw):
        self._flex_user()
        return self._render('profile_create', site='tuhoso', vals=kw, error=False)

    @http.route('/tuhoso/profiles/create', auth='user', website=True, methods=['POST'])
    def create_profile(self, **kw):
        self._flex_user()
        title = (kw.get('profile_title') or '').strip()
        kind = kw.get('kind')
        if set(kw) - {'csrf_token', 'profile_title', 'kind'} or not 2 <= len(title) <= 160 or kind not in ('recruitment', 'flexible'):
            return self._render('profile_create', site='tuhoso', vals=kw,
                error='Nhập tên hồ sơ từ 2–160 ký tự và chọn mục đích tạo hồ sơ.')
        profile = request.env['tacare.profile'].sudo().create({
            'user_id': self._user().id, 'name': self._user().name, 'profile_title': title,
            'care_recruitment_enabled': kind == 'recruitment', 'scope': 'private', 'visible': False})
        self._audit('profile.created', profile)
        url = '/tuhoso/me' if kind == 'recruitment' else '/tuhoso/work/new'
        return request.redirect('%s?profile_id=%s' % (url, profile.id))

    @http.route()
    def profile_public(self, profile_id, **kw):
        self._flex_user()
        company_ids = self._user().company_ids.ids if self._role() == 'admin' else [request.env.company.id]
        domain = [('id', '=', profile_id), ('company_id', 'in', company_ids)]
        if self._role() != 'admin':
            domain.append(('user_id', '=', self._user().id))
        profile = request.env['tacare.profile'].sudo().search(domain, limit=1)
        if not profile:
            raise NotFound()
        return self._render('profile_overview', site='tuhoso', profile=profile,
            owner=profile.user_id == self._user(), services=profile.capability_ids)
