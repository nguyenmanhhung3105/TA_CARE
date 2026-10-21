"""Purpose-specific recruitment detail on the existing profile and owner-scoped rows."""
import math
from urllib.parse import urlsplit
from odoo import api, fields, models
from odoo.exceptions import ValidationError
from .hr_job import validate_numeric_values

CAREER_LEVELS = [('intern', 'Thực tập / đang học'), ('junior', 'Mới bắt đầu'),
                 ('middle', 'Có kinh nghiệm'), ('senior', 'Chuyên môn sâu')]
RELOCATION = [('yes', 'Có thể chuyển nơi ở'), ('discuss', 'Cần trao đổi'), ('no', 'Không chuyển nơi ở')]


class RecruitmentProfile(models.Model):
    _inherit = 'tacare.profile'

    career_level = fields.Selection(CAREER_LEVELS, string='Cấp độ mong muốn')
    salary_max = fields.Monetary(currency_field='salary_currency_id', string='Thu nhập mong muốn đến mức')
    salary_negotiable = fields.Boolean(default=True, string='Có thể thương lượng thu nhập')
    relocation = fields.Selection(RELOCATION, string='Khả năng chuyển nơi ở')
    portfolio_url = fields.Char(size=1000, string='Portfolio / trang nghề nghiệp')
    preferred_conditions = fields.Text(string='Điều kiện làm việc mong muốn')
    experience_ids = fields.One2many('tacare.profile.experience', 'profile_id', string='Quá trình làm việc')
    education_ids = fields.One2many('tacare.profile.education', 'profile_id', string='Quá trình học tập')

    @api.constrains('salary_min', 'salary_max', 'portfolio_url')
    def _check_recruitment_details(self):
        for profile in self:
            if not math.isfinite(profile.salary_max) or profile.salary_max < 0 or profile.salary_max and profile.salary_max < profile.salary_min:
                raise ValidationError('Mức lương cao nhất phải là số hữu hạn, không nhỏ hơn mức thấp nhất.')
            if profile.portfolio_url:
                try:
                    url = urlsplit(profile.portfolio_url)
                except ValueError:
                    raise ValidationError('Liên kết nghề nghiệp không hợp lệ.')
                if any(ord(c) < 32 for c in profile.portfolio_url) or url.scheme != 'https' or not url.hostname or url.username or url.password:
                    raise ValidationError('Liên kết nghề nghiệp phải là HTTPS hợp lệ và không chứa thông tin đăng nhập.')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            validate_numeric_values(vals, ('salary_max',))
        return super().create(vals_list)

    def write(self, vals):
        validate_numeric_values(vals, ('salary_max',))
        # The original profile version logic still handles existing fields.
        extra = {'career_level', 'salary_max', 'salary_negotiable', 'relocation', 'portfolio_url', 'preferred_conditions'}
        if extra.intersection(vals) and not self.env.context.get('care_skip_version'):
            for profile in self:
                super(RecruitmentProfile, profile.with_context(care_skip_version=True)).write({**vals, 'version': profile.version + 1})
            return True
        return super().write(vals)

    def _recruitment_gaps(self):
        self.ensure_one()
        checks = [('Giới thiệu và thế mạnh', bool(self.headline and self.bio)),
            ('Vị trí và lĩnh vực mong muốn', bool(self.desired_position_id and self.sector)),
            ('Kinh nghiệm hoặc dự án thực hành', bool(self.experience_ids or self.work_history or self.evidence_ids)),
            ('Quá trình học tập', bool(self.education_ids or self.education_details)),
            ('Kỹ năng và cách đã sử dụng', bool(self.skill_ids)),
            ('Khu vực và hình thức làm việc', bool(self.mode and (self.mode == 'remote' or self.region_id)))]
        return [label for label, present in checks if not present]


class ProfileTimeline(models.AbstractModel):
    _name = 'tacare.profile.timeline.mixin'
    _description = 'Owner-scoped profile timeline dates and revision'

    profile_id = fields.Many2one('tacare.profile', required=True, ondelete='cascade', index=True)
    company_id = fields.Many2one('res.company', related='profile_id.company_id', store=True, index=True)
    start_date = fields.Date()
    end_date = fields.Date()
    is_current = fields.Boolean(default=False)
    sequence = fields.Integer(default=10)

    @api.constrains('start_date', 'end_date', 'is_current')
    def _check_timeline(self):
        for row in self:
            if row.start_date and row.end_date and row.end_date < row.start_date:
                raise ValidationError('Thời gian kết thúc không được trước thời gian bắt đầu.')
            if row.is_current and row.end_date:
                raise ValidationError('Mục đang tiếp tục không có tháng kết thúc.')

    def _timeline_label(self):
        self.ensure_one()
        start = self.start_date.strftime('%m/%Y') if self.start_date else 'Chưa khai thời gian bắt đầu'
        end = 'Hiện tại' if self.is_current else self.end_date.strftime('%m/%Y') if self.end_date else 'Chưa khai thời gian kết thúc'
        return '%s · %s' % (start, end)

    def _bump_profile(self):
        for profile in self.mapped('profile_id'):
            profile.with_context(care_skip_version=True).write({'version': profile.version + 1})

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._bump_profile()
        return records

    def write(self, vals):
        if 'profile_id' in vals and any(r.profile_id.id != vals['profile_id'] for r in self):
            raise ValidationError('Không chuyển mục kinh nghiệm hoặc học vấn sang hồ sơ khác.')
        result = super().write(vals)
        self._bump_profile()
        return result

    def unlink(self):
        profiles = self.mapped('profile_id')
        result = super().unlink()
        for profile in profiles.exists():
            profile.with_context(care_skip_version=True).write({'version': profile.version + 1})
        return result


class ProfileExperience(models.Model):
    _name = 'tacare.profile.experience'
    _inherit = 'tacare.profile.timeline.mixin'
    _description = 'Recruitment profile work experience'
    _order = 'sequence, start_date desc, id desc'

    organization = fields.Char(size=180, required=True)
    position = fields.Char(size=180, required=True)
    employment_type = fields.Selection([('employment', 'Nhân viên'), ('internship', 'Thực tập'),
        ('freelance', 'Cộng tác / tự do'), ('project', 'Dự án / tình nguyện')])
    location = fields.Char(size=250)
    responsibilities = fields.Text()
    achievements = fields.Text()
    tools = fields.Char(size=500)


class ProfileEducation(models.Model):
    _name = 'tacare.profile.education'
    _inherit = 'tacare.profile.timeline.mixin'
    _description = 'Recruitment profile education'
    _order = 'sequence, start_date desc, id desc'

    school = fields.Char(size=180, required=True)
    qualification_id = fields.Many2one('hr.recruitment.degree', ondelete='restrict')
    major = fields.Char(size=180)
    description = fields.Text()
