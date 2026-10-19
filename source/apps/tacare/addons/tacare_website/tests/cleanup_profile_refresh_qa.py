"""Remove only recorded temporary test records; preserve pre-existing profiles and audit."""
import json
from pathlib import Path

assert env.cr.dbname == 'tacare_local'
config = json.loads(Path('/var/lib/odoo/profile_refresh_accounts.json').read_text())
owners = [a['user_id'] for a in config['accounts']]
path = Path('/var/lib/odoo/profile_refresh_qa_records.json')
records = json.loads(path.read_text()) if path.exists() else {}
cap = env['care.profile.capability'].sudo().browse(records.get('capability_id',0)).exists()
if cap:
    assert cap.title.startswith('QA service ') and cap.profile_id.user_id.id in owners and not cap.flex_demo_key
    cap.unlink()
profile = env['tacare.profile'].sudo().browse(records.get('profile_id',0)).exists()
if profile:
    assert profile.profile_title.startswith('QA profile ') and profile.user_id.id in owners and not profile.flex_demo_key
    profile.unlink()
env.cr.commit()
path.write_text('{}')
print('PASS: recorded QA profile and service removed; existing profiles and audit preserved.')
