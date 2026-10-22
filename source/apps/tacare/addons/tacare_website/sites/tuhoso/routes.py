"""Server-rendered local first experience backed by Odoo records."""
import math
from urllib.parse import urlsplit

from markupsafe import escape
from werkzeug.exceptions import BadRequest, Forbidden, NotFound

from odoo import http, fields
from odoo.http import request
from odoo.exceptions import ValidationError
from odoo.tools import SQL

from ...models.hr_job import SECTORS, TYPES, MODES, preferred_currency
from ...controllers.site_context import site_context


class ProfileControllers(http.Controller):
    def _editable_profile(self, value, lock=False):
        self._flex_user()
        try:
            profile_id = int(value or 0)
        except (TypeError, ValueError):
            raise BadRequest('Chọn hồ sơ cụ thể trước khi chỉnh sửa.')
        if not profile_id:
            raise BadRequest('Chọn hồ sơ cụ thể trước khi chỉnh sửa.')
        company_ids = self._user().company_ids.ids
        domain = [('id', '=', profile_id), ('company_id', 'in', company_ids), ('status', '!=', 'archived')]
        if self._role() != 'admin':
            domain.append(('user_id', '=', self._user().id))
        profile = request.env['tacare.profile'].sudo().search(domain, limit=1)
        if not profile:
            raise NotFound()
        if lock:
            request.env.cr.execute('SELECT id FROM tacare_profile WHERE id = %s FOR UPDATE', [profile.id])
            if not request.env.cr.fetchone():
                raise NotFound()
            profile.invalidate_recordset()
            if profile.status == 'archived':
                raise NotFound()
        return profile

    def _my_profile(self, create=False):
        if self._role() not in ('candidate', 'business', 'admin') or self._user()._is_public():
            raise Forbidden('Đăng nhập tài khoản được cấp quyền để quản lý hồ sơ của mình.')
        domain = [('user_id', '=', self._user().id), ('company_id', 'in', self._user().company_ids.ids), ('status', '!=', 'archived')]
        selected = request.params.get('profile_id')
        if not selected and request.httprequest.method == 'POST' and request.env['tacare.profile'].sudo().search_count(domain, limit=2) > 1:
            raise BadRequest('Chọn hồ sơ cụ thể trước khi lưu thay đổi.')
        if selected:
            try:
                domain.append(('id', '=', int(selected)))
            except (ValueError, TypeError):
                raise BadRequest('Hồ sơ không hợp lệ.')
        profile = request.env['tacare.profile'].sudo().search(domain, order='care_recruitment_enabled desc, id', limit=1)
        if selected and not profile:
            raise NotFound()
        if not profile and create:
            profile = request.env['tacare.profile'].sudo().create({
                'user_id': self._user().id,
                'name': self._user().partner_id.name or self._user().name,
            })
        return profile

    def _my_child(self, model, record_id):
        if model not in ('tacare.profile.skill', 'tacare.profile.evidence', 'tacare.profile.experience', 'tacare.profile.education'):
            raise Forbidden()
        profile = self._editable_profile(request.params.get('profile_id'), lock=True)
        item = request.env[model].sudo().search([('id', '=', record_id), ('profile_id', '=', profile.id)], limit=1)
        if not item:
            raise Forbidden('Mục này không thuộc hồ sơ đang chỉnh sửa.')
        return item

    @http.route('/tuhoso/me', type='http', auth='user', website=True)
    def my_profile(self, **kw):
        profile = self._editable_profile(kw['profile_id']) if kw.get('profile_id') else self._my_profile()
        if not profile:
            return request.redirect('/tuhoso/profiles/new?kind=flexible')
        if not profile.care_recruitment_enabled:
            return self._render('profile_metadata_editor', site='tuhoso', profile=profile, vals=self._profile_values(profile), error=False)
        return self._render('live_profile', site='tuhoso', profile=profile, edit=True,
                            evidence_items=profile.evidence_ids, skill_items=profile.skill_ids,
                            vals=self._profile_values(profile), error=False, matching_enabled=bool(self._current_consent(profile, 'matching')))

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

    def _profile_values(self, profile, submitted=None):
        keys = ('name', 'profile_title', 'headline', 'bio', 'education', 'location', 'goal', 'availability', 'pay',
                'sector', 'mode', 'desired_type', 'work_fraction', 'relevant_months', 'salary_min',
                'salary_period', 'salary_tax', 'work_history', 'education_details', 'languages',
                'licenses', 'travel', 'start_date', 'career_level', 'salary_max', 'relocation', 'portfolio_url', 'preferred_conditions')
        values = {key: str(profile[key] or '') for key in keys}
        for key in ('desired_position_id', 'region_id', 'salary_currency_id'):
            values[key] = str(profile[key].id or '')
        values['salary_negotiable'] = 'on' if profile.salary_negotiable else ''
        values['profile_version'] = str(profile.version)
        values['education_level_id'] = str(profile.education_level_id.id or '')
        values['experience_known'] = 'on' if profile.experience_known else ''
        values['relevant_months'] = str(profile.relevant_months) if profile.experience_known else ''
        values['experience_position_id'] = str(profile.desired_position_id.id or '')
        if submitted is not None:
            values.update(submitted)
            values['experience_known'] = submitted.get('experience_known', '')
            values['salary_negotiable'] = submitted.get('salary_negotiable', '')
        return values

    def _profile_form_error(self, profile, submitted, message):
        return self._render('live_profile' if profile.care_recruitment_enabled else 'profile_metadata_editor',
            site='tuhoso', profile=profile, edit=True, evidence_items=profile.evidence_ids, skill_items=profile.skill_ids,
            vals=self._profile_values(profile, submitted), error=message,
            matching_enabled=bool(self._current_consent(profile, 'matching')))

    @http.route('/tuhoso/profile/<int:profile_id>/edit', auth='user', website=True, methods=['GET'])
    def edit_profile(self, profile_id, **kw):
        profile = self._editable_profile(profile_id)
        return self._render('live_profile' if profile.care_recruitment_enabled else 'profile_metadata_editor',
            site='tuhoso', profile=profile, edit=True, evidence_items=profile.evidence_ids, skill_items=profile.skill_ids,
            vals=self._profile_values(profile), error=False, matching_enabled=bool(self._current_consent(profile, 'matching')))

    @http.route('/tuhoso/profile/save', type='http', auth='user', methods=['POST'], website=True)
    def profile_save(self, **kw):
        profile = self._editable_profile(kw.get('profile_id'), lock=True)
        texts = ('name', 'profile_title', 'headline', 'bio', 'education', 'location', 'goal', 'availability',
                 'work_history', 'education_details', 'languages', 'licenses', 'portfolio_url', 'preferred_conditions')
        selections = ('sector', 'mode', 'desired_type', 'work_fraction', 'salary_period', 'salary_tax', 'travel', 'career_level', 'relocation')
        allowed = set(texts + selections + ('csrf_token', 'profile_id', 'profile_version', 'desired_position_id',
            'region_id', 'salary_currency_id', 'experience_known', 'experience_position_id', 'relevant_months',
            'salary_min', 'salary_max', 'salary_negotiable', 'start_date', 'education_level_id'))
        if set(kw) - allowed:
            raise BadRequest('Biểu mẫu có trường không được phép sửa.')
        try:
            if int(kw.get('profile_version') or 0) != profile.version:
                return self._profile_form_error(profile, kw, 'Hồ sơ đã được cập nhật ở phiên khác. Nội dung bạn nhập được giữ lại; hãy kiểm tra trước khi lưu lại.')
            vals = {}
            for key in texts:
                value = (kw.get(key) or '').strip()
                limits = {'name':160, 'profile_title':160, 'headline':180, 'education':250, 'location':250, 'availability':500, 'portfolio_url':1000}
                limit = limits.get(key, 20000)
                if len(value) > limit:
                    raise ValidationError('Có nội dung vượt độ dài cho phép. Vui lòng rút gọn họ tên, tiêu đề hoặc phần mô tả đã nhập.')
                vals[key] = value
            if not 2 <= len(vals['name']) <= 160 or not 2 <= len(vals['profile_title']) <= 160:
                raise ValidationError('Họ tên và tên hồ sơ cần từ 2 đến 160 ký tự.')
            if not profile.care_recruitment_enabled:
                metadata = {key: vals[key] for key in ('name','profile_title','headline','bio','goal')}
                with request.env.cr.savepoint():
                    profile.write(metadata)
            else:
                for key in selections:
                    value = kw.get(key) or False
                    if value and value not in dict(profile._fields[key].selection):
                        raise ValidationError('Chọn giá trị hợp lệ trong danh sách.')
                    vals[key] = value
                position = request.env['care.job.position'].sudo().browse(int(kw.get('desired_position_id') or 0)).exists()
                region = request.env['res.country.state'].sudo().browse(int(kw.get('region_id') or 0)).exists()
                currency = request.env['res.currency'].sudo().browse(int(kw.get('salary_currency_id') or request.env.company.currency_id.id)).exists()
                degree = request.env['hr.recruitment.degree'].sudo().browse(int(kw.get('education_level_id') or 0)).exists()
                months, salary, maximum = int(kw.get('relevant_months') or 0), float(kw.get('salary_min') or 0), float(kw.get('salary_max') or 0)
                start_date = fields.Date.to_date(kw.get('start_date')) if kw.get('start_date') else False
                known = kw.get('experience_known') == 'on'
                if known and (not (kw.get('relevant_months') or '').strip() or str(position.id or '') != kw.get('experience_position_id', '')):
                    raise ValidationError('Xác nhận lại số tháng kinh nghiệm cho nhóm nghề đang chọn; 0 tháng nếu chưa có kinh nghiệm.')
                if not 0 <= months <= 960 or any(not math.isfinite(n) or n < 0 for n in (salary, maximum)) or maximum and maximum < salary:
                    raise ValidationError('Kinh nghiệm từ 0–960 tháng; khoảng lương hữu hạn, không âm và mức cao nhất từ mức thấp nhất trở lên.')
                if not currency or not currency.active or kw.get('desired_position_id') and not position or kw.get('region_id') and not region or kw.get('education_level_id') and not degree:
                    raise ValidationError('Nhóm nghề, khu vực, trình độ hoặc tiền tệ không hợp lệ.')
                if position and position.sector_id.code != vals['sector'] or known and not position or region and region.country_id.code != 'VN':
                    raise ValidationError('Nhóm nghề phải thuộc lĩnh vực; chọn khu vực Việt Nam và nhóm nghề cho kinh nghiệm liên quan.')
                vals.update(desired_position_id=position.id, region_id=region.id, salary_currency_id=currency.id,
                    education_level_id=degree.id, experience_known=known, relevant_months=months if known else 0,
                    salary_min=salary, salary_max=maximum, salary_negotiable=kw.get('salary_negotiable') == 'on', start_date=start_date)
                with request.env.cr.savepoint():
                    profile.write(vals)
            self._profile_content_audit('profile.content.updated', profile)
        except (ValidationError, ValueError, TypeError, OverflowError) as exc:
            return self._profile_form_error(profile, kw, str(exc) if isinstance(exc, ValidationError) else 'Kiểm tra ngày, số tháng, mức lương và các lựa chọn.')
        return request.redirect('/tuhoso/profile/%s/edit?notice=profile' % profile.id)

    def _child_form_error(self, profile, submitted, form, message, record_id=0):
        return self._render('live_profile', site='tuhoso', profile=profile, edit=True,
            evidence_items=profile.evidence_ids, skill_items=profile.skill_ids,
            vals=self._profile_values(profile), error=message, child_form=form,
            child_id=record_id, child_values=submitted,
            matching_enabled=bool(self._current_consent(profile, 'matching')))

    @http.route('/tuhoso/skill/add', type='http', auth='user', methods=['POST'], website=True)
    def skill_add(self, **kw):
        profile = self._editable_profile(kw.get('profile_id'), lock=True)
        name = (kw.get('name') or '').strip()
        if not name or len(name) > 80:
            return self._child_form_error(profile, kw, 'skill_add', 'Tên kỹ năng cần từ 1 đến 80 ký tự.')
        if profile.skill_ids.filtered(lambda item: item.name.casefold() == name.casefold()):
            return self._child_form_error(profile, kw, 'skill_add', 'Kỹ năng đã có trong hồ sơ.')
        level = kw.get('level') or 'basic'
        if level not in dict(request.env['tacare.profile.skill']._fields['level'].selection):
            return self._child_form_error(profile, kw, 'skill_add', 'Chọn mức kỹ năng hợp lệ.')
        skill = self._catalog_skill(name)
        request.env['tacare.profile.skill'].sudo().create({
            'profile_id': profile.id, 'name': name, 'level': level, 'skill_id': skill.id,
            'use': (kw.get('use') or '').strip()[:250],
        })
        self._profile_content_audit('profile.skill.added', profile)
        return request.redirect('/tuhoso/me?profile_id=%s&notice=skill' % profile.id)

    @http.route('/tuhoso/skill/<int:skill_id>/save', type='http', auth='user', methods=['POST'], website=True)
    def skill_save(self, skill_id, **kw):
        skill = self._my_child('tacare.profile.skill', skill_id)
        name = (kw.get('name') or '').strip()
        level = kw.get('level') or 'basic'
        if not name or len(name) > 80 or level not in dict(skill._fields['level'].selection):
            return self._child_form_error(skill.profile_id, kw, 'skill_edit', 'Tên hoặc mức kỹ năng không hợp lệ.', skill.id)
        duplicates = skill.profile_id.skill_ids.filtered(lambda item: item.id != skill.id and item.name.casefold() == name.casefold())
        if duplicates:
            return self._child_form_error(skill.profile_id, kw, 'skill_edit', 'Kỹ năng đã có trong hồ sơ.', skill.id)
        skill.write({'name': name, 'level': level, 'skill_id': self._catalog_skill(name).id,
                     'use': (kw.get('use') or '').strip()[:250]})
        self._profile_content_audit('profile.skill.updated', skill.profile_id)
        return request.redirect('/tuhoso/me?profile_id=%s&notice=skill' % skill.profile_id.id)

    @http.route('/tuhoso/skill/<int:skill_id>/delete', type='http', auth='user', methods=['POST'], website=True)
    def skill_delete(self, skill_id, **kw):
        item = self._my_child('tacare.profile.skill', skill_id)
        profile = item.profile_id
        profile_id = profile.id
        item.unlink()
        self._profile_content_audit('profile.skill.deleted', profile)
        return request.redirect('/tuhoso/me?profile_id=%s&notice=skill' % profile_id)

    @http.route('/tuhoso/evidence/add', type='http', auth='user', methods=['POST'], website=True)
    def evidence_add(self, **kw):
        profile = self._editable_profile(kw.get('profile_id'), lock=True)
        title = (kw.get('title') or '').strip()
        role = (kw.get('role') or '').strip()
        if not title or not role:
            return self._child_form_error(profile, kw, 'evidence_add', 'Nhập tên và vai trò của minh chứng.')
        url = (kw.get('url') or '').strip()[:400]
        if url and urlsplit(url).scheme not in ('http', 'https'):
            return self._child_form_error(profile, kw, 'evidence_add', 'Liên kết minh chứng phải dùng http hoặc https.')
        request.env['tacare.profile.evidence'].sudo().create({
            'profile_id': profile.id, 'title': title[:160], 'role': role[:160],
            'description': (kw.get('description') or '').strip(),
            'result': (kw.get('result') or '').strip()[:250],
            'url': url, 'visibility': 'private',
        })
        self._profile_content_audit('profile.evidence.added', profile)
        return request.redirect('/tuhoso/me?profile_id=%s&notice=evidence' % profile.id)

    @http.route('/tuhoso/evidence/<int:evidence_id>/save', type='http', auth='user', methods=['POST'], website=True)
    def evidence_save(self, evidence_id, **kw):
        evidence = self._my_child('tacare.profile.evidence', evidence_id)
        title, role = (kw.get('title') or '').strip(), (kw.get('role') or '').strip()
        url = (kw.get('url') or '').strip()[:400]
        if not title or not role or url and urlsplit(url).scheme not in ('http', 'https'):
            return self._child_form_error(evidence.profile_id, kw, 'evidence_edit', 'Tên, vai trò hoặc liên kết minh chứng không hợp lệ.', evidence.id)
        visibility = kw.get('visibility') or evidence.visibility
        if evidence.profile_id.user_id != self._user() and visibility != evidence.visibility:
            raise Forbidden('Quyền chia sẻ minh chứng do chủ hồ sơ quản lý.')
        if visibility not in ('private', 'members', 'public'):
            return self._child_form_error(evidence.profile_id, kw, 'evidence_edit', 'Chọn phạm vi minh chứng hợp lệ.', evidence.id)
        evidence.write({'title': title[:160], 'role': role[:160], 'visibility': visibility,
                        'description': (kw.get('description') or '').strip(),
                        'result': (kw.get('result') or '').strip()[:250], 'url': url})
        self._profile_content_audit('profile.evidence.updated', evidence.profile_id)
        return request.redirect('/tuhoso/me?profile_id=%s&notice=evidence' % evidence.profile_id.id)

    @http.route('/tuhoso/evidence/<int:evidence_id>/delete', type='http', auth='user', methods=['POST'], website=True)
    def evidence_delete(self, evidence_id, **kw):
        item = self._my_child('tacare.profile.evidence', evidence_id)
        profile = item.profile_id
        profile_id = profile.id
        item.unlink()
        self._profile_content_audit('profile.evidence.deleted', profile)
        return request.redirect('/tuhoso/me?profile_id=%s&notice=evidence' % profile_id)

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
        return request.redirect('/tuhoso/me?profile_id=%s&notice=sharing' % profile.id)


    @http.route('/tuhoso/profile/<int:profile_id>/remove', auth='user', website=True, methods=['GET', 'POST'])
    def admin_profile_remove(self, profile_id, **kw):
        return self._admin_removal('profile', profile_id)

    @http.route('/tuhoso/work/<int:record_id>/remove', auth='user', website=True, methods=['GET', 'POST'])
    def admin_service_remove(self, record_id, **kw):
        return self._admin_removal('service', record_id)
