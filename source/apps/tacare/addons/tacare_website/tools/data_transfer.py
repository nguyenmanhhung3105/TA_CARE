"""Portable, opt-in transfer of the fictional flexible-work demo.

Run only from a trusted Odoo shell. No routes, install hooks or automatic seeds.
The private JSON bundle contains password hashes for NEW portal accounts only.
Only the four approved portal identities are selected in v2. Existing target
credentials are never rewritten. Other accounts, administrators, sessions,
consents, connections, configuration and uploaded documents are excluded.
"""
import base64
import hashlib
import json
import math
import re
from datetime import date, datetime
from pathlib import Path

FORMAT = 'tacare.demo.v2'
LEGACY_FORMAT = 'tacare.demo.v1'
NAMESPACE = 'tacare_transfer'
STATE_KEY = 'tacare.transfer.demo.v1.hashes'
MAX_BYTES = 32 * 1024 * 1024
LEGACY_LOGIN = re.compile(r'(?:demo-flex-(?:0[0-9]|1[0-5])@example\.invalid|ungvien[12]@tacare\.vn)\Z')
LOGIN = re.compile(r'(?:ungvien[12]@tacare\.vn|student\.test@tuhoso\.com|hr\.hozota@khovieclam\.vn)\Z')
KEYS = {
    'hr.job': re.compile(r'(?:recruitment-0[1-5]|flex-job-(?:0[1-9]|1[0-5]))\Z'),
    'tacare.profile': re.compile(r'(?:profile-(?:0[1-9]|1[0-5])|refresh-(?:uv[12]|student)-(?:recruitment|flexible))\Z'),
    'care.profile.capability': re.compile(r'(?:flex-service-(?:0[1-9]|1[0-5])|refresh-uv[12]-flexible)\Z'),
}
FLEX = '''flex_category_id flex_mode flex_region_id flex_location flex_destination
    flex_schedule flex_date_from flex_date_to flex_weekdays flex_time_from flex_time_to
    flex_duration flex_min_hours flex_schedule_note flex_rate_min flex_rate_max
    flex_pay_unit flex_pay_basis flex_cost_note flex_negotiable flex_tools flex_tools_note
    flex_experience flex_portfolio_url flex_image flex_trip_service flex_trip_direction
    flex_passengers flex_vehicle_note flex_skill_ids flex_preferred_skill_ids'''.split()
FIELDS = {
    'hr.job': '''name active care_opportunity_kind tacare_sector care_sector_id care_position
        care_position_id care_region_id care_candidate_requirements care_benefits
        care_training_provided care_skills_any care_salary_display care_salary_basis
        care_salary_tax care_education_note care_language_note care_license_note
        care_schedule_required care_start_flexible care_level care_work_fraction
        care_days_per_week care_duration_months care_shift_note care_income_type
        care_income_period care_requires_travel care_requires_license care_requires_portfolio
        care_requires_clinical tacare_type tacare_mode tacare_location tacare_required_skills
        tacare_preferred_skills tacare_status tacare_start tacare_deadline tacare_schedule
        tacare_pay tacare_outcome tacare_description_text care_experience_min care_salary_min
        care_salary_max care_currency_id care_matching_enabled no_of_recruitment is_published'''.split() + FLEX,
    'tacare.profile': '''name profile_title profile_type education_level_id headline bio education
        sector location goal mode availability pay desired_position_id region_id desired_type
        work_fraction experience_known relevant_months salary_min salary_currency_id salary_period
        salary_tax work_history education_details languages licenses travel start_date visible
        scope status share_contact care_recruitment_enabled'''.split(),
    'care.profile.capability': ['title', 'description', 'currency_id', 'active', 'flex_state'] + FLEX,
    'tacare.profile.skill': '''name level use skill_id skill_level_id years_experience'''.split(),
    'care.job.requirement': ['sequence', 'category', 'name', 'mandatory', 'skill_id'],
}
LEGACY_FIELDS = {model: names[:] for model, names in FIELDS.items()}
FIELDS['hr.job'] += ['description', 'website_description']
FIELDS['tacare.profile'] += ['career_level', 'salary_max', 'salary_negotiable', 'relocation', 'portfolio_url', 'preferred_conditions']
FIELDS.update({
    'tacare.profile.experience': 'sequence organization position employment_type location start_date end_date is_current responsibilities achievements tools'.split(),
    'tacare.profile.education': 'sequence school qualification_id major start_date end_date is_current description'.split(),
    'tacare.profile.evidence': 'title role description result url evidence_type issued_at category_id visibility'.split(),
})
PROFILE_CHILDREN = ('care.profile.capability', 'tacare.profile.skill', 'tacare.profile.experience',
                    'tacare.profile.education', 'tacare.profile.evidence')
