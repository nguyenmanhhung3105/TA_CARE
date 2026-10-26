"""Existing-account, rollback-only checks for live pairs and source comparisons."""
import json
from pathlib import Path
from contextlib import ExitStack
from types import SimpleNamespace
from unittest.mock import patch
from odoo.exceptions import AccessError
from werkzeug.exceptions import Forbidden, NotFound
from odoo.addons.tacare_website.sites.tacare.live_pairs import LivePairs
from odoo.addons.tacare_website.tools.account_bound_records import normalize_account_records

assert env.cr.dbname == 'tacare_local'
controller = LivePairs()
def detail_for(job_id, profile_id):
    # HTTP routing and Response adaptation are exercised by the browser check;
    # this rollback unit invokes the original endpoint with a mocked request.
    return LivePairs.live_pair_detail.original_endpoint(controller, job_id, profile_id)
modules = ('controllers.shared.routes', 'controllers.profiles', 'controllers.flexible_work',
    'sites.khovieclam.routes', 'sites.tacare.routes', 'sites.tacare.examples', 'sites.tacare.work_reviews', 'sites.tacare.live_pairs')

def actor(user):
    stack = ExitStack()
    mocked = SimpleNamespace(env=env(user=user.id, context={**env.context,
        'allowed_company_ids': user.company_id.ids}), params={}, httprequest=SimpleNamespace(method='GET'))
    for module in modules:
        stack.enter_context(patch('odoo.addons.tacare_website.' + module + '.request', mocked))
    return stack

def expect_denied(operation):
    try:
        operation()
    except (Forbidden, NotFound, AccessError):
        return
    raise AssertionError('Unauthorized pair became visible')

try:
    identities = json.loads(Path('/var/lib/odoo/live_pair_test_identities.json').read_text())
    profiles = env['tacare.profile'].sudo().search([])
    jobs = env['hr.job'].sudo().search([('care_opportunity_kind', '=', 'flexible')])
    assert all(p.user_id.active for p in profiles)
    assert all(j.tacare_owner_user_id.active for j in jobs)
    assert not env['res.partner'].sudo().search_count([('active', '=', True), ('name', '=like', 'QA %')])
    assert not env['res.partner'].sudo().search_count([('active', '=', True), ('is_company', '=', False), ('care_has_active_account', '=', False)])
    assert not normalize_account_records(env)['archive_contacts']
    before = [(p.id, p.version, p.profile_title, p.name) for p in profiles]
    normalize_account_records(env, apply=True)
    assert before == [(p.id, p.version, p.profile_title, p.name) for p in profiles]
    for p in profiles:
        assert 'demo' not in (p.profile_title + p.name + (p.bio or '')).lower()
    baseline = Path('/var/lib/odoo/live_pair_previous_compare.py')
    checked = 0
    if baseline.exists():
        previous = {}
        exec(baseline.read_text(), previous)
        for job in jobs:
            for p in profiles:
                old = previous['previous_compare'](job, p, True, True)
                new = job._care_compare_profile(p, allow_profile=True, allow_skills=True)
                assert (old['eligible'], old['rank'], old['matched'], old['missing']) == \
                    (new['eligible'], new['rank'], new['matched'], new['missing'])
                assert [(r['name'], r['result'], r['basis']) for r in old['comparisons']] == \
                    [(r['name'], r['result'], r['basis']) for r in new['comparisons']]
                checked += 1
    expected = {}
    for item in identities:
        user = env['res.users'].sudo().browse(item['user_id'])
        with actor(user):
            if item['role'] == 'admin':
                pairs = controller._home_admin_matches()['pairs']
            else:
                data = controller._home_suggestions()
                pairs = data['hire_pairs'] + data['receive_pairs']
            unique = {(p['job'].id, p['profile'].id): p for p in pairs}
            expected[item['role']] = []
            for p in unique.values():
                assert p['offer'].profile_id == p['profile']
                assert p['offer'].id == p['reason']['capability_id']
                fresh = controller._match(p['job'], p['profile'])
                assert p['reason'] == fresh
                price = next(r for r in fresh['comparisons'] if r['name'] == 'Tiền công')
                assert price['need_value'] == p['job']._flex_price_label()
                assert price['offer_value'] == p['offer']._flex_price_label()
                assert all('need_value' in r and 'offer_value' in r for r in fresh['comparisons'])
                with patch.object(controller, '_render', side_effect=lambda template, **values: values):
                    detail = detail_for(p['job'].id, p['profile'].id)
                    assert detail['pair']['offer'] == p['offer']
                expected[item['role']].append(dict(job_id=p['job'].id, profile_id=p['profile'].id,
                    capability_id=p['offer'].id, job=p['job'].name, profile=p['profile'].profile_title,
                    rows=fresh['comparisons']))
    assert expected['business'] and expected['provider']
    full_admin = env['res.users'].sudo().search([('active', '=', True)]).filtered(lambda u:
        u.has_group('base.group_system') and jobs[:1].company_id in u.company_ids and
        profiles[:1].company_id in u.company_ids)[:1]
    assert full_admin
    with actor(full_admin):
        admin_pairs = controller._home_admin_matches()['pairs']
        assert admin_pairs, 'A company-authorized administrator sees actual consented pairs'
        with patch.object(controller, '_render', side_effect=lambda template, **values: values):
            p = admin_pairs[0]
            assert detail_for(p['job'].id, p['profile'].id)['pair']['offer'] == p['offer']
    pair = expected['business'][0]
    job, profile = env['hr.job'].sudo().browse(pair['job_id']), profiles.browse(pair['profile_id'])
    offer = env['care.profile.capability'].sudo().browse(pair['capability_id'])
    buyer = env['res.users'].sudo().browse(next(i['user_id'] for i in identities if i['role'] == 'business'))
    other = env['res.users'].sudo().browse(next(i['user_id'] for i in identities if i['role'] == 'other_business'))
    with actor(other):
        expect_denied(lambda: detail_for(job.id, profile.id))
    old_price = offer.flex_rate_min
    offer.write({'flex_rate_min': (job.flex_rate_max or job.flex_rate_min) * 3})
    with actor(buyer):
        assert profile.id not in [p.id for p, r in controller._hire_matching_data(job.id)[2]]
        expect_denied(lambda: detail_for(job.id, profile.id))
    offer.write({'flex_rate_min': old_price})
    consents = env['care.consent'].sudo().search([('profile_id', '=', profile.id), ('state', '=', 'granted')])
    consents.write({'state': 'revoked'})
    with actor(buyer):
        assert profile.id not in [p.id for p, r in controller._hire_matching_data(job.id)[2]]
        expect_denied(lambda: detail_for(job.id, profile.id))
    report = Path('/var/lib/odoo/live_pair_test_expected.json')
    report.write_text(json.dumps(expected, ensure_ascii=False, default=str)); report.chmod(0o600)
    print('PASS live pairs: existing account ownership, contact archive/filter, ordinary profile prose, '
          '%s baseline algorithm pairs unchanged, exact source columns and winning offer, all owner profiles, '
          'organization isolation, changed-budget recomputation and revoked-consent denial; rolling back.' % checked)
finally:
    env.cr.rollback()
