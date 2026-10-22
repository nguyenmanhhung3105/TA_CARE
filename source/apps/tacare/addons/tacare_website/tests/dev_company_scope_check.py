"""Local rollback checks after the owner-approved company/demo reorganization."""
from contextlib import ExitStack
from types import SimpleNamespace
from unittest.mock import patch

from odoo import fields
from werkzeug.exceptions import Forbidden, NotFound
from odoo.addons.tacare_website.sites.tacare.examples import TacareExamples
from odoo.addons.tacare_website.tools.company_demo import BUSINESSES, _identity

assert env.cr.dbname == 'tacare_local'
try:
    kho = env['website'].sudo().search([('care_site_kind', '=', 'khovieclam')]).company_id
    tu = env['website'].sudo().search([('care_site_kind', '=', 'tuhoso')]).company_id
    assert kho and tu and kho != tu
    accounts = [_identity(env, 'res.users', 'user_' + key.replace('.', '_')) for key, _, _ in BUSINESSES]
    profiles = env['tacare.profile'].sudo().search([])
    assert len(profiles) == 3 and all(p.company_id == tu for p in profiles)
    assert len(profiles.mapped('capability_ids')) == 12
    for user in accounts:
        assert user.active and not user._is_internal() and user.company_id == kho and user.company_ids == kho
        assert user.tacare_account_role == 'business' and user.login.endswith('@khovieclam.vn')
        env.cr.execute('SELECT password FROM res_users WHERE id=%s', [user.id])
        encrypted = env.cr.fetchone()[0]
        assert user._crypt_context().verify(user.login.partition('@')[0], encrypted)
        assert all(user._tacare_can_access_host(host) for host in ('khovieclam.localhost', 'tacare.localhost'))
        assert not user._tacare_can_access_host('tuhoso.localhost')
        assert not env['tacare.profile'].with_user(user).search([('id', 'in', profiles.ids)])
    legacy = env['res.users'].sudo().with_context(active_test=False).search([
        ('login', '=like', 'demo-flex-%@example.invalid'), ('tacare_account_role', '=', 'business')])
    assert len(legacy) == 16 and not any(legacy.mapped('active'))
    assert all(c.active and c.company_id == kho and c.parent_id for c in legacy.mapped('partner_id'))
    controller = TacareExamples()
    modules = ('controllers.shared.routes', 'controllers.flexible_work', 'controllers.profiles',
               'sites.khovieclam.routes', 'sites.tuhoso.routes', 'sites.tacare.routes')

    def act(user, company):
        stack = ExitStack()
        mocked = SimpleNamespace(env=env(user=user.id, context={**env.context, 'allowed_company_ids': company.ids}),
                                 params={}, httprequest=SimpleNamespace(method='GET'))
        for module in modules:
            stack.enter_context(patch('odoo.addons.tacare_website.' + module + '.request', mocked))
        return stack

    first, second = accounts[:2]
    job = env['hr.job'].sudo().search([('tacare_owner_user_id', '=', first.id)], limit=1)
    other_job = env['hr.job'].sudo().search([('tacare_owner_user_id', '=', second.id)], limit=1)
    with act(first, kho):
        assert controller._flex_own('hr.job', job.id) == job
        try:
            controller._flex_own('hr.job', other_job.id)
        except Forbidden:
            pass
        else:
            raise AssertionError('Business could edit another organization')
        member = first.care_org_member_ids
        member.write({'state': 'suspended'})
        try:
            controller._flex_own('hr.job', job.id)
        except Forbidden:
            pass
        else:
            raise AssertionError('Suspended membership could edit through flexible route')
        member.write({'state': 'active'})
    profile = profiles[0]
    with act(profile.user_id, kho):
        assert controller._my_profile() == profile
        assert controller._editable_profile(profile.id) == profile
        try:
            controller._editable_profile(profiles[1].id)
        except NotFound:
            pass
        else:
            raise AssertionError('Cross-company helper bypassed profile ownership')
    profile.write({'visible': True, 'scope': 'members'})
    consent = env['care.consent'].sudo().create({
        'profile_id': profile.id, 'purpose': 'discovery', 'recipient_kind': 'organization',
        'recipient_partner_id': job.tacare_owner_partner_id.id, 'state': 'granted',
        'field_scope': ['profile'], 'valid_from': fields.Datetime.now(), 'granted_by': profile.user_id.id})
    with act(first, kho):
        assert profile in controller._visible_profiles(job.tacare_owner_partner_id)
    with act(second, kho):
        assert profile not in controller._visible_profiles(other_job.tacare_owner_partner_id)
    consent.write({'state': 'revoked'})
    with act(first, kho):
        assert profile not in controller._visible_profiles(job.tacare_owner_partner_id)
    connection = env['tacare.connection'].sudo().create({
        'type': 'application', 'job_id': job.id, 'profile_id': profile.id,
        'sender_id': profile.user_id.id, 'receiver_id': first.id})
    with act(profile.user_id, tu):
        assert controller._connection(connection.id) == connection
    with act(profiles[1].user_id, tu):
        try:
            controller._connection(connection.id)
        except Forbidden:
            pass
        else:
            raise AssertionError('Outsider accessed cross-company connection')
    print('PASS company scope: five business identities, requested initial password rule, preserved contacts, '
          'private profile ACL, owner isolation, suspended membership denial, explicit owner profile on Kho, '
          'cross-company discovery recipient/revocation and connection participants. Rolling back.')
finally:
    env.cr.rollback()
