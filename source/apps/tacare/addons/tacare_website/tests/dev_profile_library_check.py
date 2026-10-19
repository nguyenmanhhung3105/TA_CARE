"""Rollback-only checks for multiple profiles, owner isolation and preserved accounts."""
import hashlib
import json
from pathlib import Path
from odoo import fields
from odoo.exceptions import AccessError
from odoo.tools import sql


def check(env):
    assert env.cr.dbname == 'tacare_local'
    data = json.loads(Path('/var/lib/odoo/profile_refresh_accounts.json').read_text())
    logins = [a['login'] for a in data['accounts']]
    env.cr.execute('SELECT id, login, password, active, tacare_account_role FROM res_users WHERE login != ALL(%s) ORDER BY id',[logins])
    assert hashlib.sha256(repr(env.cr.fetchall()).encode()).hexdigest() == data['unchanged_other_accounts_fingerprint']
    profiles = env['tacare.profile'].sudo()
    assert profiles.search_count([]) == data['expected_profile_count']
    assert not sql.constraint_definition(env.cr,'tacare_profile','tacare_profile_unique_user')
    first,second = [env['res.users'].sudo().browse(a['user_id']) for a in data['accounts']]
    own = profiles.search([('user_id','=',first.id)])
    foreign = profiles.search([('user_id','=',second.id)])
    assert len(own) == 2 and len(foreign) == 2
    assert profiles.with_user(first).search([]) == own.sorted(key=lambda p:p.name)
    assert profiles.with_user(second).search([]) == foreign.sorted(key=lambda p:p.name)
    for operation in ('read','write','create'):
        try:
            with env.cr.savepoint():
                if operation == 'read': foreign[:1].with_user(first).read(['bio'])
                elif operation == 'write': own[:1].with_user(first).write({'bio':'illegal'})
                else: profiles.with_user(first).create({'user_id':first.id,'name':'illegal'})
        except AccessError:
            pass
        else: raise AssertionError('Portal operation should be blocked: '+operation)
    a,b = profiles.create([{'user_id':first.id,'name':first.name,'profile_title':'QA rollback profile A'},
                          {'user_id':first.id,'name':first.name,'profile_title':'QA rollback profile B'}])
    env['tacare.profile.skill'].sudo().create({'profile_id':a.id,'name':'Same skill','level':'basic'})
    env['tacare.profile.skill'].sudo().create({'profile_id':b.id,'name':'Same skill','level':'good'})
    assert a.skill_ids.level == 'basic' and b.skill_ids.level == 'good'
    env['care.consent'].sudo().create({'profile_id':a.id,'purpose':'matching','recipient_kind':'public',
        'field_scope':['profile','skills'],'state':'granted','granted_by':first.id,'valid_from':fields.Datetime.now()})
    assert len(a.consent_ids) == 1 and not b.consent_ids
    a.write({'profile_title':'QA rollback edited'})
    assert b.profile_title == 'QA rollback profile B'
    legacy=json.loads(Path('/var/lib/odoo/flexible_demo_accounts.json').read_text())
    assert len(profiles.browse(legacy['profile_ids']).exists()) == 15
    print('PASS multiple-profile ORM: two requested candidates have two profiles each; legacy IDs and other account credentials preserved; owner-only reads and blocked portal writes; per-profile skills/consent independent.')


try:
    check(env)
finally:
    env.cr.rollback()
