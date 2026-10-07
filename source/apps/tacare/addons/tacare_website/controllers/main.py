from urllib.parse import urlsplit

from odoo import http
from odoo.http import request
from odoo.addons.website.controllers.main import Website


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

        return request.render(template, {
            "khovieclam_url": (
                "http://khovieclam.localhost:8069/"
                if local else "https://khovieclam.vn/"
            ),
            "tuhoso_url": (
                "http://tuhoso.localhost:8069/"
                if local else "https://tuhoso.com/"
            ),
        })