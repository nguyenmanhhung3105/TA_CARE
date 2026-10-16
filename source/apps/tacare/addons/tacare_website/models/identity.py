"""Organization membership and non-invasive extensions of Odoo identity records."""
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ResCompany(models.Model):
    _inherit = 'res.company'

    care_unit_kind = fields.Selection([
        ('operator', 'Đơn vị vận hành'),
        ('other', 'Khác'),
    ], default='operator')


class ResPartner(models.Model):
    _inherit = 'res.partner'

    care_employer_state = fields.Selection([
        ('unreviewed', 'Chưa duyệt'),
        ('active', 'Đã duyệt'),
        ('suspended', 'Tạm ngừng'),
    ], default='unreviewed')
    care_company_intro = fields.Html(sanitize=True)
    care_business_sector_ids = fields.Many2many('care.job.sector', string='Lĩnh vực hoạt động')
    care_market_scope = fields.Char(string='Thị trường / phạm vi hoạt động')


class Website(models.Model):
    _inherit = 'website'

    care_site_kind = fields.Selection([
        ('khovieclam', 'Kho Việc Làm'),
        ('tuhoso', 'Tủ Hồ Sơ'),
        ('tacare', 'TA.CARE'),
    ])


class ResUsers(models.Model):
    _inherit = 'res.users'

    care_org_member_ids = fields.One2many('care.org.member', 'user_id')
    care_organization_ids = fields.Many2many(
        'res.partner', compute='_compute_care_organization_ids', compute_sudo=True,
        string='Tổ chức đang quản lý',
    )

    @api.depends('care_org_member_ids.state', 'care_org_member_ids.organization_id', 'tacare_account_role')
    def _compute_care_organization_ids(self):
        for user in self:
            active = user.care_org_member_ids.filtered(lambda member: member.state == 'active')
            organizations = active.mapped('organization_id')
            # Existing business accounts predate the membership table. The
            # commercial partner is their pre-existing organization boundary.
            if not user.care_org_member_ids and user.tacare_account_role == 'business':
                organizations = user.partner_id.commercial_partner_id
            user.care_organization_ids = organizations


class CareOrgMember(models.Model):
    _name = 'care.org.member'
    _description = 'TA.CARE Organization Membership'
    _order = 'organization_id, user_id'

    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company, index=True)
    organization_id = fields.Many2one('res.partner', required=True, index=True, ondelete='restrict')
    user_id = fields.Many2one('res.users', required=True, index=True, ondelete='cascade')
    role = fields.Selection([('owner', 'Chủ tổ chức'), ('recruiter', 'Người tuyển dụng'),
                             ('viewer', 'Người xem')], required=True, default='recruiter')
    state = fields.Selection([('invited', 'Đã mời'), ('active', 'Đang hoạt động'),
                              ('suspended', 'Tạm ngừng')], required=True, default='invited')
    can_manage_jobs = fields.Boolean(string='Quản lý tin tuyển dụng')
    can_handle_candidates = fields.Boolean(string='Xử lý ứng viên')

    _unique_member = models.Constraint(
        'unique(company_id, organization_id, user_id)',
        'Một tài khoản chỉ có một membership trong mỗi tổ chức và đơn vị vận hành.',
    )

    @api.constrains('organization_id', 'user_id')
    def _check_member(self):
        for member in self:
            if not member.organization_id.is_company:
                raise ValidationError('Tổ chức phải là liên hệ doanh nghiệp (is_company).')
            if member.user_id._is_public():
                raise ValidationError('Tài khoản công khai không được là thành viên tổ chức.')
