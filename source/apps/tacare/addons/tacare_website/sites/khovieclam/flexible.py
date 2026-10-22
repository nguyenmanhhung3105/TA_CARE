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


from ...controllers.flexible_work import TacareFlexible

class KhoFlexible(TacareFlexible):
    @http.route()
    def jobs(self, **kw):
        domain = self._job_domain()
        kind = 'flexible'
        if kw.get('kind') == 'recruitment':
            raise NotFound()
        if kind in ('recruitment', 'flexible'):
            domain.append(('care_opportunity_kind', '=', kind))
        jobs = request.env['hr.job'].sudo().search(domain, order='create_date desc, id desc')
        query = (kw.get('q') or '').strip().casefold()
        if query:
            jobs = jobs.filtered(lambda j: query in ' '.join(filter(None, [
                j.name, j.tacare_location, j.flex_location, j.tacare_required_skills,
                ', '.join(j.flex_skill_ids.mapped('name'))])).casefold())
        if kind == 'flexible':
            for param, attr in [('category', 'flex_category_id'), ('region', 'flex_region_id')]:
                if kw.get(param):
                    if not kw[param].isdigit():
                        raise BadRequest('Bộ lọc không hợp lệ.')
                    jobs = jobs.filtered(lambda j: j[attr].id == int(kw[param]))
            for param, attr in [('mode', 'flex_mode'), ('unit', 'flex_pay_unit'), ('schedule', 'flex_schedule')]:
                if kw.get(param):
                    jobs = jobs.filtered(lambda j: j[attr] == kw[param])
        elif kind == 'recruitment':
            if kw.get('sector'):
                jobs = jobs.filtered(lambda j: j.care_sector_id.code == kw['sector'] or j.tacare_sector == kw['sector'])
            if kw.get('type'):
                jobs = jobs.filtered(lambda j: j.tacare_type == kw['type'])
            if kw.get('mode'):
                jobs = jobs.filtered(lambda j: j.tacare_mode == kw['mode'])
        return self._render('work_jobs', site='khovieclam', jobs=jobs, query=kw,
                            kind=kind, mine=False)

    @http.route()
    def job_detail(self, job_id, **kw):
        job = request.env['hr.job'].sudo().search(self._job_domain() + [('id', '=', job_id)], limit=1)
        if not job:
            raise NotFound()
        if job.care_opportunity_kind != 'flexible':
            return super().job_detail(job_id, **kw)
        return self._render('work_detail', site='khovieclam', record=job, is_service=False,
                            owner=self._role() == 'admin' or job.tacare_owner_user_id == self._user())

    @http.route('/kvl/flexible/mine', auth='user', website=True)
    def flexible_mine(self, **kw):
        self._flex_user()
        company_ids = self._user().company_ids.ids if self._role() == 'admin' else [request.env.company.id]
        domain = [('care_opportunity_kind', '=', 'flexible'), ('company_id', 'in', company_ids)]
        if self._role() != 'admin':
            domain.append(('tacare_owner_user_id', '=', self._user().id))
        jobs = request.env['hr.job'].sudo().search(domain, order='create_date desc, id desc')
        return self._render('work_jobs', site='khovieclam', jobs=jobs, query={}, kind='flexible', mine=True)

    @http.route('/kvl/flexible/<int:record_id>', auth='user', website=True)
    def flexible_preview(self, record_id, **kw):
        item = self._flex_own('hr.job', record_id)
        return self._render('work_detail', site='khovieclam', record=item, is_service=False, owner=True)

    @http.route(['/kvl/flexible/new', '/kvl/flexible/<int:record_id>/edit'], auth='user', website=True)
    def flexible_form(self, record_id=None, **kw):
        self._flex_user()
        item = self._flex_own('hr.job', record_id) if record_id else False
        return self._render('work_form', site='khovieclam', record=item, is_service=False,
                            vals=self._work_values(item), error=False)

    @http.route()
    def manage_jobs(self, **kw):
        self._flex_user()
        return request.redirect('/kvl/flexible/mine')
