"""Manual LOCAL seasonal bundle checks; all mutations roll back, no release made."""
import copy
import hashlib
import json
from pathlib import Path
import uuid

from odoo.addons.tacare_website.tools import data_transfer as transfer

assert env.cr.dbname == 'tacare_local'
path = Path('/var/lib/odoo') / ('transfer-qa-' + uuid.uuid4().hex + '.json')


def fingerprint():
    env.cr.execute('SELECT id, login, password, active, tacare_account_role, company_id FROM res_users ORDER BY id')
    return hashlib.sha256(repr(env.cr.fetchall()).encode()).hexdigest()


def put(bundle):
    path.write_text(transfer.canonical(bundle))


def rejected(bundle, fragment):
    put(bundle)
    try:
        with env.cr.savepoint():
            transfer.import_bundle(env, path)
    except ValueError as exc:
        assert fragment in str(exc), (fragment, type(exc).__name__)
    else:
        raise AssertionError('Invalid bundle unexpectedly imported')


before = fingerprint()
counts = {model: env[model].sudo().with_context(active_test=False).search_count([])
          for model in ('res.users', *transfer.FIELDS)}
try:
    info = transfer.export_demo(env, path)
    assert info['accounts'] == 4 and info['hr.job'] == 15 and info['tacare.profile'] == 3
    assert info['care.profile.capability'] == 12
    assert all(info[m] == 0 for m in ('tacare.profile.skill', 'care.job.requirement',
        'tacare.profile.experience', 'tacare.profile.education', 'tacare.profile.evidence'))
    original = transfer.load_bundle(path)
    record_count = len(original['records'])
    assert record_count == 30
    assert all(r['values']['care_opportunity_kind'] == 'flexible' for r in original['records'] if r['model'] == 'hr.job')
    assert all(not r['values']['care_recruitment_enabled'] and r['values']['scope'] == 'private' and
        not r['values']['visible'] for r in original['records'] if r['model'] == 'tacare.profile')
    for model, field, value in [('hr.job', 'care_opportunity_kind', 'recruitment'),
                               ('tacare.profile', 'care_recruitment_enabled', True)]:
        bad = copy.deepcopy(original)
        next(r for r in bad['records'] if r['model'] == model)['values'][field] = value
        rejected(bad, 'seasonal')

    # Simulate a new target selection only within this rollback transaction.
    users = env['res.users'].sudo().with_context(active_test=False)
    for account in original['accounts']:
        user = users.search([('login', '=', account['login'])])
        assert len(user) == 1
        user.write({'login': 'transfer-qa-' + uuid.uuid4().hex + '@example.invalid'})
    for model in transfer.KEYS:
        keys = [r['key'] for r in original['records'] if r['model'] == model]
        env[model].sudo().with_context(active_test=False).search([('flex_demo_key', 'in', keys)]).write({'flex_demo_key': False})
    put(original)
    first = transfer.import_bundle(env, path)
    assert first['created'] == record_count and first['updated'] == 0
    candidate = users.search([('login', '=', 'ungvien1@tacare.vn')])
    assert len(env['tacare.profile'].sudo().search([('user_id', '=', candidate.id)])) == 1
    assert not candidate._is_internal() and not candidate.has_group('base.group_system')
    env.cr.execute('SELECT password FROM res_users WHERE id=%s', [candidate.id])
    imported_password = env.cr.fetchone()[0]
    assert imported_password == next(a['password_hash'] for a in original['accounts'] if a['login'] == candidate.login)
    candidate.write({'password': uuid.uuid4().hex})
    env.cr.execute('SELECT password FROM res_users WHERE id=%s', [candidate.id])
    changed_password = env.cr.fetchone()[0]
    repeated = transfer.import_bundle(env, path)
    assert repeated['unchanged'] == record_count and repeated['created'] == repeated['updated'] == 0
    env.cr.execute('SELECT password FROM res_users WHERE id=%s', [candidate.id])
    assert env.cr.fetchone()[0] == changed_password != imported_password

    changed = copy.deepcopy(original)
    job_row = next(r for r in changed['records'] if r['model'] == 'hr.job')
    job_row['values']['name'] += ' · bản cập nhật local'
    put(changed)
    update = transfer.import_bundle(env, path)
    assert update['updated'] == 1 and update['created'] == 0
    _, job = transfer._mapping(env, 'hr.job', job_row['key'])
    name = job.name
    job.write({'name': name + ' · sửa trên server'})
    rejected(changed, 'edited on the server')
    job.write({'name': name})
    for mutation, fragment in [
        (lambda b: next(r for r in b['records'] if r['model'] == 'hr.job')['values'].update(care_region_id=1), 'Numeric database IDs'),
        (lambda b: b['accounts'][0].update(role='admin'), 'Invalid portal account'),
        (lambda b: b['accounts'][0].update(login='admin@example.invalid'), 'outside the demo selection'),
        (lambda b: next(r for r in b['records'] if r['model'] == 'tacare.profile')['values'].update(scope='public'), 'remain private'),
        (lambda b: b['records'][0]['values'].update(company_id=99), 'forbidden fields'),
        (lambda b: b['records'].append(copy.deepcopy(b['records'][0])), 'Duplicate record identity')]:
        bad = copy.deepcopy(changed)
        mutation(bad)
        rejected(bad, fragment)
    _, offer = transfer._mapping(env, 'care.profile.capability', next(r['key'] for r in original['records'] if r['model'] == 'care.profile.capability'))
    parent = offer.profile_id
    foreign = env['tacare.profile'].sudo().search([('id', '!=', parent.id)], limit=1)
    offer.write({'profile_id': foreign.id})
    rejected(changed, 'changed owner/company/site')
    offer.write({'profile_id': parent.id})
    mapped_name, _ = transfer._mapping(env, 'res.users', candidate.login)
    with env.cr.savepoint():
        env['ir.model.data'].sudo().search([('module', '=', transfer.NAMESPACE), ('name', '=', mapped_name)]).unlink()
        rejected(changed, 'unmapped server account')
    print('PASS seasonal v2 transfer: 4 accounts, 15 jobs, 3 private profiles, 12 offers; '
          'recruitment rejection, repeat/update, password preservation, conflicts and forbidden-input checks. Rolling back.')
finally:
    env.cr.rollback()
    env.invalidate_all()
    path.unlink(missing_ok=True)
assert fingerprint() == before
for model, count in counts.items():
    assert env[model].sudo().with_context(active_test=False).search_count([]) == count, model
env.cr.rollback()
print('PASS rollback: all original users and record counts preserved.')
