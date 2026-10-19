"""Remove only records created by flexible_work_browser_check; retain all seeded demo data."""
import json
from pathlib import Path

assert env.cr.dbname == 'tacare_local'
path = Path('/var/lib/odoo/flexible_qa_records.json')
records = json.loads(path.read_text()) if path.exists() else {}
for key, model, name_field in [('capability_id', 'care.profile.capability', 'title'),
                                ('job_id', 'hr.job', 'name')]:
    record = env[model].sudo().browse(records.get(key, 0)).exists()
    if record:
        assert record[name_field].startswith('QA flexible '), 'Not a QA record'
        assert not record.flex_demo_key, 'Never delete seeded records'
        env['ir.attachment'].sudo().search([('res_model', '=', model), ('res_id', '=', record.id)]).unlink()
        record.unlink()
assert env['hr.job'].sudo().search_count([('flex_demo_key', '!=', False)]) == 20
assert env['tacare.profile'].sudo().search_count([('flex_demo_key', '=like', 'profile-%')]) == 15
assert env['care.profile.capability'].sudo().search_count([('flex_demo_key', '=like', 'flex-service-%')]) == 10
env.cr.commit()
path.write_text('{}')
print('PASS QA cleanup: original demo retained (20 jobs / 15 original profiles / 10 original capabilities); additional user profiles and audit events retained.')
