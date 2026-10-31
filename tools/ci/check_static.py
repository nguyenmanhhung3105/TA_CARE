#!/usr/bin/env python3
"""Parse repository source without importing Odoo or touching any database."""
import ast
import csv
import fnmatch
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
ADDONS = ROOT / 'source/apps/tacare/addons'


def files():
    raw = subprocess.check_output(['git', 'ls-files', '--cached', '--others', '--exclude-standard', '-z'], cwd=ROOT)
    return [ROOT / name.decode() for name in sorted(set(raw.split(b'\0'))) if name and (ROOT / name.decode()).is_file()]


def check():
    count = 0
    for path in files():
        relative = path.relative_to(ROOT).as_posix()
        if path.suffix == '.py':
            ast.parse(path.read_text(), filename=relative, feature_version=(3, 12))
            if path.name == '__manifest__.py' and path.is_relative_to(ADDONS):
                manifest = ast.literal_eval(path.read_text())
                assert manifest.get('installable') and manifest.get('license'), relative
                for name in manifest.get('data', []):
                    assert (path.parent / name).is_file(), f'{relative}: missing data file {name}'
                for values in manifest.get('assets', {}).values():
                    for value in values:
                        if isinstance(value, str) and value.startswith(path.parent.name + '/'):
                            assert any(fnmatch.fnmatch(p.relative_to(ADDONS).as_posix(), value)
                                       for p in path.parent.rglob('*') if p.is_file()), f'Missing asset {value}'
        elif path.suffix in ('.xml', '.svg'):
            ET.fromstring(path.read_bytes())
        elif path.suffix in ('.js', '.cjs', '.mjs'):
            if '/static/lib/' in relative or '/static/src/lib/' in relative:
                continue
            subprocess.run(['node', '--check', str(path)], check=True, capture_output=True)
        elif path.suffix == '.sh':
            subprocess.run(['bash', '-n', str(path)], check=True, capture_output=True)
        elif path.name == 'ir.model.access.csv':
            rows = [row for row in csv.reader(path.read_text().splitlines()) if row]
            assert rows and all(len(row) == len(rows[0]) for row in rows), relative
        else:
            continue
        count += 1
    print(f'PASS static syntax, manifests and assets: {count} files')


if __name__ == '__main__':
    try:
        check()
    except (AssertionError, SyntaxError, ValueError, ET.ParseError, subprocess.CalledProcessError) as error:
        print(f'FAIL source check: {error}', file=sys.stderr)
        raise SystemExit(1)
