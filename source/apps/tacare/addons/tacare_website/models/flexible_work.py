"""Flexible work extends the existing job and capability records, not a second profile store."""
import math
import re
from urllib.parse import urlsplit

from odoo import api, fields, models
from odoo.exceptions import ValidationError

WORK_MODES = [('onsite', 'Trực tiếp'), ('remote', 'Từ xa'), ('hybrid', 'Kết hợp')]
SCHEDULES = [('once', 'Một lần'), ('recurring', 'Định kỳ'),
             ('deadline', 'Theo hạn bàn giao'), ('flexible', 'Linh hoạt, cần hẹn')]
PAY_UNITS = [('hour', 'Giờ'), ('shift', 'Ca'), ('session', 'Buổi'), ('day', 'Ngày'),
             ('month', 'Tháng'), ('task', 'Công việc'), ('product', 'Sản phẩm'), ('trip', 'Chuyến')]
PAY_BASES = [('person', 'Mỗi người'), ('team', 'Cả nhóm'), ('package', 'Cả việc / gói / chuyến')]
WEEKDAYS = [(str(i), label) for i, label in enumerate(
    ['Thứ Hai', 'Thứ Ba', 'Thứ Tư', 'Thứ Năm', 'Thứ Sáu', 'Thứ Bảy', 'Chủ nhật'])]
TOOLS = [('client', 'Bên thuê chuẩn bị'), ('worker', 'Người làm mang theo'),
         ('shared', 'Mỗi bên một phần'), ('discuss', 'Cần trao đổi')]


