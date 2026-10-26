#!/usr/bin/env python3
"""Back up and optionally remove the two retired local website databases.

Only the local compose stack and the fixed allowlist below are supported.
Defaults to inspection. Never removes PostgreSQL templates or tacare_local.
"""
import argparse
import hashlib
from datetime import datetime
from pathlib import Path
import subprocess
import tarfile

ROOT = Path(__file__).resolve().parents[2]
RETIRED = ('khovieclam_local', 'tuhoso_local')


def docker(*args, **kwargs):
    return subprocess.run(['docker', 'compose', *args], cwd=ROOT, check=True, **kwargs)


def sql(database, statement):
    return docker('exec', '-T', 'db', 'psql', '-X', '-v', 'ON_ERROR_STOP=1',
                  '-U', 'postgres', '-d', database, '-Atc', statement,
                  capture_output=True, text=True).stdout.strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true', help='Back up, verify archives, then drop retired databases')
    args = parser.parse_args()
    config = (ROOT / 'docker/local-config/tacare.conf').read_text()
    assert 'db_name = tacare_local' in config and 'dbfilter = ^tacare_local$' in config
    assert sql('postgres', "SELECT count(*) FROM pg_database WHERE datname='tacare_local'") == '1'
    existing = sql('postgres', 'SELECT datname FROM pg_database').splitlines()
    candidates = [name for name in RETIRED if name in existing]
    for name in candidates:
        assert sql('postgres', f"SELECT count(*) FROM pg_stat_activity WHERE datname='{name}'") == '0', f'{name}: has connections'
        assert sql(name, "SELECT count(*) FROM ir_module_module WHERE name IN ('tacare_website','tacare_account_access')") == '0', f'{name}: contains application modules'
        assert sql(name, "SELECT count(*) FROM information_schema.tables WHERE table_schema='public' AND (table_name LIKE 'care_%' OR table_name LIKE 'tacare_%')") == '0', f'{name}: contains application tables'
        print(f'{name}: retired, no connections or TA.CARE modules/tables')
    if not args.apply or not candidates:
        return
    backup = ROOT / 'backups' / ('unused_local_databases_' + datetime.now().strftime('%Y%m%d_%H%M%S'))
    backup.mkdir(parents=True, mode=0o700)
    # Back up every candidate before dropping any database. Filestores stay in place.
    for name in candidates:
        dump = backup / f'{name}.dump'
        with dump.open('wb') as stream:
            docker('exec', '-T', 'db', 'pg_dump', '-U', 'postgres', '-Fc', name, stdout=stream)
        with dump.open('rb') as stream:
            listing = docker('exec', '-T', 'db', 'pg_restore', '--list', stdin=stream, capture_output=True).stdout
        assert b'TABLE DATA' in listing, f'{name}: empty archive'
        (backup / f'{name}.contents').write_bytes(listing)
        for store in (ROOT / 'runtime').glob(f'*/filestore/{name}'):
            archive = backup / f'{store.parents[1].name}_{name}_filestore.tar.gz'
            with tarfile.open(archive, 'w:gz') as output:
                output.add(store, arcname=name)
            with tarfile.open(archive) as check:
                assert check.getnames()
    files = [path for path in backup.iterdir() if path.is_file()]
    (backup / 'SHA256SUMS').write_text(''.join(f'{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}\n' for path in sorted(files)))
    for name in candidates:
        # No FORCE: a new connection aborts deletion instead of terminating clients.
        sql('postgres', f'DROP DATABASE "{name}"')
        print(f'{name}: removed; backup: {backup.relative_to(ROOT)}')
    print('tacare_local and existing filestores preserved.')


if __name__ == '__main__':
    main()
