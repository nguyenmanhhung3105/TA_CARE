"""Remove only fictional seasonal QA actors and their dependent records locally."""
from pathlib import Path
assert env.cr.dbname == 'tacare_local'
users = env['res.users'].sudo().with_context(active_test=False).search([('login', '=like', 'qa-seasonal-%@example.invalid')])
assert users
jobs = env['hr.job'].sudo().with_context(active_test=False).search([('tacare_owner_user_id', 'in', users.ids)])
profiles = env['tacare.profile'].sudo().with_context(active_test=False).search([('user_id', 'in', users.ids)])
assert not jobs.filtered('flex_demo_key') and not profiles.filtered('flex_demo_key')
env['tacare.connection'].sudo().search(['|', ('job_id', 'in', jobs.ids), ('profile_id', 'in', profiles.ids)]).unlink()
env['care.job.revision'].sudo().search([('job_id', 'in', jobs.ids)]).unlink()
jobs.unlink()
profiles.unlink()
users.unlink()
assert env['hr.job'].sudo().search_count([('care_opportunity_kind', '=', 'flexible')]) == 15
assert env['tacare.profile'].sudo().search_count([]) == 3
assert env['care.profile.capability'].sudo().search_count([]) == 12
env.cr.commit()
Path('/var/lib/odoo/seasonal_qa.json').unlink(missing_ok=True)
print('PASS seasonal QA cleanup; original 15 jobs, 3 profiles, 12 offers preserved; audit retained')
