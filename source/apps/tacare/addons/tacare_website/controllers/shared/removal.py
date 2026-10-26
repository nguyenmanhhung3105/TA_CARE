"""Scoped admin confirmation and POST handling, used by each product route."""
from odoo import http
from odoo.http import request
from odoo.exceptions import AccessError, ValidationError
from werkzeug.exceptions import BadRequest, Forbidden, NotFound
from ...models.operations.admin_removal import KINDS, check_admin, plan_removal, remove_record


class AdminRemovalControllers(http.Controller):
    def _admin_removal(self, kind, record_id):
        try:
            check_admin(self._user())
        except AccessError as exc:
            raise Forbidden(str(exc))
        domain = [('id', '=', record_id), ('company_id', 'in', self._user().company_ids.ids)]
        if kind == 'profile':
            domain.append(('status', '!=', 'archived'))
        record = request.env[KINDS[kind][0]].sudo().search(domain, limit=1)
        if not record:
            raise NotFound()
        site = 'khovieclam' if kind == 'job' else 'tuhoso'
        cancel = ('/kvl/flexible/%s' if record.care_opportunity_kind == 'flexible' else '/kvl/job/%s/preview') % record.id if kind == 'job' else ('/tuhoso/profile/%s' if kind == 'profile' else '/tuhoso/work/%s') % record.id
        if request.httprequest.method == 'POST':
            if set(request.httprequest.form) - {'csrf_token', 'confirm'} or request.httprequest.form.get('confirm') != 'delete':
                raise BadRequest('Đánh dấu xác nhận trước khi xóa bản ghi.')
            try:
                with request.env.cr.savepoint():
                    outcome = remove_record(record, self._user())
            except (ValidationError, AccessError) as exc:
                return self._render('admin_removal', site=site, plan=plan_removal(record, self._user()),
                    cancel_url=cancel, error=str(exc))
            target = '/kvl/flexible/mine' if kind == 'job' and '/flexible/' in cancel else KINDS[kind][2]
            return request.redirect(target + ('&' if '?' in target else '?') + 'notice=' + outcome)
        return self._render('admin_removal', site=site, plan=plan_removal(record, self._user()), cancel_url=cancel, error=False)
