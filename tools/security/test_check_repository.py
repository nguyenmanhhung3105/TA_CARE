"""Synthetic fixtures only; no real credentials, network or database."""
import importlib.util
import ipaddress
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('checker', Path(__file__).with_name('check_repository.py'))
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class RepositoryCheckTests(unittest.TestCase):
    def test_runtime_variables_and_placeholders_are_allowed(self):
        source = "password = secrets.token_urlsafe(24)\nconfig = {'password': account.password}\npassword = 'YOUR_PASSWORD'\n"
        self.assertEqual(checker.scan_text('fixture.py', source), [])
        self.assertEqual(checker.scan_text('fixture.xml', '<button data-show-password="#password-input"/>'), [])
        self.assertEqual(checker.scan_text('fixture.md', 'http://127.0.0.1:8069 0.0.0.0 198.51.100.1 19.0.9.0.0'), [])

    def test_literal_credentials_are_reported_without_values(self):
        generated = 'synthetic' + '-test-value'
        findings = checker.scan_text('fixture.py', "config = {'password': '" + generated + "'}")
        self.assertIn((1, 'literal-credential'), findings)
        self.assertNotIn(generated, repr(findings))

    def test_nonlocal_ip_hash_key_and_token_are_rejected(self):
        host = str(ipaddress.IPv4Address(0x08080808))
        source = '\n'.join([host, '-----BEGIN ' + 'OPENSSH PRIVATE KEY-----',
                            '$pbkdf2-sha512$' + '60000$' + 'a' * 20 + '$' + 'b' * 40,
                            'ghp_' + 'a' * 36])
        self.assertEqual({kind for _, kind in checker.scan_text('fixture.txt', source)},
                         {'server-ip', 'private-key', 'password-hash', 'access-token'})


if __name__ == '__main__':
    unittest.main()
