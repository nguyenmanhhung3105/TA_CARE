"""Rollback validation, owner isolation and revision checks for detailed recruitment profiles."""
from odoo.exceptions import AccessError, ValidationError


def check(env):
    assert env.cr.dbname == 'tacare_local'
    users=env['res.users'].sudo().with_context(no_reset_password=True)
    a,b=users.create([{'name':'QA profile detail A','login':'qa-profile-detail-a@example.invalid','tacare_account_role':'candidate'},
                     {'name':'QA profile detail B','login':'qa-profile-detail-b@example.invalid','tacare_account_role':'candidate'}])
    profiles=env['tacare.profile'].sudo()
    p,q=profiles.create([{'user_id':a.id,'name':a.name,'profile_title':'QA detailed','care_recruitment_enabled':True,'scope':'private'},
                         {'user_id':b.id,'name':b.name,'profile_title':'QA other','scope':'private'}])
    initial=p.version
    experience=env['tacare.profile.experience'].sudo().create({'profile_id':p.id,'organization':'QA practice group',
        'position':'QA Frontend','start_date':'2025-01-01','end_date':'2025-06-01','responsibilities':'QA duties','achievements':'QA output'})
    education=env['tacare.profile.education'].sudo().create({'profile_id':p.id,'school':'QA learning program',
        'start_date':'2024-09-01','is_current':True,'major':'QA software'})
    assert p.version == initial+2
    assert 'Hiện tại' in education._timeline_label()
    assert experience.with_user(a).read(['organization'])[0]['organization']=='QA practice group'
    for row in (experience,education):
        for operation in ('read','write','create'):
            try:
                with env.cr.savepoint():
                    if operation=='read':row.with_user(b).read(['profile_id'])
                    elif operation=='write':row.with_user(a).write({'end_date':'2025-01-01'})
                    else:env[row._name].with_user(a).create({'profile_id':p.id})
            except AccessError:pass
            else:raise AssertionError('Portal operation was allowed: '+operation)
    for values in ({'end_date':'2024-12-01'}, {'is_current':True}, {'profile_id':q.id}):
        try:
            with env.cr.savepoint():experience.write(values)
        except ValidationError:pass
        else:raise AssertionError('Invalid timeline accepted')
    for values in ({'salary_min':100,'salary_max':50},{'salary_max':float('inf')},
                   {'portfolio_url':'http://example.invalid/profile'},{'portfolio_url':'https://user@example.invalid/profile'}):
        try:
            with env.cr.savepoint():p.write(values)
        except ValidationError:pass
        else:raise AssertionError('Invalid profile preference accepted')
    v=p.version
    p.write({'salary_min':100,'salary_max':150,'portfolio_url':'https://example.invalid/portfolio','preferred_conditions':'QA conditions'})
    assert p.version==v+1
    assert p.salary_max==150 and p.salary_min==100
    v=p.version;experience.write({'achievements':'QA improved output'});assert p.version==v+1
    v=p.version;education.unlink();assert p.version==v+1
    assert experience.profile_id==p and profiles.with_user(a).search([('id','in',(p|q).ids)])==p
    print('PASS detailed profile: timeline dates/current state, non-reparentable children, portal read isolation/direct write denial, salary interval/finite values, HTTPS portfolio, profile version bumps')


try:check(env)
finally:env.cr.rollback()
