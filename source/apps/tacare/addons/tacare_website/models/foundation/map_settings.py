"""Admin-only provider selection, shared by the three marketplace websites."""
from odoo import api, fields, models
from odoo.exceptions import ValidationError

from ...map_config import browser_config


class Website(models.Model):
    _inherit = 'website'

    def _care_map_config(self):
        # The output is deliberately public: only the provider and a read-only
        # public token. No arbitrary system parameters reach QWeb or the browser.
        params = self.env['ir.config_parameter'].sudo()
        return browser_config(params.get_param('tacare.map_provider'),
                              params.get_param('tacare.mapbox_public_token'))


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    care_map_provider = fields.Selection([
        ('openfreemap', 'OpenFreeMap (hiện tại)'), ('mapbox', 'Mapbox Standard')],
        string='Nền bản đồ', default='openfreemap',
        config_parameter='tacare.map_provider', groups='base.group_system')
    care_mapbox_public_token = fields.Char(string='Mapbox public access token',
        config_parameter='tacare.mapbox_public_token', groups='base.group_system')

    @api.constrains('care_map_provider', 'care_mapbox_public_token')
    def _check_mapbox_token(self):
        for settings in self:
            if settings.care_map_provider == 'mapbox' and browser_config(
                    'mapbox', settings.care_mapbox_public_token)['provider'] != 'mapbox':
                raise ValidationError('Nhập public access token Mapbox bắt đầu bằng pk. '
                                      'Không dùng secret token sk. cho bản đồ trên website.')
