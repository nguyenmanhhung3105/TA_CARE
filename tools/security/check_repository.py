#!/usr/bin/env python3
"""Check tracked and non-ignored files without printing detected values."""
import argparse
import ast
import ipaddress
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[2]
IPV4 = re.compile(r'(?<![\w.])(?:\d{1,3}\.){3}\d{1,3}(?![\w.])')
DOCUMENTATION_NETS = tuple(ipaddress.ip_network(n) for n in ('192.0.2.0/24', '198.51.100.0/24', '203.0.113.0/24'))
PRIVATE_KEY = re.compile('-----BEGIN ' + r'(?:OPENSSH |RSA |EC |DSA |ENCRYPTED )?PRIVATE KEY-----')
PASSWORD_HASH = re.compile(r'\$pbkdf2-sha512\$\d+\$[./A-Za-z0-9]+\$[./A-Za-z0-9]+|\$2[aby]\$\d{2}\$[./A-Za-z0-9]{53}')
API_TOKEN = re.compile(r'\b(?:ghp_[A-Za-z0-9]{36}|github_pat_[A-Za-z0-9_]{30,}|(?:AKIA|ASIA)[A-Z0-9]{16}|xox[baprs]-[A-Za-z0-9-]{20,})\b')
CREDENTIAL_URL = re.compile(r'(?:https?|ssh|postgres(?:ql)?)://[^\s/:]+:[^\s/@]+@')
SECRET_NAMES = {'password', 'passwd', 'pwd', 'db_password', 'admin_passwd', 'api_key', 'client_secret',
                'secret_key', 'access_token', 'ssh_private_key', 'password_hash'}
LITERAL_ASSIGNMENT = re.compile(r'''(?<![\w-])\b(password|passwd|pwd|db_password|admin_passwd|api_key|client_secret|secret_key|access_token|password_hash)\s*[:=]\s*(['"])([^'"\r\n]+)\2''', re.I)
PRIVATE_PATHS = ('runtime/', 'backups/', 'docker/local-config/', '.private/', '.secrets/', '.ssh/')
KEY_SUFFIXES = ('.pem', '.key', '.p12', '.pfx', '.ppk', '.kdbx')


def placeholder(value):
    return not value or value.startswith(('CHANGE_ME', 'YOUR_', 'EXAMPLE_', '${', '<')) or value in ('False', 'None')


def scan_text(path, text):
    findings = set()
    for line_no, line in enumerate(text.splitlines(), 1):
        for pattern, kind in ((PRIVATE_KEY, 'private-key'), (PASSWORD_HASH, 'password-hash'),
                              (API_TOKEN, 'access-token'), (CREDENTIAL_URL, 'credential-url')):
            if pattern.search(line):
                findings.add((line_no, kind))
        for match in IPV4.finditer(line):
            try:
                address = ipaddress.ip_address(match.group())
            except ValueError:
                continue
            if not (address.is_loopback or address.is_unspecified or any(address in network for network in DOCUMENTATION_NETS)):
                findings.add((line_no, 'server-ip'))
        for match in LITERAL_ASSIGNMENT.finditer(line):
            if not placeholder(match.group(3)):
                findings.add((line_no, 'literal-credential'))
    if str(path).endswith('.py'):
        try:
            tree = ast.parse(text)
        except SyntaxError:
            tree = None
        for node in ast.walk(tree) if tree else ():
            candidates = []
            if isinstance(node, ast.Dict):
                candidates = [(key.value, value) for key, value in zip(node.keys, node.values)
                              if isinstance(key, ast.Constant) and isinstance(key.value, str)]
            elif isinstance(node, ast.Assign):
                candidates = [(target.id, node.value) for target in node.targets if isinstance(target, ast.Name)]
            for name, value in candidates:
                if name.lower() in SECRET_NAMES and isinstance(value, ast.Constant) and isinstance(value.value, str) and not placeholder(value.value):
                    findings.add((value.lineno, 'literal-credential'))
    return sorted(findings)


def repository_files():
    result = subprocess.run(['git', 'ls-files', '--cached', '--others', '--exclude-standard', '-z'],
                            cwd=ROOT, check=True, capture_output=True)
    return sorted(set(Path(p.decode()) for p in result.stdout.split(b'\0') if p))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('paths', nargs='*', type=Path)
    args = parser.parse_args(argv)
    files = args.paths or repository_files()
    count = failures = 0
    for relative in files:
        path = relative if relative.is_absolute() else ROOT / relative
        if not path.is_file():
            continue
        name = relative.as_posix()
        if name.startswith(PRIVATE_PATHS) or path.name in ('id_rsa', 'id_ed25519', '.env') or path.suffix in KEY_SUFFIXES:
            print(f'{relative}:1: private-storage-file')
            failures += 1
            continue
        try:
            text = path.read_text()
        except (OSError, UnicodeError):
            continue
        if '\x00' in text:
            continue
        count += 1
        for line, kind in scan_text(relative, text):
            print(f'{relative}:{line}: {kind}')
            failures += 1
    if failures:
        print(f'FAIL: {failures} finding(s); values were not printed.')
        return 1
    print(f'PASS: {count} text files checked; no matching embedded credentials or server IPs.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