MODEL_ORDER = list(FIELDS)


def bundle_fields(bundle):
    return LEGACY_FIELDS if bundle['format'] == LEGACY_FORMAT else FIELDS


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate JSON key')
        result[key] = value
    return result


def load_bundle(path):
    raw = Path(path).read_bytes()
    if len(raw) > MAX_BYTES:
        raise ValueError('Data bundle exceeds 32 MiB')
    data = json.loads(raw, object_pairs_hook=unique_object,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError('Nonfinite JSON')))
    validate_bundle(data)
    return data


def validate_bundle(data):
    if not isinstance(data, dict) or set(data) != {'format', 'accounts', 'records'} or data['format'] not in (FORMAT, LEGACY_FORMAT):
        raise ValueError('Unsupported data bundle format')
    if not isinstance(data['accounts'], list) or not 1 <= len(data['accounts']) <= 18:
        raise ValueError('Expected selected portal accounts')
    allowed_fields = bundle_fields(data)
    login_pattern = LEGACY_LOGIN if data['format'] == LEGACY_FORMAT else LOGIN
    logins, roles = set(), {}
    for account in data['accounts']:
        if not isinstance(account, dict) or set(account) != {'login', 'name', 'role', 'password_hash'}:
            raise ValueError('Invalid account fields')
        login = account['login']
        if not isinstance(login, str) or not login_pattern.fullmatch(login) or login in logins:
            raise ValueError('Account is outside the demo selection or duplicated')
        logins.add(login)
        if account['role'] not in ('business', 'candidate') or not isinstance(account['name'], str) or not account['name'].strip():
            raise ValueError('Invalid portal account')
        roles[login] = account['role']
        password = account['password_hash']
        if not isinstance(password, str) or not re.fullmatch(r'\$pbkdf2-sha512\$[1-9][0-9]{3,6}\$[./A-Za-z0-9]+\$[./A-Za-z0-9]+', password):
            raise ValueError('Only Odoo PBKDF2 password hashes are accepted')
    if not isinstance(data['records'], list) or not data['records'] or len(data['records']) > 500:
        raise ValueError('Invalid record count')
    seen = set()
    for row in data['records']:
        if not isinstance(row, dict) or set(row) != {'model', 'key', 'parent', 'values'}:
            raise ValueError('Invalid record envelope')
        model, key, values = row['model'], row['key'], row['values']
        if model not in allowed_fields or not isinstance(key, str) or not key or len(key) > 250:
            raise ValueError('Unsupported model/key')
        if (model, key) in seen:
            raise ValueError('Duplicate record identity')
        seen.add((model, key))
        if model in KEYS and not KEYS[model].fullmatch(key):
            raise ValueError('Record is outside the demo selection')
        if not isinstance(values, dict) or set(values) != set(allowed_fields[model]):
            raise ValueError('Missing or forbidden fields in data bundle')
        parent = row['parent']
        if not isinstance(parent, str):
            raise ValueError('Invalid parent reference')
        if model in ('hr.job', 'tacare.profile') and parent not in logins:
            raise ValueError('Owner is outside the selected accounts')
        if model == 'tacare.profile' and (values['scope'] != 'private' or values['visible'] is not False or values['share_contact'] is not False):
            raise ValueError('Transferred profiles must remain private')
        if model == 'tacare.profile.evidence' and values['visibility'] != 'private':
            raise ValueError('Transferred evidence must remain private')
        if model == 'hr.job' and values['care_matching_enabled'] is not False:
            raise ValueError('Demo matching must remain disabled')
        if model == 'hr.job':
            if values['care_opportunity_kind'] == 'recruitment' and roles[parent] != 'business':
                raise ValueError('A recruitment publisher must be a business portal account')
            if values['is_published'] != (values['tacare_status'] == 'published'):
                raise ValueError('Public visibility must agree with the job state')
    keys = {model: {key for kind, key in seen if kind == model} for model in FIELDS}
    for row in data['records']:
        if row['model'] in PROFILE_CHILDREN and row['parent'] not in keys['tacare.profile']:
            raise ValueError('Missing parent profile')
        if row['model'] == 'care.job.requirement' and row['parent'] not in keys['hr.job']:
            raise ValueError('Missing parent job')
    # Also rejects NaN/Infinity at every nesting level.
    canonical(data)


