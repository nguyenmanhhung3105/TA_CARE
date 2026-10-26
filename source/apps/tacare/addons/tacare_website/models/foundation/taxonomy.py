"""Reuse Odoo HR skill taxonomy and job-skill relation."""
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class HrSkill(models.Model):
    _inherit = 'hr.skill'

    care_code = fields.Char(index=True)
    care_active = fields.Boolean(default=True)
    _unique_care_code = models.Constraint('unique(care_code)', 'Mã kỹ năng TA.CARE phải duy nhất.')


class HrJobSkill(models.Model):
    _inherit = 'hr.job.skill'

    care_mandatory = fields.Boolean(default=True)
    care_weight = fields.Float(default=1.0)

    @api.constrains('care_weight')
    def _check_weight(self):
        for item in self:
            if item.care_weight < 0 or item.care_weight > 100:
                raise ValidationError('Trọng số kỹ năng phải từ 0 đến 100.')


class CareCapabilityCategory(models.Model):
    _name = 'care.capability.category'
    _description = 'TA.CARE Capability Category'
    _order = 'name'

    code = fields.Char(required=True, index=True)
    name = fields.Char(required=True)
    parent_id = fields.Many2one('care.capability.category', ondelete='restrict', index=True)
    child_ids = fields.One2many('care.capability.category', 'parent_id')
    risk_level = fields.Selection([('low', 'Thấp'), ('medium', 'Trung bình'),
                                   ('high', 'Cao')], default='low', required=True)
    active = fields.Boolean(default=True)

    _unique_code = models.Constraint('unique(code)', 'Mã danh mục năng lực phải duy nhất.')

    @api.constrains('parent_id')
    def _check_parent(self):
        if not self._check_recursion():
            raise ValidationError('Danh mục năng lực không được có quan hệ cha con vòng lặp.')
