"""Rollback-only homepage suggestion policy checks, using the private local QA seed."""
import json
from contextlib import ExitStack
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from werkzeug.exceptions import Forbidden
from odoo.addons.tacare_website.sites.tacare.examples import TacareExamples

assert env.cr.dbname == 'tacare_local'
qa = json.loads(Path('/var/lib/odoo/seasonal_qa.json').read_text())
users = {a['role']: a['user_id'] for a in qa['accounts']}
modules = ('controllers.shared.routes', 'controllers.flexible_work', 'controllers.profiles',
           'sites.khovieclam.routes', 'sites.tuhoso.routes', 'sites.tacare.routes', 'sites.tacare.examples')


def home(role):
    uid = env.ref('base.public_user').id if role == 'guest' else users[role]
    mocked = SimpleNamespace(env=env(user=uid), params={}, httprequest=SimpleNamespace(method='GET'))
    with ExitStack() as stack:
        for module in modules:
            stack.enter_context(patch('odoo.addons.tacare_website.' + module + '.request', mocked))
        return TacareExamples()._home_suggestions()


class RollbackCase(Exception):
    pass


try:
    client, provider, business, outsider = [home(role) for role in ('client', 'provider', 'business', 'outsider')]
    assert qa['client_job_id'] in client['jobs'].ids
    assert all(j.tacare_owner_user_id.id == users['client'] for j in client['jobs'])
    assert any(p.id == qa['profile_id'] for p, reason in client['hire'])
    assert {j.id for j, reason in provider['receive']} >= {qa['client_job_id'], qa['business_job_id']}
    assert qa['business_job_id'] in business['jobs'].ids
    assert all(j.tacare_owner_user_id.id == users['business'] for j in business['jobs'])
    assert not business['can_receive'] and not business['profile'] and not business['receive']
    assert not outsider['jobs'] and not outsider['hire'] and not outsider['profile'] and not outsider['receive']
    try:
        home('guest')
    except Forbidden:
        pass
    else:
        raise AssertionError('Guest cannot load personalized suggestions')
    for purpose in ('matching', 'discovery'):
        try:
            with env.cr.savepoint():
                env['care.consent'].sudo().search([
                    ('profile_id', '=', qa['profile_id']), ('purpose', '=', purpose),
                    ('state', '=', 'granted')]).write({'state': 'revoked'})
                assert not any(p.id == qa['profile_id'] for p, reason in home('client')['hire'])
                if purpose == 'matching':
                    assert not home('provider')['receive']
                raise RollbackCase()
        except RollbackCase:
            pass
        env.invalidate_all()
    try:
        with env.cr.savepoint():
            env['hr.job'].sudo().browse(qa['client_job_id']).write({'care_matching_enabled': False})
            assert qa['client_job_id'] not in home('client')['jobs'].ids
            raise RollbackCase()
    except RollbackCase:
        pass
    env.invalidate_all()
    assert any(p.id == qa['profile_id'] for p, reason in home('client')['hire'])
    print('PASS homepage policy: owner/job and organization scoping, individual receive suggestions, business restriction, guest/outsider isolation, current discovery/matching consent and disabled job; rollback only')
finally:
    env.cr.rollback()