def _environment(env):
    if not env.su or env.cr.dbname not in ('tacare_local', 'tacare_prod'):
        raise ValueError('Trusted shell and a TA.CARE database are required')
    return env(context=dict(env.context, lang='vi_VN', active_test=False,
                            tracking_disable=True, mail_create_nosubscribe=True,
                            mail_notrack=True, no_reset_password=True))


def _reference(record):
    if not record:
        return False
    xmlid = record.get_external_id().get(record.id)
    if not xmlid or xmlid.split('.', 1)[0] not in ('base', 'tacare_website', 'hr_recruitment', 'hr_skills'):
        raise ValueError('A selected catalog relation needs a portable XML ID: ' + record._name)
    return {'xmlid': xmlid}


def _pack(record, field_map=None):
    result = {}
    for name in (field_map or FIELDS)[record._name]:
        field, value = record._fields[name], record[name]
        if field.type == 'many2one':
            value = _reference(value)
        elif field.type == 'many2many':
            value = sorted((_reference(item) for item in value), key=lambda item: item['xmlid'])
        elif isinstance(value, (date, datetime)):
            value = value.isoformat()
        elif isinstance(value, bytes):
            value = value.decode('ascii')
        result[name] = value
    return result


def _snapshot(record, field_map=None):
    # A server edit in another website language must also block an overwrite.
    protected = {'tacare.profile': ['verification_level', 'reputation_score'],
                 'tacare.profile.skill': ['verified', 'verified_on'],
                 'tacare.profile.evidence': ['status', 'verified_by', 'verified_at', 'assigned_verifier_id', 'verification_note', 'score']}.get(record._name, [])
    return {'values': _pack(record, field_map), 'protected': {name: str(record[name]) for name in protected}, 'translations': {
        name: record._fields[name]._get_stored_translations(record)
        for name in (field_map or FIELDS)[record._name]
        if record._fields[name].store and record._fields[name].translate}}


def export_demo(env, path):
    """Export current selected demo rows, not seed defaults and never all DB users."""
    env = _environment(env)
    if env.cr.dbname != 'tacare_local':
        raise ValueError('Export is local-only')
    records, owners, parents = [], env['res.users'], {}
    for model in ('hr.job', 'tacare.profile', 'care.profile.capability'):
        selected = env[model].search([('flex_demo_key', '!=', False)], order='id')
        selected = selected.filtered(lambda row: KEYS[model].fullmatch(row.flex_demo_key or ''))
        for record in selected:
            if model == 'care.profile.capability':
                parent = parents.get(('tacare.profile', record.profile_id.id))
                if not parent:
                    raise ValueError('Capability owner/profile is not selected')
            else:
                owner = record.tacare_owner_user_id if model == 'hr.job' else record.user_id
                if not LOGIN.fullmatch(owner.login or '') or owner._is_internal() or not owner.active:
                    raise ValueError('Selected record is not owned by an active demo portal user')
                owners |= owner
                parent = owner.login
            values = _pack(record)
            if model == 'tacare.profile':
                values.update(scope='private', visible=False, share_contact=False)
            if model == 'hr.job':
                values['care_matching_enabled'] = False
            records.append(dict(model=model, key=record.flex_demo_key, parent=parent, values=values))
            parents[(model, record.id)] = record.flex_demo_key
            if model == 'tacare.profile':
                if record.availability_ids or record.service_area_ids or record.preference_ids:
                    raise ValueError('Extended profile children need a separate reviewed transfer; export stopped')
                for skill in record.skill_ids.sorted('id'):
                    records.append(dict(model=skill._name, key=record.flex_demo_key + ':' + skill.name,
                                        parent=record.flex_demo_key, values=_pack(skill)))
                for kind, children in [('experience', record.experience_ids), ('education', record.education_ids), ('evidence', record.evidence_ids)]:
                    for child in children.sorted('id'):
                        if kind == 'evidence' and (child.status != 'unverified' or child.document_ids or child.profile_skill_id or child.issued_by_partner_id or child.supersedes_id or child.assigned_verifier_id or child.verified_by or child.verified_at or child.verification_note or child.score):
                            raise ValueError('Verified/linked/uploaded evidence needs a separate reviewed transfer')
                        child_values = _pack(child)
                        if kind == 'evidence':
                            child_values['visibility'] = 'private'
                        records.append(dict(model=child._name, key=record.flex_demo_key + ':' + kind + ':' + str(child.id),
                                            parent=record.flex_demo_key, values=child_values))
            if model == 'hr.job':
                if record.care_revision_ids:
                    raise ValueError('Reviewed job history needs a separate transfer; export stopped')
                for requirement in record.care_requirement_ids.sorted('id'):
                    records.append(dict(model=requirement._name,
                                        key=record.flex_demo_key + ':' + str(requirement.sequence) + ':' + requirement.name,
                                        parent=record.flex_demo_key, values=_pack(requirement)))
    accounts = []
    for owner in owners.sorted('login'):
        env.cr.execute('SELECT password FROM res_users WHERE id=%s', [owner.id])
        password_hash = env.cr.fetchone()[0]
        accounts.append(dict(login=owner.login, name=owner.name, role=owner.tacare_account_role,
                             password_hash=password_hash))
    bundle = dict(format=FORMAT, accounts=accounts, records=records)
    validate_bundle(bundle)
    target = Path(path)
    # Do not follow or overwrite an existing private file.
    import os
    fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'w', encoding='utf-8') as output:
        output.write(canonical(bundle) + '\n')
    return summary(bundle)


