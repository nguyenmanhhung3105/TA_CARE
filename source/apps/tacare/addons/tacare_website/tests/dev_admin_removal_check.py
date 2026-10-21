"""Rollback admin deletion, retention of linked history, isolation and consent checks."""
from odoo import fields
from odoo.exceptions import AccessError
from odoo.addons.tacare_website.models.admin_removal import plan_removal, remove_record


def check(env):
    assert env.cr.dbname == 'tacare_local'
    users = env['res.users'].sudo().with_context(no_reset_password=True)
    candidate = users.create({'name': 'QA remove candidate', 'login': 'qa-removal-candidate@example.invalid', 'tacare_account_role': 'candidate'})
    business = users.create({'name': 'QA remove business', 'login': 'qa-removal-business@example.invalid', 'tacare_account_role': 'business'})
    admin = users.create({'name': 'QA remove admin', 'login': 'qa-removal-admin@example.invalid',
        'group_ids': [(6, 0, [env.ref('base.group_user').id, env.ref('base.group_system').id])],
        'company_id': env.company.id, 'company_ids': [(6, 0, [env.company.id])]})
    profiles = env['tacare.profile'].sudo()
    profile = profiles.create({'name': 'QA disposable profile', 'user_id': candidate.id, 'scope': 'private', 'visible': False})
    cap = env['care.profile.capability'].sudo().create({'profile_id': profile.id, 'title': 'QA disposable offer',
        'category_id': env.ref('tacare_website.flex_category_cleaning').id})
    for actor in (candidate, business):
        try:
            remove_record(profile, actor)
        except AccessError:
            pass
        else:
            raise AssertionError('Non-admin deletion was allowed')
    assert profile.exists() and cap.exists()
    assert remove_record(cap, admin) == 'deleted' and profile.exists() and not cap.exists()
    assert remove_record(profile, admin) == 'deleted' and candidate.exists() and not profile.exists()
    source = env['hr.job'].sudo().search([('flex_demo_key', '=', 'recruitment-01')])
    job = source.copy({'name': 'QA disposable job', 'flex_demo_key': False,
        'tacare_owner_user_id': business.id, 'tacare_owner_partner_id': business.partner_id.id})
    assert not plan_removal(job, admin)['archive']
    assert remove_record(job, admin) == 'deleted' and not job.exists() and business.exists()
    job = source.copy({'name': 'QA job with connection', 'flex_demo_key': False,
        'tacare_owner_user_id': business.id, 'tacare_owner_partner_id': business.partner_id.id})
    profile = profiles.create({'name': 'QA linked profile', 'user_id': candidate.id, 'scope': 'members', 'visible': True})
    consent = env['care.consent'].sudo().create({'profile_id': profile.id, 'purpose': 'matching',
        'recipient_kind': 'members', 'field_scope': ['profile','skills'], 'state': 'granted', 'granted_by': candidate.id})
    connection = env['tacare.connection'].sudo().create({'type': 'application', 'job_id': job.id,
        'profile_id': profile.id, 'sender_id': candidate.id, 'receiver_id': business.id})
    assert plan_removal(job, admin)['archive']
    assert remove_record(job, admin) == 'removed'
    assert job.exists() and not job.active and not job.is_published and not job.care_matching_enabled
    assert connection.exists() and connection.status == 'cancelled'
    assert remove_record(profile, admin) == 'removed'
    assert profile.exists() and profile.status == 'archived' and not profile.visible and profile.scope == 'private'
    assert not consent.is_current('matching') and candidate.exists()
    company = env['res.company'].sudo().create({'name': 'QA disallowed company'})
    foreign = source.copy({'name': 'QA company isolation', 'company_id': company.id, 'flex_demo_key': False})
    try:
        remove_record(foreign, admin)
    except AccessError:
        pass
    else:
        raise AssertionError('Admin deleted outside allowed companies')
    assert foreign.exists()
    print('PASS admin-only deletion; account retained; child removal; linked job/profile retained outside library; pending request cancelled; consent revoked; allowed-company isolation')


try:
    check(env)
finally:
    env.cr.rollback()
