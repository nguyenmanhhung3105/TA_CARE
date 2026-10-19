"""Create one temporary local MFA test account; secrets remain in ignored runtime."""
import base64
import json
import os
import secrets
from pathlib import Path

assert env.cr.dbname == 'tacare_local'
path = Path('/var/lib/odoo/sso_mfa_qa.json')
assert not path.exists(), 'Clean the previous MFA QA account first.'
login = 'qa-sso-' + secrets.token_hex(8) + '@example.invalid'
password = secrets.token_urlsafe(24)
secret = base64.b32encode(secrets.token_bytes(20)).decode()
user = env['res.users'].sudo().with_context(no_reset_password=True).create({
    'name': 'QA SSO MFA temporary', 'login': login, 'password': password,
    'tacare_account_role': 'candidate', 'totp_secret': secret,
})
assert user.totp_enabled
with path.open('x') as out:
    os.chmod(path, 0o600)
    json.dump({'user_id':user.id, 'partner_id':user.partner_id.id,
               'login':login, 'password':password, 'totp_secret':secret}, out)
env.cr.commit()
print('Created one temporary MFA QA account; no credential output.')
