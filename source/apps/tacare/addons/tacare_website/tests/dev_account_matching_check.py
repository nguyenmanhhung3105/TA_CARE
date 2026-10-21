"""Rollback-only regression: account dataset, conservative flexible matching and consent."""
from odoo.exceptions import AccessError


def check(env):
    assert env.cr.dbname == 'tacare_local'
    p = env['tacare.profile'].sudo()
    all_profiles = p.search([])
    assert all(x.user_id.active and not x.user_id.login.startswith('demo-flex-') for x in all_profiles)
    assert len(all_profiles) == 7
    jobs = env['hr.job'].sudo().search([('flex_demo_key', '!=', False)])
    assert len(jobs) == 20 and not any(j._care_publish_errors() for j in jobs)
    source = jobs.filtered(lambda j: j.flex_demo_key == 'flex-job-01')
    assert source
    cap = env['care.profile.capability'].sudo().search([('flex_demo_key', '=', 'refresh-uv2-flexible')])
    assert cap and cap.profile_id.user_id.active
    job = source.copy({'flex_rate_min': 100000, 'flex_rate_max': 100000,
        'flex_date_from': False, 'flex_date_to': False, 'flex_weekdays': False,
        'flex_schedule': 'flexible', 'flex_time_from': False, 'flex_time_to': False})
    profile = cap.profile_id
    result = job._care_compare_profile(profile, True, True)
    assert result['eligible'] and result['rank'] > 0
    assert not job._care_compare_profile(profile, True, False)['eligible']
    assert not job._care_compare_profile(profile, False, True)['eligible']
    original = cap.flex_region_id
    other_region = env['res.country.state'].search([('country_id.code', '=', 'VN'), ('id', '!=', original.id)], limit=1)
    # Restrict to one test offer so another offer cannot hide a conflict.
    for other in profile.capability_ids - cap:
        other.write({'flex_state': 'paused'})
    cap.write({'flex_region_id': other_region.id})
    assert not job._care_compare_profile(profile, True, True)['eligible']
    cap.write({'flex_region_id': original.id, 'flex_rate_min': 200000, 'flex_rate_max': 200000})
    assert not job._care_compare_profile(profile, True, True)['eligible']
    cap.write({'flex_rate_min': 65000, 'flex_rate_max': 80000,
        'flex_schedule': 'recurring', 'flex_weekdays': '5,6', 'flex_time_from': '08:00', 'flex_time_to': '12:00'})
    job.write({'flex_schedule': 'recurring', 'flex_weekdays': '0', 'flex_time_from': '08:00', 'flex_time_to': '11:00'})
    assert not job._care_compare_profile(profile, True, True)['eligible']
    job.write({'flex_weekdays': '5'})
    assert job._care_compare_profile(profile, True, True)['eligible']
    job.write({'flex_time_to': '13:00'})
    assert not job._care_compare_profile(profile, True, True)['eligible']
    job.write({'flex_time_from': False, 'flex_time_to': False, 'flex_pay_unit': 'trip'})
    assert not job._care_compare_profile(profile, True, True)['eligible']
    user = profile.user_id
    own = p.with_user(user).search([])
    assert own and all(x.user_id == user for x in own)
    try:
        with env.cr.savepoint():
            cap.with_user(user).write({'title': 'Forbidden portal direct write'})
    except AccessError:
        pass
    else:
        raise AssertionError('Portal direct capability write must fail')
    consent = env['care.consent'].sudo().create({'profile_id': profile.id, 'purpose': 'matching',
        'recipient_kind': 'members', 'field_scope': ['profile', 'skills'], 'state': 'granted', 'granted_by': user.id})
    assert consent.is_current('matching', field='skills')
    consent.write({'state': 'revoked'})
    assert not consent.is_current('matching', field='skills')
    print('PASS account dataset, flexible category/region/day/time/price exclusions, unknowns, trip disabled, ACL isolation and current consent')


try:
    check(env)
finally:
    env.cr.rollback()
