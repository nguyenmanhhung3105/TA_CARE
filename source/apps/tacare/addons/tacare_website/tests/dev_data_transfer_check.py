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
    assert info['accounts'] == 4 and info['hr.job'] == 20 and info['tacare.profile'] == 6
    assert info['care.profile.capability'] == 12 and info['tacare.profile.skill'] == 11
    assert info['tacare.profile.experience'] == 3 and info['tacare.profile.education'] == 3 and info['tacare.profile.evidence'] == 3
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
    assert first['created'] == 58 and first['updated'] == 0, first
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
    assert repeated['created'] == 0 and repeated['updated'] == 0 and repeated['unchanged'] == 58, repeated
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
    history_row = next(row for row in changed['records'] if row['model'] == 'tacare.profile.experience')
    _, history = transfer._mapping(env, history_row['model'], history_row['key'])
    old_tools = history.tools
    history.write({'tools': 'QA changed on target'})
    rejected(changed, 'edited on the server')
    history.write({'tools': old_tools})
    evidence_row = next(row for row in changed['records'] if row['model'] == 'tacare.profile.evidence')
    _, evidence = transfer._mapping(env, evidence_row['model'], evidence_row['key'])
    assert evidence.visibility == 'private' and evidence.status == 'unverified' and not evidence.document_ids
    evidence.write({'verification_note': 'QA target verification note'})
    rejected(changed, 'edited on the server')
    evidence.write({'verification_note': False})
    bad = copy.deepcopy(changed)
    next(row for row in bad['records'] if row['model'] == 'tacare.profile.evidence')['values']['visibility'] = 'public'
    rejected(bad, 'evidence must remain private')
    bad = copy.deepcopy(changed)
    next(row for row in bad['records'] if row['model'] == 'tacare.profile.experience')['parent'] = 'missing'
    rejected(bad, 'Missing parent profile')
    bad = copy.deepcopy(changed)
    next(row for row in bad['records'] if row['model'] == 'tacare.profile.education')['values']['profile_id'] = 1
    rejected(bad, 'forbidden fields')
    bad = copy.deepcopy(changed)
    next(row for row in bad['records'] if row['model'] == 'tacare.profile')['values']['scope'] = 'public'
    rejected(bad, 'remain private')
    bad = copy.deepcopy(changed)
    bad['records'][0]['values']['company_id'] = 99
    rejected(bad, 'forbidden fields')
    bad = copy.deepcopy(changed)
    bad['records'].append(copy.deepcopy(bad['records'][0]))
    rejected(bad, 'Duplicate record identity')

    # Existing mappings from v1 keep their identities. New fields can be adopted
    # only when they are still defaults; subsequent v1 payloads cannot erase v2.
    source_profile = next(row for row in original['records'] if row['model'] == 'tacare.profile' and row['parent'] == 'ungvien1@tacare.vn' and row['values']['care_recruitment_enabled'])
    legacy = {'format': transfer.LEGACY_FORMAT, 'accounts': [next(a for a in original['accounts'] if a['login'] == source_profile['parent'])],
              'records': [{'model': 'tacare.profile', 'key': 'profile-01', 'parent': source_profile['parent'],
                           'values': {k: source_profile['values'][k] for k in transfer.LEGACY_FIELDS['tacare.profile']}}]}
    put(legacy)
    assert transfer.import_bundle(env, path)['created'] == 1
    upgraded = copy.deepcopy(legacy)
    upgraded['format'] = transfer.FORMAT
    upgraded['records'][0]['values'] = copy.deepcopy(source_profile['values'])
    _, legacy_profile = transfer._mapping(env, 'tacare.profile', 'profile-01')
    legacy_profile.write({'portfolio_url': 'https://example.invalid/server-edit'})
    rejected(upgraded, 'edited on the server')
    legacy_profile.write({'portfolio_url': False})
    put(upgraded)
    assert transfer.import_bundle(env, path)['updated'] == 1
    rejected(legacy, 'edited on the server')
    put(upgraded)
    assert transfer.import_bundle(env, path)['unchanged'] == 1
    # A changed server parent is never silently reassigned to the local owner.
    _, offer = transfer._mapping(env, 'care.profile.capability', next(row['key'] for row in original['records'] if row['model'] == 'care.profile.capability'))
    previous_parent = offer.profile_id
    offer.write({'profile_id': transfer._mapping(env, 'tacare.profile', 'profile-01')[1].id})
    rejected(changed, 'changed owner/company/site')
    offer.write({'profile_id': previous_parent.id})

    # An existing unmapped account is never adopted, reset or granted a role.
    mapped_name, _ = transfer._mapping(env, 'res.users', candidate.login)
    with env.cr.savepoint():
        mapping = env['ir.model.data'].sudo().search([('module', '=', transfer.NAMESPACE), ('name', '=', mapped_name)])
        mapping.unlink()
        rejected(changed, 'unmapped server account')
    print('PASS transfer v2: 4 portal accounts; 20 jobs, 6 profiles, 12 offers, 11 skills, 3 experience/education/evidence each; '
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
