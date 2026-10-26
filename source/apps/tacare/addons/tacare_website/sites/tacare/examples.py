"""Fictional UI scenarios; no personal data, consent or connection is fabricated."""
from odoo import http
from odoo.http import request
from werkzeug.exceptions import Forbidden, BadRequest
from ...controllers.profiles import TacareProfiles


class TacareExamples(TacareProfiles):
    @http.route('/how-it-works', auth='public', website=True, methods=['GET'])
    def seasonal_journey(self, **kw):
        return self._render('seasonal_journey', site='tacare')

    def _example_cards(self):
        # Compatibility hook: curated fictional pairs are retired. Only live
        # authorized comparisons are rendered by the homepage/matching pages.
        return []

    def _live_pair(self, job, profile, reason, view='hire'):
        offer = request.env['care.profile.capability'].sudo().search([
            ('id', '=', reason.get('capability_id', 0)), ('profile_id', '=', profile.id),
            ('active', '=', True), ('flex_state', '=', 'available')], limit=1)
        if not reason.get('eligible') or not offer or not profile.user_id.active:
            return False
        rows = reason['comparisons']
        return dict(job=job, profile=profile, offer=offer, reason=reason, view=view,
            detail_url='/tacare/pair/%s/%s' % (job.id, profile.id),
            met_count=sum(r['result'] == 'met' for r in rows),
            unknown_count=sum(r['result'] == 'unknown' for r in rows),
            highlights=[r for r in rows if r['name'] in ('Nghề / đầu việc', 'Khung giờ', 'Tiền công')])

    def _home_suggestions(self):
        self._flex_user()
        jobs, selected, hire = self._hire_matching_data()
        hire_pairs = []
        for job in jobs:
            for profile, reason in self._hire_matching_data(job.id)[2]:
                pair = self._live_pair(job, profile, reason)
                if pair:
                    hire_pairs.append(pair)
        receive_pairs = []
        profiles = request.env['tacare.profile'].sudo().browse()
        if self._role() != 'business':
            profiles = request.env['tacare.profile'].sudo().search([
                ('user_id', '=', self._user().id), ('status', '=', 'active'),
                ('company_id', 'in', self._user().company_ids.ids)], order='id desc', limit=100)
            for profile in profiles:
                for job, reason in self._receive_matching_data(profile):
                    pair = self._live_pair(job, profile, reason, 'receive')
                    if pair:
                        receive_pairs.append(pair)
        hire_pairs.sort(key=lambda p: p['reason']['rank'], reverse=True)
        receive_pairs.sort(key=lambda p: p['reason']['rank'], reverse=True)
        return dict(jobs=jobs, selected=selected, hire=hire[:3], profile=profiles[:1], receive=[],
            can_receive=self._role() != 'business', hire_pairs=hire_pairs[:6], receive_pairs=receive_pairs[:6])

    @http.route('/tacare/examples', auth='user', website=True, methods=['GET'])
    def examples(self, **kw):
        return request.redirect('/tacare/matching')

    def _home_admin_matches(self, **kw):
        if self._role() != 'admin':
            raise Forbidden('Chỉ quản trị được xem tổng quan đối chiếu.')
        jobs = request.env['hr.job'].sudo().search(self._job_domain() + [
            ('company_id', 'in', self._user().company_ids.ids), ('care_matching_enabled', '=', True)],
            order='write_date desc, id desc', limit=100)
        selected_id = str(kw.get('home_job') or '')
        if selected_id and not selected_id.isdigit():
            raise BadRequest('Tin đối chiếu không hợp lệ.')
        selected = jobs.filtered(lambda j: j.id == int(selected_id)) if selected_id else jobs
        if selected_id and not selected:
            raise BadRequest('Tin không còn sẵn sàng hoặc nằm ngoài phạm vi quản lý.')
        pairs = []
        for job in selected:
            profiles = self._visible_profiles(job.tacare_owner_partner_id).filtered(lambda p:
                self._current_consent(p, 'matching', job.tacare_owner_partner_id, 'profile') and
                self._current_consent(p, 'matching', job.tacare_owner_partner_id, 'skills'))
            for profile in profiles:
                reason = self._match(job, profile)
                if reason.get('eligible', True) and reason['rank']:
                    pair = self._live_pair(job, profile, reason)
                    if pair:
                        pairs.append(pair)
        pairs.sort(key=lambda p: p['reason']['rank'], reverse=True)
        return {'jobs': jobs, 'selected_id': selected_id, 'pairs': pairs[:12], 'checked_job_count': len(selected),
                'examples': self._example_cards()}
