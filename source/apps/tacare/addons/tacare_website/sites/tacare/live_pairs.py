"""Live job/provider pairs. No persisted or hand-authored matching outcomes."""
from odoo import http
from odoo.http import request
from werkzeug.exceptions import NotFound
from .work_reviews import WorkReviews


class LivePairs(WorkReviews):
    def _render(self, template, site='tacare', **values):
        if template == 'live_matching':
            pairs = []
            for record, reason in values.get('matches', []):
                job = values['selected'] if values['kind'] == 'profiles' else record
                profile = record if values['kind'] == 'profiles' else values['profile']
                pair = self._live_pair(job, profile, reason, 'hire' if values['kind'] == 'profiles' else 'receive')
                if pair:
                    pairs.append(pair)
            values['live_pairs'] = pairs
        return super()._render(template, site=site, **values)

    @http.route('/tacare/pair/<int:job_id>/<int:profile_id>', auth='user', website=True, methods=['GET'])
    def live_pair_detail(self, job_id, profile_id, **kw):
        self._flex_user()
        job = request.env['hr.job'].sudo().search(self._job_domain() + [
            ('id', '=', job_id), ('care_matching_enabled', '=', True)], limit=1)
        if not job or job.company_id not in self._user().company_ids:
            raise NotFound()
        profile = request.env['tacare.profile'].sudo().search([
            ('id', '=', profile_id), ('status', '=', 'active'), ('user_id.active', '=', True)], limit=1)
        own = profile and profile.user_id == self._user() and profile.company_id in self._user().company_ids
        recipient = job.tacare_owner_partner_id
        if not own:
            self._own_job(job.id, 'handle')
            if not profile or profile not in self._visible_profiles(recipient):
                raise NotFound()
        if not profile or not self._current_consent(profile, 'matching', recipient, 'profile') or not \
                self._current_consent(profile, 'matching', recipient, 'skills'):
            raise NotFound('Quyền đối chiếu không còn hiệu lực.')
        reason = self._match(job, profile)
        pair = self._live_pair(job, profile, reason, 'receive' if own else 'hire')
        if not pair:
            raise NotFound('Thông tin đã thay đổi; cặp này không còn trong gợi ý hiện tại.')
        pair['is_detail'] = True
        return self._render('live_pair_detail', pair=pair,
            review_summary=request.env['care.feedback'].sudo()._summary(profile=profile))
