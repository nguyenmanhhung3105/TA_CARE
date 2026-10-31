"""Synthetic, account-owned records for disposable CI databases only."""
import base64
import hashlib
import json
from pathlib import Path
import secrets

assert env.cr.dbname in ('tacare_ci', 'tacare_ci_upgrade')
assert env.cr._cnx.info.host == '/ci-socket', 'CI fixtures require the private CI socket'
destination = Path('/var/lib/odoo') / (env.cr.dbname + '-fixture.json')
assert not destination.exists(), 'Never reseed an existing fixture'
websites = env['website'].sudo()
sites = {}
for index, site in enumerate(('khovieclam', 'tuhoso', 'tacare')):
    values = {'name': 'CI ' + site, 'domain': 'http://' + site + '.localhost:8069',
              'care_site_kind': site, 'company_id': env.company.id}
    record = websites.search([], order='id', limit=1) if index == 0 else websites.browse()
    if record:
        record.write(values)
    else:
        record = websites.create(values)
    sites[site] = record
env['ir.config_parameter'].sudo().set_param('web.base.url', 'http://tacare.localhost:8069')
env['ir.config_parameter'].sudo().set_param('web.base.url.freeze', 'True')
vnd = env.ref('base.VND')
vnd.active = True
env.company.currency_id = vnd
users = env['res.users'].sudo().with_context(no_reset_password=True, mail_create_nosubscribe=True)
organization = env['res.partner'].sudo().create({'name': 'CI Synthetic Organization', 'is_company': True})
accounts = {}
for kind, role in (('person', 'candidate'), ('other', 'candidate'), ('business', 'business'), ('admin', 'pending')):
    credential = secrets.token_urlsafe(32)
    values = {'name': 'CI ' + kind, 'login': 'ci-' + kind + '@example.invalid',
              'password': credential, 'tacare_account_role': role,
              'company_id': env.company.id, 'company_ids': [(6, 0, env.company.ids)]}
    if kind == 'business':
        values['partner_id'] = env['res.partner'].sudo().create({
            'name': 'CI business', 'parent_id': organization.id}).id
    if kind == 'admin':
        values['group_ids'] = [(6, 0, [env.ref('base.group_user').id, env.ref('base.group_system').id])]
    account = users.create(values)
    accounts[kind] = {'id': account.id, 'login': account.login, 'credential': credential}
users.browse(env.ref('base.user_admin').id).write({'password': secrets.token_urlsafe(40)})
env['care.org.member'].sudo().create({'organization_id': organization.id,
    'user_id': accounts['business']['id'], 'company_id': env.company.id, 'role': 'owner', 'state': 'active'})
profile = env['tacare.profile'].sudo().create({'name': 'CI Synthetic Provider', 'profile_title': 'CI Digital Work',
    'user_id': accounts['person']['id'], 'scope': 'members', 'visible': True})
private_profile = env['tacare.profile'].sudo().create({'name': 'CI Private Profile',
    'profile_title': 'CI Private Profile', 'user_id': accounts['person']['id'], 'scope': 'private', 'visible': False})
category = env['care.capability.category'].sudo().search([('code', '=', 'digital')], limit=1)
assert category
terms = {'flex_mode': 'remote', 'flex_schedule': 'flexible', 'flex_rate_min': 100000,
         'flex_rate_max': 200000, 'flex_pay_unit': 'hour', 'flex_pay_basis': 'person'}
capability = env['care.profile.capability'].sudo().create({**terms, 'profile_id': profile.id,
    'category_id': category.id, 'title': 'CI Digital Service', 'description': 'Synthetic CI work scope.',
    'currency_id': vnd.id, 'flex_state': 'available'})
photo = Path('/mnt/addons/tacare_website/static/src/img/services/digital.webp').read_bytes()
job = env['hr.job'].sudo().create({**terms, 'name': 'CI Public Seasonal Need',
    'flex_category_id': category.id, 'tacare_description_text': 'Synthetic CI need for permission and navigation checks.',
    'tacare_owner_user_id': accounts['business']['id'], 'tacare_owner_partner_id': organization.id,
    'company_id': env.company.id, 'website_id': sites['khovieclam'].id,
    'no_of_recruitment': 2, 'care_matching_enabled': True, 'flex_image': base64.b64encode(photo),
    'tacare_status': 'published', 'is_published': True})
grants = env['care.consent'].sudo().browse()
for purpose in ('discovery', 'matching'):
    grants |= env['care.consent'].sudo().create({'profile_id': profile.id, 'purpose': purpose,
        'recipient_kind': 'organization', 'recipient_partner_id': organization.id,
        'field_scope': ['profile', 'skills'], 'state': 'granted', 'granted_by': accounts['person']['id']})
env['ir.cron'].sudo().search([('active', '=', True)]).write({'active': False})
env['ir.mail_server'].sudo().search([('active', '=', True)]).write({'active': False})
env.flush_all()
env.cr.execute('SELECT id, password FROM res_users WHERE id = ANY(%s) ORDER BY id',
               [[account['id'] for account in accounts.values()]])
identity_digest = hashlib.sha256(json.dumps(env.cr.fetchall()).encode()).hexdigest()
payload = {'accounts': accounts, 'job_id': job.id, 'profile_id': profile.id,
           'private_profile_id': private_profile.id, 'capability_id': capability.id,
           'organization_id': organization.id, 'consent_ids': grants.ids, 'identity_digest': identity_digest,
           'image_digest': hashlib.sha256(base64.b64decode(job.flex_image)).hexdigest()}
destination.write_text(json.dumps(payload))
destination.chmod(0o600)
env.cr.commit()
print('PASS synthetic CI fixture: three sites, account-owned records and exact-organization grants')
