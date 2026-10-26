"""Server-rendered local first experience backed by Odoo records."""
import math
from urllib.parse import urlsplit

from markupsafe import escape
from werkzeug.exceptions import BadRequest, Forbidden, NotFound

from odoo import http, fields
from odoo.http import request

from ...models.jobs.hr_job import SECTORS, TYPES, MODES, preferred_currency
from ...controllers.site_context import site_context


class KhoControllers(http.Controller):
    def _own_job(self, job_id, capability='manage'):
        self._flex_user()
        company_ids = self._user().company_ids.ids
        job = request.env['hr.job'].sudo().search([('id','=',job_id),
            ('care_opportunity_kind','=','flexible'), ('company_id','in',company_ids)], limit=1)
        if not job:
            raise NotFound()
        organization_access = self._role() == 'business' and job.tacare_owner_partner_id in self._authorized_organizations(capability)
        personal_access = self._role() == 'candidate' and job.tacare_owner_user_id == self._user()
        if self._role() != 'admin' and not personal_access and not organization_access:
            raise Forbidden('Bạn không có quyền quản lý việc này.')
        return job

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
            'position_id': 'care_position_id', 'region_id': 'care_region_id',
            'requirements_text': 'care_candidate_requirements', 'benefits': 'care_benefits',
            'salary_display': 'care_salary_display', 'salary_basis': 'care_salary_basis',
            'salary_tax': 'care_salary_tax', 'education_note': 'care_education_note',
            'language_note': 'care_language_note', 'license_note': 'care_license_note',
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
                values[source] = str(value.id if job._fields[target].type == 'many2one' and value else value or '')
            if not job.care_sector_id and job.tacare_sector:
                legacy_sector = request.env['care.job.sector'].sudo().search([
                    ('code', '=', job.tacare_sector)], limit=1)
                if legacy_sector:
                    values['sector_id'] = str(legacy_sector.id)
            for checkbox, target in [('matching_enabled', 'care_matching_enabled'),
                                     ('requires_travel', 'care_requires_travel'),
                                     ('requires_license', 'care_requires_license'),
                                     ('requires_portfolio', 'care_requires_portfolio'),
                                     ('requires_clinical', 'care_requires_clinical'),
                                     ('training_provided', 'care_training_provided'),
                                     ('skills_any', 'care_skills_any'),
                                     ('schedule_required', 'care_schedule_required'),
                                     ('start_flexible', 'care_start_flexible')]:
                values[checkbox] = 'on' if job[target] else ''
        if values.get('type') in ('full_time', 'part_time'):
            values['work_fraction'] = values.get('work_fraction') or ('full' if values['type'] == 'full_time' else 'part')
            values['type'] = 'employment'
        values['main_skills'] = ', '.join(filter(None, (values.get('required_skills'), values.get('preferred_skills'))))
        values['mandatory_names'] = self._skills(values.get('required_skills'))
        if not job:
            values.update(matching_enabled='on', start_flexible='on', salary_display='negotiable',
                          salary_basis='base', salary_tax='unknown', income_period='month', type='employment')
        if overrides:
            for key in ('matching_enabled', 'training_provided', 'skills_any', 'schedule_required',
                        'start_flexible', 'requires_travel'):
                values[key] = overrides.get(key, '')
            values.update(overrides)
            values['mandatory_names'] = request.httprequest.form.getlist('mandatory_skill')
        values.setdefault('currency_id', str(preferred_currency(request.env).id))
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
                                 query in (item.tacare_location or '').casefold() or
                                 query in (item.care_position or '').casefold() or
                                 query in (item.tacare_required_skills or '').casefold() or
                                 query in (item.tacare_preferred_skills or '').casefold())
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
        if profile and not profile.care_recruitment_enabled:
            profile = False
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
        if job and kw.get('form_version') == '2':
            rows = [{'category': row.category, 'name': row.name, 'mandatory': row.mandatory}
                    for row in job.care_requirement_ids]
        sector_id = kw.get('sector_id') or ''
        try:
            sector = request.env['care.job.sector'].sudo().browse(int(sector_id)).exists() if sector_id else False
        except ValueError:
            raise BadRequest('Ngành nghề không hợp lệ.')
        if sector_id and not sector:
            raise BadRequest('Ngành nghề không hợp lệ.')
        try:
            currency_id = int(kw.get('currency_id') or (job.care_currency_id.id if job else preferred_currency(request.env).id))
        except ValueError:
            raise BadRequest('Đơn vị tiền tệ không hợp lệ.')
        currency = request.env['res.currency'].sudo().browse(currency_id).exists()
        if not currency or not currency.active:
            raise BadRequest('Đơn vị tiền tệ không hợp lệ.')
        try:
            position = request.env['care.job.position'].sudo().browse(int(kw.get('position_id') or 0)).exists()
            region = request.env['res.country.state'].sudo().browse(int(kw.get('region_id') or 0)).exists()
        except ValueError:
            return self._job_form_error(job, kw, rows, 'position_id', 'Chọn nhóm nghề và khu vực hợp lệ.')
        if position and position.sector_id != sector:
            return self._job_form_error(job, kw, rows, 'position_id', 'Nhóm nghề phải thuộc lĩnh vực đã chọn.')
        if region and region.country_id.code != 'VN':
            return self._job_form_error(job, kw, rows, 'region_id', 'Chọn tỉnh / thành trong danh sách.')
        if kw.get('position_id') and not position or kw.get('region_id') and not region:
            return self._job_form_error(job, kw, rows, 'position_id', 'Nhóm nghề hoặc khu vực không còn trong danh sách.')
        vals = {
            'name': (kw.get('name') or '').strip(),
            'tacare_sector': sector.code if sector and sector.code in dict(SECTORS) else False,
            'care_sector_id': sector.id if sector else False,
            'care_position': position.name if position else (kw.get('position') or '').strip()[:160],
            'care_position_id': position.id, 'care_region_id': region.id,
            'care_candidate_requirements': (kw.get('requirements_text') or '').strip()[:20000],
            'care_benefits': (kw.get('benefits') or '').strip()[:20000],
            'care_training_provided': kw.get('training_provided') == 'on',
            'care_skills_any': kw.get('skills_any') == 'on',
            'care_salary_display': kw.get('salary_display') or 'negotiable',
            'care_salary_basis': kw.get('salary_basis') or 'base',
            'care_salary_tax': kw.get('salary_tax') or 'unknown',
            'care_education_note': (kw.get('education_note') or '').strip()[:300],
            'care_language_note': (kw.get('language_note') or '').strip()[:300],
            'care_license_note': (kw.get('license_note') or '').strip()[:300],
            'care_schedule_required': kw.get('schedule_required') == 'on',
            'care_start_flexible': kw.get('start_flexible') == 'on',
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
        if kw.get('form_version') == '2':
            all_skills = list({name.casefold(): name for name in self._skills(kw.get('main_skills'))}.values())
            required_keys = {name.casefold() for name in request.httprequest.form.getlist('mandatory_skill')}
            if len(all_skills) > 20 or any(len(name) > 80 for name in all_skills):
                return self._job_form_error(job, kw, rows, 'main_skills', 'Tối đa 20 kỹ năng, mỗi tên tối đa 80 ký tự.')
            vals['tacare_required_skills'] = ', '.join(name for name in all_skills if name.casefold() in required_keys)
            vals['tacare_preferred_skills'] = ', '.join(name for name in all_skills if name.casefold() not in required_keys)
            if vals['care_salary_display'] == 'negotiable':
                vals.update(care_salary_min=0, care_salary_max=0)
            vals['care_income_type'] = 'negotiable' if vals['care_salary_display'] == 'negotiable' else 'salary'
        if len(vals['profile_title']) > 160:
            return self._profile_form_error(profile, kw, 'Tên hồ sơ tối đa 160 ký tự.')
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
                                ('care_income_type', 'income_type'), ('care_income_period', 'income_period'),
                                ('care_salary_display', 'salary_display'), ('care_salary_basis', 'salary_basis'),
                                ('care_salary_tax', 'salary_tax')]:
            if vals[source] and vals[source] not in dict(request.env['hr.job']._fields[source].selection):
                raise BadRequest('Giá trị ' + options + ' không hợp lệ.')
        for source, target in [('experience_min', 'care_experience_min'),
                               ('salary_min', 'care_salary_min'), ('salary_max', 'care_salary_max')]:
            try:
                vals[target] = float(kw.get(source) or 0)
            except ValueError:
                return self._job_form_error(job, kw, rows, source, 'Nhập một số hợp lệ.')
            if not math.isfinite(vals[target]) or vals[target] < 0:
                return self._job_form_error(job, kw, rows, source, 'Giá trị không được âm.')
        if kw.get('form_version') == '2':
            display = vals['care_salary_display']
            if display in ('negotiable', 'to'):
                vals['care_salary_min'] = 0
            if display in ('negotiable', 'from'):
                vals['care_salary_max'] = 0
            if intent == 'publish' and display != 'negotiable' and not (vals['care_salary_min'] or vals['care_salary_max']):
                return self._job_form_error(job, kw, rows, 'salary_min', 'Nhập mức lương hoặc chọn Thỏa thuận.')
            if intent == 'publish' and display == 'range' and not (vals['care_salary_min'] and vals['care_salary_max']):
                return self._job_form_error(job, kw, rows, 'salary_min', 'Khoảng lương cần cả mức thấp nhất và cao nhất.')
        if vals['care_salary_max'] and vals['care_salary_max'] < vals['care_salary_min']:
            return self._job_form_error(job, kw, rows, 'salary_max', 'Mức cao nhất phải từ mức thấp nhất trở lên.')
        try:
            vals['no_of_recruitment'] = int(kw.get('quantity') or '1')
            if not 1 <= vals['no_of_recruitment'] <= 10000:
                raise ValueError()
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
            if kw.get('form_version') == '2' and not position:
                field_errors['position_id'] = 'Chọn nhóm nghề để đối chiếu đúng vị trí.'
            if kw.get('form_version') == '2' and not vals['care_candidate_requirements']:
                field_errors['requirements_text'] = 'Nêu yêu cầu ứng viên hoặc chính sách đào tạo từ đầu.'
            if kw.get('form_version') == '2' and not vals['care_work_fraction']:
                field_errors['work_fraction'] = 'Chọn thời lượng làm việc.'
            if vals['tacare_mode'] != 'remote' and kw.get('form_version') == '2' and not region:
                field_errors['region_id'] = 'Chọn tỉnh / thành làm việc.'
            if vals['tacare_deadline'] and vals['tacare_deadline'] < fields.Date.today().isoformat():
                field_errors['deadline'] = 'Hạn nhận đề nghị đã qua.'
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
                       key=lambda pair: pair[1]['rank'], reverse=True) if selected else []
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
        comparisons = self._match(job, profile)['comparisons']
        return self._render('kvl_candidate_detail', site='khovieclam', job=job,
                            profile=profile, evidence=evidence, comparisons=comparisons)


    @http.route('/kvl/job/<int:job_id>/remove', auth='user', website=True, methods=['GET', 'POST'])
    def admin_job_remove(self, job_id, **kw):
        return self._admin_removal('job', job_id)
