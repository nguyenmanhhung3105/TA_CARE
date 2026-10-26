"""Rollback-only integration/security tests on existing local account records."""
from contextlib import ExitStack, contextmanager
from types import SimpleNamespace
from unittest.mock import patch
from datetime import timedelta

from odoo import fields
from odoo.exceptions import AccessError, ValidationError
from werkzeug.exceptions import BadRequest, Forbidden, NotFound
from odoo.addons.tacare_website.geo_utils import approximate
from odoo.addons.tacare_website.sites.tacare.nearby import Nearby, parse_location
from odoo.addons.tacare_website.tools.map_test_profiles import account

assert env.cr.dbname == 'tacare_local'
controller = Nearby()
modules = ('controllers.shared.routes', 'controllers.profiles', 'controllers.flexible_work',
    'sites.khovieclam.routes', 'sites.tacare.routes', 'sites.tacare.examples',
    'sites.tacare.work_reviews', 'sites.tacare.live_pairs', 'sites.tacare.nearby')


def actor(user):
    stack = ExitStack()
    mocked = SimpleNamespace(env=env(user=user.id, context={**env.context,
        'allowed_company_ids': user.company_id.ids}), params={},
        httprequest=SimpleNamespace(method='GET', host='tacare.localhost:8069'),
        make_json_response=lambda value, **kw: value)
    for module in modules:
        stack.enter_context(patch('odoo.addons.tacare_website.' + module + '.request', mocked))
    return stack


class RollbackCase(Exception):
    pass


@contextmanager
def temporary():
    try:
        with env.cr.savepoint():
            yield
            raise RollbackCase()
    except RollbackCase:
        pass


def denied(call):
    try:
        call()
    except (AccessError, Forbidden, NotFound, BadRequest, ValidationError):
        return
    raise AssertionError('Expected denial')


try:
    business = account(env, 'home')
    other = account(env, 'digital')
    public = env.ref('base.public_user')
    assert business and other
    with actor(business):
        payloads = [controller._nearby_payload('hire', r.id, 50) for r in controller._nearby_sources('hire')]
        payload = next(p for p in payloads if p['markers'])
        job_id = payload['source']['id']
        item = payload['markers'][0]
        pair_job, profile_id = map(int, item['key'].split('-'))
        job = env['hr.job'].sudo().browse(pair_job)
        profile = env['tacare.profile'].sudo().browse(profile_id)
        reason = controller._match(job, profile)
        offer = env['care.profile.capability'].sudo().browse(reason['capability_id'])
        assert item['point'] == approximate(offer.geo_lat, offer.geo_lon)
        assert item['point'] != [offer.geo_lat, offer.geo_lon]
        expected_url = 'https://www.google.com/maps/search/?api=1&query=%.6f%%2C%.6f' % (offer.geo_lat, offer.geo_lon)
        assert offer.geo_map_url == expected_url
        env.cr.execute('SELECT geo_map_url FROM care_profile_capability WHERE id=%s', [offer.id])
        assert env.cr.fetchone()[0] == expected_url, 'Map URL must be stored in the database'
        assert set(item) == {'key', 'point', 'title', 'subtitle', 'category', 'icon', 'price', 'region', 'url', 'sample'}
        def visible():
            return item['key'] in [m['key'] for m in controller._nearby_payload('hire', job_id, 50)['markers']]
        assert visible()
        for changes, target in [({'geo_share': False}, offer), ({'geo_set': False, 'geo_share': False}, offer),
                                ({'scope': 'private'}, profile), ({'visible': False}, profile)]:
            with temporary():
                target.write(changes)
                assert not visible(), changes
        grants = env['care.consent'].sudo().search([('profile_id', '=', profile.id),
            ('purpose', 'in', ['discovery', 'matching']), ('state', '=', 'granted')])
        assert grants
        with temporary():
            grants.write({'state': 'revoked'})
            assert not visible()
        with temporary():
            grants.write({'valid_from': fields.Datetime.now() - timedelta(days=3),
                          'valid_until': fields.Datetime.now() - timedelta(days=1)})
            assert not visible()
        # Both points stay in a covered prefix; only the exact distance excludes
        # the target. Moving a valid offer never changes its profession/terms.
        with temporary():
            offer.write({'geo_lat': job.geo_lat + .03, 'geo_lon': job.geo_lon})
            assert item['key'] not in [m['key'] for m in controller._nearby_payload('hire', job_id, 2)['markers']]
            assert item['key'] in [m['key'] for m in controller._nearby_payload('hire', job_id, 5)['markers']]
        with temporary():
            job.write({'care_matching_enabled': False})
            denied(lambda: controller._nearby_payload('hire', job_id, 50))
        denied(lambda: controller._nearby_payload('receive', offer.id, 50))
        denied(lambda: controller._nearby_payload('hire', job_id, 500))
        denied(lambda: offer.with_user(business).read(['geo_lat', 'geo_lon']))
        denied(lambda: offer.with_user(business).read(['geo_map_url']))
    with actor(profile.user_id):
        received = controller._nearby_payload('receive', offer.id, 50)
        assert item['key'] in [m['key'] for m in received['markers']]
        marker = next(m for m in received['markers'] if m['key'] == item['key'])
        assert marker['point'] == approximate(job.geo_lat, job.geo_lon)
        denied(lambda: controller._nearby_payload('hire', job.id, 50))
        with temporary():
            offer.write({'geo_share': False})
            assert not controller._nearby_payload('receive', offer.id, 50)['markers']
        with temporary():
            grants.write({'state': 'revoked'})
            assert not controller._nearby_payload('receive', offer.id, 50)['markers']
        denied(lambda: controller._flex_own('hr.job', job.id))
    with actor(other):
        denied(lambda: controller._nearby_payload('hire', job.id, 50))
        denied(lambda: controller._nearby_payload('receive', offer.id, 50))
    with actor(public):
        denied(lambda: controller._nearby_payload('hire', job.id, 50))
    for lat, lon in [('nan', '106'), ('10', 'inf'), ('10', ''), ('80', '106'), ('10', '150')]:
        denied(lambda: parse_location({'geo_lat': lat, 'geo_lon': lon}))
    denied(lambda: parse_location({'geo_share': 'on'}))
    assert not parse_location({})['geo_set']
    print('PASS nearby: bilateral winning-offer match; exact radius/coarse projection; current purpose/organization consent, expiry/revoke/private/hidden/disabled; guest/foreign role and owner isolation; controller-only exact fields; invalid locations; all rolled back')
finally:
    env.cr.rollback()
