"""Rollback-only checks for anonymous marketing and owner-only pair details."""
from contextlib import ExitStack, contextmanager
from types import SimpleNamespace
from unittest.mock import patch

from odoo.exceptions import AccessError
from werkzeug.exceptions import Forbidden, NotFound
from odoo.addons.tacare_website.sites.khovieclam.matching_preview import matching_previews
from odoo.addons.tacare_website.sites.tacare.live_pairs import LivePairs
from odoo.addons.tacare_website.sites.tacare.routes import HubControllers

assert env.cr.dbname == 'tacare_local'
controller = LivePairs()
modules = ('controllers.shared.routes', 'controllers.profiles', 'controllers.flexible_work',
           'sites.khovieclam.routes', 'sites.tacare.routes', 'sites.tacare.examples',
           'sites.tacare.work_reviews', 'sites.tacare.live_pairs')


def actor(user):
    stack = ExitStack()
    mocked = SimpleNamespace(env=env(user=user.id, context={**env.context,
        'allowed_company_ids': user.company_id.ids}), params={},
        httprequest=SimpleNamespace(method='GET'))
    for module in modules:
        stack.enter_context(patch('odoo.addons.tacare_website.' + module + '.request', mocked))
    return stack


def denied(operation):
    try:
        operation()
    except (Forbidden, NotFound, AccessError):
        return
    raise AssertionError('Private comparison became accessible')


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


try:
    previews = matching_previews(env)
    assert len(previews) == 2, 'Expected two existing professions with real suggestions'
    assert len({p['category'] for p in previews}) == 2
    expected_fields = {'job_title', 'category', 'photo', 'region', 'schedule', 'price'}
    assert all(set(p) == expected_fields and all(isinstance(v, str) for v in p.values())
               for p in previews), 'Projection must contain only public job strings'
    kho = env['website'].sudo().search([('domain', 'ilike', 'khovieclam')], limit=1)
    assert matching_previews(env(user=kho.user_id.id)) == previews
    # No static/fabricated fallback if the actual algorithm has no result.
    with patch.object(type(env['hr.job']), '_care_compare_profile', return_value={'eligible': False}):
        assert matching_previews(env) == []

    from odoo.addons.tacare_website.tools.map_test_profiles import account
    business = account(env, 'home')
    outsider = account(env, 'green')
    assert business and outsider
    with actor(business):
        pairs = controller._home_suggestions()['hire_pairs']
        assert pairs
        pair = pairs[0]
        detail = lambda: LivePairs.live_pair_detail.original_endpoint(
            controller, pair['job'].id, pair['profile'].id)
        with patch.object(controller, '_render', side_effect=lambda template, **values: values):
            assert detail()['pair']['profile'].id == pair['profile'].id
            landing = HubControllers.matching.original_endpoint(controller)
            assert landing['matches'], 'Marketing CTA should select an own need with matches'
        with patch.object(controller, '_match', return_value={'eligible': False}):
            denied(detail)
            denied(lambda: HubControllers.matching_profile_detail.original_endpoint(
                controller, pair['job'].id, pair['profile'].id))
    with actor(pair['profile'].user_id):
        with patch.object(controller, '_render', side_effect=lambda template, **values: values):
            assert detail()['pair']['profile'].id == pair['profile'].id
    with actor(outsider):
        denied(detail)
    with actor(kho.user_id):
        denied(detail)

    grants = env['care.consent'].sudo().search([
        ('purpose', 'in', ['discovery', 'matching']), ('state', '=', 'granted')])
    with temporary():
        grants.write({'state': 'revoked'})
        assert matching_previews(env) == []
        with actor(business):
            denied(detail)
            with patch.object(controller, '_render', side_effect=lambda template, **values: values):
                assert not HubControllers.matching.original_endpoint(controller)['matches']
    with temporary():
        from datetime import timedelta
        from odoo import fields
        now = fields.Datetime.now()
        grants.write({'valid_from': now - timedelta(days=3), 'valid_until': now - timedelta(days=1)})
        assert matching_previews(env) == []
    with temporary():
        env['tacare.profile'].sudo().search([]).write({'scope': 'private'})
        assert matching_previews(env) == []
    with temporary():
        env['hr.job'].sudo().search([]).write({'care_matching_enabled': False})
        assert matching_previews(env) == []
    assert matching_previews(env) == previews
    print('PASS anonymous previews: two real categories, public job strings only; algorithm/consent/expiry/private/disabled gates; own buyer/provider detail allowed, guest/other organization denied; own landing and no-match state; rollback only')
finally:
    env.cr.rollback()
