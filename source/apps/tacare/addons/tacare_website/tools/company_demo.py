"""Manual, local-only organization of the existing fictional seasonal demo.

No install hook or web route. Preview by default. Passwords for newly created
business demo accounts follow the owner's requested rule and are never logged.
Existing account passwords, profile IDs and provider ownership are preserved.
"""
import hashlib
import re

from odoo import Command


BUSINESSES = (
    ('nhaviet.demo', 'Dịch vụ Nhà Việt · Demo', ('cleaning', 'cooking', 'pets')),
    ('vuonxanh.demo', 'Cảnh quan Vườn Xanh · Demo', ('garden', 'farm')),
    ('tienich.demo', 'Dịch vụ Tiện Ích · Demo', ('loading', 'repair', 'driving')),
    ('sangtao.demo', 'Xưởng Sáng Tạo Số · Demo', ('digital',)),
    ('hoctot.demo', 'Không gian Học Tốt · Demo', ('tutoring',)),
)
LEGACY_ORGS = ('nhaviet.demo', 'sangtao.demo', 'sangtao.demo', 'sangtao.demo',
               'tienich.demo', 'sangtao.demo', 'nhaviet.demo', 'nhaviet.demo',
               'tienich.demo', 'vuonxanh.demo', 'vuonxanh.demo', 'tienich.demo',
               'hoctot.demo', 'sangtao.demo', 'tienich.demo', 'nhaviet.demo')
NAMESPACE = 'tacare_local_demo'


def _identity(env, model, key):
    row = env['ir.model.data'].sudo().search([
        ('module', '=', NAMESPACE), ('name', '=', key)], limit=1)
    if row and row.model != model:
        raise ValueError('Demo mapping has a different model')
    return env[model].sudo().browse(row.res_id).exists() if row else env[model]


def _register(env, record, key):
    env['ir.model.data'].sudo().create({
        'module': NAMESPACE, 'name': key, 'model': record._name,
        'res_id': record.id, 'noupdate': True})


