"""Run without Odoo: only allowlisted public provider settings may leave server."""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('map_config', Path(__file__).parents[1] / 'map_config.py')
config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config)


class MapConfigTests(unittest.TestCase):
    def test_public_token_only_when_explicitly_enabled(self):
        token = 'pk.' + 'a' * 40
        self.assertEqual(config.browser_config('mapbox', token), {'provider': 'mapbox', 'token': token})
        for provider in (None, '', 'unknown', 'openfreemap'):
            self.assertEqual(config.browser_config(provider, token), {'provider': 'openfreemap', 'token': ''})

    def test_never_project_secret_or_malformed_tokens(self):
        for token in (False, '', 'sk.' + 'a' * 40, 'pk.short', 'pk.' + 'a' * 2001,
                      'pk.' + 'a' * 30 + '<script>', 'https://untrusted.invalid/token'):
            self.assertEqual(config.browser_config('mapbox', token), {'provider': 'openfreemap', 'token': ''})


if __name__ == '__main__':
    unittest.main()
