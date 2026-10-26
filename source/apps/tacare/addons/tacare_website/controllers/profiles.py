"""Personal profile library: multiple profiles, explicit IDs, and an admin-only all tab."""
from odoo import http
from odoo.exceptions import ValidationError
from odoo.http import request
from werkzeug.exceptions import BadRequest, Forbidden, NotFound

from ..sites.tuhoso.flexible import ProfileFlexible


class TacareProfiles(ProfileFlexible):
    def _source_job(self, value):
        if not value:
            return request.env['hr.job'].sudo().browse()
        try:
            job_id = int(value)
        except (TypeError, ValueError):
            raise BadRequest('Tin tham khảo không hợp lệ.')
        job = request.env['hr.job'].sudo().search(self._job_domain() + [('id', '=', job_id)], limit=1)
        if not job:
            raise NotFound('Tin tham khảo không còn mở.')
        return job

    def _render(self, template, site='tacare', **values):
        if template in ('kvl_job_detail', 'kvl_candidate_detail') and '/tacare/job/' in request.httprequest.path:
            site = 'tacare'
        if template in ('work_form', 'live_profile', 'live_matching', 'kvl_job_detail') and not self._user()._is_public():
            values['own_profiles'] = request.env['tacare.profile'].sudo().search([
                ('user_id', '=', self._user().id), ('company_id', 'in', self._user().company_ids.ids), ('status', '!=', 'archived')], order='id desc')
        if template in ('live_profile', 'profile_overview', 'profile_metadata_editor') and values.get('profile'):
            profile = values['profile']
            values.update(degree_options=request.env['hr.recruitment.degree'].sudo().search([]),
                recruitment_gaps=profile._recruitment_gaps(),
                timeline_values={'%s-%s' % (kind, row.id): self._timeline_values(row, kind)
                    for kind, rows in [('experience', profile.experience_ids), ('education', profile.education_ids)] for row in rows})
        return super()._render(template, site=site, **values)

    @http.route('/tacare/job/<int:job_id>', auth='user', website=True, methods=['GET'])
    def matching_job(self, job_id, **kw):
        # Reuse published-job lookup, explicit owner profile selection and current
        # matching consent. Candidates keep the application flow inside TA.CARE.
        self._flex_user()
        if not request.env['hr.job'].sudo().search_count(self._job_domain() + [
                ('id', '=', job_id)]):
            raise NotFound()
        job = request.env['hr.job'].sudo().browse(job_id)
        if job.care_opportunity_kind == 'flexible':
            profile = self._my_profile()
            return self._render('work_detail', site='tacare', record=job, is_service=False,
                owner=False, profile=profile, matching_detail=True,
                reason=self._match(job, profile) if profile else False)
        return self.job_detail(job_id, **kw)

    def _flex_profile(self, create=False):
        self._flex_user()
        if request.params.get('profile_id'):
            return self._my_profile()
        profiles = request.env['tacare.profile'].sudo()
        if profiles.search_count([('user_id', '=', self._user().id)]):
            raise BadRequest('Chọn hồ sơ cụ thể để lưu công việc nhận làm.')
        if create:
            return profiles.create({'user_id': self._user().id, 'name': self._user().name,
                'profile_title': 'Hồ sơ nhận việc', 'care_recruitment_enabled': False,
                'scope': 'private', 'visible': False})
        return profiles

    @http.route()
    def profile_library(self, **kw):
        self._flex_user()
        kind = 'flexible'
        if kw.get('kind') == 'recruitment':
            raise NotFound()
        scope = kw.get('scope') or ('all' if self._role() == 'admin' else 'mine')
        if kind not in ('all', 'recruitment', 'flexible') or scope not in ('mine', 'all'):
            raise BadRequest('Bộ lọc hồ sơ không hợp lệ.')
        if scope == 'all' and self._role() != 'admin':
            raise Forbidden('Chỉ quản trị được xem toàn bộ hồ sơ.')
        company_ids = self._user().company_ids.ids
        domain = [('care_recruitment_enabled', '=', False), ('company_id', 'in', company_ids), ('status', '!=', 'archived')]
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
        if kw.get('kind') == 'recruitment':
            raise NotFound()
        job = self._source_job(kw.get('source_job_id'))
        vals = {**kw, 'kind': 'flexible'}
        if job:
            vals.setdefault('profile_title', 'Nhận ' + job.flex_category_id.name.lower())
        return self._render('profile_create', site='tuhoso', vals=vals, source_job=job, error=False)

    @http.route('/tuhoso/profiles/create', auth='user', website=True, methods=['POST'])
    def create_profile(self, **kw):
        self._flex_user()
        title = (kw.get('profile_title') or '').strip()
        kind = kw.get('kind')
        try:
            job = self._source_job(kw.get('source_job_id'))
        except NotFound:
            return self._render('profile_create', site='tuhoso', vals=kw, source_job=False,
                error='Tin tham khảo không còn mở. Tên bạn đã nhập được giữ lại; có thể tạo hồ sơ độc lập hoặc quay lại chọn tin khác.')
        if kind != 'flexible':
            raise BadRequest('Chỉ hỗ trợ hồ sơ nhận việc thời vụ.')
        if set(kw) - {'csrf_token', 'profile_title', 'kind', 'source_job_id'} or not 2 <= len(title) <= 160:
            return self._render('profile_create', site='tuhoso', vals=kw,
                source_job=job, error='Nhập tên hồ sơ nhận việc từ 2–160 ký tự.')
        profile = request.env['tacare.profile'].sudo().create({
            'user_id': self._user().id, 'name': self._user().name, 'profile_title': title,
            'care_recruitment_enabled': False, 'scope': 'private', 'visible': False,
            'source_job_id': job.id})
        self._audit('profile.created', profile)
        return request.redirect('/tuhoso/work/new?profile_id=%s%s' % (profile.id,
            '&source_job_id=%s' % job.id if job else ''))

    @http.route()
    def profile_public(self, profile_id, **kw):
        self._flex_user()
        company_ids = self._user().company_ids.ids
        domain = [('id', '=', profile_id), ('care_recruitment_enabled', '=', False), ('company_id', 'in', company_ids), ('status', '!=', 'archived')]
        if self._role() != 'admin':
            domain.append(('user_id', '=', self._user().id))
        profile = request.env['tacare.profile'].sudo().search(domain, limit=1)
        if not profile:
            raise NotFound()
        return self._render('profile_overview', site='tuhoso', profile=profile,
            owner=profile.user_id == self._user(), services=profile.capability_ids,
            matching_enabled=bool(self._current_consent(profile, 'matching')))

    @http.route('/tacare/job/<int:job_id>/profile/<int:profile_id>', auth='user', website=True, methods=['GET'])
    def hub_candidate_detail(self, job_id, profile_id, **kw):
        return self.kvl_candidate_detail(job_id, profile_id, **kw)
