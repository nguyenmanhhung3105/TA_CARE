from urllib.parse import urlsplit
from odoo import api, fields, models, _, Command
from odoo.exceptions import AccessDenied, AccessError
from odoo.http import request

ROLE_HOSTS = {
    'business': {'khovieclam.vn', 'www.khovieclam.vn', 'tacare.vn', 'www.tacare.vn',
                 'khovieclam.localhost', 'tacare.localhost'},
    'candidate': {'tuhoso.com', 'www.tuhoso.com', 'tacare.vn', 'www.tacare.vn',
                  'tuhoso.localhost', 'tacare.localhost'},
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

    def _tacare_sync_role_groups(self):
        business = self.env.ref('tacare_account_access.group_tacare_business', raise_if_not_found=False)
        candidate = self.env.ref('tacare_account_access.group_tacare_candidate', raise_if_not_found=False)
        if not business or not candidate:
            return
        for user in self.sudo():
            desired = {'business': business, 'candidate': candidate}.get(user.tacare_account_role)
            commands = [Command.unlink(group.id) for group in (business | candidate) if group in user.group_ids]
            if desired:
                internal = self.env.ref('base.group_user')
                if internal in user.group_ids:
                    commands.append(Command.unlink(internal.id))
                commands.append(Command.link(desired.id))
            if commands:
                user.with_context(tacare_sync_role=True).write({'group_ids': commands})

    @api.model_create_multi
    def create(self, vals_list):
        if any('tacare_account_role' in vals and vals['tacare_account_role'] != 'pending' for vals in vals_list):
            if not self.env.user.has_group('base.group_system') and not self.env.su:
                raise AccessError('Chỉ quản trị được cấp vai trò TA.CARE.')
        users = super().create(vals_list)
        users._tacare_sync_role_groups()
        return users

    def write(self, vals):
        if 'tacare_account_role' in vals and not self.env.context.get('tacare_sync_role'):
            if not self.env.user.has_group('base.group_system') and not self.env.su:
                raise AccessError('Chỉ quản trị được cấp vai trò TA.CARE.')
        result = super().write(vals)
        if 'tacare_account_role' in vals and not self.env.context.get('tacare_sync_role'):
            self._tacare_sync_role_groups()
        return result

    @api.depends('tacare_account_role', 'group_ids')
    def _compute_tacare_websites(self):
        websites = self.env['website'].sudo().search([])
        for user in self:
            if user.has_group('base.group_system'):
                user.tacare_allowed_website_ids = websites
            else:
                hosts = ROLE_HOSTS.get(user.tacare_account_role, set())
                user.tacare_allowed_website_ids = websites.filtered(
                    lambda w: hostname(w.domain) in hosts)

    def _tacare_can_access_host(self, host):
        self.ensure_one()
        user = self.sudo()
        # Only system administrators can use all three product websites.
        if user.has_group('base.group_system') or user._is_public():
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
                    'Liên hệ quản trị để kiểm tra vai trò và website được cấp.'))
        return auth_info
