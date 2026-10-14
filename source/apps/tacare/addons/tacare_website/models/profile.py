from odoo import api, fields, models
from odoo.exceptions import ValidationError
from .hr_job import SECTORS, MODES


class TacareProfile(models.Model):
    _name = 'tacare.profile'
    _description = 'TA.CARE Candidate Profile'
    _order = 'name'

    user_id = fields.Many2one('res.users', required=True, ondelete='cascade', index=True)
    company_id = fields.Many2one('res.company', related='user_id.company_id', store=True, index=True)
    partner_id = fields.Many2one('res.partner', related='user_id.partner_id', store=True, index=True)
    profile_type = fields.Selection([('individual', 'Cá nhân'), ('team', 'Nhóm')],
                                    default='individual', required=True)
    operator_user_ids = fields.Many2many('res.users', relation='tacare_profile_operator_rel',
                                          string='Người hỗ trợ hồ sơ')
    education_level_id = fields.Many2one('hr.recruitment.degree')
    name = fields.Char(required=True)
    headline = fields.Char()
    bio = fields.Text()
    education = fields.Char()
    sector = fields.Selection(SECTORS)
    location = fields.Char()
    goal = fields.Text()
    mode = fields.Selection(MODES)
    availability = fields.Char()
    pay = fields.Char()
    visible = fields.Boolean(default=True)
    scope = fields.Selection([('public', 'Công khai'), ('members', 'Thành viên'),
                              ('private', 'Riêng tư')], default='private', required=True)
    visibility = fields.Selection(related='scope', readonly=False, string='Phạm vi xem hồ sơ')
    status = fields.Selection([('active', 'Đang hoạt động'), ('paused', 'Tạm ẩn'),
                               ('archived', 'Lưu trữ')], default='active', required=True)
    version = fields.Integer(default=1, required=True, readonly=True)
    verification_level = fields.Selection([('none', 'Chưa xác minh'), ('basic', 'Cơ bản'),
                                           ('enhanced', 'Nâng cao')], default='none',
                                          groups='base.group_system')
    reputation_score = fields.Float(default=0.0, groups='base.group_system')
    home_lat = fields.Float(groups='base.group_system')
    home_lng = fields.Float(groups='base.group_system')
    service_radius_km = fields.Float()
    share_contact = fields.Boolean(default=False)
    skill_ids = fields.One2many('tacare.profile.skill', 'profile_id')
    evidence_ids = fields.One2many('tacare.profile.evidence', 'profile_id')
    capability_ids = fields.One2many('care.profile.capability', 'profile_id')
    availability_ids = fields.One2many('care.availability', 'profile_id', string='Lịch sẵn sàng chi tiết')
    service_area_ids = fields.One2many('care.service.area', 'profile_id')
    preference_ids = fields.One2many('care.preference', 'profile_id')
    consent_ids = fields.One2many('care.consent', 'profile_id')
    _unique_user = models.Constraint('unique(user_id)', 'Mỗi tài khoản chỉ có một hồ sơ TA.CARE.')

    def write(self, vals):
        tracked = {'name', 'headline', 'bio', 'education', 'education_level_id', 'sector',
                   'location', 'goal', 'mode', 'availability', 'pay', 'visible', 'scope',
                   'status', 'share_contact'}
        if tracked.intersection(vals) and not self.env.context.get('care_skip_version'):
            for profile in self:
                super(TacareProfile, profile).write({**vals, 'version': profile.version + 1})
            return True
        return super().write(vals)


