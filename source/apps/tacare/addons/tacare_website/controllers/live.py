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
        user = self._user().sudo()
        memberships = user.care_org_member_ids.filtered(lambda item: item.company_id == request.env.company)
        if memberships:
            return memberships.filtered(lambda item: item.state == 'active' and
                                      item.role in ('owner', 'recruiter')).mapped('organization_id')
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
        values.update(site=site, role=self._role(), account_name=self._user().name,
                      is_guest=self._user()._is_public(), urls=self._urls(),
                      sectors=SECTORS, types=TYPES, modes=MODES,
                      notice=request.params.get('notice'))
        return request.render('tacare_website.' + template, values)

    def _own_job(self, job_id):
        self._require_business()
        job = request.env['hr.job'].sudo().browse(job_id).exists()
        if not job or not job.tacare_owner_partner_id:
            raise NotFound()
        if self._role() != 'admin' and (job.company_id != request.env.company or
                                       job.tacare_owner_partner_id not in self._editable_organizations()):
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
        if not item or self._role() != 'admin' and self._user().id not in (item.sender_id.id, item.receiver_id.id):
            raise Forbidden('Kết nối không thuộc tài khoản này.')
        return item

    def _job_domain(self):
        website = self._website('khovieclam')
        return [('tacare_status', '=', 'published'), ('is_published', '=', True),
                ('website_id', '=', website.id)]

    def _visible_profiles(self):
        profiles = request.env['tacare.profile'].sudo().search([
            ('visible', '=', True), ('status', '=', 'active'), ('scope', '!=', 'private')])
        if self._user()._is_public():
            profiles = profiles.filtered(lambda item: item.scope == 'public')
        return profiles.filtered(lambda item: bool(self._current_consent(item, 'discovery')))

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
        names = set(profile.skill_ids.mapped('name'))
        required = self._skills(job.tacare_required_skills)
        preferred = self._skills(job.tacare_preferred_skills)
        matched = [name for name in required if name in names]
        missing = [name for name in required if name not in names]
        preferred_found = [name for name in preferred if name in names]
        same_mode = bool(profile.mode) and (not job.tacare_mode or profile.mode == job.tacare_mode or
                                              'hybrid' in (profile.mode, job.tacare_mode))
        same_location = bool(profile.location) and (job.tacare_mode == 'remote' or
                                                     (job.tacare_location or '').casefold() == profile.location.casefold())
        score = round(65 * (len(matched) / len(required) if required else 1) +
                      20 * (len(preferred_found) / len(preferred) if preferred else 1) +
                      10 * same_mode + 5 * same_location)
        return {'score': score, 'matched': matched, 'missing': missing,
                'preferred_found': preferred_found, 'same_mode': same_mode,
                'same_location': same_location}

    def _notify(self, user, text, connection=None):
        request.env['tacare.notification'].sudo().create({
            'user_id': user.id, 'message': text,
            'connection_id': connection.id if connection else False,
        })

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
            jobs = jobs.filtered(lambda item: item.tacare_sector == sector)
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
        return self._render('live_job_detail', site='khovieclam', job=job,
                            required=self._skills(job.tacare_required_skills),
                            preferred=self._skills(job.tacare_preferred_skills),
                            profile=profile, match=self._match(job, profile) if can_match else False)

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
        jobs = request.env['hr.job'].sudo().search(domain, order='create_date desc')
        revisions = request.env['care.job.revision'].sudo().search([
            ('job_id', 'in', jobs.ids), ('state', '=', 'submitted')], order='create_date desc')
        return self._render('live_manage_jobs', site='khovieclam', jobs=jobs,
                            revisions=revisions, editable_org_ids=self._editable_organizations().ids,
                            selected_status=status or '')

    @http.route(['/kvl/job/new', '/kvl/job/<int:job_id>/edit'], type='http', auth='user', website=True)
    def job_form(self, job_id=None, **kw):
        self._require_business()
        if self._role() != 'admin' and not self._editable_organizations():
            raise Forbidden('Bạn chỉ có quyền xem tổ chức, chưa được sửa tin.')
        job = self._own_job(job_id) if job_id else False
        if job and job.tacare_status == 'closed':
            raise Forbidden('Tin đã đóng chỉ được xem.')
        owners = request.env['res.users'].sudo().search([('tacare_account_role', '=', 'business')]) if self._role() == 'admin' else False
        return self._render('live_job_form', site='khovieclam', job=job, owners=owners,
                            organizations=self._editable_organizations() if self._role() != 'admin' else False,
                            error=False, vals={})

    @http.route('/kvl/job/save', type='http', auth='user', methods=['POST'], website=True)
    def job_save(self, **kw):
        self._require_business()
        raw_id = kw.get('job_id') or ''
        try:
            job = self._own_job(int(raw_id)) if raw_id else False
        except ValueError:
            raise BadRequest('ID tin không hợp lệ.')
        intent = kw.get('intent')
        if intent not in ('draft', 'publish'):
            raise BadRequest('Thao tác không hợp lệ.')
        vals = {
            'name': (kw.get('name') or '').strip(),
            'tacare_sector': kw.get('sector') or False,
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
        for source, target in [('experience_min', 'care_experience_min'),
                               ('salary_min', 'care_salary_min'), ('salary_max', 'care_salary_max')]:
            try:
                vals[target] = float(kw.get(source) or 0)
            except ValueError:
                raise BadRequest('Kinh nghiệm hoặc thù lao không hợp lệ.')
            if vals[target] < 0:
                raise BadRequest('Kinh nghiệm hoặc thù lao không được âm.')
        if vals['care_salary_max'] and vals['care_salary_max'] < vals['care_salary_min']:
            raise BadRequest('Thù lao tối đa phải lớn hơn mức tối thiểu.')
        try:
            vals['no_of_recruitment'] = max(1, int(kw.get('quantity') or '1'))
        except ValueError:
            raise BadRequest('Số lượng không hợp lệ.')
        for source, target in [('start', 'tacare_start'), ('deadline', 'tacare_deadline')]:
            value = kw.get(source) or False
            try:
                vals[target] = fields.Date.to_string(fields.Date.to_date(value)) if value else False
            except (ValueError, TypeError):
                raise BadRequest('Ngày không hợp lệ.')
        if vals['tacare_sector'] and vals['tacare_sector'] not in dict(SECTORS):
            raise BadRequest('Lĩnh vực không hợp lệ.')
        if vals['tacare_type'] and vals['tacare_type'] not in dict(TYPES):
            raise BadRequest('Loại cơ hội không hợp lệ.')
        if vals['tacare_mode'] and vals['tacare_mode'] not in dict(MODES):
            raise BadRequest('Hình thức không hợp lệ.')
        error = False
        if intent == 'publish' and not all([vals['name'], vals['tacare_sector'], vals['tacare_type'],
                                             vals['tacare_mode'], vals['tacare_location'],
                                             vals['tacare_required_skills'], kw.get('description'),
                                             vals['tacare_deadline']]):
            error = 'Điền đủ tên, lĩnh vực, loại, hình thức, địa điểm, kỹ năng, mô tả và hạn nhận đề nghị.'
        if vals['tacare_start'] and vals['tacare_deadline'] and vals['tacare_deadline'] < vals['tacare_start']:
            error = 'Hạn nhận đề nghị phải sau ngày bắt đầu.'
        if error:
            owners = request.env['res.users'].sudo().search([('tacare_account_role', '=', 'business')]) if self._role() == 'admin' else False
            return self._render('live_job_form', site='khovieclam', job=job, owners=owners,
                                organizations=self._editable_organizations() if self._role() != 'admin' else False,
                                error=error, vals=kw)
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
                'job_id': job.id, 'version': version, 'payload': vals,
                'state': 'submitted', 'submitted_by': self._user().id})
            return request.redirect('/kvl/manage?notice=revision')
        vals.update(tacare_status='published' if intent == 'publish' else (job.tacare_status if job else 'draft'),
                    website_published=intent == 'publish' or bool(job and job.tacare_status == 'published'),
                    is_published=intent == 'publish' or bool(job and job.tacare_status == 'published'))
        if job:
            job.write(vals)
        else:
            job = request.env['hr.job'].sudo().create(vals)
        job._care_sync_job_skills()
        return request.redirect('/kvl/manage?notice=saved')

    @http.route('/kvl/revision/<int:revision_id>/review', type='http', auth='user', methods=['POST'], website=True)
    def revision_review(self, revision_id, **kw):
        if self._role() != 'admin':
            raise Forbidden('Chỉ quản trị được duyệt thay đổi tin.')
        revision = request.env['care.job.revision'].sudo().browse(revision_id).exists()
        if not revision or revision.state != 'submitted':
            raise NotFound()
        decision = kw.get('decision')
        if decision == 'approve':
            revision.action_publish(self._user(), (kw.get('note') or '')[:1000])
        elif decision == 'reject':
            revision.write({'state': 'rejected', 'reviewed_by': self._user().id,
                            'reviewed_at': fields.Datetime.now(), 'review_note': (kw.get('note') or '')[:1000]})
        else:
            raise BadRequest('Quyết định không hợp lệ.')
        return request.redirect('/kvl/manage?notice=review')

    @http.route('/kvl/job/<int:job_id>/status', type='http', auth='user', methods=['POST'], website=True)
    def job_status(self, job_id, **kw):
        job = self._own_job(job_id)
        new = kw.get('status')
        allowed = {'draft': ('published',), 'published': ('paused', 'closed'),
                   'paused': ('published', 'closed'), 'closed': ()}
        if new not in allowed[job.tacare_status]:
            raise BadRequest('Không thể chuyển trạng thái tin.')
        if new == 'published' and not all([job.name, job.tacare_sector, job.tacare_type,
                                            job.tacare_mode, job.tacare_location,
                                            job.tacare_required_skills, job.description,
                                            job.tacare_deadline]):
            raise BadRequest('Tin chưa đủ dữ liệu để đăng.')
        job.write({'tacare_status': new, 'website_published': new == 'published',
                   'is_published': new == 'published'})
        return request.redirect('/kvl/manage?notice=status')

    @http.route('/tuhoso/me', type='http', auth='user', website=True)
    def my_profile(self, **kw):
        profile = self._my_profile(create=True)
        return self._render('live_profile', site='tuhoso', profile=profile, edit=True,
                            evidence_items=profile.evidence_ids,
                            matching_enabled=bool(self._current_consent(profile, 'matching')))

    @http.route('/tuhoso/profile/<int:profile_id>', type='http', auth='public', website=True)
    def profile_public(self, profile_id, **kw):
        profile = self._visible_profiles().filtered(lambda item: item.id == profile_id)[:1]
        if not profile:
            raise NotFound()
        evidence_items = profile.evidence_ids.filtered(
            lambda item: item.visibility == 'public' or
            item.visibility == 'members' and not self._user()._is_public())
        return self._render('live_profile', site='tuhoso', profile=profile, edit=False,
                            evidence_items=evidence_items)

    @http.route('/tuhoso/profile/save', type='http', auth='user', methods=['POST'], website=True)
    def profile_save(self, **kw):
        profile = self._my_profile(create=True)
        vals = {key: (kw.get(key) or '').strip() for key in
                ('name', 'headline', 'education', 'location', 'goal', 'availability', 'pay')}
        if len(vals['name']) < 2:
            return self._render('live_profile', site='tuhoso', profile=profile, edit=True,
                                evidence_items=profile.evidence_ids,
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
                             key=lambda pair: pair[1]['score'], reverse=True)
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
        profiles = self._visible_profiles().filtered(lambda item: bool(self._current_consent(item, 'matching'))) if selected else request.env['tacare.profile']
        matches = sorted([(profile, self._match(selected, profile)) for profile in profiles],
                         key=lambda pair: pair[1]['score'], reverse=True) if selected else []
        return self._render('live_matching', matches=matches, kind='profiles', jobs=jobs,
                            selected=selected, editable_org_ids=self._editable_organizations().ids)

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
        if not job or not profile or job.tacare_status != 'published' or not job.is_published:
            raise BadRequest('Tin hoặc hồ sơ không còn sẵn sàng.')
        if kind == 'application':
            self._require_candidate()
            if profile.user_id != self._user():
                raise Forbidden('Chỉ chủ hồ sơ được ứng tuyển.')
            receiver = job.tacare_owner_user_id
        else:
            self._own_job(job.id)
            if not job.care_matching_enabled:
                raise BadRequest('Tin đã tắt gợi ý kết nối.')
            if profile not in self._visible_profiles() or not self._current_consent(profile, 'matching'):
                raise BadRequest('Hồ sơ không nhận lời mời mới.')
            receiver = profile.user_id
        if not receiver:
            raise BadRequest('Chưa có tài khoản nhận đề nghị.')
        existing = request.env['tacare.connection'].sudo().search([
            ('job_id', '=', job.id), ('profile_id', '=', profile.id),
            ('status', 'in', ('pending', 'accepted'))], limit=1)
        if existing:
            raise BadRequest('Đã có kết nối đang chờ hoặc đã đồng ý cho tin và hồ sơ này.')
        vals = {
            'type': kind, 'job_id': job.id, 'profile_id': profile.id,
            'sender_id': self._user().id, 'receiver_id': receiver.id,
            'message': (kw.get('message') or '').strip()[:2000],
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
        self._notify(receiver, ('Có đề nghị ứng tuyển mới: ' if kind == 'application' else 'Có lời mời trao đổi mới: ') + job.name, connection)
        return request.redirect(f'/tacare/connection/{connection.id}?notice=sent')

    @http.route('/tacare/connections', type='http', auth='user', website=True)
    def connections(self, **kw):
        domain = [] if self._role() == 'admin' else ['|', ('sender_id', '=', self._user().id),
                                                      ('receiver_id', '=', self._user().id)]
        items = request.env['tacare.connection'].sudo().search(domain, limit=100)
        return self._render('live_connections', items=items)

    @http.route('/tacare/connection/<int:connection_id>', type='http', auth='user', website=True)
    def connection_detail(self, connection_id, **kw):
        item = self._connection(connection_id)
        show_contact = (item.status == 'accepted' and item.contact_consent_id and
                        item.contact_consent_id.is_current('contact', item.organization_id, 'email'))
        return self._render('live_connection_detail', item=item, show_contact=show_contact)

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
        if item.receiver_id != self._user() or item.status != 'pending':
            raise Forbidden('Chỉ bên nhận phản hồi đề nghị đang chờ.')
        status = kw.get('status')
        if status not in ('accepted', 'declined'):
            raise BadRequest('Trạng thái không hợp lệ.')
        item.write({'status': status, 'decided_at': fields.Datetime.now()})
        self._notify(item.sender_id, ('Đã đồng ý trao đổi: ' if status == 'accepted' else 'Đã từ chối: ') + item.job_id.name, item)
        return request.redirect(f'/tacare/connection/{item.id}?notice=responded')

    @http.route('/tacare/connection/<int:connection_id>/cancel', type='http', auth='user', methods=['POST'], website=True)
    def connection_cancel(self, connection_id, **kw):
        item = self._connection(connection_id)
        if item.sender_id != self._user() or item.status != 'pending':
            raise Forbidden('Chỉ bên gửi hủy đề nghị đang chờ.')
        item.write({'status': 'cancelled'})
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
