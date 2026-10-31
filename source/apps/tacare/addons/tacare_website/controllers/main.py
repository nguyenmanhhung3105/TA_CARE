from urllib.parse import urlencode, urlsplit

from odoo import http, fields
from odoo.http import request
from odoo.addons.website.controllers.main import Website
from ..models.jobs.hr_job import SECTORS, TYPES, MODES
from .site_context import safe_next, site_context
from odoo.addons.tacare_account_access.models.auth_session import FRESH_KEY
from odoo.addons.tacare_account_access.deployment import origin_info, product_urls


class TacareWebsite(Website):

    @http.route()
    def index(self, **kw):
        domain = request.website.domain or ""
        host = urlsplit(
            domain if "://" in domain else "//" + domain
        ).hostname or ""

        info = origin_info(host)
        if not info:
            return super().index(**kw)
        site = info[1]
        urls = product_urls(host)
        admin_overview = False
        home_examples = []
        home_suggestions = False
        marketing_matches = []
        if site == 'khovieclam':
            from ..sites.khovieclam.matching_preview import matching_previews
            marketing_matches = matching_previews(request.env)
        if site == 'tacare':
            from ..sites.tacare.examples import TacareExamples
            hub = TacareExamples()
            home_examples = hub._example_cards()
            if not request.env.user._is_public() and request.env.user._tacare_can_access_host(request.httprequest.host):
                home_suggestions = hub._home_suggestions()
        if site == 'tacare' and not request.env.user._is_public() and request.env.user.has_group('base.group_system'):
            from ..sites.tacare.examples import TacareExamples
            admin_overview = TacareExamples()._home_admin_matches(**kw)
        from .seasonal import marketplace_context
        home_live_pairs = []
        if admin_overview:
            home_live_pairs = admin_overview['pairs']
        elif home_suggestions:
            seen = set()
            for pair in home_suggestions['hire_pairs'] + home_suggestions['receive_pairs']:
                key = (pair['job'].id, pair['profile'].id)
                if key not in seen:
                    home_live_pairs.append(pair)
                    seen.add(key)
        response = request.render('tacare_website.live_home', {
            **marketplace_context(request.env),
            'admin_overview': admin_overview,
            'home_examples': home_examples, 'home_suggestions': home_suggestions,
            'home_live_pairs': home_live_pairs,
            'marketing_matches': marketing_matches,
            **site_context(site, urls),
            'site': site,
            'role': ('admin' if request.env.user.has_group('base.group_system') else
                     request.env.user.sudo().tacare_account_role),
            'is_guest': request.env.user._is_public(),
            'account_name': request.env.user.name,
            'sectors': SECTORS,
            'job_sectors': request.env['care.job.sector'].sudo().search([]),
            'positions': request.env['care.job.position'].sudo().search([]),
            'types': TYPES,
            'modes': MODES,
            'notice': False,
            'jobs': request.env['hr.job'].sudo().search([
                ('care_remaining_slots', '>', 0),
                ('care_opportunity_kind', '=', 'flexible'), ('tacare_status', '=', 'published'),
                ('is_published', '=', True), '|', ('tacare_deadline', '=', False),
                ('tacare_deadline', '>=', fields.Date.today()),
                ('website_id', '=', request.env['website'].sudo().search([
                    ('domain', 'ilike', 'khovieclam')], limit=1).id),
            ], limit=4, order='create_date desc, id desc'),
            'job_count': request.env['hr.job'].sudo().search_count([
                ('care_remaining_slots', '>', 0),
                ('care_opportunity_kind', '=', 'flexible'), ('tacare_status', '=', 'published'),
                ('is_published', '=', True), '|', ('tacare_deadline', '=', False),
                ('tacare_deadline', '>=', fields.Date.today()),
                ('website_id', '=', request.env['website'].sudo().search([
                    ('domain', 'ilike', 'khovieclam')], limit=1).id),
            ]),
            'urls': urls,
            "khovieclam_url": urls['khovieclam'],
            "tuhoso_url": urls['tuhoso'],
            "tacare_url": urls['tacare'],
        })
        response.headers['Cache-Control'] = 'private, no-store'
        return response

    @http.route()
    def web_login(self, redirect=None, **kw):
        host = urlsplit('//' + request.httprequest.host).hostname or ''
        if not origin_info(host):
            return super().web_login(redirect=redirect, **kw)
        target = safe_next(redirect, request.website.language_ids.mapped('url_code'))
        if request.httprequest.method == 'GET':
            if request.session.uid and request.env.user._tacare_can_access_host(host):
                return request.redirect(target)
            return request.redirect('/?' + urlencode({'login': '1', 'next': target}))
        # Keep Odoo authentication, throttling, CAPTCHA and MFA intact. A failed
        # native POST renders the same homepage with its login dialog still open.
        response = super().web_login(redirect=target, **kw)
        if request.params.get('login_success'):
            request.session[FRESH_KEY] = True
        if response.status_code in (301, 302, 303, 307, 308):
            if request.params.get('login_success') and request.session.uid:
                return request.redirect('/care/sso/start?' + urlencode({'next': target}), code=303)
            return response
        error = response.qcontext.get('error') if response.qcontext else False
        if not error:
            return response
        request._tacare_login_feedback = {
            'error': 'Thông tin đăng nhập chưa đúng hoặc tài khoản chưa có quyền trên website này.',
            'login': (kw.get('login') or '')[:254], 'next': target,
        }
        result = self.index()
        result.headers.update({'Cache-Control': 'private, no-store',
                               'X-Frame-Options': 'SAMEORIGIN',
                               'Content-Security-Policy': "frame-ancestors 'self'"})
        return result
