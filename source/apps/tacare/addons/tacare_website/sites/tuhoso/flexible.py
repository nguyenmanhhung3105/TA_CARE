"""Owner-scoped demo workflows for flexible work, using the existing Odoo records."""
import base64
from io import BytesIO

from PIL import Image, ImageOps, UnidentifiedImageError
from werkzeug.exceptions import BadRequest, Forbidden, NotFound
from odoo import fields, http
from odoo.exceptions import ValidationError
from odoo.http import request

from ...controllers.live import TacareLive
from ...models.flexible_work import WORK_MODES, SCHEDULES, PAY_UNITS, PAY_BASES, WEEKDAYS, TOOLS


from ..khovieclam.flexible import KhoFlexible

class ProfileFlexible(KhoFlexible):
    @http.route('/tuhoso/profiles', auth='user', website=True)
    def profile_library(self, **kw):
        self._flex_user()
        kind = kw.get('kind', 'recruitment')
        if kind not in ('recruitment', 'flexible'):
            raise BadRequest('Loại hồ sơ không hợp lệ.')
        domain = [('company_id', 'in', self._user().company_ids.ids)]
        if self._role() != 'admin':
            domain.append(('user_id', '=', self._user().id))
        profiles = request.env['tacare.profile'].sudo().search(domain)
        services = request.env['care.profile.capability'].sudo().search([('profile_id', 'in', profiles.ids)])
        if kind == 'recruitment':
            profiles = profiles.filtered('care_recruitment_enabled')
            if kw.get('q'):
                q = kw['q'].casefold()
                profiles = profiles.filtered(lambda p: q in ((p.name or '') + ' ' + (p.headline or '')).casefold())
            if kw.get('sector'):
                profiles = profiles.filtered(lambda p: p.sector == kw['sector'])
        else:
            if kw.get('q'):
                q = kw['q'].casefold()
                services = services.filtered(lambda s: q in ((s.title or '') + ' ' + s.profile_id.name).casefold())
            for param, attr in [('category', 'category_id'), ('region', 'flex_region_id')]:
                if kw.get(param):
                    if not kw[param].isdigit():
                        raise BadRequest('Bộ lọc không hợp lệ.')
                    services = services.filtered(lambda s: s[attr].id == int(kw[param]))
            for param, attr in [('mode', 'flex_mode'), ('unit', 'flex_pay_unit'), ('state', 'flex_state')]:
                if kw.get(param):
                    services = services.filtered(lambda s: s[attr] == kw[param])
        return self._render('work_profiles', site='tuhoso', kind=kind, profiles=profiles,
                            services=services, query=kw)

    @http.route(auth='user')
    def profile_public(self, profile_id, **kw):
        # Tủ Hồ Sơ is now a personal workspace. Recruitment candidate access remains
        # on the separately authorized Kho routes, never this URL.
        self._flex_user()
        domain = [('id', '=', profile_id), ('company_id', 'in', self._user().company_ids.ids)]
        if self._role() != 'admin':
            domain.append(('user_id', '=', self._user().id))
        profile = request.env['tacare.profile'].sudo().search(domain, limit=1)
        if not profile:
            raise NotFound()
        return self._render('live_profile', site='tuhoso', profile=profile, edit=False,
                            evidence_items=profile.evidence_ids, skill_items=profile.skill_ids)

    @http.route('/tuhoso/work/<int:record_id>', auth='user', website=True)
    def service_detail(self, record_id, **kw):
        item = self._flex_own('care.profile.capability', record_id)
        return self._render('work_detail', site='tuhoso', record=item, is_service=True, owner=True)

    @http.route(['/tuhoso/work/new', '/tuhoso/work/<int:record_id>/edit'], auth='user', website=True)
    def service_form(self, record_id=None, **kw):
        self._flex_user()
        item = self._flex_own('care.profile.capability', record_id) if record_id else False
        return self._render('work_form', site='tuhoso', record=item, is_service=True,
                            vals=self._work_values(item), error=False)
