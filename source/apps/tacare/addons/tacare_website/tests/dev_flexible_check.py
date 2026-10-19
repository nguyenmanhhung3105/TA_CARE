"""Rollback-only flexible work ORM security/validation checks on the seeded local demo."""
import hashlib
import json
from pathlib import Path

from odoo.exceptions import AccessError, ValidationError


def check(env):
    assert env.cr.dbname == 'tacare_local'
    credentials = json.loads(Path('/var/lib/odoo/flexible_demo_accounts.json').read_text())
    jobs = env['hr.job'].sudo().search([('flex_demo_key', '!=', False)])
    demo_profiles = env['tacare.profile'].sudo().search([('flex_demo_key', '=like', 'profile-%')])
    demo_caps = env['care.profile.capability'].sudo().search([('flex_demo_key', '=like', 'flex-service-%')])
    assert len(jobs) == 20 and len(demo_profiles) == 15 and len(demo_caps) == 10
    assert len(jobs.filtered(lambda j: j.care_opportunity_kind == 'recruitment')) == 5
    assert not jobs.filtered('care_matching_enabled')
    assert not any(j._care_publish_errors() for j in jobs)
    assert not any(c._flex_ready_errors() for c in demo_caps)
    print('PASS original demo dataset: 20 jobs (5 recruitment + 15 flexible), 15 profiles, 10 work capabilities; publishing data valid; flexible matching disabled')
    print('Local totals: jobs=%s, profiles=%s, capabilities=%s' % (
        env['hr.job'].sudo().search_count([]), env['tacare.profile'].sudo().search_count([]),
        env['care.profile.capability'].sudo().search_count([])))
    env.cr.execute("SELECT id, login, password, active, tacare_account_role FROM res_users WHERE login NOT LIKE 'demo-flex-%' AND login NOT IN ('ungvien1@tacare.vn', 'ungvien2@tacare.vn') ORDER BY id")
    assert hashlib.sha256(repr(env.cr.fetchall()).encode()).hexdigest() == credentials['original_accounts_fingerprint']
    users = env['res.users'].sudo()
    first = users.search([('login', '=', 'demo-flex-06@example.invalid')])
    second = users.search([('login', '=', 'demo-flex-07@example.invalid')])
    business = users.search([('login', '=', 'demo-flex-00@example.invalid')])
    for user in (first, second, business):
        for host in ('khovieclam.localhost', 'tuhoso.localhost', 'tacare.localhost'):
            allowed = {'khovieclam.localhost', 'tacare.localhost'} if user == business else {'tuhoso.localhost', 'tacare.localhost'}
            assert user._tacare_can_access_host(host) == (host in allowed)
    caps = env['care.profile.capability'].sudo()
    own = caps.search([('profile_id.user_id', '=', first.id)], limit=1)
    other = caps.search([('profile_id.user_id', '=', second.id)], limit=1)
    assert own and other
    assert caps.with_user(first).search([('id', 'in', (own | other).ids)]) == own
    assert env['tacare.profile'].with_user(first).search([('flex_demo_key', '!=', False)]) == own.profile_id
    for operation in ('write', 'create'):
        try:
            with env.cr.savepoint():
                if operation == 'write':
                    own.with_user(first).write({'title': 'illegal portal mutation'})
                else:
                    caps.with_user(first).create({'profile_id': first.id, 'title': 'illegal'})
        except AccessError:
            pass
        else:
            raise AssertionError('Direct portal mutation allowed')
    for values in ({'flex_rate_min': float('nan')}, {'flex_rate_max': -1},
                   {'flex_time_from': '24:30'}, {'flex_time_from':'10:00','flex_time_to':'09:00'},
                   {'flex_weekdays':'8'}, {'flex_portfolio_url':'javascript:alert(1)'}):
        try:
            with env.cr.savepoint():
                own.write(values)
        except (ValidationError, ValueError):
            pass
        else:
            raise AssertionError('Invalid structured data accepted')
    item = caps.create({'profile_id': own.profile_id.id, 'title':'QA rollback capability',
        'flex_category_id':own.category_id.id,'flex_rate_min':125000,'currency_id':own.currency_id.id})
    assert item.category_id == own.category_id and item.rate_min == 125000
    with env.cr.savepoint():
        own.write({'description': False})
        assert 'tiêu đề và mô tả công việc nhận làm' in own._flex_ready_errors()
    print('PASS flexible ORM: original accounts unchanged, host access, private profile/capability reads, blocked portal writes, numeric/time/URL validation, canonical aliases')


try:
    check(env)
finally:
    env.cr.rollback()
