"""Temporary fictional local actors for the seasonal-only HTTP checks."""
import json, os, secrets
from pathlib import Path
from odoo import fields
assert env.cr.dbname == 'tacare_local'
assert not env['res.users'].sudo().with_context(active_test=False).search_count([('login','=like','qa-seasonal-%@example.invalid')])
data={'accounts':[]}
job_company=env['website'].sudo().search([('domain','ilike','khovieclam.localhost')],limit=1).company_id
profile_company=env['website'].sudo().search([('domain','ilike','tuhoso.localhost')],limit=1).company_id
assert job_company and profile_company and job_company != profile_company
for role in ('client','provider','outsider','business','admin'):
    password=secrets.token_urlsafe(28)
    user=env['res.users'].sudo().with_context(no_reset_password=True).create({'name':'QA hư cấu '+role,
        'login':'qa-seasonal-'+role+'@example.invalid','email':'qa-seasonal-'+role+'@example.invalid',
        'password':password,'tacare_account_role':'business' if role=='business' else 'pending' if role=='admin' else 'candidate',
        'company_id':job_company.id if role=='business' else profile_company.id,
        'company_ids':[(6,0,env['res.company'].sudo().search([]).ids if role=='admin' else
            job_company.ids if role=='business' else (profile_company|job_company).ids)]})
    if role=='admin':user.write({'group_ids':[(6,0,[env.ref('base.group_user').id,env.ref('base.group_system').id])]})
    data['accounts'].append({'role':role,'login':user.login,'password':password,'user_id':user.id})
users={a['role']:env['res.users'].sudo().browse(a['user_id']) for a in data['accounts']}
category=env['care.capability.category'].sudo().search([('code','=','cleaning')],limit=1)
region=env['res.country.state'].sudo().search([('country_id.code','=','VN'),('name','ilike','Hồ Chí Minh')],limit=1)
site=env['website'].sudo().search([('domain','ilike','khovieclam.localhost')],limit=1)
common={'flex_category_id':category.id,'flex_mode':'onsite','flex_region_id':region.id,
        'flex_location':'QA khu vực hư cấu','flex_rate_min':100000,'flex_rate_max':120000,'flex_pay_unit':'hour',
        'flex_pay_basis':'person','flex_schedule':'flexible','flex_tools':'client'}
profile=env['tacare.profile'].sudo().create({'user_id':users['provider'].id,'name':'QA người nhận làm',
    'profile_title':'QA dọn nhà thời vụ','care_recruitment_enabled':False,'scope':'members','visible':True})
client_profile=env['tacare.profile'].sudo().create({'user_id':users['client'].id,'name':'QA cá nhân cần người',
    'profile_title':'QA hồ sơ riêng','care_recruitment_enabled':False,'scope':'private','visible':False})
offer=env['care.profile.capability'].sudo().create({**common,'profile_id':profile.id,
    'title':'QA nhận dọn nhà','description':'QA dữ liệu hư cấu: lau sàn và vệ sinh bếp.',
    'currency_id':env.ref('base.VND').id,'flex_state':'available'})
for purpose in ('discovery','matching'):
    env['care.consent'].sudo().create({'profile_id':profile.id,'purpose':purpose,'recipient_kind':'members',
        'field_scope':['profile','skills','evidence'],'state':'granted','granted_by':users['provider'].id,
        'valid_from':fields.Datetime.now()})
jobs=[]
for role in ('client','business'):
    user=users[role]
    job=env['hr.job'].sudo().create({**common,'name':'QA nhu cầu '+role,
        'tacare_description_text':'QA dữ liệu hư cấu: cần lau sàn và vệ sinh bếp trong ba giờ.',
        'care_opportunity_kind':'flexible','tacare_owner_user_id':user.id,
        'tacare_owner_partner_id':user.partner_id.commercial_partner_id.id,'website_id':site.id,
        'company_id':job_company.id,'tacare_status':'published','is_published':True,
        'care_matching_enabled':True,'no_of_recruitment':1})
    assert not job._care_publish_errors()
    jobs.append(job)
data.update(profile_id=profile.id,client_profile_id=client_profile.id,client_job_id=jobs[0].id,
            business_job_id=jobs[1].id,category_id=category.id,region_id=region.id)
p=Path('/var/lib/odoo/seasonal_qa.json');p.write_text(json.dumps(data));os.chmod(p,0o600)
env.cr.commit()
print('PASS seasonal QA created: only fictional local accounts, jobs and profiles; credentials private')
