"""Manual Odoo LOCAL shell check. Every database change rolls back."""
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
    assert info['accounts'] == 18 and info['hr.job'] == 20 and info['tacare.profile'] == 19
    assert info['care.profile.capability'] == 12 and info['tacare.profile.skill'] == 4
    original = transfer.load_bundle(path)
    assert all(not row['key'] == '61' for row in original['records'])
    # Simulate an empty target selection in THIS transaction, preserving all
    # unrelated records and rolling the original names/keys back in finally.
    users = env['res.users'].sudo().with_context(active_test=False)
    for account in original['accounts']:
        user = users.search([('login', '=', account['login'])])
        assert len(user) == 1
        user.write({'login': 'transfer-qa-' + uuid.uuid4().hex + '@example.invalid'})
    for model in transfer.KEYS:
        keys = [row['key'] for row in original['records'] if row['model'] == model]
        env[model].sudo().with_context(active_test=False).search([('flex_demo_key', 'in', keys)]).write({'flex_demo_key': False})

    first = transfer.import_bundle(env, path)
    assert first['created'] == 55 and first['updated'] == 0, first
    candidate = users.search([('login', '=', 'ungvien1@tacare.vn')])
    assert len(env['tacare.profile'].sudo().search([('user_id', '=', candidate.id)])) == 2
    assert not candidate._is_internal() and not candidate.has_group('base.group_system')
    env.cr.execute('SELECT password FROM res_users WHERE id=%s', [candidate.id])
    imported_password = env.cr.fetchone()[0]
    assert imported_password == next(a['password_hash'] for a in original['accounts'] if a['login'] == candidate.login)
    candidate.write({'password': uuid.uuid4().hex})
    env.cr.execute('SELECT password FROM res_users WHERE id=%s', [candidate.id])
    changed_password = env.cr.fetchone()[0]

    repeated = transfer.import_bundle(env, path)
    assert repeated['created'] == 0 and repeated['updated'] == 0 and repeated['unchanged'] == 55, repeated
    env.cr.execute('SELECT password FROM res_users WHERE id=%s', [candidate.id])
    assert env.cr.fetchone()[0] == changed_password != imported_password

    changed = copy.deepcopy(original)
    job_row = next(row for row in changed['records'] if row['model'] == 'hr.job')
    job_row['values']['name'] += ' · bản cập nhật local'
    put(changed)
    update = transfer.import_bundle(env, path)
    assert update['updated'] == 1 and update['created'] == 0, update

    _, target_job = transfer._mapping(env, 'hr.job', job_row['key'])
    previous_name = target_job.name
    target_job.write({'name': target_job.name + ' · sửa trên server'})
    rejected(changed, 'edited on the server')
    # Reconcile in the test transaction so the remaining rejection cases reach
    # the relevant input checks rather than this intentional content conflict.
    target_job.write({'name': previous_name})

    skill_row = next(row for row in changed['records'] if row['model'] == 'tacare.profile.skill')
    _, target_skill = transfer._mapping(env, 'tacare.profile.skill', skill_row['key'])
    target_skill.write({'verified': True})
    rejected(changed, 'edited on the server')
    target_skill.write({'verified': False})

    bad = copy.deepcopy(changed)
    next(row for row in bad['records'] if row['model'] == 'hr.job')['values']['care_region_id'] = 1
    rejected(bad, 'Numeric database IDs')
    bad = copy.deepcopy(changed)
    bad['accounts'][0]['role'] = 'admin'
    rejected(bad, 'Invalid portal account')
    bad = copy.deepcopy(changed)
    bad['accounts'][0]['login'] = 'admin@example.invalid'
    rejected(bad, 'outside the demo selection')
    bad = copy.deepcopy(changed)
    next(row for row in bad['records'] if row['model'] == 'tacare.profile')['values']['scope'] = 'public'
    rejected(bad, 'remain private')
    bad = copy.deepcopy(changed)
    bad['records'][0]['values']['company_id'] = 99
    rejected(bad, 'forbidden fields')
    bad = copy.deepcopy(changed)
    bad['records'].append(copy.deepcopy(bad['records'][0]))
    rejected(bad, 'Duplicate record identity')

    # An existing unmapped account is never adopted, reset or granted a role.
    mapped_name, _ = transfer._mapping(env, 'res.users', candidate.login)
    with env.cr.savepoint():
        mapping = env['ir.model.data'].sudo().search([('module', '=', transfer.NAMESPACE), ('name', '=', mapped_name)])
        mapping.unlink()
        rejected(changed, 'unmapped server account')
    print('PASS transfer: 18 portal accounts; 20 jobs, 19 demo profiles, 12 offers, 4 skills; '
          'repeat/update, password preservation, conflict and forbidden-input checks. Rolling back.')
finally:
    env.cr.rollback()
    env.invalidate_all()
    path.unlink(missing_ok=True)
assert fingerprint() == before, 'Existing account credentials/roles changed'
for model, count in counts.items():
    assert env[model].sudo().with_context(active_test=False).search_count([]) == count, model
env.cr.rollback()
print('PASS rollback: all original users and record counts preserved.')