def summary(bundle):
    return {'accounts': len(bundle['accounts']), **{
        model: sum(row['model'] == model for row in bundle['records']) for model in FIELDS}}


def _unpack(env, model, values):
    result = {}
    for name, value in values.items():
        field = env[model]._fields[name]
        if field.type in ('many2one', 'many2many'):
            def resolve(ref):
                if not isinstance(ref, dict) or set(ref) != {'xmlid'} or not isinstance(ref['xmlid'], str):
                    raise ValueError('Invalid catalog reference')
                if ref['xmlid'].split('.', 1)[0] not in ('base', 'tacare_website', 'hr_recruitment', 'hr_skills'):
                    raise ValueError('Unapproved catalog namespace')
                target = env.ref(ref['xmlid'])
                if target._name != field.comodel_name or not target.exists():
                    raise ValueError('Catalog reference has the wrong model')
                return target.id
            if field.type == 'many2one':
                if value is not False and not isinstance(value, dict):
                    raise ValueError('Numeric database IDs are forbidden in bundles')
                value = resolve(value) if value is not False else False
            else:
                if not isinstance(value, list) or len(value) > 100:
                    raise ValueError('Invalid catalog relation list')
                value = [(6, 0, [resolve(item) for item in value])]
        elif field.type == 'boolean':
            if type(value) is not bool:
                raise ValueError('Invalid boolean')
        elif field.type in ('float', 'monetary', 'integer'):
            if type(value) not in (int, float) or not math.isfinite(value):
                raise ValueError('Invalid number')
            if field.type == 'integer' and type(value) is not int:
                raise ValueError('Invalid integer')
        elif value is not False and not isinstance(value, str):
            raise ValueError('Invalid text/date/selection/image')
        if field.type == 'binary' and value:
            if len(value) > 7 * 1024 * 1024:
                raise ValueError('Image exceeds transfer limit')
            base64.b64decode(value, validate=True)
        result[name] = value
    return result


def _mapping(env, model, key):
    name = 'r_' + digest([model, key])
    item = env['ir.model.data'].search([('module', '=', NAMESPACE), ('name', '=', name)])
    if len(item) > 1 or item and item.model != model:
        raise ValueError('Conflicting transfer identity')
    record = env[model].browse(item.res_id).exists() if item else env[model]
    if item and not record:
        raise ValueError('A transferred record was removed on the server; refusing to recreate it')
    return name, record


def _register(env, model, name, record):
    env['ir.model.data'].create(dict(module=NAMESPACE, name=name, model=model,
                                     res_id=record.id, noupdate=True))


