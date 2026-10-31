"""Server-side browser session groups and short-lived, browser-bound handoffs."""
import hashlib
import secrets
from datetime import timedelta
from hmac import compare_digest

from odoo import api, fields, models
from odoo.http import get_session_max_inactivity


FAMILY_KEY = 'tacare_sso_family'
PENDING_KEY = 'tacare_sso_pending'
FRESH_KEY = 'tacare_sso_fresh_login'
SYNC_KEY = 'tacare_sso_flow'


def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


def user_role(user):
    return 'admin' if user.has_group('base.group_system') else user.sudo().tacare_account_role


class CareAuthSession(models.Model):
    _name = 'care.auth.session'
    _description = 'TA.CARE browser session group'

    user_id = fields.Many2one('res.users', required=True, ondelete='cascade', index=True)
    role = fields.Selection([('admin', 'Quản trị'), ('business', 'Doanh nghiệp'),
                             ('candidate', 'Cá nhân')], required=True)
    nonce = fields.Char(required=True, copy=False)
    credential_stamp = fields.Char(required=True, copy=False)
    expires_at = fields.Datetime(required=True, index=True)
    revoked_at = fields.Datetime(index=True, copy=False)

    @api.model
    def _start_for(self, user):
        nonce = secrets.token_hex(32)
        return self.sudo().create({
            'user_id': user.id, 'role': user_role(user), 'nonce': nonce,
            'credential_stamp': user.sudo()._compute_session_token(nonce),
            'expires_at': fields.Datetime.now() + timedelta(seconds=get_session_max_inactivity(self.env)),
        })

    def _valid_for(self, uid):
        self.ensure_one()
        user = self.user_id.sudo()
        return bool(user.id == uid and user.active and not self.revoked_at and
                    self.expires_at > fields.Datetime.now() and self.role == user_role(user) and
                    compare_digest(self.credential_stamp, user._compute_session_token(self.nonce) or ''))

    def _revoke(self):
        self.filtered(lambda f: not f.revoked_at).sudo().write({'revoked_at': fields.Datetime.now()})

    @api.autovacuum
    def _gc_auth_sessions(self):
        self.sudo().search([('expires_at', '<', fields.Datetime.now() - timedelta(days=7))]).unlink()


class CareAuthHandoff(models.TransientModel):
    _name = 'care.auth.handoff'
    _description = 'TA.CARE one-time browser-bound login handoff'
    _transient_max_hours = 0.25

    handle_hash = fields.Char(required=True, index=True, copy=False)
    family_id = fields.Many2one('care.auth.session', required=True, ondelete='cascade')
    source_origin = fields.Char(required=True)
    targets = fields.Json(required=True)
    network = fields.Selection([('local', 'Local'), ('production', 'Production'),
                               ('uat', 'UAT')], required=True)
    return_path = fields.Char(required=True, default='/')
    phase = fields.Selection([('prepare', 'Chuẩn bị'), ('authorize', 'Xác nhận nguồn'),
                              ('finish', 'Hoàn tất'), ('done', 'Đã dùng')], required=True, default='prepare')
    state_hash = fields.Char(copy=False)
    expires_at = fields.Datetime(required=True)

    _handle_unique = models.Constraint('UNIQUE(handle_hash)', 'Handoff đã tồn tại.')
