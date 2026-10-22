"""Rollback checks for the seasonal-only scope, account projections and ACLs."""
from odoo.exceptions import ValidationError, AccessError
from unittest.mock import patch
from types import SimpleNamespace
from contextlib import ExitStack
from werkzeug.exceptions import Forbidden
from odoo.addons.tacare_website.sites.tacare.examples import TacareExamples
assert env.cr.dbname=='tacare_local'
try:
    users=env['res.users'].sudo().with_context(no_reset_password=True)
    a,b=users.create([{'name':'QA scope A','login':'qa-seasonal-orm-a@example.invalid','tacare_account_role':'candidate'},
                      {'name':'QA scope B','login':'qa-seasonal-orm-b@example.invalid','tacare_account_role':'candidate'}])
    assert all(a._tacare_can_access_host(h+'.localhost') for h in ('khovieclam','tuhoso','tacare'))
    assert len(a.tacare_allowed_website_ids)==3
    p=env['tacare.profile'].sudo().create({'name':'QA seasonal scope','user_id':a.id})
    assert not p.care_recruitment_enabled
    j=env['hr.job'].sudo().create({'name':'QA seasonal draft','tacare_owner_user_id':a.id,
        'tacare_owner_partner_id':a.partner_id.id,'company_id':a.company_id.id})
    assert j.care_opportunity_kind=='flexible'
    assert env['hr.job'].sudo().with_context(default_care_opportunity_kind='recruitment').create({'name':'QA context default'}).care_opportunity_kind == 'flexible'
    assert not env['tacare.profile'].sudo().with_context(default_care_recruitment_enabled=True).create({'name':'QA context profile','user_id':a.id}).care_recruitment_enabled
    for operation in (lambda:env['hr.job'].sudo().create({'name':'QA blocked','care_opportunity_kind':'recruitment'}),
        lambda:j.write({'care_opportunity_kind':'recruitment'}),
        lambda:env['tacare.profile'].sudo().create({'name':'QA blocked','user_id':a.id,'care_recruitment_enabled':True}),
        lambda:p.write({'care_recruitment_enabled':True})):
        try:
            with env.cr.savepoint():operation()
        except ValidationError:pass
        else:raise AssertionError('Retired recruitment write allowed')
    assert env['hr.job'].with_user(a).search([('id','=',j.id)])==j
    assert not env['hr.job'].with_user(b).search([('id','=',j.id)])
    for actor in (a,b):
        try:
            with env.cr.savepoint():j.with_user(actor).write({'name':'QA forbidden'})
        except AccessError:pass
        else:raise AssertionError('Direct portal job write allowed')
    assert env['tacare.profile'].with_user(a).search([('id','=',p.id)])==p
    assert not env['tacare.profile'].with_user(b).search([('id','=',p.id)])
    org = env['res.partner'].sudo().create({'name':'QA seasonal organization','is_company':True})
    person = env['res.partner'].sudo().create({'name':'QA seasonal member','parent_id':org.id})
    business = users.create({'name':'QA seasonal business','login':'qa-seasonal-orm-biz@example.invalid',
        'partner_id':person.id,'tacare_account_role':'business'})
    member = env['care.org.member'].sudo().create({'organization_id':org.id,'user_id':business.id,
        'role':'viewer','state':'active','can_manage_jobs':True,'can_handle_candidates':False})
    business_job = env['hr.job'].sudo().create({'name':'QA business need',
        'tacare_owner_user_id':business.id,'tacare_owner_partner_id':org.id})
    connection = env['tacare.connection'].sudo().create({'job_id':business_job.id,'profile_id':p.id,
        'type':'application','sender_id':a.id,'receiver_id':business.id})
    controller = TacareExamples()
    mocked = SimpleNamespace(env=env(user=business.id))
    with ExitStack() as stack:
        for module in ('controllers.shared.routes','sites.khovieclam.routes','sites.tacare.routes'):
            stack.enter_context(patch('odoo.addons.tacare_website.'+module+'.request',mocked))
        assert controller._own_job(business_job.id,'manage').id == business_job.id
        for operation in (lambda:controller._own_job(business_job.id,'handle'), lambda:controller._connection(connection.id)):
            try: operation()
            except Forbidden: pass
            else: raise AssertionError('Business ownership bypassed membership capability')
        member.write({'can_handle_candidates':True})
        assert controller._connection(connection.id).id == connection.id
        assert controller._can_respond_connection(connection)
        member.write({'state':'suspended'})
        try: controller._connection(connection.id)
        except Forbidden: pass
        else: raise AssertionError('Suspended organization member retained connection access')
    print('PASS seasonal scope: no recruitment create/write or context-default bypass; personal three-site projection, '
          'owner isolation, portal direct-write denial and business membership capability/suspension checks')
finally:env.cr.rollback()
