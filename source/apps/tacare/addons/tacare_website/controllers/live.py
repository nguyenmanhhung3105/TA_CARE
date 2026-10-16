"""Server-rendered local first experience backed by Odoo records."""
from urllib.parse import urlsplit

from markupsafe import escape
from werkzeug.exceptions import BadRequest, Forbidden, NotFound

from odoo import http, fields
from odoo.http import request

from ..models.hr_job import SECTORS, TYPES, MODES


class TacareLive(http.Controller):
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
            raise Forbidden('Chỉ tài khoản ứng viên được thực hiện.')

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
        sector_records = request.env['care.job.sector'].sudo().search([])
        values.update(site=site, role=self._role(), account_name=self._user().name,
                      is_guest=self._user()._is_public(), urls=self._urls(),
                      sectors=SECTORS, job_sectors=sector_records, types=TYPES, modes=MODES,
                      currencies=request.env['res.currency'].sudo().search([('active', '=', True)]),
                      notice=request.params.get('notice'))
        return request.render('tacare_website.' + template, values)

    def _own_job(self, job_id, capability='manage'):
        self._require_business()
        job = request.env['hr.job'].sudo().browse(job_id).exists()
        if not job or not job.tacare_owner_partner_id:
            raise NotFound()
        if self._role() != 'admin' and (job.company_id != request.env.company or
                                       job.tacare_owner_partner_id not in self._authorized_organizations(capability)):
            raise Forbidden('Tin thuộc tổ chức khác.')
        return job

    def _my_profile(self, create=False):
        self._require_candidate()
        profile = request.env['tacare.profile'].sudo().search([('user_id', '=', self._user().id)], limit=1)
        if not profile and create:
            profile = request.env['tacare.profile'].sudo().create({
                'user_id': self._user().id,
                'name': self._user().partner_id.name or self._user().name,
            })
        return profile

    def _my_child(self, model, record_id):
        profile = self._my_profile()
        item = request.env[model].sudo().browse(record_id).exists()
        if not item or item.profile_id != profile:
            raise Forbidden('Mục này không thuộc hồ sơ của bạn.')
        return item

    def _connection(self, connection_id):
        item = request.env['tacare.connection'].sudo().browse(connection_id).exists()
        business_access = (item and self._is_business() and item.job_id.company_id == request.env.company
                           and item.organization_id in self._authorized_organizations('handle'))
        candidate_access = item and self._is_candidate() and item.profile_id.user_id == self._user()
        if not item or self._role() != 'admin' and not business_access and not candidate_access:
            raise Forbidden('Kết nối không thuộc tài khoản này.')
        return item

    def _job_domain(self):
        website = self._website('khovieclam')
        return [('tacare_status', '=', 'published'), ('is_published', '=', True),
                ('website_id', '=', website.id)]

    def _visible_profiles(self, recipient=None):
        profiles = request.env['tacare.profile'].sudo().search([
            ('visible', '=', True), ('status', '=', 'active'), ('scope', '!=', 'private')])
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

    def _match(self, job, profile):
        names = {name.casefold() for name in profile.skill_ids.mapped('name')} if profile.user_id == self._user() or self._current_consent(profile, 'matching', job.tacare_owner_partner_id, 'skills') else set()
        required = self._skills(job.tacare_required_skills)
        preferred = self._skills(job.tacare_preferred_skills)
        matched = [name for name in required if name.casefold() in names]
        missing = [name for name in required if name.casefold() not in names]
        preferred_found = [name for name in preferred if name.casefold() in names]
        same_mode = bool(profile.mode) and (not job.tacare_mode or profile.mode == job.tacare_mode or
                                              'hybrid' in (profile.mode, job.tacare_mode))
        same_location = bool(profile.location) and (job.tacare_mode == 'remote' or
                                                     (job.tacare_location or '').casefold() == profile.location.casefold())
        return {'matched': matched, 'missing': missing,
                'preferred_found': preferred_found, 'same_mode': same_mode,
                'same_location': same_location}

    def _notify(self, user, text, connection=None):
        request.env['tacare.notification'].sudo().create({
            'user_id': user.id, 'message': text,
            'connection_id': connection.id if connection else False,
        })

    def _audit(self, action, record, reason='', changes=None):
        request.env['care.audit.event'].sudo().create({
            'company_id': request.env.company.id, 'actor_user_id': self._user().id,
            'action': action, 'target_model': record._name, 'target_res_id': record.id,
            'reason': reason[:250], 'changes': changes or {},
        })

    def _requirement_inputs(self):
        form = request.httprequest.form
        categories = form.getlist('requirement_category')
        names = form.getlist('requirement_name')
        priorities = form.getlist('requirement_priority')
        allowed = dict(request.env['care.job.requirement']._fields['category'].selection)
        if not (len(categories) == len(names) == len(priorities)) or len(names) > 40:
            raise BadRequest('Danh sách điều kiện không hợp lệ.')
        rows = []
        for category, name, priority in zip(categories, names, priorities):
            name = name.strip()
            if not name:
                continue
            if category not in allowed or priority not in ('mandatory', 'preferred') or not 2 <= len(name) <= 200:
                raise BadRequest('Điều kiện tuyển dụng không hợp lệ.')
            rows.append({'category': category, 'name': name, 'mandatory': priority == 'mandatory'})
        return rows

    def _replace_requirements(self, job, rows):
        requirements = request.env['care.job.requirement'].sudo()
        requirements.search([('job_id', '=', job.id)]).unlink()
        for index, row in enumerate(rows):
            requirements.create({'job_id': job.id, 'sequence': (index + 1) * 10, **row})
        job._care_sync_requirement_skills()

    def _job_form_values(self, job, overrides=None):
        mapping = {
            'name': 'name', 'position': 'care_position', 'sector_id': 'care_sector_id',
            'type': 'tacare_type', 'level': 'care_level', 'mode': 'tacare_mode',
            'work_fraction': 'care_work_fraction', 'location': 'tacare_location',
            'quantity': 'no_of_recruitment', 'start': 'tacare_start',
            'deadline': 'tacare_deadline', 'days_per_week': 'care_days_per_week',
            'duration_months': 'care_duration_months', 'shift_note': 'care_shift_note',
            'income_type': 'care_income_type', 'income_period': 'care_income_period',
            'salary_min': 'care_salary_min', 'salary_max': 'care_salary_max',
            'currency_id': 'care_currency_id',
            'experience_min': 'care_experience_min', 'schedule': 'tacare_schedule',
            'pay': 'tacare_pay', 'required_skills': 'tacare_required_skills',
            'preferred_skills': 'tacare_preferred_skills',
            'description': 'tacare_description_text', 'outcome': 'tacare_outcome',
        }
        values = {}
        if job:
            for source, target in mapping.items():
                value = job[target]
                values[source] = str(value.id if target == 'care_sector_id' and value else value or '')
            if not job.care_sector_id and job.tacare_sector:
                legacy_sector = request.env['care.job.sector'].sudo().search([
                    ('code', '=', job.tacare_sector)], limit=1)
                if legacy_sector:
                    values['sector_id'] = str(legacy_sector.id)
            for checkbox, target in [('matching_enabled', 'care_matching_enabled'),
                                     ('requires_travel', 'care_requires_travel'),
                                     ('requires_license', 'care_requires_license'),
                                     ('requires_portfolio', 'care_requires_portfolio'),
                                     ('requires_clinical', 'care_requires_clinical')]:
                values[checkbox] = 'on' if job[target] else ''
        if overrides:
            values.update(overrides)
        values.setdefault('currency_id', str(request.env.company.currency_id.id))
        return values

    def _job_form_error(self, job, submitted, rows, field, message):
        owners = request.env['res.users'].sudo().search([
            ('tacare_account_role', '=', 'business')]) if self._role() == 'admin' else False
        return self._render('kvl_job_form', site='khovieclam', job=job, owners=owners,
            organizations=self._editable_organizations() if self._role() != 'admin' else False,
            error='Kiểm tra trường được đánh dấu bên dưới.', field_errors={field: message},
            vals=self._job_form_values(job, submitted), requirements=rows,
            requirement_types=request.env['care.job.requirement']._fields['category'].selection)

    @http.route('/kvl/jobs', type='http', auth='public', website=True)
    def jobs(self, **kw):
        jobs = request.env['hr.job'].sudo().search(self._job_domain(), order='create_date desc')
        query = (kw.get('q') or '').strip().casefold()
        sector = kw.get('sector') or ''
        kind = kw.get('type') or ''
        if query:
            jobs = jobs.filtered(lambda item: query in (item.name or '').casefold() or
                                 query in (item.tacare_location or '').casefold())
        if sector:
            jobs = jobs.filtered(lambda item: item.care_sector_id.code == sector or item.tacare_sector == sector)
        if kind:
            jobs = jobs.filtered(lambda item: item.tacare_type == kind)
        return self._render('live_jobs', site='khovieclam', jobs=jobs, query=kw)

    @http.route('/kvl/job/<int:job_id>', type='http', auth='public', website=True)
    def job_detail(self, job_id, **kw):
        job = request.env['hr.job'].sudo().search(self._job_domain() + [('id', '=', job_id)], limit=1)
        if not job:
            raise NotFound()
        profile = self._my_profile() if self._is_candidate() else False
        can_match = profile and job.care_matching_enabled and self._current_consent(profile, 'matching')
        return self._render('kvl_job_detail', site='khovieclam', job=job,
                            required=self._skills(job.tacare_required_skills),
                            preferred=self._skills(job.tacare_preferred_skills),
                            profile=profile, match=self._match(job, profile) if can_match else False,
                            preview=False)

    @http.route('/kvl/job/<int:job_id>/preview', type='http', auth='user', website=True)
    def job_preview(self, job_id, **kw):
        job = self._own_job(job_id)
        return self._render('kvl_job_detail', site='khovieclam', job=job,
                            required=self._skills(job.tacare_required_skills),
                            preferred=self._skills(job.tacare_preferred_skills),
                            profile=False, match=False, preview=True)

    @http.route('/kvl/job/<int:job_id>/history', type='http', auth='user', website=True)
    def job_history(self, job_id, **kw):
        job = self._own_job(job_id)
        events = request.env['care.audit.event'].sudo().search([
            ('target_model', '=', 'hr.job'), ('target_res_id', '=', job.id)],
            order='occurred_at desc, id desc', limit=100)
        return self._render('kvl_job_history', site='khovieclam', job=job, events=events)

    @http.route('/kvl/manage', type='http', auth='user', website=True)
    def manage_jobs(self, **kw):
        self._require_business()
        domain = [('tacare_owner_partner_id', '!=', False)]
        if self._role() != 'admin':
            domain.extend([('company_id', '=', request.env.company.id),
                           ('tacare_owner_partner_id', 'in', self._organizations().ids)])
        status = kw.get('status')
        if status in ('draft', 'published', 'paused', 'closed'):
            domain.append(('tacare_status', '=', status))
        keyword = (kw.get('q') or '').strip()
        if keyword:
            domain.append(('name', 'ilike', keyword[:100]))
        date_from = kw.get('date_from') or ''
        date_to = kw.get('date_to') or ''
        try:
            if date_from:
                fields.Date.to_date(date_from)
                domain.append(('create_date', '>=', date_from))
            if date_to:
                fields.Date.to_date(date_to)
                domain.append(('create_date', '<=', date_to + ' 23:59:59'))
        except (TypeError, ValueError):
            raise BadRequest('Khoảng thời gian không hợp lệ.')
        jobs = request.env['hr.job'].sudo().search(domain, order='create_date desc')
        revisions = request.env['care.job.revision'].sudo().search([
            ('job_id', 'in', jobs.ids), ('state', '=', 'submitted')], order='create_date desc')
        pending = request.env['tacare.connection'].sudo().search([
            ('job_id', 'in', jobs.ids), ('status', '=', 'pending')])
        pending_counts = {job.id: len(pending.filtered(lambda item: item.job_id == job)) for job in jobs}
        return self._render('kvl_manage_jobs', site='khovieclam', jobs=jobs,
                            revisions=revisions, editable_org_ids=self._editable_organizations().ids,
                            organizations=self._editable_organizations(),
                            selected_status=status or '', query=kw, pending_counts=pending_counts)

    @http.route('/kvl/organization/<int:organization_id>', type='http', auth='user', website=True)
    def organization_form(self, organization_id, **kw):
        self._require_business()
        organization = self._editable_organizations().filtered(lambda item: item.id == organization_id)[:1]
        if not organization and self._role() != 'admin':
            raise Forbidden('Bạn chưa được cấp quyền quản lý tổ chức này.')
        organization = organization or request.env['res.partner'].sudo().browse(organization_id).exists()
        if not organization or not organization.is_company:
            raise NotFound()
        return self._render('kvl_organization_form', site='khovieclam', organization=organization)

    @http.route('/kvl/organization/<int:organization_id>/save', type='http', auth='user', methods=['POST'], website=True)
    def organization_save(self, organization_id, **kw):
        self._require_business()
        organization = self._editable_organizations().filtered(lambda item: item.id == organization_id)[:1]
        if not organization and self._role() != 'admin':
            raise Forbidden('Bạn chưa được cấp quyền quản lý tổ chức này.')
        organization = organization or request.env['res.partner'].sudo().browse(organization_id).exists()
        if not organization or not organization.is_company:
            raise NotFound()
        try:
            ids = [int(value) for value in request.httprequest.form.getlist('sector_ids')]
        except ValueError:
            raise BadRequest('Lĩnh vực không hợp lệ.')
        sectors = request.env['care.job.sector'].sudo().browse(ids).exists()
        if len(sectors) != len(set(ids)):
            raise BadRequest('Lĩnh vực không hợp lệ.')
        scope = (kw.get('market_scope') or '').strip()[:160]
        old = {'sectors': organization.care_business_sector_ids.mapped('name'),
               'market_scope': organization.care_market_scope or ''}
        organization.sudo().write({'care_business_sector_ids': [(6, 0, sectors.ids)],
                                   'care_market_scope': scope})
        self._audit('organization.recruitment.updated', organization, 'Cập nhật lĩnh vực và thị trường',
                    {'before': old, 'after': {'sectors': sectors.mapped('name'), 'market_scope': scope}})
        return request.redirect('/kvl/manage?notice=organization')

    @http.route(['/kvl/job/new', '/kvl/job/<int:job_id>/edit'], type='http', auth='user', website=True)
    def job_form(self, job_id=None, **kw):
        self._require_business()
        if self._role() != 'admin' and not self._editable_organizations():
            raise Forbidden('Bạn chỉ có quyền xem tổ chức, chưa được sửa tin.')
        job = self._own_job(job_id) if job_id else False
        owners = request.env['res.users'].sudo().search([('tacare_account_role', '=', 'business')]) if self._role() == 'admin' else False
        return self._render('kvl_job_form', site='khovieclam', job=job, owners=owners,
                            organizations=self._editable_organizations() if self._role() != 'admin' else False,
                            error=False, field_errors={}, vals=self._job_form_values(job),
                            requirements=[{'category': row.category, 'name': row.name,
                                           'mandatory': row.mandatory} for row in job.care_requirement_ids] if job else [],
                            requirement_types=request.env['care.job.requirement']._fields['category'].selection)

    @http.route('/kvl/job/save', type='http', auth='user', methods=['POST'], website=True)
    def job_save(self, **kw):
        self._require_business()
        raw_id = kw.get('job_id') or ''
        try:
            job = self._own_job(int(raw_id)) if raw_id else False
        except ValueError:
            raise BadRequest('ID tin không hợp lệ.')
        if job:
            request.env.cr.execute('SELECT id FROM hr_job WHERE id = %s FOR UPDATE', [job.id])
            job.invalidate_recordset(['tacare_status', 'care_revision'])
        intent = kw.get('intent')
        if intent not in ('draft', 'publish'):
            raise BadRequest('Thao tác không hợp lệ.')
        if intent == 'publish' and kw.get('publish_confirm') != 'yes':
            raise BadRequest('Cần xác nhận trước khi đăng tin.')
        if intent == 'publish' and job and job.tacare_status != 'draft':
            raise BadRequest('Chỉ tin Nháp được đăng bằng thao tác này.')
        rows = self._requirement_inputs()
        sector_id = kw.get('sector_id') or ''
        try:
            sector = request.env['care.job.sector'].sudo().browse(int(sector_id)).exists() if sector_id else False
        except ValueError:
            raise BadRequest('Ngành nghề không hợp lệ.')
        if sector_id and not sector:
            raise BadRequest('Ngành nghề không hợp lệ.')
        try:
            currency_id = int(kw.get('currency_id') or request.env.company.currency_id.id)
        except ValueError:
            raise BadRequest('Đơn vị tiền tệ không hợp lệ.')
        currency = request.env['res.currency'].sudo().browse(currency_id).exists()
        if not currency or not currency.active:
            raise BadRequest('Đơn vị tiền tệ không hợp lệ.')
        vals = {
            'name': (kw.get('name') or '').strip(),
            'tacare_sector': sector.code if sector and sector.code in dict(SECTORS) else False,
            'care_sector_id': sector.id if sector else False,
            'care_position': (kw.get('position') or '').strip()[:160],
            'care_level': kw.get('level') or False,
            'care_work_fraction': kw.get('work_fraction') or False,
            'care_shift_note': (kw.get('shift_note') or '').strip()[:160],
            'care_income_type': kw.get('income_type') or False,
            'care_income_period': kw.get('income_period') or False,
            'care_currency_id': currency.id,
            'care_requires_travel': kw.get('requires_travel') == 'on',
            'care_requires_license': kw.get('requires_license') == 'on',
            'care_requires_portfolio': kw.get('requires_portfolio') == 'on',
            'care_requires_clinical': kw.get('requires_clinical') == 'on',
            'tacare_type': kw.get('type') or False,
            'tacare_mode': kw.get('mode') or False,
            'tacare_location': (kw.get('location') or '').strip(),
            'tacare_required_skills': (kw.get('required_skills') or '').strip(),
            'tacare_preferred_skills': (kw.get('preferred_skills') or '').strip(),
            'tacare_schedule': (kw.get('schedule') or '').strip(),
            'tacare_pay': (kw.get('pay') or '').strip(),
            'tacare_outcome': (kw.get('outcome') or '').strip(),
            'tacare_description_text': (kw.get('description') or '').strip(),
            'description': '<p>%s</p>' % escape((kw.get('description') or '').strip()),
            'website_description': '<p>%s</p>' % escape((kw.get('description') or '').strip()),
            'care_matching_enabled': kw.get('matching_enabled') == 'on',
        }
        if len(vals['name']) < 2:
            return self._render('kvl_job_form', site='khovieclam', job=job,
                owners=request.env['res.users'].sudo().search([('tacare_account_role', '=', 'business')]) if self._role() == 'admin' else False,
                organizations=self._editable_organizations() if self._role() != 'admin' else False,
                error='Tiêu đề cần ít nhất hai ký tự để lưu nháp.',
                field_errors={'name': 'Nhập ít nhất hai ký tự.'}, vals=self._job_form_values(job, kw),
                requirements=rows, requirement_types=request.env['care.job.requirement']._fields['category'].selection)
        for source, target in [('days_per_week', 'care_days_per_week'), ('duration_months', 'care_duration_months')]:
            try:
                vals[target] = int(kw.get(source) or 0)
            except ValueError:
                return self._job_form_error(job, kw, rows, source, 'Nhập số nguyên không âm.')
        if not 0 <= vals['care_days_per_week'] <= 7:
            return self._job_form_error(job, kw, rows, 'days_per_week', 'Số ngày mỗi tuần phải từ 0 đến 7.')
        if vals['care_duration_months'] < 0:
            return self._job_form_error(job, kw, rows, 'duration_months', 'Thời lượng không được âm.')
        for source, options in [('care_level', 'level'), ('care_work_fraction', 'work_fraction'),
                                ('care_income_type', 'income_type'), ('care_income_period', 'income_period')]:
            if vals[source] and vals[source] not in dict(request.env['hr.job']._fields[source].selection):
                raise BadRequest('Giá trị ' + options + ' không hợp lệ.')
        for source, target in [('experience_min', 'care_experience_min'),
                               ('salary_min', 'care_salary_min'), ('salary_max', 'care_salary_max')]:
            try:
                vals[target] = float(kw.get(source) or 0)
            except ValueError:
                return self._job_form_error(job, kw, rows, source, 'Nhập một số hợp lệ.')
            if vals[target] < 0:
                return self._job_form_error(job, kw, rows, source, 'Giá trị không được âm.')
        if vals['care_salary_max'] and vals['care_salary_max'] < vals['care_salary_min']:
            return self._job_form_error(job, kw, rows, 'salary_max', 'Mức cao nhất phải từ mức thấp nhất trở lên.')
        try:
            vals['no_of_recruitment'] = max(1, int(kw.get('quantity') or '1'))
        except ValueError:
            return self._job_form_error(job, kw, rows, 'quantity', 'Nhập số lượng hợp lệ.')
        for source, target in [('start', 'tacare_start'), ('deadline', 'tacare_deadline')]:
            value = kw.get(source) or False
            try:
                vals[target] = fields.Date.to_string(fields.Date.to_date(value)) if value else False
            except (ValueError, TypeError):
                return self._job_form_error(job, kw, rows, source, 'Ngày không hợp lệ.')
        if vals['tacare_type'] and vals['tacare_type'] not in dict(TYPES):
            raise BadRequest('Loại cơ hội không hợp lệ.')
        if vals['tacare_mode'] and vals['tacare_mode'] not in dict(MODES):
            raise BadRequest('Hình thức không hợp lệ.')
        field_errors = {}
        if intent == 'publish':
            for key, value, label in [
                ('position', vals['care_position'], 'Nhập vị trí tuyển dụng.'),
                ('sector_id', sector, 'Chọn ngành nghề.'),
                ('type', vals['tacare_type'], 'Chọn loại cơ hội.'),
                ('mode', vals['tacare_mode'], 'Chọn hình thức làm việc.'),
                ('description', vals['tacare_description_text'], 'Nhập mô tả công việc.'),
                ('deadline', vals['tacare_deadline'], 'Chọn hạn nhận đề nghị.'),
            ]:
                if not value:
                    field_errors[key] = label
            if vals['tacare_mode'] != 'remote' and not vals['tacare_location']:
                field_errors['location'] = 'Nhập địa điểm nếu không làm từ xa.'
            if not vals['tacare_required_skills'] and not any(row['mandatory'] for row in rows):
                field_errors['requirements'] = 'Cần ít nhất một kỹ năng hoặc điều kiện bắt buộc.'
            if vals['tacare_deadline'] and vals['tacare_deadline'] < fields.Date.today().isoformat():
                field_errors['deadline'] = 'Hạn nhận đề nghị đã qua.'
        if vals['tacare_start'] and vals['tacare_deadline'] and vals['tacare_deadline'] < vals['tacare_start']:
            field_errors['deadline'] = 'Hạn nhận phải sau ngày bắt đầu.'
        if field_errors:
            owners = request.env['res.users'].sudo().search([('tacare_account_role', '=', 'business')]) if self._role() == 'admin' else False
            return self._render('kvl_job_form', site='khovieclam', job=job, owners=owners,
                                organizations=self._editable_organizations() if self._role() != 'admin' else False,
                                error='Kiểm tra các trường được đánh dấu bên dưới.', field_errors=field_errors,
                                vals=self._job_form_values(job, kw), requirements=rows,
                                requirement_types=request.env['care.job.requirement']._fields['category'].selection)
        if not job:
            if self._role() == 'admin':
                try:
                    owner_id = int(kw.get('owner_id') or 0)
                except ValueError:
                    raise BadRequest('Tổ chức không hợp lệ.')
                owner = request.env['res.users'].sudo().search([('id', '=', owner_id),
                                                                 ('tacare_account_role', '=', 'business')], limit=1)
                if not owner:
                    raise BadRequest('Chọn tài khoản doanh nghiệp sở hữu tin.')
            else:
                owner = self._user()
            organization = (owner.partner_id.commercial_partner_id if self._role() == 'admin'
                            else self._organization(kw.get('organization_id')))
            vals.update(tacare_owner_partner_id=organization.id,
                        tacare_owner_user_id=owner.id, website_id=self._website('khovieclam').id,
                        company_id=request.env.company.id, user_id=False)
        if job and job.tacare_status == 'published' and self._role() != 'admin':
            if request.env['care.job.revision'].sudo().search_count([
                ('job_id', '=', job.id), ('state', '=', 'submitted')]):
                raise BadRequest('Tin đang có bản sửa chờ duyệt.')
            version = max([job.care_revision] + job.care_revision_ids.mapped('version')) + 1
            request.env['care.job.revision'].sudo().create({
                'job_id': job.id, 'version': version, 'payload': {**vals, '_requirements': rows},
                'state': 'submitted', 'submitted_by': self._user().id})
            changes = {key: {'before': str(job[key] or ''), 'proposed': str(value or '')}
                       for key, value in vals.items() if str(job[key] or '') != str(value or '')}
            changes['requirements'] = {'before': [
                {'category': item.category, 'name': item.name, 'mandatory': item.mandatory}
                for item in job.care_requirement_ids], 'proposed': rows}
            self._audit('job.revision.submitted', job, 'Bản sửa chờ duyệt', changes)
            return request.redirect('/kvl/manage?notice=revision')
        old_values = {key: str(job[key] or '') for key in vals} if job else {}
        old_requirements = ([{'category': row.category, 'name': row.name, 'mandatory': row.mandatory}
                             for row in job.care_requirement_ids] if job else [])
        vals.update(tacare_status='published' if intent == 'publish' else (job.tacare_status if job else 'draft'),
                    website_published=intent == 'publish' or bool(job and job.tacare_status == 'published'),
                    is_published=intent == 'publish' or bool(job and job.tacare_status == 'published'))
        if job:
            job.write(vals)
        else:
            job = request.env['hr.job'].sudo().create(vals)
        self._replace_requirements(job, rows)
        if intent == 'publish' and job._care_publish_errors():
            raise BadRequest('Tin chưa đủ điều kiện đăng: ' + ', '.join(job._care_publish_errors()))
        job._care_sync_job_skills()
        changes = {key: {'before': old_values.get(key, ''), 'after': str(job[key] or '')}
                   for key in vals if old_values.get(key, '') != str(job[key] or '')}
        if old_requirements != rows:
            changes['requirements'] = {'before': old_requirements, 'after': rows}
        self._audit('job.created' if not raw_id else 'job.updated', job,
                    'Đăng tin' if intent == 'publish' else 'Lưu nội dung', changes)
        return request.redirect('/kvl/manage?notice=saved')

    @http.route('/kvl/revision/<int:revision_id>/review', type='http', auth='user', methods=['POST'], website=True)
    def revision_review(self, revision_id, **kw):
        if self._role() != 'admin':
            raise Forbidden('Chỉ quản trị được duyệt thay đổi tin.')
        revision = request.env['care.job.revision'].sudo().browse(revision_id).exists()
        if revision:
            request.env.cr.execute('SELECT id FROM care_job_revision WHERE id = %s FOR UPDATE', [revision.id])
            revision.invalidate_recordset(['state'])
        if not revision or revision.state != 'submitted':
            raise NotFound()
        decision = kw.get('decision')
        if decision == 'approve':
            revision.action_publish(self._user(), (kw.get('note') or '')[:1000])
            self._audit('job.revision.approved', revision.job_id,
                        'Phiên bản %s đã áp dụng' % revision.version,
                        {'revision': {'before': 'submitted', 'after': 'published'}})
        elif decision == 'reject':
            revision.write({'state': 'rejected', 'reviewed_by': self._user().id,
                            'reviewed_at': fields.Datetime.now(), 'review_note': (kw.get('note') or '')[:1000]})
            self._audit('job.revision.rejected', revision.job_id,
                        'Phiên bản %s bị từ chối' % revision.version,
                        {'revision': {'before': 'submitted', 'after': 'rejected'}})
        else:
            raise BadRequest('Quyết định không hợp lệ.')
        return request.redirect('/kvl/manage?notice=review')

    @http.route('/kvl/job/<int:job_id>/status', type='http', auth='user', methods=['POST'], website=True)
    def job_status(self, job_id, **kw):
        job = self._own_job(job_id)
        request.env.cr.execute('SELECT id FROM hr_job WHERE id = %s FOR UPDATE', [job.id])
        job.invalidate_recordset(['tacare_status'])
        new = kw.get('status')
        allowed = {'draft': ('published',), 'published': ('paused', 'closed'),
                   'paused': ('published', 'closed'), 'closed': ('published',)}
        if new not in allowed[job.tacare_status]:
            raise BadRequest('Không thể chuyển trạng thái tin.')
        if kw.get('confirm') != 'yes':
            raise BadRequest('Cần xác nhận thao tác.')
        if new == 'published' and job._care_publish_errors():
            raise BadRequest('Tin chưa đủ dữ liệu: ' + ', '.join(job._care_publish_errors()))
        old = job.tacare_status
        job.write({'tacare_status': new, 'website_published': new == 'published',
                   'is_published': new == 'published'})
        self._audit('job.status.' + new, job,
                    'Đã xác nhận còn nhu cầu tuyển dụng' if new == 'published' else '',
                    {'status': {'before': old, 'after': new}})
        return request.redirect('/kvl/manage?notice=status')

    @http.route('/kvl/job/<int:job_id>/delete', type='http', auth='user', methods=['POST'], website=True)
    def job_delete(self, job_id, **kw):
        job = self._own_job(job_id)
        request.env.cr.execute('SELECT id FROM hr_job WHERE id = %s FOR UPDATE', [job.id])
        job.invalidate_recordset(['tacare_status'])
        if job.tacare_status != 'draft' or kw.get('confirm') != 'yes':
            raise BadRequest('Chỉ được xóa bản nháp sau khi xác nhận.')
        if request.env['tacare.connection'].sudo().search_count([('job_id', '=', job.id)]):
            raise BadRequest('Tin đã có kết nối, không thể xóa.')
        self._audit('job.draft.deleted', job, job.name)
        job.unlink()
        return request.redirect('/kvl/manage?notice=deleted')

    @http.route('/tuhoso/me', type='http', auth='user', website=True)
    def my_profile(self, **kw):
        profile = self._my_profile(create=True)
        return self._render('live_profile', site='tuhoso', profile=profile, edit=True,
                            evidence_items=profile.evidence_ids, skill_items=profile.skill_ids,
                            matching_enabled=bool(self._current_consent(profile, 'matching')))

    @http.route('/tuhoso/profile/<int:profile_id>', type='http', auth='public', website=True)
    def profile_public(self, profile_id, **kw):
        profile = self._visible_profiles().filtered(lambda item: item.id == profile_id)[:1]
        if not profile:
            raise NotFound()
        evidence_items = profile.evidence_ids.filtered(
            lambda item: item.visibility == 'public' or
            item.visibility == 'members' and not self._user()._is_public())
        if not self._current_consent(profile, 'discovery', field='evidence'):
            evidence_items = request.env['tacare.profile.evidence']
        skill_items = profile.skill_ids if self._current_consent(profile, 'discovery', field='skills') else request.env['tacare.profile.skill']
        return self._render('live_profile', site='tuhoso', profile=profile, edit=False,
                            evidence_items=evidence_items, skill_items=skill_items)

    @http.route('/tuhoso/profile/save', type='http', auth='user', methods=['POST'], website=True)
    def profile_save(self, **kw):
        profile = self._my_profile(create=True)
        vals = {key: (kw.get(key) or '').strip() for key in
                ('name', 'headline', 'education', 'location', 'goal', 'availability', 'pay')}
        if len(vals['name']) < 2:
            return self._render('live_profile', site='tuhoso', profile=profile, edit=True,
                                evidence_items=profile.evidence_ids, skill_items=profile.skill_ids,
                                matching_enabled=bool(self._current_consent(profile, 'matching')),
                                error='Tên cần ít nhất hai ký tự.')
        for key, allowed in [('sector', SECTORS), ('mode', MODES)]:
            value = kw.get(key) or False
            if value and value not in dict(allowed):
                raise BadRequest('Giá trị không hợp lệ.')
            vals[key] = value
        profile.write(vals)
        return request.redirect('/tuhoso/me?notice=profile')

    @http.route('/tuhoso/skill/add', type='http', auth='user', methods=['POST'], website=True)
    def skill_add(self, **kw):
        profile = self._my_profile(create=True)
        name = (kw.get('name') or '').strip()
        if not name or len(name) > 80:
            raise BadRequest('Tên kỹ năng không hợp lệ.')
        if profile.skill_ids.filtered(lambda item: item.name.casefold() == name.casefold()):
            raise BadRequest('Kỹ năng đã có trong hồ sơ.')
        level = kw.get('level') or 'basic'
        if level not in dict(request.env['tacare.profile.skill']._fields['level'].selection):
            raise BadRequest('Mức độ không hợp lệ.')
        skill = self._catalog_skill(name)
        request.env['tacare.profile.skill'].sudo().create({
            'profile_id': profile.id, 'name': name, 'level': level, 'skill_id': skill.id,
            'use': (kw.get('use') or '').strip()[:250],
        })
        return request.redirect('/tuhoso/me?notice=skill')

    @http.route('/tuhoso/skill/<int:skill_id>/save', type='http', auth='user', methods=['POST'], website=True)
    def skill_save(self, skill_id, **kw):
        skill = self._my_child('tacare.profile.skill', skill_id)
        name = (kw.get('name') or '').strip()
        level = kw.get('level') or 'basic'
        if not name or len(name) > 80 or level not in dict(skill._fields['level'].selection):
            raise BadRequest('Kỹ năng không hợp lệ.')
        duplicates = skill.profile_id.skill_ids.filtered(lambda item: item.id != skill.id and item.name.casefold() == name.casefold())
        if duplicates:
            raise BadRequest('Kỹ năng đã có trong hồ sơ.')
        skill.write({'name': name, 'level': level, 'skill_id': self._catalog_skill(name).id,
                     'use': (kw.get('use') or '').strip()[:250]})
        return request.redirect('/tuhoso/me?notice=skill')

    @http.route('/tuhoso/skill/<int:skill_id>/delete', type='http', auth='user', methods=['POST'], website=True)
    def skill_delete(self, skill_id, **kw):
        self._my_child('tacare.profile.skill', skill_id).unlink()
        return request.redirect('/tuhoso/me?notice=skill')

    @http.route('/tuhoso/evidence/add', type='http', auth='user', methods=['POST'], website=True)
    def evidence_add(self, **kw):
        profile = self._my_profile(create=True)
        title = (kw.get('title') or '').strip()
        role = (kw.get('role') or '').strip()
        if not title or not role:
            raise BadRequest('Nhập tên và vai trò của minh chứng.')
        url = (kw.get('url') or '').strip()[:400]
        if url and urlsplit(url).scheme not in ('http', 'https'):
            raise BadRequest('Liên kết minh chứng phải dùng http hoặc https.')
        request.env['tacare.profile.evidence'].sudo().create({
            'profile_id': profile.id, 'title': title[:160], 'role': role[:160],
            'description': (kw.get('description') or '').strip(),
            'result': (kw.get('result') or '').strip()[:250],
            'url': url, 'visibility': 'private',
        })
        return request.redirect('/tuhoso/me?notice=evidence')

    @http.route('/tuhoso/evidence/<int:evidence_id>/save', type='http', auth='user', methods=['POST'], website=True)
    def evidence_save(self, evidence_id, **kw):
        evidence = self._my_child('tacare.profile.evidence', evidence_id)
        title, role = (kw.get('title') or '').strip(), (kw.get('role') or '').strip()
        url = (kw.get('url') or '').strip()[:400]
        if not title or not role or url and urlsplit(url).scheme not in ('http', 'https'):
            raise BadRequest('Tên, vai trò hoặc liên kết minh chứng không hợp lệ.')
        visibility = kw.get('visibility') or 'private'
        if visibility not in ('private', 'members', 'public'):
            raise BadRequest('Phạm vi minh chứng không hợp lệ.')
        evidence.write({'title': title[:160], 'role': role[:160], 'visibility': visibility,
                        'description': (kw.get('description') or '').strip(),
                        'result': (kw.get('result') or '').strip()[:250], 'url': url})
        return request.redirect('/tuhoso/me?notice=evidence')

    @http.route('/tuhoso/evidence/<int:evidence_id>/delete', type='http', auth='user', methods=['POST'], website=True)
    def evidence_delete(self, evidence_id, **kw):
        self._my_child('tacare.profile.evidence', evidence_id).unlink()
        return request.redirect('/tuhoso/me?notice=evidence')

    @http.route('/tuhoso/sharing/save', type='http', auth='user', methods=['POST'], website=True)
    def sharing_save(self, **kw):
        profile = self._my_profile(create=True)
        scope = kw.get('scope')
        if scope not in ('public', 'members', 'private'):
            raise BadRequest('Phạm vi chia sẻ không hợp lệ.')
        visible = kw.get('visible') == 'on' and scope != 'private'
        profile.write({'scope': scope, 'visible': visible, 'share_contact': False})
        consents = request.env['care.consent'].sudo()
        for purpose in ('discovery', 'matching'):
            old = consents.search([('profile_id', '=', profile.id),
                                   ('purpose', '=', purpose), ('state', '=', 'granted')])
            if old:
                old.write({'state': 'revoked', 'revoked_at': fields.Datetime.now(),
                           'revoke_reason': 'Ứng viên cập nhật chia sẻ'})
            if visible and (purpose == 'discovery' or kw.get('matching') == 'on'):
                consents.create({'profile_id': profile.id, 'purpose': purpose,
                                 'recipient_kind': 'public' if scope == 'public' else 'members',
                                 'field_scope': ['profile', 'skills', 'evidence'],
                                 'state': 'granted', 'granted_by': self._user().id,
                                 'valid_from': fields.Datetime.now()})
        return request.redirect('/tuhoso/me?notice=sharing')

    @http.route('/tacare/matching', type='http', auth='user', website=True)
    def matching(self, **kw):
        role = self._role()
        if role == 'candidate':
            profile = self._my_profile(create=True)
            jobs = request.env['hr.job'].sudo().search(
                self._job_domain() + [('care_matching_enabled', '=', True)]) if self._current_consent(profile, 'matching') else request.env['hr.job']
            matches = sorted([(job, self._match(job, profile)) for job in jobs],
                             key=lambda pair: len(pair[1]['matched']), reverse=True)
            return self._render('live_matching', matches=matches, kind='jobs', profile=profile,
                                matching_enabled=bool(self._current_consent(profile, 'matching')))
        self._require_business()
        domain = [('tacare_owner_partner_id', '!=', False)]
        if role != 'admin':
            domain.extend([('company_id', '=', request.env.company.id),
                           ('tacare_owner_partner_id', 'in', self._organizations().ids)])
        jobs = request.env['hr.job'].sudo().search(domain + [
            ('tacare_status', '=', 'published'), ('care_matching_enabled', '=', True)])
        try:
            selected_id = int(kw.get('job') or 0)
        except ValueError:
            raise BadRequest('ID tin không hợp lệ.')
        selected = jobs.filtered(lambda item: item.id == selected_id)[:1] or jobs[:1]
        profiles = self._visible_profiles(selected.tacare_owner_partner_id).filtered(lambda item: bool(self._current_consent(item, 'matching', selected.tacare_owner_partner_id, 'skills'))) if selected else request.env['tacare.profile']
        matches = sorted([(profile, self._match(selected, profile)) for profile in profiles],
                         key=lambda pair: len(pair[1]['matched']), reverse=True) if selected else []
        return self._render('live_matching', matches=matches, kind='profiles', jobs=jobs,
                            selected=selected, editable_org_ids=self._editable_organizations().ids)

    @http.route('/kvl/candidates', type='http', auth='user', website=True)
    def kvl_candidates(self, **kw):
        self._require_business()
        organizations = self._authorized_organizations('handle')
        if not organizations and self._role() != 'admin':
            raise Forbidden('Bạn chưa được cấp quyền xử lý ứng viên.')
        domain = [('company_id', '=', request.env.company.id),
                  ('tacare_owner_partner_id', '!=', False),
                  ('tacare_status', '=', 'published'), ('care_matching_enabled', '=', True)]
        if self._role() != 'admin':
            domain.append(('tacare_owner_partner_id', 'in', organizations.ids))
        jobs = request.env['hr.job'].sudo().search(domain)
        try:
            selected_id = int(kw.get('job') or 0)
        except ValueError:
            raise BadRequest('Tin không hợp lệ.')
        selected = jobs.filtered(lambda job: job.id == selected_id)[:1] if selected_id else jobs[:1]
        profiles = (self._visible_profiles(selected.tacare_owner_partner_id).filtered(
            lambda profile: bool(self._current_consent(profile, 'matching', selected.tacare_owner_partner_id, 'skills'))) if selected else
            request.env['tacare.profile'])
        pairs = sorted([(profile, self._match(selected, profile)) for profile in profiles],
                       key=lambda pair: len(pair[1]['matched']), reverse=True) if selected else []
        return self._render('kvl_candidates', site='khovieclam', jobs=jobs,
                            selected=selected, pairs=pairs)

    @http.route('/kvl/job/<int:job_id>/candidate/<int:profile_id>', type='http', auth='user', website=True)
    def kvl_candidate_detail(self, job_id, profile_id, **kw):
        job = self._own_job(job_id, 'handle')
        profile = self._visible_profiles(job.tacare_owner_partner_id).filtered(lambda item: item.id == profile_id)[:1]
        if not profile or not self._current_consent(profile, 'matching', job.tacare_owner_partner_id, 'skills'):
            raise NotFound()
        evidence = profile.evidence_ids.filtered(
            lambda item: item.visibility == 'public' or item.visibility == 'members')
        if not self._current_consent(profile, 'discovery', job.tacare_owner_partner_id, 'evidence'):
            evidence = request.env['tacare.profile.evidence']
        skills = {skill.name.casefold(): skill for skill in profile.skill_ids}
        comparisons = []
        condition_rows = [(row.category, row.name, row.mandatory) for row in job.care_requirement_ids]
        condition_rows += [('technical', name, True) for name in self._skills(job.tacare_required_skills)]
        condition_rows += [('technical', name, False) for name in self._skills(job.tacare_preferred_skills)]
        labels = dict(request.env['care.job.requirement']._fields['category'].selection)
        for category, name, mandatory in condition_rows:
            skill = skills.get(name.casefold())
            education_match = category in ('education', 'major') and name.casefold() in (profile.education or '').casefold()
            proof = evidence.filtered(lambda item: name.casefold() in (item.title or '').casefold())[:1]
            basis = ('Kỹ năng ứng viên tự khai: ' + skill.name +
                     (' — ' + skill.use if skill.use else '')) if skill else (
                     'Học vấn ứng viên tự khai: ' + profile.education if education_match else (
                     'Minh chứng được chia sẻ: ' + proof.title + ' (' + dict(proof._fields['status'].selection).get(proof.status, '') + ')' if proof else
                     'Hồ sơ chưa có dữ liệu trực tiếp cho điều kiện này.'))
            comparisons.append({'name': name, 'category': labels[category], 'mandatory': mandatory,
                                'result': 'met' if skill or education_match or proof else 'unknown',
                                'basis': basis})
        if job.tacare_mode and profile.mode and job.tacare_mode != profile.mode and 'hybrid' not in (job.tacare_mode, profile.mode):
            comparisons.append({'name': 'Hình thức làm việc', 'category': 'Điều kiện làm việc',
                                'mandatory': True, 'result': 'unmet',
                                'basis': 'Tin yêu cầu %s; hồ sơ nêu %s.' % (dict(MODES)[job.tacare_mode], dict(MODES)[profile.mode])})
        return self._render('kvl_candidate_detail', site='khovieclam', job=job,
                            profile=profile, evidence=evidence, comparisons=comparisons)

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
        if not job or not profile:
            raise BadRequest('Tin hoặc hồ sơ không tồn tại.')
        request.env.cr.execute('SELECT id FROM hr_job WHERE id = %s FOR UPDATE', [job.id])
        job.invalidate_recordset(['tacare_status', 'is_published'])
        if job.tacare_status != 'published' or not job.is_published:
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
        if kind == 'application':
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
