from werkzeug.exceptions import Forbidden
from odoo import models
from odoo.http import request


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    @classmethod
    def _pre_dispatch(cls, rule, arguments):
        # Check before route handlers, including auth=none and JSON-RPC routes.
        uid = request.session.uid or request.session.get('pre_uid')
        if uid and request.httprequest.path.rstrip('/') != '/web/session/logout':
            user = request.env['res.users'].sudo().browse(uid).exists()
            if user and not user._tacare_can_access_host(request.httprequest.host):
                raise Forbidden(
                    'Tài khoản không được phép sử dụng website này. '
                    'Vui lòng đăng xuất và mở website đúng với vai trò của bạn.')
        return super()._pre_dispatch(rule, arguments)