class TacareProfileSkill(models.Model):
    _name = 'tacare.profile.skill'
    _description = 'TA.CARE Profile Skill'

    profile_id = fields.Many2one('tacare.profile', required=True, ondelete='cascade', index=True)
    company_id = fields.Many2one('res.company', related='profile_id.company_id', store=True, index=True)
    name = fields.Char(required=True)
    level = fields.Selection([('learning', 'Mới học'), ('basic', 'Cơ bản'),
                              ('good', 'Khá'), ('advanced', 'Thành thạo')], default='basic')
    use = fields.Char()
    skill_id = fields.Many2one('hr.skill', index=True, ondelete='restrict')
    skill_level_id = fields.Many2one('hr.skill.level', ondelete='restrict')
    years_experience = fields.Float(default=0)
    verified = fields.Boolean(default=False, groups='base.group_system')
    verified_on = fields.Datetime(groups='base.group_system')
    _unique_profile_skill = models.Constraint('unique(profile_id, name)', 'Kỹ năng đã có trong hồ sơ.')

    @api.constrains('skill_id', 'skill_level_id', 'years_experience')
    def _check_skill(self):
        for item in self:
            if item.years_experience < 0:
                raise ValidationError('Số năm kinh nghiệm không được âm.')
            if item.skill_id and item.skill_level_id and item.skill_id.skill_type_id != item.skill_level_id.skill_type_id:
                raise ValidationError('Cấp độ phải thuộc cùng nhóm với kỹ năng.')

    def _bump_profile(self):
        for profile in self.mapped('profile_id'):
            profile.with_context(care_skip_version=True).write({'version': profile.version + 1})

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._bump_profile()
        return records

    def write(self, vals):
        result = super().write(vals)
        if {'name', 'level', 'use', 'skill_id', 'skill_level_id', 'years_experience'} & vals.keys():
            self._bump_profile()
        return result

    def unlink(self):
        profiles = self.mapped('profile_id')
        result = super().unlink()
        for profile in profiles.exists():
            profile.with_context(care_skip_version=True).write({'version': profile.version + 1})
        return result


class TacareProfileEvidence(models.Model):
    _name = 'tacare.profile.evidence'
    _description = 'TA.CARE Profile Evidence'

    profile_id = fields.Many2one('tacare.profile', required=True, ondelete='cascade', index=True)
    company_id = fields.Many2one('res.company', related='profile_id.company_id', store=True, index=True)
    category_id = fields.Many2one('care.capability.category', ondelete='restrict')
    profile_skill_id = fields.Many2one('tacare.profile.skill', ondelete='set null')
    title = fields.Char(required=True)
    role = fields.Char(required=True)
    description = fields.Text()
    result = fields.Char()
    url = fields.Char()
    status = fields.Selection([('unverified', 'Chưa xác minh'),
                               ('pending', 'Chờ xác minh'),
                               ('verified', 'Đã xác minh'),
                               ('declined', 'Từ chối')], default='unverified', required=True)
    evidence_type = fields.Selection([('project', 'Dự án'), ('work', 'Kinh nghiệm'),
                                      ('certificate', 'Chứng chỉ'), ('other', 'Khác')],
                                     default='project', required=True)
    issued_by_partner_id = fields.Many2one('res.partner', ondelete='set null')
    issued_at = fields.Date()
    verification_state = fields.Selection(related='status', string='Trạng thái xác minh minh chứng')
    assigned_verifier_id = fields.Many2one('res.users', groups='base.group_system')
    verified_by = fields.Many2one('res.users', groups='base.group_system')
    verified_at = fields.Datetime(groups='base.group_system')
    verification_note = fields.Text(groups='base.group_system')
    visibility = fields.Selection([('private', 'Riêng tư'), ('members', 'Thành viên'),
                                   ('public', 'Công khai')], default='private', required=True)
    score = fields.Float(groups='base.group_system')
    supersedes_id = fields.Many2one('tacare.profile.evidence', ondelete='restrict')
    document_ids = fields.One2many('care.document', 'evidence_id')

    @api.constrains('profile_skill_id', 'supersedes_id', 'verified_by', 'status')
    def _check_evidence(self):
        for item in self:
            if item.profile_skill_id and item.profile_skill_id.profile_id != item.profile_id:
                raise ValidationError('Kỹ năng liên kết phải thuộc cùng hồ sơ.')
            if item.supersedes_id and item.supersedes_id.profile_id != item.profile_id:
                raise ValidationError('Minh chứng thay thế phải thuộc cùng hồ sơ.')
            if item.status == 'verified' and not item.verified_by:
                raise ValidationError('Minh chứng xác minh phải có người xác minh.')

    def _bump_profile(self):
        for profile in self.mapped('profile_id'):
            profile.with_context(care_skip_version=True).write({'version': profile.version + 1})

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._bump_profile()
        return records

    def write(self, vals):
        result = super().write(vals)
        if {'title', 'role', 'description', 'result', 'url', 'visibility', 'status'} & vals.keys():
            self._bump_profile()
        return result

    def unlink(self):
        profiles = self.mapped('profile_id')
        result = super().unlink()
        for profile in profiles.exists():
            profile.with_context(care_skip_version=True).write({'version': profile.version + 1})
        return result
