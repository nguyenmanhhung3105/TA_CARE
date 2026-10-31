"""Local ORM checks. Every temporary provider/token change is rolled back."""
from odoo.exceptions import ValidationError

assert env.cr.dbname == 'tacare_local'
try:
    params = env['ir.config_parameter'].sudo()
    website = env['website'].search([], limit=1)
    public = env.ref('base.public_user')
    params.set_param('tacare.map_provider', 'mapbox')
    params.set_param('tacare.mapbox_public_token', 'sk.' + 'x' * 40)
    assert website.with_user(public)._care_map_config() == {'provider': 'openfreemap', 'token': ''}
    params.set_param('tacare.mapbox_public_token', 'pk.' + 'x' * 40)
    projected = website.with_user(public)._care_map_config()
    assert set(projected) == {'provider', 'token'} and projected['provider'] == 'mapbox'
    for field in ('care_map_provider', 'care_mapbox_public_token'):
        assert 'base.group_system' in env['res.config.settings']._fields[field].groups
    try:
        with env.cr.savepoint():
            env['res.config.settings'].create({'care_map_provider': 'mapbox',
                'care_mapbox_public_token': 'sk.' + 'x' * 40})
    except ValidationError:
        pass
    else:
        raise AssertionError('Secret token must be rejected')
    view = env.ref('tacare_website.map_provider_settings')
    assert view.active and view.model == 'res.config.settings'
    print('PASS provider settings: allowlisted public projection, admin-only fields, secret-token rejection, inherited view')
finally:
    env.cr.rollback()
