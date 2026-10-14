"""Structured capability, availability, service area and preferences."""
from odoo import api, fields, models
from odoo.exceptions import ValidationError

from .hr_job import TYPES


class CareProfileCapability(models.Model):
    _name = 'care.profile.capability'
    _description = 'TA.CARE Profile Capability'

    company_id = fields.Many2one('res.company', related='profile_id.company_id', store=True, index=True)
    profile_id = fields.Many2one('tacare.profile', required=True, ondelete='cascade', index=True)
    category_id = fields.Many2one('care.capability.category', required=True, ondelete='restrict')
    title = fields.Char(required=True)
    description = fields.Text()
    rate_min = fields.Monetary(currency_field='currency_id')
    rate_max = fields.Monetary(currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    active = fields.Boolean(default=True)

    @api.constrains('rate_min', 'rate_max')
    def _check_rates(self):
        for item in self:
            if item.rate_min < 0 or item.rate_max < 0 or item.rate_max and item.rate_min > item.rate_max:
                raise ValidationError('Khoảng thù lao năng lực không hợp lệ.')


class CareAvailability(models.Model):
    _name = 'care.availability'
    _description = 'TA.CARE Availability'

    company_id = fields.Many2one('res.company', related='profile_id.company_id', store=True, index=True)
    profile_id = fields.Many2one('tacare.profile', required=True, ondelete='cascade', index=True)
    availability_type = fields.Selection([('weekly', 'Hàng tuần'), ('date', 'Theo ngày')],
                                         required=True, default='weekly')
    weekday = fields.Selection([(str(i), label) for i, label in enumerate([
        'Thứ hai', 'Thứ ba', 'Thứ tư', 'Thứ năm', 'Thứ sáu', 'Thứ bảy', 'Chủ nhật'])])
    date = fields.Date()
    time_from = fields.Float()
    time_to = fields.Float()
    timezone = fields.Char(default='Asia/Ho_Chi_Minh', required=True)
    active = fields.Boolean(default=True)

    @api.constrains('availability_type', 'weekday', 'date', 'time_from', 'time_to')
    def _check_window(self):
        for item in self:
            if item.availability_type == 'weekly' and not item.weekday:
                raise ValidationError('Lịch hàng tuần cần chọn thứ.')
            if item.availability_type == 'date' and not item.date:
                raise ValidationError('Lịch theo ngày cần có ngày.')
            if not (0 <= item.time_from < item.time_to <= 24):
                raise ValidationError('Giờ bắt đầu/kết thúc phải nằm trong một ngày và theo đúng thứ tự.')


class CareServiceArea(models.Model):
    _name = 'care.service.area'
    _description = 'TA.CARE Service Area'

    company_id = fields.Many2one('res.company', related='profile_id.company_id', store=True, index=True)
    profile_id = fields.Many2one('tacare.profile', required=True, ondelete='cascade', index=True)
    area_type = fields.Selection([('remote', 'Từ xa'), ('city', 'Thành phố'),
                                  ('radius', 'Bán kính')], required=True, default='city')
    lat = fields.Float(groups='base.group_system')
    lng = fields.Float(groups='base.group_system')
    radius_km = fields.Float()
    city_text = fields.Char()
    district_text = fields.Char()
    active = fields.Boolean(default=True)

    @api.constrains('radius_km', 'lat', 'lng')
    def _check_area(self):
        for item in self:
            if item.radius_km < 0 or not -90 <= item.lat <= 90 or not -180 <= item.lng <= 180:
                raise ValidationError('Tọa độ hoặc bán kính không hợp lệ.')


class CarePreference(models.Model):
    _name = 'care.preference'
    _description = 'TA.CARE Opportunity Preference'

    company_id = fields.Many2one('res.company', related='profile_id.company_id', store=True, index=True)
    profile_id = fields.Many2one('tacare.profile', required=True, ondelete='cascade', index=True)
    opportunity_kind = fields.Selection(TYPES, required=True)
    min_rate = fields.Monetary(currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    max_distance_km = fields.Float()
    preferred_time = fields.Text()
    excluded_category_ids = fields.Many2many('care.capability.category',
                                               relation='care_preference_excluded_category_rel')

    @api.constrains('min_rate', 'max_distance_km')
    def _check_preference(self):
        for item in self:
            if item.min_rate < 0 or item.max_distance_km < 0:
                raise ValidationError('Mức tối thiểu và khoảng cách không được âm.')
