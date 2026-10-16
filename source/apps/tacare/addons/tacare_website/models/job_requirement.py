from odoo import api, fields, models
from odoo.exceptions import ValidationError


class CareJobSector(models.Model):
    _name = 'care.job.sector'
    _description = 'Ngành nghề tuyển dụng TA.CARE'
    _order = 'name'

    name = fields.Char(required=True, translate=True)
    code = fields.Char(required=True, index=True)
    active = fields.Boolean(default=True)
    _unique_code = models.Constraint('unique(code)', 'Mã ngành nghề đã tồn tại.')


class CareJobRequirement(models.Model):
    _name = 'care.job.requirement'
    _description = 'Điều kiện tuyển dụng TA.CARE'
    _order = 'sequence, id'

    job_id = fields.Many2one('hr.job', required=True, ondelete='cascade', index=True)
    company_id = fields.Many2one('res.company', related='job_id.company_id', store=True)
    sequence = fields.Integer(default=10)
    category = fields.Selection([
        ('education', 'Học vấn'), ('major', 'Chuyên ngành học'),
        ('experience', 'Kinh nghiệm'), ('technical', 'Kỹ năng chuyên môn'),
        ('soft', 'Kỹ năng mềm'), ('tool', 'Công cụ / nền tảng'),
        ('language', 'Ngoại ngữ'), ('certificate', 'Chứng chỉ'),
        ('evidence', 'Minh chứng'), ('other', 'Điều kiện khác'),
    ], required=True, index=True)
    name = fields.Char(required=True)
    mandatory = fields.Boolean(default=True, index=True)
    skill_id = fields.Many2one('hr.skill', ondelete='set null')

    @api.constrains('name')
    def _check_name(self):
        for item in self:
            if len((item.name or '').strip()) < 2:
                raise ValidationError('Điều kiện cần ít nhất hai ký tự.')
