import math
from odoo import api, fields, models
from odoo.exceptions import ValidationError

SECTORS = [
    ('it', 'Công nghệ thông tin'), ('ecommerce', 'Thương mại điện tử'),
    ('logistics', 'Logistics'), ('marketing', 'Marketing'),
    ('sales', 'Kinh doanh/bán hàng'), ('health', 'Y tế'),
    ('food', 'Nông nghiệp/thực phẩm'), ('support', 'Chăm sóc khách hàng'),
    ('hr', 'Nhân sự/tuyển dụng'), ('design', 'Thiết kế'),
]
TYPES = [
    ('employment', 'Việc làm'),
    ('internship', 'Thực tập'), ('full_time', 'Toàn thời gian'),
    ('part_time', 'Bán thời gian'), ('freelance', 'Freelance'),
    ('task', 'Task'), ('project', 'Dự án'),
]
MODES = [('office', 'Tại văn phòng'), ('hybrid', 'Kết hợp'), ('remote', 'Từ xa')]
STATES = [('draft', 'Nháp'), ('published', 'Đang hiển thị'),
          ('paused', 'Tạm ngừng'), ('closed', 'Đã đóng')]


def preferred_currency(env):
    vnd = env.ref('base.VND', raise_if_not_found=False)
    return vnd if vnd and vnd.active else env.company.currency_id


def validate_numeric_values(values, names):
    for name in names:
        if name in values:
            try:
                number = float(values[name] or 0)
            except (ValueError, TypeError, OverflowError):
                raise ValidationError('Giá trị số không hợp lệ.')
            if not math.isfinite(number) or number < 0:
                raise ValidationError('Giá trị phải là số hữu hạn không âm.')