class FlexibleWorkMixin(models.AbstractModel):
    _name = 'care.flex.mixin'
    _description = 'Structured flexible work terms'

    flex_category_id = fields.Many2one('care.capability.category', ondelete='restrict')
    flex_mode = fields.Selection(WORK_MODES)
    flex_region_id = fields.Many2one('res.country.state', ondelete='restrict')
    flex_location = fields.Char(size=250)
    flex_destination = fields.Char(size=250)
    flex_schedule = fields.Selection(SCHEDULES, default='flexible')
    flex_date_from = fields.Date()
    flex_date_to = fields.Date()
    flex_weekdays = fields.Char(size=20)
    flex_time_from = fields.Char(size=5)
    flex_time_to = fields.Char(size=5)
    flex_duration = fields.Float(string='Số giờ mỗi ca / buổi / ngày')
    flex_min_hours = fields.Float(string='Số giờ tối thiểu mỗi lần')
    flex_schedule_note = fields.Char(size=300)
    flex_rate_min = fields.Float()
    flex_rate_max = fields.Float()
    flex_pay_unit = fields.Selection(PAY_UNITS, default='hour')
    flex_pay_basis = fields.Selection(PAY_BASES, default='person')
    flex_cost_note = fields.Char(size=500)
    flex_negotiable = fields.Boolean(default=True)
    flex_tools = fields.Selection(TOOLS, default='discuss')
    flex_tools_note = fields.Char(size=500)
    flex_experience = fields.Text()
    flex_portfolio_url = fields.Char(size=1000)
    flex_image = fields.Image(max_width=1600, max_height=1200, attachment=True)
    flex_trip_service = fields.Selection([('driver', 'Chỉ tài xế, xe của khách'),
                                           ('vehicle', 'Xe kèm tài xế')])
    flex_trip_direction = fields.Selection([('oneway', 'Một chiều'), ('return', 'Khứ hồi')])
    flex_passengers = fields.Integer()
    flex_vehicle_note = fields.Char(size=300)
    flex_demo_key = fields.Char(index=True, copy=False)

    @api.constrains('flex_rate_min', 'flex_rate_max', 'flex_duration', 'flex_min_hours',
                    'flex_date_from', 'flex_date_to', 'flex_time_from', 'flex_time_to',
                    'flex_weekdays', 'flex_region_id', 'flex_portfolio_url', 'flex_passengers')
    def _check_flexible_values(self):
        for item in self:
            numbers = (item.flex_rate_min, item.flex_rate_max, item.flex_duration, item.flex_min_hours)
            if any(not math.isfinite(n) or n < 0 for n in numbers):
                raise ValidationError('Tiền công và thời lượng phải là số hữu hạn không âm.')
            if item.flex_rate_max and item.flex_rate_max < item.flex_rate_min:
                raise ValidationError('Mức cao nhất phải từ mức thấp nhất trở lên.')
            if item.flex_date_from and item.flex_date_to and item.flex_date_to < item.flex_date_from:
                raise ValidationError('Ngày kết thúc không được trước ngày bắt đầu.')
            for value in (item.flex_time_from, item.flex_time_to):
                if value and not re.fullmatch(r'(?:[01]\d|2[0-3]):[0-5]\d', value):
                    raise ValidationError('Giờ cần có dạng HH:MM, từ 00:00 đến 23:59.')
            if bool(item.flex_time_from) != bool(item.flex_time_to):
                raise ValidationError('Điền cả giờ bắt đầu và giờ kết thúc, hoặc để trống cả hai.')
            if item.flex_time_from and item.flex_time_to <= item.flex_time_from:
                raise ValidationError('Giờ kết thúc phải sau giờ bắt đầu; tách riêng ca qua đêm.')
            if item.flex_weekdays and any(x not in dict(WEEKDAYS) for x in item.flex_weekdays.split(',')):
                raise ValidationError('Ngày trong tuần không hợp lệ.')
            if item.flex_region_id and item.flex_region_id.country_id.code != 'VN':
                raise ValidationError('Chọn tỉnh / thành Việt Nam.')
            if item.flex_portfolio_url:
                url = urlsplit(item.flex_portfolio_url)
                if url.scheme != 'https' or not url.hostname or url.username or url.password:
                    raise ValidationError('Liên kết sản phẩm phải là HTTPS hợp lệ, không có thông tin đăng nhập.')
            if not 0 <= item.flex_passengers <= 100:
                raise ValidationError('Số hành khách không hợp lệ.')

    def _care_photo_url(self):
        """Existing credited stock photos illustrate a category, never its author."""
        self.ensure_one()
        photos = {'cleaning': 'cleaning', 'cooking': 'cooking', 'garden': 'garden',
                  'farm': 'farm', 'loading': 'warehouse', 'repair': 'tools',
                  'tutoring': 'learning', 'digital': 'digital', 'driving': 'driving', 'pets': 'cat'}
        category = self.flex_category_id.code
        if category in ('cleaning', 'cooking', 'garden', 'farm', 'loading', 'repair', 'tutoring', 'digital', 'pets'):
            return '/tacare_website/static/src/img/services/%s.webp' % category
        if self._name == 'hr.job' and self.care_opportunity_kind == 'recruitment':
            category = {'it': 'digital', 'marketing': 'digital', 'health': 'health',
                        'education': 'tutoring', 'logistics': 'loading'}.get(self.tacare_sector, '')
        if category not in photos:
            return '/tacare_website/static/src/img/services/placeholder.svg'
        return '/tacare_website/static/src/img/work-%s.jpg' % photos[category]

    def _flex_label(self, field):
        self.ensure_one()
        return dict(self._fields[field].selection).get(self[field], '')

    def _flex_price_label(self):
        self.ensure_one()
        if not self.flex_rate_min:
            return 'Chưa khai tiền công'
        money = lambda n: format(n, ',.0f').replace(',', '.')
        value = money(self.flex_rate_min)
        if self.flex_rate_max and self.flex_rate_max != self.flex_rate_min:
            value += '–' + money(self.flex_rate_max)
        unit = 'công việc' if self.flex_pay_unit == 'task' else self._flex_label('flex_pay_unit').lower()
        basis = '' if self.flex_pay_basis == 'package' else ' · ' + self._flex_label('flex_pay_basis').lower()
        return '%sđ / %s%s' % (value, unit, basis)

    def _flex_schedule_label(self):
        self.ensure_one()
        if self.flex_schedule == 'deadline':
            return ('Giao trước ' + self.flex_date_to.strftime('%d/%m/%Y')) if self.flex_date_to else 'Chưa khai hạn bàn giao'
        pieces = [self._flex_label('flex_schedule')]
        if self.flex_date_from:
            pieces.append(self.flex_date_from.strftime('%d/%m/%Y'))
        if self.flex_date_to:
            pieces.append('đến ' + self.flex_date_to.strftime('%d/%m/%Y'))
        if self.flex_schedule == 'recurring' and self.flex_weekdays:
            pieces.append(', '.join(dict(WEEKDAYS)[day] for day in self.flex_weekdays.split(',')))
        if self.flex_time_from:
            pieces.append(self.flex_time_from + '–' + self.flex_time_to)
        if self.flex_duration:
            pieces.append('%g giờ / lần' % self.flex_duration)
        return ' · '.join(filter(None, pieces))

    def _flex_ready_errors(self):
        self.ensure_one()
        errors = []
        for key, label in [('flex_category_id', 'nghề'), ('flex_mode', 'cách thực hiện'),
                           ('flex_schedule', 'kiểu lịch'), ('flex_rate_min', 'tiền công'),
                           ('flex_pay_unit', 'đơn vị giá'), ('flex_pay_basis', 'phạm vi giá')]:
            if not self[key]:
                errors.append(label)
        if self.flex_mode != 'remote' and (not self.flex_region_id or not self.flex_location):
            errors.append('tỉnh / thành và khu vực làm việc')
        if self.flex_schedule == 'once' and not self.flex_date_from:
            errors.append('ngày thực hiện')
        if self.flex_schedule == 'deadline' and not self.flex_date_to:
            errors.append('hạn bàn giao')
        if self.flex_schedule == 'recurring' and not self.flex_weekdays:
            errors.append('ngày trong tuần')
        if self.flex_pay_unit in ('shift', 'session', 'day') and not self.flex_duration:
            errors.append('số giờ của ca / buổi / ngày')
        if self.flex_pay_unit == 'trip' and (not self.flex_destination or not self.flex_trip_service or not self.flex_trip_direction):
            errors.append('điểm đến, loại dịch vụ và chiều chuyến')
        if self.flex_trip_service == 'vehicle' and (not self.flex_passengers or not self.flex_vehicle_note):
            errors.append('số hành khách và yêu cầu xe')
        return errors


