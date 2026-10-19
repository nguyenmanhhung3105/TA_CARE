"""Rollback-only checks, including the existing admin with another company selected."""
from types import SimpleNamespace
from unittest.mock import patch

from odoo.addons.tacare_website.controllers import profiles, live, flexible_work
from odoo.addons.tacare_website.controllers.profiles import TacareProfiles
from odoo.addons.tacare_website.controllers.site_context import safe_next


try:
    assert env.cr.dbname == 'tacare_local'
    admin = env['res.users'].sudo().browse(2)
    assert admin.has_group('base.group_system')
    expected = env['tacare.profile'].sudo().search([('company_id', 'in', admin.company_ids.ids)])
    for company in admin.company_ids:
        test_env = env(user=admin, context=dict(env.context, allowed_company_ids=[company.id] +
                       [i for i in admin.company_ids.ids if i != company.id]))
        fake = SimpleNamespace(env=test_env)
        ctrl = TacareProfiles()
        with patch.object(profiles, 'request', fake), patch.object(live, 'request', fake), \
                patch.object(flexible_work, 'request', fake), \
                patch.object(ctrl, '_render', side_effect=lambda template, **values: values):
            result = TacareProfiles.profile_library.__wrapped__(ctrl)
            assert result['scope'] == 'all'
            assert set(result['profiles'].ids) == set(expected.ids)
            result = TacareProfiles.profile_library.__wrapped__(ctrl, scope='mine')
            assert all(p.user_id.id == admin.id for p in result['profiles'])
    for value in ('https://example.invalid/', 'http://[', '//example.invalid/', '/\\example.invalid', '/web/become', '/odoo', '\n/abc'):
        assert safe_next(value) == '/'
    assert safe_next('/tuhoso/profiles?scope=mine') == '/tuhoso/profiles?scope=mine'
    assert safe_next('/en/tacare/matching') == '/en/tacare/matching'
    assert safe_next('/vi/web/become') == '/'
    for role, allowed in [('candidate', {'tuhoso.localhost','tacare.localhost'}),
                          ('business', {'khovieclam.localhost','tacare.localhost'})]:
        user = env['res.users'].sudo().search([('tacare_account_role','=',role),('share','=',True)],limit=1)
        assert user
        for host in ('khovieclam.localhost','tuhoso.localhost','tacare.localhost'):
            assert user._tacare_can_access_host(host) == (host in allowed)
    print('PASS existing admin: all profiles under every allowed active company; owner tab scoped; 2-of-3 role policy; unsafe login returns rejected.')
finally:
    env.cr.rollback()
