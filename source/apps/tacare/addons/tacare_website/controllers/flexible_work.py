"""Owner-scoped demo workflows for flexible work, using the existing Odoo records."""
import base64
from io import BytesIO

from PIL import Image, ImageOps, UnidentifiedImageError
from werkzeug.exceptions import BadRequest, Forbidden, NotFound
from odoo import fields, http
from odoo.exceptions import ValidationError
from odoo.http import request

from .live import TacareLive
from ..models.marketplace.flexible_work import WORK_MODES, SCHEDULES, PAY_UNITS, PAY_BASES, WEEKDAYS, TOOLS


class TacareFlexible(TacareLive):
    def _flex_user(self):
        if self._user()._is_public() or self._role() not in ('candidate', 'business', 'admin'):
            raise Forbidden('Đăng nhập tài khoản đã được cấp quyền để tiếp tục.')

    def _render(self, template, site='tacare', **values):
        values.setdefault('work_categories', request.env['care.capability.category'].sudo().search([]))
        values.setdefault('work_skills', request.env['hr.skill'].sudo().search([
            ('care_code', '=like', 'flex_%'), ('care_active', '=', True)]))
        values.update(work_modes=WORK_MODES, work_schedules=SCHEDULES, pay_units=PAY_UNITS,
                      pay_bases=PAY_BASES, weekdays=WEEKDAYS, work_tools=TOOLS)
        return super()._render(template, site=site, **values)

    def _flex_own(self, model, record_id):
        self._flex_user()
        if model == 'hr.job' and self._role() == 'business':
            return self._own_job(record_id, 'manage')
        company_ids = self._user().company_ids.ids
        domain = [('id', '=', record_id), ('company_id', 'in', company_ids)]
        if model == 'hr.job':
            domain.append(('care_opportunity_kind', '=', 'flexible'))
            if self._role() != 'admin':
                domain.append(('tacare_owner_user_id', '=', self._user().id))
        else:
            domain.append(('profile_id.status', '!=', 'archived'))
            if self._role() != 'admin':
                domain.append(('profile_id.user_id', '=', self._user().id))
        record = request.env[model].sudo().search(domain, limit=1)
        if not record:
            raise NotFound()
        return record

    def _flex_profile(self, create=False):
        self._flex_user()
        profile = request.env['tacare.profile'].sudo().search([('user_id', '=', self._user().id)], limit=1)
        if not profile and create:
            profile = request.env['tacare.profile'].sudo().create({
                'user_id': self._user().id, 'name': self._user().name,
                'care_recruitment_enabled': False, 'scope': 'private'})
        return profile








    def _work_values(self, record, submitted=None):
        vals = {'matching_enabled': 'on' if not record or record._name == 'hr.job' and record.care_matching_enabled else ''}
        if record:
            for name, field in record._fields.items():
                if name.startswith('flex_') and field.type not in ('many2many', 'binary'):
                    value = record[name]
                    vals[name] = str(value.id if field.type == 'many2one' and value else value or '')
            vals.update(name=record.title if record._name == 'care.profile.capability' else record.name,
                        description=record.description if record._name == 'care.profile.capability' else record.tacare_description_text,
                        quantity=str(record.no_of_recruitment) if record._name == 'hr.job' else '1',
                        skill_ids=record.flex_skill_ids.ids, preferred_skill_ids=record.flex_preferred_skill_ids.ids,
                        flex_negotiable='on' if record.flex_negotiable else '')
            if record._name == 'care.profile.capability':
                vals['profile_id'] = str(record.profile_id.id)
        else:
            vals.update(flex_mode='onsite', flex_schedule='flexible', flex_pay_unit='hour',
                        flex_pay_basis='person', flex_tools='discuss', flex_negotiable='on', quantity='1')
            vals['profile_id'] = request.params.get('profile_id', '')
        if submitted is not None:
            vals.update(submitted)
            vals['skill_ids'] = [int(x) for x in request.httprequest.form.getlist('skill_ids') if x.isdigit()]
            vals['preferred_skill_ids'] = [int(x) for x in request.httprequest.form.getlist('preferred_skill_ids') if x.isdigit()]
            vals['flex_weekdays'] = ','.join(request.httprequest.form.getlist('weekdays'))
            vals['flex_negotiable'] = submitted.get('flex_negotiable', '')
            vals['matching_enabled'] = submitted.get('matching_enabled', '')
        for name in ('geo_lat', 'geo_lon', 'geo_address', 'geo_share'):
            if submitted is not None:
                vals[name] = submitted.get(name, '')
            elif record:
                vals[name] = ('on' if record.geo_share else '') if name == 'geo_share' else (
                    str(record[name]) if record.geo_set else '')
        return vals



    def _parse_work(self, kw):
        form = request.httprequest.form
        vals = {}
        model = request.env['hr.job']
        texts = ('flex_location', 'flex_destination', 'flex_time_from', 'flex_time_to',
                 'flex_schedule_note', 'flex_cost_note', 'flex_tools_note', 'flex_experience',
                 'flex_portfolio_url', 'flex_vehicle_note')
        selections = ('flex_mode', 'flex_schedule', 'flex_pay_unit', 'flex_pay_basis', 'flex_tools',
                      'flex_trip_service', 'flex_trip_direction')
        numbers = ('flex_rate_min', 'flex_rate_max', 'flex_duration', 'flex_min_hours')
        allowed = set(texts + selections + numbers + ('name', 'description', 'quantity', 'id', 'intent',
            'csrf_token', 'flex_category_id', 'flex_region_id', 'flex_date_from', 'flex_date_to',
            'weekdays', 'skill_ids', 'preferred_skill_ids', 'flex_negotiable', 'flex_passengers',
            'flex_image', 'remove_image', 'matching_enabled'))
        from ..sites.tacare.nearby import GEO_INPUTS, parse_location
        allowed.update(GEO_INPUTS)
        if request.httprequest.path.startswith('/tuhoso/'):
            allowed.add('profile_id')
        if set(form.keys()) - allowed:
            raise ValidationError('Biểu mẫu có trường không được phép thay đổi.')
        for key in texts:
            value = (kw.get(key) or '').strip()
            if len(value) > (model._fields[key].size or 5000):
                raise ValidationError('Nội dung quá dài, vui lòng rút gọn.')
            vals[key] = value
        for key in selections:
            value = kw.get(key) or False
            if value and value not in dict(model._fields[key].selection):
                raise ValidationError('Chọn giá trị hợp lệ trong danh sách.')
            vals[key] = value
        for key in numbers:
            vals[key] = float(kw.get(key) or 0)
        vals['flex_passengers'] = int(kw.get('flex_passengers') or 0)
        for key in ('flex_date_from', 'flex_date_to'):
            vals[key] = fields.Date.to_date(kw[key]) if kw.get(key) else False
        for key, target in [('flex_category_id', 'care.capability.category'), ('flex_region_id', 'res.country.state')]:
            record_id = int(kw.get(key) or 0)
            record = request.env[target].sudo().browse(record_id).exists()
            if record_id and not record:
                raise ValidationError('Nghề hoặc khu vực không tồn tại.')
            vals[key] = record.id
        days = form.getlist('weekdays')
        if any(x not in dict(WEEKDAYS) for x in days):
            raise ValidationError('Lịch tuần không hợp lệ.')
        vals['flex_weekdays'] = ','.join(sorted(set(days)))
        for field, key in [('flex_skill_ids', 'skill_ids'), ('flex_preferred_skill_ids', 'preferred_skill_ids')]:
            ids = [int(x) for x in form.getlist(key)]
            skills = request.env['hr.skill'].sudo().search([('id', 'in', ids),
                ('care_code', '=like', 'flex_%'), ('care_active', '=', True)])
            if set(ids) != set(skills.ids) or len(ids) > 30:
                raise ValidationError('Kỹ năng không hợp lệ.')
            vals[field] = [(6, 0, skills.ids)]
        if set(form.getlist('skill_ids')) & set(form.getlist('preferred_skill_ids')):
            raise ValidationError('Một kỹ năng chỉ chọn bắt buộc hoặc ưu tiên.')
        vals['flex_negotiable'] = kw.get('flex_negotiable') == 'on'
        vals.update(parse_location(kw))
        if vals['geo_set'] and vals['flex_mode'] != 'remote':
            if not vals['flex_location']:
                raise ValidationError('Điền địa chỉ đầy đủ cho điểm đã chọn trước khi lưu.')
            # One canonical visible address; never silently save a different
            # hidden geocoder label or accept a client-provided map URL.
            vals['geo_address'] = vals['flex_location']
        if vals['flex_pay_unit'] != 'trip':
            # Hidden trip inputs can still contain values after switching price unit.
            vals.update(flex_destination=False, flex_trip_service=False,
                        flex_trip_direction=False, flex_passengers=0, flex_vehicle_note=False)
        if vals['flex_mode'] == 'remote':
            vals.update(flex_region_id=False, flex_location=False)
            vals.update(geo_set=False, geo_lat=0, geo_lon=0, geo_address=False, geo_share=False)
            if vals['flex_pay_unit'] == 'trip':
                raise ValidationError('Việc theo chuyến cần cách thực hiện trực tiếp hoặc kết hợp.')
        if kw.get('remove_image') == 'on':
            vals['flex_image'] = False
        upload = request.httprequest.files.get('flex_image')
        if upload and upload.filename:
            raw = upload.read(5 * 1024 * 1024 + 1)
            if len(raw) > 5 * 1024 * 1024:
                raise ValidationError('Ảnh tối đa 5 MB.')
            try:
                with Image.open(BytesIO(raw)) as image:
                    if image.width * image.height > 20000000:
                        raise ValidationError('Ảnh quá lớn; tối đa 20 megapixel.')
                    image = ImageOps.exif_transpose(image).convert('RGB')
                    image.thumbnail((1600, 1200))
                    output = BytesIO()
                    image.save(output, format='JPEG', quality=85)  # Re-encode without EXIF/location.
                    vals['flex_image'] = base64.b64encode(output.getvalue())
            except (UnidentifiedImageError, OSError, Image.DecompressionBombError):
                raise ValidationError('Chọn một ảnh JPG, PNG hoặc WebP hợp lệ.')
        return vals

    @http.route(['/kvl/flexible/save', '/tuhoso/work/save'], auth='user', methods=['POST'], website=True)
    def work_save(self, **kw):
        self._flex_user()
        service = request.httprequest.path.startswith('/tuhoso/')
        try:
            record_id = int(kw.get('id') or 0)
        except ValueError:
            raise BadRequest('ID không hợp lệ.')
        item = self._flex_own('care.profile.capability' if service else 'hr.job', record_id) if record_id else False
        if item and service and kw.get('profile_id') and kw['profile_id'] != str(item.profile_id.id):
            raise Forbidden('Không chuyển mục nhận việc sang hồ sơ khác qua biểu mẫu này.')
        if item and not service and item.tacare_status not in ('draft', 'published', 'paused', 'closed'):
            raise Forbidden()
        try:
            with request.env.cr.savepoint():
                name = (kw.get('name') or '').strip()
                description = (kw.get('description') or '').strip()
                if not 2 <= len(name) <= 180 or len(description) > 20000:
                    raise ValidationError('Tiêu đề cần 2–180 ký tự; mô tả tối đa 20.000 ký tự.')
                if kw.get('intent') not in ('draft', 'publish'):
                    raise ValidationError('Thao tác không hợp lệ.')
                vals = self._parse_work(kw)
                publish = kw['intent'] == 'publish'
                if service:
                    if not vals['flex_category_id']:
                        raise ValidationError('Chọn nghề cho công việc nhận làm.')
                    vals.update(title=name, description=description,
                                flex_state='available' if publish else 'draft')
                    if not item:
                        vals['profile_id'] = self._flex_profile(create=True).id
                        vals['currency_id'] = request.env.ref('base.VND').id
                else:
                    quantity = int(kw.get('quantity') or 1)
                    if not 1 <= quantity <= 100:
                        raise ValidationError('Số người cần từ 1 đến 100.')
                    vals.update(name=name, tacare_description_text=description, no_of_recruitment=quantity,
                        tacare_location=vals['flex_location'], tacare_type='task',
                        tacare_mode={'onsite': 'office', 'remote': 'remote', 'hybrid': 'hybrid'}.get(vals['flex_mode']),
                        care_matching_enabled=kw.get('matching_enabled') == 'on',
                        tacare_status='published' if publish else 'draft', is_published=publish)
                    if not item:
                        work_company = self._website('khovieclam').company_id
                        if work_company not in self._user().company_ids:
                            raise Forbidden('Tài khoản chưa được cấp phạm vi Kho Việc Làm.')
                        organization = self._organization() if self._role() == 'business' else self._user().partner_id.commercial_partner_id
                        vals.update(care_opportunity_kind='flexible',
                            tacare_owner_user_id=self._user().id,
                            tacare_owner_partner_id=organization.id,
                            company_id=work_company.id, website_id=self._website('khovieclam').id)
                if item:
                    item.write(vals)
                else:
                    item = request.env['care.profile.capability' if service else 'hr.job'].sudo().create(vals)
                if publish:
                    missing = item._flex_ready_errors() if service else item._care_publish_errors()
                    if not description:
                        missing.append('mô tả công việc')
                    if missing:
                        raise ValidationError('Bổ sung: ' + ', '.join(missing) + '.')
                self._audit('flexible.save', item)
        except (ValidationError, ValueError, TypeError, OverflowError) as exc:
            # Savepoint rolls back partial records/attachments; submitted values stay visible.
            record = self._flex_own('care.profile.capability' if service else 'hr.job', record_id) if record_id else False
            return self._render('work_form', site='tuhoso' if service else 'khovieclam',
                record=record, is_service=service, vals=self._work_values(record, kw),
                error=str(exc) if isinstance(exc, ValidationError) else 'Kiểm tra số tiền, thời lượng, ngày và các lựa chọn.')
        return request.redirect('/tuhoso/work/%s' % item.id if service else '/kvl/flexible/mine?notice=saved')

    @http.route(['/kvl/flexible/<int:record_id>/status', '/tuhoso/work/<int:record_id>/status'],
                auth='user', methods=['POST'], website=True)
    def work_status(self, record_id, **kw):
        service = request.httprequest.path.startswith('/tuhoso/')
        item = self._flex_own('care.profile.capability' if service else 'hr.job', record_id)
        allowed = ('draft', 'available', 'paused') if service else ('draft', 'published', 'paused', 'closed')
        state = kw.get('state')
        if set(kw) - {'csrf_token', 'state'}:
            raise BadRequest('Biểu mẫu có trường không được phép thay đổi.')
        if state not in allowed:
            raise BadRequest('Trạng thái không hợp lệ.')
        current = item.flex_state if service else item.tacare_status
        transitions = ({'draft': ('available',), 'available': ('paused',), 'paused': ('available',)} if service else
            {'draft': ('published',), 'published': ('paused', 'closed'), 'paused': ('published', 'closed'), 'closed': ('published',)})
        if state not in transitions.get(current, ()):
            raise BadRequest('Thao tác không phù hợp với trạng thái hiện tại. Vui lòng tải lại trang.')
        if state in ('available', 'published'):
            missing = item._flex_ready_errors() if service else item._care_publish_errors()
            if missing:
                raise BadRequest('Bổ sung dữ liệu trước khi mở lại: ' + ', '.join(missing))
        item.write({'flex_state': state} if service else {'tacare_status': state, 'is_published': state == 'published'})
        self._audit('flexible.status', item, changes={'state': state})
        return request.redirect('/tuhoso/profiles?kind=flexible' if service else '/kvl/flexible/mine')

    @http.route(['/kvl/flexible/<int:record_id>/image', '/tuhoso/work/<int:record_id>/image'],
                auth='public', website=True)
    def work_image(self, record_id, **kw):
        service = request.httprequest.path.startswith('/tuhoso/')
        if service:
            item = self._flex_own('care.profile.capability', record_id)
        else:
            item = request.env['hr.job'].sudo().search(self._job_domain() + [
                ('id', '=', record_id), ('care_opportunity_kind', '=', 'flexible')], limit=1)
            if not item:
                item = self._flex_own('hr.job', record_id)
        if not item.flex_image:
            raise NotFound()
        return request.make_response(base64.b64decode(item.flex_image), headers=[
            ('Content-Type', 'image/jpeg'), ('Cache-Control', 'private, no-store'),
            ('X-Content-Type-Options', 'nosniff')])
