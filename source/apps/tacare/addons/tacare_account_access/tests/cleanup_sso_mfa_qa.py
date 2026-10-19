"""Delete only the recorded temporary MFA fixture, never existing users."""
import json
from pathlib import Path

assert env.cr.dbname == 'tacare_local'
path = Path('/var/lib/odoo/sso_mfa_qa.json')
data = json.loads(path.read_text())
user = env['res.users'].sudo().browse(data['user_id']).exists()
assert user and user.login == data['login'] and user.login.startswith('qa-sso-')
assert user.name == 'QA SSO MFA temporary'
profiles = env['tacare.profile'].sudo().search([('user_id','=',user.id)])
assert not profiles
partner = user.partner_id
assert partner.id == data['partner_id']
user.unlink()
partner.unlink()
env.cr.commit()
path.unlink()
print('Removed temporary MFA QA account and its contact; original accounts untouched.')
