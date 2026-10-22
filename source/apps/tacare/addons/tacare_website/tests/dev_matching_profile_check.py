"""Rollback-only seasonal detail authorization checks; requires the private local QA seed."""
import json
from contextlib import ExitStack
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from werkzeug.exceptions import Forbidden, NotFound
from odoo.addons.tacare_website.controllers.profiles import TacareProfiles

assert env.cr.dbname == 'tacare_local'
qa = json.loads(Path('/var/lib/odoo/seasonal_qa.json').read_text())
users = {a['role']: a['user_id'] for a in qa['accounts']}
controller = TacareProfiles()
modules = ('controllers.shared.routes', 'controllers.flexible_work', 'controllers.profiles',
           'sites.khovieclam.routes', 'sites.tacare.routes')


def detail(role='client'):
    mocked = SimpleNamespace(env=env(user=users[role]))
    with ExitStack() as stack:
        for module in modules:
            stack.enter_context(patch('odoo.addons.tacare_website.' + module + '.request', mocked))
        stack.enter_context(patch.object(controller, '_render', lambda *args, **kw: 'allowed'))
        return controller.matching_profile_detail(qa['client_job_id'], qa['profile_id'])


def denied(exception, role='client'):
    try:
        detail(role)
    except exception:
        return
    raise AssertionError('Expected scoped detail rejection')


class RollbackCase(Exception):
    pass


try:
    detail()
    denied(Forbidden, 'outsider')
    denied(Forbidden, 'provider')
    denied(Forbidden, 'business')
    for purpose in ('matching', 'discovery'):
        try:
            with env.cr.savepoint():
                env['care.consent'].sudo().search([
                    ('profile_id', '=', qa['profile_id']), ('purpose', '=', purpose),
                    ('state', '=', 'granted')]).write({'state': 'revoked'})
                denied(NotFound)
                raise RollbackCase()
        except RollbackCase:
            pass
        env.invalidate_all()
        detail()
    try:
        with env.cr.savepoint():
            env['hr.job'].sudo().browse(qa['client_job_id']).write({'care_matching_enabled': False})
            denied(NotFound)
            raise RollbackCase()
    except RollbackCase:
        pass
    env.invalidate_all()
    detail()
    print('PASS seasonal profile detail: owner authorized; outsider/provider/other business denied; revoked discovery/matching and disabled job reject; rollback only')
finally:
    env.cr.rollback()