class FlexibleJob(models.Model):
    _name = 'hr.job'
    _inherit = ['hr.job', 'care.flex.mixin']

    care_opportunity_kind = fields.Selection([('recruitment', 'Tuyển dụng'),
                                               ('flexible', 'Việc thời vụ')],
                                              default='flexible', required=True, index=True)
    flex_skill_ids = fields.Many2many('hr.skill', 'care_flex_job_skill_rel')
    flex_preferred_skill_ids = fields.Many2many('hr.skill', 'care_flex_job_preferred_rel')

    def _care_publish_errors(self):
        self.ensure_one()
        if self.care_opportunity_kind != 'flexible':
            return super()._care_publish_errors()
        errors = self._flex_ready_errors()
        if not self.name or not self.tacare_description_text:
            errors.append('tiêu đề và mô tả')
        if not self.tacare_owner_user_id or self.no_of_recruitment < 1:
            errors.append('người đăng và số người cần')
        return errors

    def _care_income_label(self):
        self.ensure_one()
        return self._flex_price_label() if self.care_opportunity_kind == 'flexible' else super()._care_income_label()


class FlexibleCapability(models.Model):
    _name = 'care.profile.capability'
    _inherit = ['care.profile.capability', 'care.flex.mixin']

    flex_category_id = fields.Many2one(related='category_id', readonly=False, string='Nghề nhận việc')
    flex_rate_min = fields.Monetary(related='rate_min', readonly=False, string='Tiền công từ mức')
    flex_rate_max = fields.Monetary(related='rate_max', readonly=False, string='Tiền công đến mức')
    flex_skill_ids = fields.Many2many('hr.skill', 'care_flex_capability_skill_rel')
    flex_preferred_skill_ids = fields.Many2many('hr.skill', 'care_flex_capability_preferred_rel')
    flex_state = fields.Selection([('draft', 'Nháp'), ('available', 'Đang nhận việc'),
                                    ('paused', 'Tạm ngừng')], default='draft', required=True)

    def _flex_ready_errors(self):
        errors = super()._flex_ready_errors()
        if not self.title or not self.description:
            errors.append('tiêu đề và mô tả công việc nhận làm')
        return errors

    def _flex_canonical_values(self, values):
        values = dict(values)
        for alias, original in [('flex_category_id', 'category_id'),
                                ('flex_rate_min', 'rate_min'), ('flex_rate_max', 'rate_max')]:
            if alias in values:
                values[original] = values.pop(alias)
        return values

    @api.model_create_multi
    def create(self, vals_list):
        # Resolve aliases before INSERT: the original category is SQL NOT NULL.
        records = super().create([self._flex_canonical_values(v) for v in vals_list])
        records._check_flexible_values()
        return records

    def write(self, vals):
        result = super().write(self._flex_canonical_values(vals))
        self._check_flexible_values()
        return result


class FlexibleProfile(models.Model):
    _inherit = 'tacare.profile'

    care_recruitment_enabled = fields.Boolean(default=False)
    flex_demo_key = fields.Char(index=True, copy=False)