class HrJob(models.Model):
    _inherit = 'hr.job'

    tacare_owner_partner_id = fields.Many2one('res.partner', index=True, copy=False)
    tacare_owner_user_id = fields.Many2one('res.users', copy=False)
    tacare_sector = fields.Selection(SECTORS)
    care_sector_id = fields.Many2one('care.job.sector', string='Ngành nghề tuyển dụng', ondelete='restrict')
    care_position = fields.Char(string='Vị trí tuyển dụng')
    care_position_id = fields.Many2one('care.job.position', ondelete='restrict', string='Nhóm nghề')
    care_region_id = fields.Many2one('res.country.state', ondelete='restrict', string='Tỉnh / thành làm việc')
    care_candidate_requirements = fields.Text(string='Yêu cầu ứng viên')
    care_benefits = fields.Text(string='Quyền lợi')
    care_training_provided = fields.Boolean(string='Chấp nhận đào tạo từ đầu')
    care_skills_any = fields.Boolean(string='Chỉ cần một trong các kỹ năng bắt buộc')
    care_salary_display = fields.Selection([('range', 'Khoảng lương'), ('from', 'Từ mức'),
        ('to', 'Đến mức'), ('negotiable', 'Thỏa thuận')], default='negotiable')
    care_salary_basis = fields.Selection([('base', 'Lương cố định'), ('total', 'Tổng thu nhập')], default='base')
    care_salary_tax = fields.Selection([('gross', 'Trước thuế (gross)'), ('net', 'Sau thuế (net)'),
        ('unknown', 'Chưa xác định')], default='unknown')
    care_education_note = fields.Char(string='Học vấn bắt buộc')
    care_language_note = fields.Char(string='Ngoại ngữ bắt buộc')
    care_license_note = fields.Char(string='Giấy phép / chứng chỉ bắt buộc')
    care_schedule_required = fields.Boolean(string='Lịch làm việc là điều kiện bắt buộc')
    care_start_flexible = fields.Boolean(default=True, string='Có thể thỏa thuận ngày bắt đầu')
    care_level = fields.Selection([('intern', 'Thực tập'), ('junior', 'Mới bắt đầu'),
                                   ('middle', 'Có kinh nghiệm'), ('senior', 'Chuyên gia')])
    care_work_fraction = fields.Selection([('full', 'Toàn thời gian'), ('part', 'Bán thời gian'),
                                           ('flexible', 'Theo đầu ra / linh hoạt')])
    care_days_per_week = fields.Integer(string='Số ngày mỗi tuần')
    care_duration_months = fields.Integer(string='Thời lượng (tháng)')
    care_shift_note = fields.Char(string='Ca làm việc')
    care_income_type = fields.Selection([('salary', 'Lương'), ('allowance', 'Trợ cấp'),
                                         ('negotiable', 'Thỏa thuận'), ('unpaid', 'Không trả')])
    care_income_period = fields.Selection([('month', 'Tháng'), ('hour', 'Giờ'),
                                           ('project', 'Dự án')])
    care_requires_travel = fields.Boolean(string='Cần di chuyển')
    care_requires_license = fields.Boolean(string='Cần giấy phép lái xe')
    care_requires_portfolio = fields.Boolean(string='Cần portfolio')
    care_requires_clinical = fields.Boolean(string='Cần thực hành lâm sàng')
    care_requirement_ids = fields.One2many('care.job.requirement', 'job_id', string='Điều kiện tuyển dụng')
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
    care_currency_id = fields.Many2one('res.currency', default=lambda self: preferred_currency(self.env))
    care_operator_user_ids = fields.Many2many('res.users', relation='hr_job_care_operator_rel')
    care_revision = fields.Integer(default=1, required=True, readonly=True)
    care_matching_enabled = fields.Boolean(default=True)
    care_revision_ids = fields.One2many('care.job.revision', 'job_id', string='Các phiên bản tin')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            validate_numeric_values(vals, ('care_salary_min', 'care_salary_max', 'care_experience_min'))
        return super().create(vals_list)

    def write(self, vals):
        validate_numeric_values(vals, ('care_salary_min', 'care_salary_max', 'care_experience_min'))
        return super().write(vals)

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

    def _care_sync_requirement_skills(self):
        skill_model = self.env['hr.skill'].sudo()
        type_model = self.env['hr.skill.type'].sudo()
        for item in self.mapped('care_requirement_ids').filtered(
                lambda row: row.category in ('technical', 'soft', 'tool', 'language') and not row.skill_id):
            skill = skill_model.search([('name', '=ilike', item.name)], limit=1)
            if not skill:
                skill_type = type_model.search([('name', '=', 'TA.CARE')], limit=1)
                if not skill_type:
                    skill_type = type_model.create({'name': 'TA.CARE'})
                skill = skill_model.create({'name': item.name, 'skill_type_id': skill_type.id})
            item.sudo().write({'skill_id': skill.id})

    @api.constrains('care_experience_min', 'care_salary_min', 'care_salary_max', 'tacare_start',
                   'tacare_deadline', 'care_days_per_week', 'care_duration_months')
    def _check_care_requirements(self):
        for job in self:
            if any(not math.isfinite(value) or value < 0 for value in
                   (job.care_experience_min, job.care_salary_min, job.care_salary_max)):
                raise ValidationError('Kinh nghiệm và thù lao không được âm.')
            if job.care_salary_max and job.care_salary_min > job.care_salary_max:
                raise ValidationError('Mức thù lao cao nhất phải từ mức thấp nhất trở lên.')
            if job.care_days_per_week < 0 or job.care_days_per_week > 7 or job.care_duration_months < 0:
                raise ValidationError('Số ngày mỗi tuần phải từ 0 đến 7 và thời lượng không được âm.')

    def _care_publish_errors(self):
        self.ensure_one()
        missing = []
        for field, label in [('name', 'Tiêu đề'), ('care_position', 'Vị trí'),
                             ('tacare_type', 'Loại cơ hội'), ('tacare_mode', 'Hình thức làm việc'),
                             ('tacare_description_text', 'Mô tả'), ('tacare_deadline', 'Hạn nhận')]:
            if not self[field]:
                missing.append(label)
        if not self.care_sector_id and not self.tacare_sector:
            missing.append('Ngành nghề')
        if self.tacare_mode != 'remote' and not self.tacare_location:
            missing.append('Địa điểm')
        if self.care_position_id:
            if not self.care_candidate_requirements:
                missing.append('Yêu cầu ứng viên')
            if not self.care_work_fraction:
                missing.append('Thời lượng làm việc')
            if self.tacare_mode != 'remote' and not self.care_region_id:
                missing.append('Tỉnh / thành làm việc')
        if self.tacare_deadline and self.tacare_deadline < fields.Date.today():
            missing.append('Hạn nhận chưa qua')
        return missing

    def _care_income_label(self):
        self.ensure_one()
        if self.care_salary_display == 'negotiable' or not (self.care_salary_min or self.care_salary_max):
            return self.tacare_pay or 'Thỏa thuận'
        amount = lambda value: format(value, ',.0f').replace(',', '.')
        if self.care_salary_min and self.care_salary_max:
            label = amount(self.care_salary_min) + ' – ' + amount(self.care_salary_max)
        elif self.care_salary_min:
            label = 'Từ ' + amount(self.care_salary_min)
        else:
            label = 'Đến ' + amount(self.care_salary_max)
        label += ' ' + (self.care_currency_id.name or '')
        if self.care_income_period:
            label += ' / ' + dict(self._fields['care_income_period'].selection)[self.care_income_period].lower()
        if self.care_salary_tax in ('gross', 'net'):
            label += ' (' + self.care_salary_tax + ')'
        if self.care_salary_basis == 'total':
            label += ' · Tổng thu nhập'
        return label

    @api.constrains('care_position_id', 'care_sector_id')
    def _check_position_sector(self):
        for job in self:
            if job.care_position_id and job.care_position_id.sector_id != job.care_sector_id:
                raise ValidationError('Nhóm nghề phải thuộc lĩnh vực đã chọn.')
