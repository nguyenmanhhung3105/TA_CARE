"""Temporary fictional local HTTP QA accounts; secrets only in ignored runtime."""
import json
import secrets
from pathlib import Path
from odoo import fields

assert env.cr.dbname == 'tacare_local'
users = env['res.users'].sudo().with_context(no_reset_password=True, mail_create_nosubscribe=True)
assert not users.search_count([('login', '=like', 'qa-refresh-20261021-%')]), 'Clean previous QA first'
data = {'accounts': []}
for role in ('business', 'candidate', 'other', 'admin'):
    login = 'qa-refresh-20261021-%s@example.invalid' % role
    password = secrets.token_urlsafe(25)
    user = users.create({'name': 'QA hư cấu ' + role, 'login': login, 'password': password,
        'tacare_account_role': 'business' if role == 'business' else 'pending' if role == 'admin' else 'candidate',
        'company_id': env.company.id, 'company_ids': [(6, 0, [env.company.id])]})
    if role == 'admin':
        user.write({'group_ids': [(6, 0, [env.ref('base.group_user').id, env.ref('base.group_system').id])]})
    if role == 'business':
        user.partner_id.write({'is_company': True})
        business = user
    data['accounts'].append({'role': role, 'login': login, 'password': password, 'user_id': user.id})
candidate = users.browse(data['accounts'][1]['user_id'])
profile = env['tacare.profile'].sudo().create({'user_id': candidate.id, 'name': 'QA người nhận việc',
    'profile_title': 'QA dọn nhà', 'care_recruitment_enabled': False, 'visible': True, 'scope': 'members'})
second = env['tacare.profile'].sudo().create({'user_id': candidate.id, 'name': 'QA người ứng tuyển',
    'profile_title': 'QA Frontend', 'care_recruitment_enabled': True, 'visible': True, 'scope': 'members',
    'mode': 'hybrid', 'desired_type': 'employment'})
for p in (profile, second):
    for purpose in ('discovery', 'matching'):
        env['care.consent'].sudo().create({'profile_id': p.id, 'purpose': purpose,
            'recipient_kind': 'members', 'field_scope': ['profile', 'skills', 'evidence'],
            'state': 'granted', 'granted_by': candidate.id, 'valid_from': fields.Datetime.now()})
source = env['hr.job'].sudo().search([('flex_demo_key', '=', 'flex-job-01')])
job = source.copy({'name': 'QA dọn căn hộ', 'flex_demo_key': False,
    'tacare_owner_user_id': business.id, 'tacare_owner_partner_id': business.partner_id.id,
    'flex_rate_min': 100000, 'flex_rate_max': 100000, 'flex_schedule': 'flexible',
    'flex_date_from': False, 'flex_date_to': False, 'flex_time_from': False, 'flex_time_to': False,
    'care_matching_enabled': True, 'tacare_status': 'published', 'is_published': True})
cap = env['care.profile.capability'].sudo().create({'profile_id': profile.id, 'title': 'QA nhận dọn căn hộ',
    'description': 'Dữ liệu QA hư cấu: lau sàn, bếp và nhà tắm.',
    'flex_category_id': job.flex_category_id.id, 'flex_mode': 'onsite',
    'flex_region_id': job.flex_region_id.id, 'flex_location': 'TP.HCM', 'flex_schedule': 'flexible',
    'flex_rate_min': 70000, 'flex_pay_unit': 'hour', 'flex_pay_basis': 'person',
    'currency_id': env.ref('base.VND').id, 'flex_state': 'available',
    'flex_skill_ids': [(6, 0, job.flex_skill_ids.ids)]})
rec = env['hr.job'].sudo().search([('flex_demo_key', '=', 'recruitment-01')]).copy({
    'name': 'QA Frontend', 'flex_demo_key': False, 'tacare_owner_user_id': business.id,
    'tacare_owner_partner_id': business.partner_id.id, 'care_matching_enabled': True,
    'tacare_status': 'published', 'is_published': True})
disposable_profile = env['tacare.profile'].sudo().create({'user_id': data['accounts'][2]['user_id'],
    'name': 'QA hồ sơ có thể xóa', 'profile_title': 'QA hồ sơ có thể xóa', 'scope': 'private', 'visible': False})
disposable_caps = env['care.profile.capability'].sudo().create([{'profile_id': disposable_profile.id,
    'title': 'QA công việc xóa %s' % i, 'category_id': cap.category_id.id} for i in (1,2)])
disposable_job = job.copy({'name': 'QA tin có thể xóa', 'tacare_owner_user_id': business.id,
    'tacare_owner_partner_id': business.partner_id.id})
data.update(delete_profile_id=disposable_profile.id, delete_cap_id=disposable_caps[0].id,
    delete_job_id=disposable_job.id)
data.update(profile_id=profile.id, recruitment_profile_id=second.id, cap_id=cap.id, job_id=job.id, recruitment_job_id=rec.id)
p=Path('/var/lib/odoo/refresh_qa.json');p.write_text(json.dumps(data));p.chmod(0o600)
env.cr.commit()
print('PASS temporary fictional QA records created; credentials stored privately in runtime')
