from odoo import api, fields, models
from odoo.exceptions import ValidationError

SECTORS = [
    ('it', 'Công nghệ thông tin'), ('ecommerce', 'Thương mại điện tử'),
    ('logistics', 'Logistics'), ('marketing', 'Marketing'),
    ('sales', 'Kinh doanh/bán hàng'), ('health', 'Y tế'),
    ('food', 'Nông nghiệp/thực phẩm'), ('support', 'Chăm sóc khách hàng'),
    ('hr', 'Nhân sự/tuyển dụng'),
]
TYPES = [
    ('internship', 'Thực tập'), ('full_time', 'Toàn thời gian'),
    ('part_time', 'Bán thời gian'), ('freelance', 'Freelance'),
    ('task', 'Task'), ('project', 'Dự án'),
]
MODES = [('office', 'Tại văn phòng'), ('hybrid', 'Kết hợp'), ('remote', 'Từ xa')]
STATES = [('draft', 'Nháp'), ('published', 'Đang hiển thị'),
          ('paused', 'Tạm ngừng'), ('closed', 'Đã đóng')]


class HrJob(models.Model):
    _inherit = 'hr.job'

    tacare_owner_partner_id = fields.Many2one('res.partner', index=True, copy=False)
    tacare_owner_user_id = fields.Many2one('res.users', copy=False)
    tacare_sector = fields.Selection(SECTORS)
    tacare_type = fields.Selection(TYPES)
    tacare_mode = fields.Selection(MODES)
    tacare_location = fields.Char()
    tacare_required_skills = fields.Char(help='Comma-separated skills for the local first version.')
    tacare_preferred_skills = fields.Char()
    tacare_status = fields.Selection(STATES, default='draft', required=True, index=True)
    tacare_start = fields.Date()
    tacare_deadline = fields.Date()
    tacare_schedule = fields.Char()
    tacare_pay = fields.Char()
    tacare_outcome = fields.Text()
    tacare_description_text = fields.Text()
    # JSON design names map onto the already stored tacare_* fields. Related
    # aliases avoid a second, diverging owner/state/location/deadline column.
    care_employer_partner_id = fields.Many2one(related='tacare_owner_partner_id', readonly=False, string='Tổ chức tuyển dụng TA.CARE')
    care_state = fields.Selection(related='tacare_status', readonly=False, string='Trạng thái cơ hội TA.CARE')
    care_deadline = fields.Date(related='tacare_deadline', readonly=False, string='Hạn ứng tuyển TA.CARE')
    care_location = fields.Char(related='tacare_location', readonly=False, string='Địa điểm cơ hội TA.CARE')
    care_experience_min = fields.Float(default=0)
    care_salary_min = fields.Monetary(currency_field='care_currency_id')
    care_salary_max = fields.Monetary(currency_field='care_currency_id')
    care_currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    care_operator_user_ids = fields.Many2many('res.users', relation='hr_job_care_operator_rel')
    care_revision = fields.Integer(default=1, required=True, readonly=True)
    care_matching_enabled = fields.Boolean(default=True)
    care_revision_ids = fields.One2many('care.job.revision', 'job_id', string='Các phiên bản tin')

    def _care_sync_job_skills(self):
        """Keep Odoo's native recruitment skill relation aligned with the web form."""
        skill_model = self.env['hr.skill'].sudo()
        type_model = self.env['hr.skill.type'].sudo()
        level_model = self.env['hr.skill.level'].sudo()
        relation_model = self.env['hr.job.skill'].sudo()
        for job in self:
            required = [x.strip() for x in (job.tacare_required_skills or '').split(',') if x.strip()]
            preferred = [x.strip() for x in (job.tacare_preferred_skills or '').split(',') if x.strip()]
            relation_model.search([('job_id', '=', job.id)]).unlink()
            seen = set()
            for name, mandatory in [(x, True) for x in required] + [(x, False) for x in preferred]:
                key = name.casefold()
                if key in seen:
                    continue
                seen.add(key)
                skill = skill_model.search([('name', '=ilike', name)], limit=1)
                if not skill:
                    skill_type = type_model.search([('name', '=', 'TA.CARE')], limit=1)
                    if not skill_type:
                        skill_type = type_model.create({'name': 'TA.CARE'})
                    skill = skill_model.create({'name': name, 'skill_type_id': skill_type.id})
                level = level_model.search([('skill_type_id', '=', skill.skill_type_id.id)], order='level_progress asc, id asc', limit=1)
                if not level:
                    level = level_model.create({'name': 'Cơ bản', 'skill_type_id': skill.skill_type_id.id})
                relation_model.create({'job_id': job.id, 'skill_id': skill.id,
                                       'skill_type_id': skill.skill_type_id.id,
                                       'skill_level_id': level.id,
                                       'care_mandatory': mandatory})

    @api.constrains('care_experience_min', 'care_salary_min', 'care_salary_max', 'tacare_start', 'tacare_deadline')
    def _check_care_requirements(self):
        for job in self:
            if job.care_experience_min < 0 or job.care_salary_min < 0 or job.care_salary_max < 0:
                raise ValidationError('Kinh nghiệm và thù lao không được âm.')
            if job.care_salary_max and job.care_salary_min > job.care_salary_max:
                raise ValidationError('Mức thù lao cao nhất phải từ mức thấp nhất trở lên.')
            if job.tacare_start and job.tacare_deadline and job.tacare_deadline < job.tacare_start:
                raise ValidationError('Hạn nhận đề nghị phải sau ngày bắt đầu.')