def import_bundle(env, path):
    """Atomic caller-owned transaction. Does not commit; the worker commits last."""
    env = _environment(env)
    bundle = load_bundle(path)
    env.cr.execute("SELECT pg_advisory_xact_lock(hashtext('tacare.transfer.demo.v1'))")
    field_map = bundle_fields(bundle)
    company = env.ref('base.main_company')
    websites = env['website'].search([])
    from urllib.parse import urlsplit
    hosts = ('khovieclam.localhost', 'khovieclam.vn') if env.cr.dbname == 'tacare_local' else ('khovieclam.vn',)
    sites = websites.filtered(lambda row: urlsplit(row.domain or '').hostname in hosts)
    if len(sites) != 1:
        raise ValueError('Expected one canonical Kho website in the target environment')
    site = sites[0]
    state_model = env['ir.config_parameter']
    hashes = json.loads(state_model.get_param(STATE_KEY, '{}'))
    users, identities = {}, {}
    created = updated = unchanged = 0
    for account in bundle['accounts']:
        login = account['login']
        name, user = _mapping(env, 'res.users', login)
        if not user:
            collision = env['res.users'].search([('login', '=', login)])
            if collision:
                raise ValueError('An unmapped server account uses a selected login; explicit reconciliation is required')
            user = env['res.users'].create(dict(name=account['name'], login=login, email=login,
                tacare_account_role=account['role'], company_id=company.id,
                company_ids=[(6, 0, company.ids)]))
            if user._is_internal() or user.has_group('base.group_system'):
                raise ValueError('Import must never grant internal/admin access')
            user._set_encrypted_password(user.id, account['password_hash'])
            _register(env, 'res.users', name, user)
        if user.login != login or user._is_internal() or user.has_group('base.group_system') or not user.active:
            raise ValueError('Transferred account no longer has the expected portal identity')
        if user.tacare_account_role != account['role'] or user.company_id != company:
            raise ValueError('Transferred account role/company was changed on the server')
        # Existing user names, passwords, group memberships and MFA are never rewritten.
        users[login] = user
    for model in MODEL_ORDER:
        for row in (item for item in bundle['records'] if item['model'] == model):
            key, parent, values = row['key'], row['parent'], row['values']
            name, record = _mapping(env, model, key)
            decoded = _unpack(env, model, values)
            if model == 'hr.job':
                owner = users[parent]
                fixed = dict(tacare_owner_user_id=owner.id, tacare_owner_partner_id=owner.partner_id.id,
                             website_id=site.id, company_id=company.id, flex_demo_key=key)
            elif model == 'tacare.profile':
                fixed = dict(user_id=users[parent].id, flex_demo_key=key)
            else:
                parent_model = 'hr.job' if model == 'care.job.requirement' else 'tacare.profile'
                fixed = {('job_id' if parent_model == 'hr.job' else 'profile_id'): identities[(parent_model, parent)].id}
                if model == 'care.profile.capability':
                    fixed['flex_demo_key'] = key
            if not record:
                if model in KEYS and env[model].search_count([('flex_demo_key', '=', key)]):
                    raise ValueError('An unmapped server record has a selected demo key')
                record = env[model].create({**decoded, **fixed})
                _register(env, model, name, record)
                created += 1
            else:
                if model == 'hr.job' and record.care_revision_ids:
                    raise ValueError('Server job revision history requires explicit reconciliation')
                for field_name, expected in fixed.items():
                    actual = record[field_name]
                    if record._fields[field_name].type == 'many2one':
                        actual = actual.id
                    if actual != expected:
                        raise ValueError('A transferred record changed owner/company/site; refusing to overwrite')
                current = _pack(record, field_map)
                expected = hashes.get(name)
                snapshot = digest(_snapshot(record, field_map))
                # A v1 hash can be upgraded only if all newly managed fields are still defaults.
                legacy_ok = False
                if bundle['format'] == FORMAT and model in LEGACY_FIELDS and expected != snapshot:
                    extras = set(FIELDS[model]) - set(LEGACY_FIELDS[model])
                    defaults = env[model].default_get(list(extras))
                    legacy_ok = all(record[k] == defaults.get(k, False) for k in extras) and expected == digest(_snapshot(record, LEGACY_FIELDS))
                if expected != snapshot and not legacy_ok:
                    raise ValueError('A transferred record was edited on the server; reconcile before importing')
                if current == values:
                    unchanged += 1
                else:
                    record.write(decoded)
                    updated += 1
            identities[(model, key)] = record
            hashes[name] = digest(_snapshot(record, field_map))
            if model == 'hr.job' and record.tacare_status == 'published' and record._care_publish_errors():
                raise ValueError('An imported job is not publishable')
            if model == 'care.profile.capability' and record.flex_state == 'available' and record._flex_ready_errors():
                raise ValueError('An imported service offer is not ready')
    state_model.set_param(STATE_KEY, canonical(hashes))
    env.flush_all()
    return {**summary(bundle), 'created': created, 'updated': updated, 'unchanged': unchanged}
