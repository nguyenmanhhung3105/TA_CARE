from urllib.parse import urlsplit

from odoo import http
from odoo.http import request
from odoo.addons.website.controllers.main import Website
from ..models.hr_job import SECTORS, TYPES, MODES


class TacareWebsite(Website):

    @http.route()
    def index(self, **kw):
        domain = request.website.domain or ""
        host = urlsplit(
            domain if "://" in domain else "//" + domain
        ).hostname or ""

        templates = {
            "khovieclam.localhost": "tacare_website.khovieclam_home",
            "khovieclam.vn": "tacare_website.khovieclam_home",
            "www.khovieclam.vn": "tacare_website.khovieclam_home",

            "tuhoso.localhost": "tacare_website.tuhoso_home",
            "tuhoso.com": "tacare_website.tuhoso_home",
            "www.tuhoso.com": "tacare_website.tuhoso_home",

            "tacare.localhost": "tacare_website.tacare_home",
            "tacare.vn": "tacare_website.tacare_home",
            "www.tacare.vn": "tacare_website.tacare_home",
        }

        template = templates.get(host)
        if not template:
            return super().index(**kw)

        local = host.endswith(".localhost")

        site = ('khovieclam' if 'khovieclam' in host else
                'tuhoso' if 'tuhoso' in host else 'tacare')
        return request.render('tacare_website.live_home', {
            'site': site,
            'role': ('admin' if request.env.user.has_group('base.group_system') else
                     request.env.user.sudo().tacare_account_role),
            'is_guest': request.env.user._is_public(),
            'account_name': request.env.user.name,
            'sectors': SECTORS,
            'types': TYPES,
            'modes': MODES,
            'notice': False,
            'jobs': request.env['hr.job'].sudo().search([
                ('tacare_status', '=', 'published'),
                ('website_published', '=', True),
                ('website_id', '=', request.env['website'].sudo().search([
                    ('domain', 'ilike', 'khovieclam')], limit=1).id),
            ], limit=3),
            'job_count': request.env['hr.job'].sudo().search_count([
                ('tacare_status', '=', 'published'),
                ('is_published', '=', True),
                ('website_id', '=', request.env['website'].sudo().search([
                    ('domain', 'ilike', 'khovieclam')], limit=1).id),
            ]),
            'urls': {
                'khovieclam': 'http://khovieclam.localhost:8069/' if local else 'https://khovieclam.vn/',
                'tuhoso': 'http://tuhoso.localhost:8069/' if local else 'https://tuhoso.com/',
                'tacare': 'http://tacare.localhost:8069/' if local else 'https://tacare.vn/',
            },
            "khovieclam_url": (
                "http://khovieclam.localhost:8069/"
                if local else "https://khovieclam.vn/"
            ),
            "tuhoso_url": (
                "http://tuhoso.localhost:8069/"
                if local else "https://tuhoso.com/"
            ),
            "tacare_url": (
                "http://tacare.localhost:8069/"
                if local else "https://tacare.vn/"
            ),
        })
