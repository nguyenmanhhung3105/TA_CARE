"""First-party redirects work across .vn/.com without third-party cookies.

No password, native session ID or bearer credential crosses a URL. Each handoff
requires an HttpOnly target session nonce AND the authenticated source browser.
"""
import re
import secrets
from datetime import timedelta
from hmac import compare_digest
from urllib.parse import urlencode, urlsplit

from werkzeug.exceptions import BadRequest, Forbidden
from odoo import fields, http
from odoo.http import request
from odoo.addons.web.controllers.session import Session

from ..models.auth_session import FAMILY_KEY, PENDING_KEY, FRESH_KEY, SYNC_KEY, digest, user_role
from ..models.res_users import hostname


ORIGINS = {
    'local': {'khovieclam': 'http://khovieclam.localhost:8069',
              'tuhoso': 'http://tuhoso.localhost:8069', 'tacare': 'http://tacare.localhost:8069'},
    'production': {'khovieclam': 'https://khovieclam.vn',
                   'tuhoso': 'https://tuhoso.com', 'tacare': 'https://tacare.vn'},
}


def origin_info():
    host = hostname(request.httprequest.host)
    for network, sites in ORIGINS.items():
        for site, origin in sites.items():
            known_host = urlsplit(origin).hostname
            if host == known_host:
                return network, site, origin
            if network == 'production' and host == 'www.' + known_host:
                return network, site, 'https://' + host
    return None


def return_path(value):
    if not isinstance(value, str) or '\\' in value or any(ord(c) < 32 for c in value):
        return '/'
    try:
        parsed = urlsplit(value)
    except ValueError:
        return '/'
    if parsed.scheme or parsed.netloc or not value.startswith('/') or value.startswith('//'):
        return '/'
    path = parsed.path
    codes = request.website.language_ids.mapped('url_code')
    first = path.split('/')[1]
    if first in codes:
        path = path[len(first) + 1:] or '/'
    if path != '/' and not path.startswith(('/kvl/', '/tuhoso/', '/tacare/')):
        return '/'
    return value


def protected_response(response):
    response.headers.update({'Cache-Control': 'private, no-store', 'Pragma': 'no-cache',
                             'Referrer-Policy': 'no-referrer', 'X-Frame-Options': 'DENY'})
    return response


