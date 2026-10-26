"""Remove only fictional seasonal QA actors and their dependent records locally."""
from pathlib import Path
import json
assert env.cr.dbname == 'tacare_local'
users = env['res.users'].sudo().with_context(active_test=False).search([('login', '=like', 'qa-seasonal-%@example.invalid')])
assert users
jobs = env['hr.job'].sudo().with_context(active_test=False).search([('tacare_owner_user_id', 'in', users.ids)])
profiles = env['tacare.profile'].sudo().with_context(active_test=False).search([('user_id', 'in', users.ids)])
assert not jobs.filtered('flex_demo_key') and not profiles.filtered('flex_demo_key')
parts = env['care.work.participation'].sudo().search([('job_id', 'in', jobs.ids)])
reviews = env['care.feedback'].sudo().search([('participation_id', 'in', parts.ids)])
orders = env['care.work.order'].sudo().search([('job_id', 'in', jobs.ids)])
assert all(p.provider_user_id in users and p.profile_id.user_id in users for p in parts)
assert all(r.author_user_id in users for r in reviews)
assert all(p in parts for p in orders.participation_ids)
# Teardown only these verified, fictional local fixture rows. The production
# model keeps transaction reviews immutable and retains audit events.
env.flush_all()
env.cr.execute('DELETE FROM care_feedback WHERE id=ANY(%s)', [reviews.ids])
env.cr.execute('DELETE FROM care_work_participation WHERE id=ANY(%s)', [parts.ids])
env.cr.execute('DELETE FROM care_work_order WHERE id=ANY(%s)', [orders.ids])
env.invalidate_all()
env['tacare.connection'].sudo().search(['|', ('job_id', 'in', jobs.ids), ('profile_id', 'in', profiles.ids)]).unlink()
env['care.job.revision'].sudo().search([('job_id', 'in', jobs.ids)]).unlink()
jobs.unlink()
profiles.unlink()
users.unlink()
# Deleting res.users retains its delegated contact in Odoo. Keep that audit
# reference, but archive only our now-orphaned seasonal QA contacts so they do
# not accumulate in the operating contact directory.
qa_contacts = env['res.partner'].sudo().with_context(active_test=False).search([
    ('email', '=like', 'qa-seasonal-%@example.invalid'), ('user_ids', '=', False)])
qa_contacts.write({'active': False})
baseline = json.loads(Path('/var/lib/odoo/seasonal_qa.json').read_text()).get('baseline')
if baseline:
    assert set(env['hr.job'].sudo().search([('care_opportunity_kind','=','flexible')]).ids) == set(baseline['jobs'])
    assert set(env['tacare.profile'].sudo().search([]).ids) == set(baseline['profiles'])
    assert set(env['care.profile.capability'].sudo().search([]).ids) == set(baseline['offers'])
else:  # Earlier private QA receipts, before the matching-demo expansion.
    assert env['hr.job'].sudo().search_count([('care_opportunity_kind', '=', 'flexible')]) == 15
    assert env['tacare.profile'].sudo().search_count([]) == 3
    assert env['care.profile.capability'].sudo().search_count([]) == 12
env.cr.commit()
Path('/var/lib/odoo/seasonal_qa.json').unlink(missing_ok=True)
print('PASS seasonal QA cleanup; baseline jobs/profiles/offers preserved; test reviews removed; audit retained')
