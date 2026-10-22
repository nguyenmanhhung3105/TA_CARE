"""Manual local-only removal after verified DB+filestore backup. No install hook."""
import hashlib
import json
from pathlib import Path

assert env.cr.dbname == 'tacare_local'
assert env['website'].sudo().search_count([('domain','ilike','.localhost')]) == 3
receipt = json.loads(Path('/var/lib/odoo/seasonal_backup_receipt.json').read_text())
assert all(receipt['files'][name]['bytes'] > 0 for name in ('tacare_local.dump','filestore.tar.gz'))
users = env['res.users'].sudo().with_context(active_test=False)
env.cr.execute('SELECT id, login, password, active, tacare_account_role FROM res_users ORDER BY id')
fingerprint = hashlib.sha256(repr(env.cr.fetchall()).encode()).hexdigest()
jobs = env['hr.job'].sudo().with_context(active_test=False).search([('care_opportunity_kind','=','recruitment')])
profiles = env['tacare.profile'].sudo().search([('care_recruitment_enabled','=',True)])
kept_jobs = env['hr.job'].sudo().with_context(active_test=False).search([('care_opportunity_kind','=','flexible')])
kept_profiles = env['tacare.profile'].sudo().search([('care_recruitment_enabled','=',False)])
offers = env['care.profile.capability'].sudo().search([])
kept = (kept_jobs.ids, kept_profiles.ids, [(r.id,r.profile_id.id) for r in offers])
for model,field,ids in [('tacare.connection','job_id',jobs.ids),('tacare.connection','profile_id',profiles.ids),
    ('care.match.session','job_id',jobs.ids),('care.match.session','profile_id',profiles.ids),
    ('care.match.input','job_id',jobs.ids),('care.match.input','profile_id',profiles.ids),
    ('hr.applicant','job_id',jobs.ids),('hr.employee','job_id',jobs.ids),
    ('care.document','profile_id',profiles.ids),('care.ocr.job','profile_id',profiles.ids),
    ('care.profile.capability','profile_id',profiles.ids),('care.job.revision','job_id',jobs.ids)]:
    assert not env[model].sudo().with_context(active_test=False).search_count([(field,'in',ids)]), 'Review linked data before removal: '+model
removed = {'job_ids':jobs.ids, 'profile_ids':profiles.ids}
jobs.unlink()
profiles.unlink()
assert all(env['hr.job'].sudo().with_context(active_test=False).browse(kept[0]).exists())
assert env['tacare.profile'].sudo().browse(kept[1]).exists().ids == kept[1]
assert [(r.id,r.profile_id.id) for r in env['care.profile.capability'].sudo().search([])] == kept[2]
env.cr.execute('SELECT id, login, password, active, tacare_account_role FROM res_users ORDER BY id')
assert fingerprint == hashlib.sha256(repr(env.cr.fetchall()).encode()).hexdigest()
assert not env['hr.job'].sudo().with_context(active_test=False).search_count([('care_opportunity_kind','=','recruitment')])
assert not env['tacare.profile'].sudo().search_count([('care_recruitment_enabled','=',True)])
env.cr.commit()
Path('/var/lib/odoo/seasonal_removal_receipt.json').write_text(json.dumps(removed))
print('PASS removed',len(removed['job_ids']),'recruitment jobs and',len(removed['profile_ids']),'recruitment profiles; all accounts and seasonal data preserved')