class TacareSSO(http.Controller):
    def _redirect(self, origin, endpoint, handle):
        return protected_response(request.redirect(origin + '/care/sso/' + endpoint + '?' +
                                                   urlencode({'flow': handle}), code=303, local=False))

    def _flow(self, handle, phase):
        info = origin_info()
        if not info or not isinstance(handle, str) or not re.fullmatch('[0-9a-f]{64}', handle):
            raise BadRequest('Phiên đồng bộ không hợp lệ.')
        flow = request.env['care.auth.handoff'].sudo().search([('handle_hash', '=', digest(handle))], limit=1)
        if not flow:
            raise BadRequest('Phiên đồng bộ đã hết hạn. Vui lòng đăng nhập lại.')
        # Serialize phase changes so a finish cannot be consumed twice.
        request.env.cr.execute('SELECT id FROM care_auth_handoff WHERE id = %s FOR UPDATE', [flow.id])
        flow.invalidate_recordset()
        if flow.phase != phase or flow.expires_at <= fields.Datetime.now() or \
                info[0] != flow.network or not flow.family_id._valid_for(flow.family_id.user_id.id):
            raise Forbidden('Phiên đồng bộ đã hết hạn hoặc không còn hiệu lực.')
        return flow, info

    @http.route('/care/sso/start', type='http', auth='user', website=True, multilang=False, methods=['GET'], readonly=False)
    def start(self, next='/', **kw):
        info = origin_info()
        user = request.env.user
        if not info or user._is_public() or user_role(user) not in ('admin', 'business', 'candidate') or \
                not user._tacare_can_access_host(request.httprequest.host):
            raise Forbidden('Tài khoản không có quyền đăng nhập hệ thống này.')
        old = request.env['care.auth.session'].sudo().browse(request.session.get(FAMILY_KEY) or []).exists()
        fresh = request.session.pop(FRESH_KEY, False)
        if old and old._valid_for(user.id) and not fresh:
            family = old
        else:
            if old:
                old._revoke()
            family = request.env['care.auth.session']._start_for(user)
            request.session[FAMILY_KEY] = family.id
        network, site, origin = info
        targets = [key for key, value in ORIGINS[network].items() if value != origin]
        handle = secrets.token_hex(32)
        item = request.env['care.auth.handoff'].sudo().create({
            'handle_hash': digest(handle), 'family_id': family.id, 'source_origin': origin,
            'network': network, 'targets': targets, 'return_path': return_path(next),
            'expires_at': fields.Datetime.now() + timedelta(minutes=3),
        })
        request.session[SYNC_KEY] = item.id
        return self._redirect(ORIGINS[network][targets[0]], 'prepare', handle)

    @http.route('/care/sso/prepare', type='http', auth='public', website=True, multilang=False, methods=['GET'], readonly=False)
    def prepare(self, flow=None, **kw):
        item, info = self._flow(flow, 'prepare')
        if not item.targets or info[2] != ORIGINS[item.network][item.targets[0]]:
            raise Forbidden('Website nhận không hợp lệ.')
        state = secrets.token_hex(32)
        request.session[PENDING_KEY] = {'flow': digest(flow), 'state': state}
        item.write({'state_hash': digest(state), 'phase': 'authorize'})
        return self._redirect(item.source_origin, 'authorize', flow)

    @http.route('/care/sso/authorize', type='http', auth='user', website=True, multilang=False, methods=['GET'], readonly=False)
    def authorize(self, flow=None, **kw):
        item, info = self._flow(flow, 'authorize')
        if info[2] != item.source_origin or request.session.uid != item.family_id.user_id.id or \
                request.session.get(FAMILY_KEY) != item.family_id.id:
            raise Forbidden('Phiên đăng nhập nguồn không khớp.')
        item.write({'phase': 'finish'})
        return self._redirect(ORIGINS[item.network][item.targets[0]], 'finish', flow)

    @http.route('/care/sso/finish', type='http', auth='public', website=True, multilang=False, methods=['GET'], readonly=False)
    def finish(self, flow=None, **kw):
        item, info = self._flow(flow, 'finish')
        pending = request.session.get(PENDING_KEY) or {}
        if not item.targets or info[2] != ORIGINS[item.network][item.targets[0]] or \
                pending.get('flow') != digest(flow) or not isinstance(pending.get('state'), str) or \
                not compare_digest(digest(pending['state']), item.state_hash or ''):
            raise Forbidden('Trình duyệt nhận không khớp phiên đồng bộ.')
        family, user = item.family_id, item.family_id.user_id.sudo()
        can_login = user._tacare_can_access_host(request.httprequest.host)
        # Completion is bound to this browser and authorized source. Clear any
        # previous account, including the third site outside the new role's scope.
        same = request.session.uid == user.id and request.session.get(FAMILY_KEY) == family.id
        if not same or not can_login:
            request._tacare_sso_preserve_logout = same
            try:
                request.session.logout(keep_db=True)
            finally:
                request._tacare_sso_preserve_logout = False
        if can_login:
            if not same:
                request.session['pre_login'] = user.login
                request.session['pre_uid'] = user.id
                request.session.finalize(request.env)
            request.session[FAMILY_KEY] = family.id
            request.session[SYNC_KEY] = item.id
            request.update_env(user=user.id, context=request.session.context)
        else:
            request.update_env(user=None, context=request.session.context)
        request.session.pop(PENDING_KEY, None)
        remaining = item.targets[1:]
        item.write({'targets': remaining or item.targets, 'state_hash': False,
                    'phase': 'prepare' if remaining else 'done'})
        if remaining:
            return self._redirect(ORIGINS[item.network][remaining[0]], 'prepare', flow)
        return protected_response(request.redirect(item.source_origin + item.return_path, code=303, local=False))

    @http.route('/care/sso/status', type='http', auth='public', website=True, multilang=False, methods=['GET'], readonly=False)
    def status(self, **kw):
        flow = request.env['care.auth.handoff'].sudo().browse(request.session.get(SYNC_KEY) or []).exists()
        syncing = bool(request.session.get(FRESH_KEY) or flow and flow.phase != 'done' and
                       flow.expires_at > fields.Datetime.now())
        return protected_response(request.make_json_response({'uid': request.session.uid or False, 'syncing': syncing}))


class TacareSessionLogout(Session):
    # Global revocation writes a DB row; native endpoints are otherwise readonly.
    @http.route(readonly=False)
    def logout(self, redirect='/'):
        return super().logout(redirect=return_path(redirect))

    @http.route(readonly=False)
    def destroy(self):
        return super().destroy()