def organize_local_demo(env, apply=False, backup_receipt=None):
    """Arrange five employers, archive legacy logins, retain all demo contacts."""
    if apply:
        raise ValueError('Luồng tổ chức demo cũ đã ngừng; không khôi phục liên hệ không có tài khoản hoạt động.')
    if not env.su or env.cr.dbname != 'tacare_local':
        raise ValueError('This operation is restricted to the trusted local shell')
    env = env(context=dict(env.context, active_test=False, tracking_disable=True,
                          mail_notrack=True, mail_create_nosubscribe=True,
                          no_reset_password=True, lang='vi_VN'))
    sites = {}
    for kind in ('khovieclam', 'tuhoso', 'tacare'):
        site = env['website'].sudo().search([
            ('domain', '=', 'http://%s.localhost:8069' % kind)])
        if len(site) != 1:
            raise ValueError('Expected the three exact local websites')
        sites[kind] = site
    companies = env['res.company'].sudo()
    parent = companies.search([('name', '=', 'TAA')])
    hub = companies.search([('name', '=', 'TACARE'), ('parent_id', '=', parent.id)])
    kho, tu = sites['khovieclam'].company_id, sites['tuhoso'].company_id
    if len(parent) != 1 or len(hub) != 1 or kho == tu or any(
            company.parent_id != parent for company in (kho, tu)):
        raise ValueError('Unexpected company tree; inspect before reorganizing')
    users = env['res.users'].sudo()
    legacy = users.search([('login', '=like', 'demo-flex-%@example.invalid')]).filtered(
        lambda user: re.fullmatch(r'demo-flex-(?:0\d|1[0-5])@example\.invalid', user.login or ''))
    if len(legacy) != 16 or env['tacare.profile'].sudo().search_count([('user_id', 'in', legacy.ids)]):
        raise ValueError('Legacy selection differs or still owns provider profiles')
    profiles = env['tacare.profile'].sudo().search([])
    providers = profiles.mapped('user_id')
    approved = {'ungvien1@tacare.vn', 'ungvien2@tacare.vn', 'student.test@tuhoso.com'}
    if len(profiles) != 3 or set(providers.mapped('login')) != approved:
        raise ValueError('Review provider identities before moving their company')
    jobs = env['hr.job'].sudo().search([('flex_demo_key', '=like', 'flex-job-%')])
    if len(jobs) != 15 or any(job.care_opportunity_kind != 'flexible' for job in jobs):
        raise ValueError('Expected the existing fifteen seasonal demo needs')
    if jobs.mapped('care_revision_ids') or env['tacare.connection'].sudo().search_count([
            ('job_id', 'in', jobs.ids)]) or env['care.match.input'].sudo().search_count([
            ('job_id', 'in', jobs.ids)]) or env['care.match.session'].sudo().search_count([
            ('job_id', 'in', jobs.ids)]):
        raise ValueError('Review linked history before moving demo ownership')
    selection = {category: key for key, _, categories in BUSINESSES for category in categories}
    if any(job.flex_category_id.code not in selection for job in jobs):
        raise ValueError('Unknown demo category')
    plan = {'businesses': len(BUSINESSES), 'retained_legacy_contacts': len(legacy),
            'archived_legacy_logins': len(legacy), 'jobs': len(jobs),
            'profiles': len(profiles), 'offers': len(profiles.mapped('capability_ids')),
            'apply': bool(apply)}
    if not apply:
        return plan
    if not backup_receipt or not backup_receipt.get('verification', {}).get('database_restore') or \
            backup_receipt['verification'].get('missing_attachment_files') != 0:
        raise ValueError('A verified full database and filestore backup is required')
    before_profiles = [(p.id, p.user_id.id, p.capability_ids.ids) for p in profiles]
    env.cr.execute('SELECT id, password FROM res_users ORDER BY id')
    original_passwords = {row[0]: hashlib.sha256((row[1] or '').encode()).hexdigest() for row in env.cr.fetchall()}
    organizations, owners = {}, {}
    for key, name, _ in BUSINESSES:
        mapping = key.replace('.', '_')
        organization = _identity(env, 'res.partner', 'org_' + mapping)
        if not organization:
            organization = env['res.partner'].sudo().create({
                'name': name, 'is_company': True, 'company_id': kho.id,
                'email': key + '@khovieclam.vn', 'care_employer_state': 'active',
                'care_market_scope': 'Dữ liệu doanh nghiệp hư cấu phục vụ minh họa việc thời vụ',
                'care_company_intro': '<p>Doanh nghiệp mẫu hư cấu, đăng nhu cầu theo giờ, ca hoặc công việc; không tuyển dụng nhân viên.</p>'})
            _register(env, organization, 'org_' + mapping)
        account = _identity(env, 'res.users', 'user_' + mapping)
        login = key + '@khovieclam.vn'
        if not account:
            if users.search_count([('login', '=', login)]):
                raise ValueError('Business login exists without the reviewed demo mapping')
            contact = env['res.partner'].sudo().create({
                'name': 'Điều phối ' + name, 'email': login,
                'parent_id': organization.id, 'company_id': kho.id})
            account = users.create({
                'name': contact.name, 'login': login, 'email': login,
                'partner_id': contact.id, 'company_id': kho.id,
                'company_ids': [Command.set(kho.ids)], 'tacare_account_role': 'business',
                'password': login.partition('@')[0], 'active': True})
            _register(env, account, 'user_' + mapping)
        if account._is_internal() or account.has_group('base.group_system') or \
                account.company_id != kho or account.partner_id.parent_id != organization:
            raise ValueError('Existing demo business differs from the expected organization')
        if not env['care.org.member'].sudo().search_count([
                ('company_id', '=', kho.id), ('organization_id', '=', organization.id), ('user_id', '=', account.id)]):
            env['care.org.member'].sudo().create({
                'company_id': kho.id, 'organization_id': organization.id, 'user_id': account.id,
                'role': 'owner', 'state': 'active', 'can_manage_jobs': True, 'can_handle_candidates': True})
        organizations[key], owners[key] = organization, account
    for user in legacy:
        number = int(user.login.split('@')[0].rsplit('-', 1)[1])
        user.write({'active': False, 'tacare_account_role': 'business',
                    'company_id': kho.id, 'company_ids': [Command.set(kho.ids)]})
        user.partner_id.write({
            'name': user.name.replace('Hồ sơ demo', 'Mẫu dịch vụ').replace('Đơn vị tuyển dụng', 'Liên hệ điều phối'),
            'active': True, 'company_id': kho.id, 'parent_id': organizations[LEGACY_ORGS[number]].id})
    env['care.auth.session'].sudo().search([('user_id', 'in', legacy.ids)])._revoke()
    providers.write({'company_id': tu.id, 'company_ids': [Command.set((tu | kho).ids)]})
    providers.mapped('partner_id').write({'company_id': tu.id})
    for job in jobs:
        key = selection[job.flex_category_id.code]
        if job.tacare_owner_user_id.login != 'hr.hozota@khovieclam.vn' and job.tacare_owner_user_id != owners[key]:
            raise ValueError('Demo publisher differs; do not overwrite an unexpected owner')
        job.write({'company_id': kho.id, 'website_id': sites['khovieclam'].id,
                   'tacare_owner_user_id': owners[key].id, 'tacare_owner_partner_id': organizations[key].id})
    hr = users.search([('login', '=', 'hr.hozota@khovieclam.vn')])
    if len(hr) != 1 or hr.company_id != kho:
        raise ValueError('Existing business identity differs')
    hr.partner_id.write({'company_id': kho.id})
    hr.partner_id.commercial_partner_id.write({'company_id': kho.id})
    public_hub = _identity(env, 'res.users', 'public_hub_user')
    if not public_hub:
        public_hub = users.create({
            'name': 'Khách công khai TA.CARE', 'login': 'public-tacare-local-demo',
            'active': True, 'company_id': hub.id, 'company_ids': [Command.set(hub.ids)],
            'group_ids': [Command.set(env.ref('base.group_public').ids)], 'tacare_account_role': 'pending'})
        public_hub.partner_id.write({'company_id': hub.id})
        _register(env, public_hub, 'public_hub_user')
    if not public_hub._is_public() or public_hub.company_id != hub or public_hub._is_internal():
        raise ValueError('Unexpected hub public user')
    for kind, site in sites.items():
        vals = {'care_site_kind': kind}
        if kind == 'tacare':
            vals.update(company_id=hub.id, user_id=public_hub.id)
        site.write(vals)
    env.flush_all()
    env.cr.execute('SELECT id, password FROM res_users ORDER BY id')
    after = {row[0]: hashlib.sha256((row[1] or '').encode()).hexdigest() for row in env.cr.fetchall()}
    if any(after.get(key) != value for key, value in original_passwords.items()):
        raise ValueError('An existing account password changed; rollback required')
    if [(p.id, p.user_id.id, p.capability_ids.ids) for p in profiles] != before_profiles or \
            any(p.company_id != tu for p in profiles) or any(j.company_id != kho for j in jobs):
        raise ValueError('Provider ownership or target company verification failed')
    if any(contact.company_id != kho or not contact.parent_id for contact in legacy.mapped('partner_id')):
        raise ValueError('An old demo contact is still unscoped')
    plan['existing_passwords_preserved'] = True
    plan['company_ids'] = {'parent': parent.id, 'hub': hub.id, 'jobs': kho.id, 'profiles': tu.id}
    return plan
