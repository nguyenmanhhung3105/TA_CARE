"""Remove only explicitly prefixed fictional QA data after HTTP checks."""
from pathlib import Path
assert env.cr.dbname == 'tacare_local'
users=env['res.users'].sudo().with_context(active_test=False).search([('login','=like','qa-refresh-20261021-%')])
assert users
jobs=env['hr.job'].sudo().with_context(active_test=False).search([('tacare_owner_user_id','in',users.ids)])
connections=env['tacare.connection'].sudo().search([('job_id','in',jobs.ids)])
applicants=connections.mapped('applicant_id')
connections.unlink();applicants.unlink()
env['care.job.revision'].sudo().search([('job_id','in',jobs.ids)]).unlink()
jobs.unlink()
env['tacare.profile'].sudo().search([('user_id','in',users.ids)]).unlink()
users.unlink()
env.cr.commit()
p=Path('/var/lib/odoo/refresh_qa.json')
if p.exists(): p.unlink()
print('PASS temporary QA jobs, connections, profiles and accounts removed')
