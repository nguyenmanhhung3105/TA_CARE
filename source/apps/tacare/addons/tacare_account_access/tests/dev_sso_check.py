"""Rollback-only session lifecycle and direct-ACL checks."""
from datetime import timedelta
from odoo import fields
from odoo.exceptions import AccessError

try:
    assert env.cr.dbname == 'tacare_local'
    user = env['res.users'].sudo().search([('login','=','ungvien1@tacare.vn')],limit=1)
    sessions = env['care.auth.session']
    family = sessions._start_for(user)
    assert family._valid_for(user.id)
    assert not family._valid_for(env.user.id)
    for model in ('care.auth.session','care.auth.handoff'):
        for operation in ('read','create','write'):
            try:
                with env.cr.savepoint():
                    portal = env[model].with_user(user)
                    if operation == 'read': portal.search([]).read()
                    elif operation == 'create': portal.create({})
                    else: portal.check_access('write')
            except AccessError:
                pass
            else:
                raise AssertionError('Portal direct SSO access allowed: '+model+' '+operation)
    family.write({'expires_at':fields.Datetime.now()-timedelta(seconds=1)})
    assert not family._valid_for(user.id)
    family.write({'expires_at':fields.Datetime.now()+timedelta(minutes=1)})
    family._revoke()
    assert not family._valid_for(user.id)
    print('PASS SSO ORM: session owner, expiry, revocation and blocked portal access to session/handoff records.')
finally:
    env.cr.rollback()
