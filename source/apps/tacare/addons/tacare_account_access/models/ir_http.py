from urllib.parse import urlencode

from werkzeug.exceptions import Forbidden, abort
from odoo import api, models
from odoo.http import request
from .res_users import hostname, ROLE_HOSTS
from .auth_session import FAMILY_KEY, FRESH_KEY


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    @classmethod
    def _authenticate_explicit(cls, auth):
        # The browser only holds Odoo's opaque HttpOnly cookie. Group membership
        # lives in its server-side session and is never accepted from a request.
        uid, family_id = request.session.uid, request.session.get(FAMILY_KEY)
        if family_id and not uid:
            # Native password verification can leave an earlier browser group
            # attached while the replacement account is waiting for MFA.
            previous = request.env['care.auth.session'].sudo().browse(family_id).exists()
            uid = previous.user_id.id if previous else None
        request._tacare_sso_logout_snapshot = (family_id, uid) if family_id and uid else None
        result = super()._authenticate_explicit(auth)
        if request.session.uid and family_id:
            family = request.env['care.auth.session'].sudo().browse(family_id).exists()
            if family and family.user_id.id != request.session.uid:
                # Native authentication has just switched accounts (also MFA).
                family._revoke()
                request.session.pop(FAMILY_KEY, None)
                request._tacare_sso_logout_snapshot = None
            elif not family or not family._valid_for(request.session.uid):
                request.session.logout(keep_db=True)
                request.env = api.Environment(request.env.cr, None, request.session.context)
                return super()._authenticate_explicit(auth)
        return result

    @classmethod
    def _post_logout(cls):
        snapshot = getattr(request, '_tacare_sso_logout_snapshot', None)
        if snapshot and not getattr(request, '_tacare_sso_preserve_logout', False):
            family_id, uid = snapshot
            family = request.env['care.auth.session'].sudo().search([
                ('id', '=', family_id), ('user_id', '=', uid)], limit=1)
            family._revoke()
        return super()._post_logout()

    @classmethod
    def _pre_dispatch(cls, rule, arguments):
        # Product homepages stay public. Every product function is checked on the
        # server, even when its URL is entered manually or under another host.
        path = request.httprequest.path.rstrip('/') or '/'
        host = hostname(request.httprequest.host)
        managed = host in set().union(*ROLE_HOSTS.values())
        uid = request.session.uid or request.session.get('pre_uid')
        user = request.env['res.users'].sudo().browse(uid).exists() if uid else False
        prefix = next((p for p in ('/kvl', '/tuhoso', '/tacare', '/jobs', '/my')
                       if path == p or path.startswith(p + '/')), None)
        if managed or prefix:
            host_allowed = bool(user and user._tacare_can_access_host(host))
            role = ('admin' if user and user.has_group('base.group_system') else
                    user.tacare_account_role if user else 'pending')
            if managed and request.session.uid and host_allowed and role in ('admin', 'business', 'candidate') and \
                    (not request.session.get(FAMILY_KEY) or request.session.get(FRESH_KEY)) and \
                    (path == '/' or prefix) and request.httprequest.method == 'GET' and \
                    rule.endpoint.routing['type'] == 'http':
                # Upgrade existing native logins and complete post-MFA sign-in.
                target = request.httprequest.full_path.rstrip('?')
                abort(request.redirect('/care/sso/start?' + urlencode({'next': target}), code=303))
            route_allowed = not user or ((prefix != '/kvl' or role in ('business', 'admin')) and
                                         (prefix != '/tuhoso' or role in ('candidate', 'admin')))
            # Native authentication, MFA, assets and logout must still work.
            public_plumbing = (path == '/' or path in ('/web/login', '/web/signup', '/web/reset_password',
                                                       '/website/translations') or
                               path.startswith(('/web/assets/', '/web/image/', '/web/content/',
                                                '/web/session/', '/web/login/', '/auth_oauth/',
                                                '/website/translations/', '/care/sso/')))
            blocked = (prefix and (not request.session.uid or not host_allowed or not route_allowed)) or \
                      (user and not host_allowed and not public_plumbing)
            if blocked:
                if request.httprequest.method in ('GET', 'HEAD') and rule.endpoint.routing['type'] == 'http':
                    target = request.httprequest.full_path.rstrip('?') if route_allowed else '/'
                    query = {'login': '1', 'next': target}
                    if user:
                        query['reason'] = 'role'
                    abort(request.redirect('/?' + urlencode(query), code=303))
                raise Forbidden('Đăng nhập tài khoản có quyền sử dụng chức năng trên website này.')
        return super()._pre_dispatch(rule, arguments)
