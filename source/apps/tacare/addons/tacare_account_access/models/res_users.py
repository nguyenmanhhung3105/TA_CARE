from urllib.parse import urlsplit
from odoo import api, fields, models, _
from odoo.exceptions import AccessDenied
from odoo.http import request

ROLE_HOSTS = {
    'business': {'khovieclam.vn', 'tacare.vn'},
    'candidate': {'tuhoso.com', 'tacare.vn'},
    'pending': set(),
}


def hostname(value):
    value = (value or '').strip()
    if not value:
        return ''
    return (urlsplit(value if '://' in value else '//' + value).hostname or '').lower().rstrip('.')


class ResUsers(models.Model):
    _inherit = 'res.users'

    tacare_account_role = fields.Selection(
        [('pending', 'Chưa cấp vai trò'),
         ('business', 'Doanh nghiệp'),
         ('candidate', 'Sinh viên / Ứng viên')],
        default='pending', required=True, copy=False,
        string='Vai trò TA.CARE', groups='base.group_system',
    )
    tacare_allowed_website_ids = fields.Many2many(
        'website', compute='_compute_tacare_websites', compute_sudo=True,
        string='Website được phép', groups='base.group_system',
    )

    @api.depends('tacare_account_role')
    def _compute_tacare_websites(self):
        websites = self.env['website'].sudo().search([])
        for user in self:
            if user._is_internal():
                user.tacare_allowed_website_ids = websites
            else:
                hosts = ROLE_HOSTS.get(user.tacare_account_role, set())
                user.tacare_allowed_website_ids = websites.filtered(
                    lambda w: hostname(w.domain) in hosts)

    def _tacare_can_access_host(self, host):
        self.ensure_one()
        user = self.sudo()
        # Existing internal administrators/operators remain governed by Odoo ACLs.
        if user._is_internal() or user._is_public():
            return True
        host = hostname(host)
        if host not in ROLE_HOSTS.get(user.tacare_account_role, set()):
            return False
        # Never accept Odoo's fallback website for an unmatched host.
        websites = self.env['website'].sudo().search([])
        return any(hostname(w.domain) == host for w in websites)

    def _check_credentials(self, credential, env):
        auth_info = super()._check_credentials(credential, env)
        if request:
            host = request.httprequest.host
            if not self._tacare_can_access_host(host):
                raise AccessDenied(_(
                    'Tài khoản chưa được cấp quyền đăng nhập website này. '
                    'Doanh nghiệp dùng KhoViecLam hoặc TA.CARE; '
                    'ứng viên dùng TuHoSo hoặc TA.CARE.'))
        return auth_info
