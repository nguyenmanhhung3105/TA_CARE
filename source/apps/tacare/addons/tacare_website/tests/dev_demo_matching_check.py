"""Rollback checks for both matching directions with recipient-specific demo consent."""
from contextlib import ExitStack
from types import SimpleNamespace
from unittest.mock import patch
from datetime import timedelta
from odoo import fields
from odoo.addons.tacare_website.sites.tacare.work_reviews import WorkReviews
from odoo.addons.tacare_website.tools.matching_demo import prepare_matching_demo

assert env.cr.dbname == 'tacare_local'
controller = WorkReviews()
modules = ('controllers.shared.routes', 'controllers.profiles', 'controllers.flexible_work',
           'sites.tacare.routes', 'sites.tacare.work_reviews')

def actor(user, company):
    stack = ExitStack()
    mocked = SimpleNamespace(env=env(user=user.id, context={**env.context, 'allowed_company_ids': company.ids}),
        params={}, httprequest=SimpleNamespace(method='GET'))
    for module in modules:
        stack.enter_context(patch('odoo.addons.tacare_website.' + module + '.request', mocked))
    return stack

try:
    cases = prepare_matching_demo(env, apply=True)
    for job_id, profile_id, variant in cases:
        job = env['hr.job'].sudo().browse(job_id)
        profile = env['tacare.profile'].sudo().browse(profile_id)
        with actor(job.tacare_owner_user_id, job.company_id):
            _, selected, matches = controller._hire_matching_data(job.id)
            assert selected == job
            assert (profile.id in [p.id for p, reason in matches]) == (variant == 'fit')
        with actor(profile.user_id, profile.company_id):
            assert controller._matching_is_enabled(profile)
            matches = controller._receive_matching_data(profile)
            assert (job.id in [j.id for j, reason in matches]) == (variant == 'fit')
            assert all(j.tacare_owner_partner_id == job.tacare_owner_partner_id for j, reason in matches)
    job_id, profile_id, _ = cases[0]
    job = env['hr.job'].sudo().browse(job_id)
    profile = env['tacare.profile'].sudo().browse(profile_id)
    consents = env['care.consent'].sudo().search([('profile_id', '=', profile.id)])
    consents.write({'state': 'revoked'})
    with actor(profile.user_id, profile.company_id):
        assert not controller._matching_is_enabled(profile)
        assert not controller._receive_matching_data(profile)
    with actor(job.tacare_owner_user_id, job.company_id):
        assert profile not in controller._visible_profiles(job.tacare_owner_partner_id)
        assert profile.id not in [p.id for p, reason in controller._hire_matching_data(job.id)[2]]
    consents.write({'state': 'granted', 'valid_from': fields.Datetime.now() - timedelta(days=3),
        'valid_until': fields.Datetime.now() - timedelta(days=1)})
    with actor(profile.user_id, profile.company_id):
        assert not controller._receive_matching_data(profile)
    print('PASS demo matching: both directions, nine professions, three budget conflicts, exact recipient, '
          'revocation and expiry; original profiles untouched. Rolling back.')
finally:
    env.cr.rollback()
