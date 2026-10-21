#!/usr/bin/env python3
"""Root-owned transport gate. Never imports or executes repository Python."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import pwd
import re
import stat
import sys

STORE = Path('/var/lib/tacare-deploy/data')
WORK = Path('/var/lib/tacare-deploy/work')
MAX_BYTES = 32 * 1024 * 1024
SHA = re.compile(r'[0-9a-f]{64}\Z')


def pairs(items):
    result = {}
    for key, value in items:
        if key in result:
            raise ValueError('Duplicate JSON key')
        result[key] = value
    return result


def verify(raw, expected):
    if not SHA.fullmatch(expected) or len(raw) > MAX_BYTES or hashlib.sha256(raw).hexdigest() != expected:
        raise ValueError('Invalid data size or SHA256')
    data = json.loads(raw, object_pairs_hook=pairs,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError('Nonfinite JSON')))
    if not isinstance(data, dict) or set(data) != {'format', 'accounts', 'records'} or data['format'] not in ('tacare.demo.v1', 'tacare.demo.v2'):
        raise ValueError('Only the reviewed demo bundle format is supported')
    if not isinstance(data['accounts'], list) or not 1 <= len(data['accounts']) <= 18:
        raise ValueError('Invalid account count')
    if not isinstance(data['records'], list) or not 1 <= len(data['records']) <= 500:
        raise ValueError('Invalid record count')
    return {'sha256': expected, 'accounts': len(data['accounts']), 'records': len(data['records'])}


def private_directory(path, create=False):
    """All ancestors must be root-owned, non-symlink and not writable by others."""
    if not path.is_absolute():
        raise ValueError('Expected an absolute directory')
    current = Path('/')
    for part in path.parts[1:]:
        current = current / part
        if create and not current.exists():
            current.mkdir(mode=0o700)
        info = current.lstat()
        if not stat.S_ISDIR(info.st_mode) or info.st_uid != 0 or info.st_mode & 0o022:
            raise ValueError('Unsafe directory ownership, permissions or symlink')
    if path.stat().st_mode & 0o077:
        raise ValueError('Bundle store must be private (0700)')


def read_file(path, root_only=False):
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, 'rb') as source:
        info = os.fstat(source.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_size > MAX_BYTES or info.st_nlink != 1:
            raise ValueError('Expected a regular private bundle file')
        if info.st_mode & 0o077 or root_only and (info.st_uid != 0 or info.st_mode & 0o222):
            raise ValueError('Unsafe bundle file permissions')
        return source.read(MAX_BYTES + 1)


def approved(expected):
    if not SHA.fullmatch(expected):
        raise ValueError('Expected a SHA256, not a file path')
    private_directory(STORE)
    raw = read_file(STORE / (expected + '.json'), root_only=True)
    verify(raw, expected)
    return raw


def write_exclusive(path, raw, uid, gid, mode=0o600):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, mode)
    with os.fdopen(fd, 'wb') as target:
        os.fchown(target.fileno(), uid, gid)
        target.write(raw)
        target.flush()
        os.fsync(target.fileno())


def prepare(expected, directory):
    raw = approved(expected)
    # The root-owned work parent prevents the app directory from being replaced.
    if directory.parent.parent != WORK or directory.name != 'app' or not re.fullmatch(r'deploy-[A-Za-z0-9]{8}', directory.parent.name):
        raise ValueError('Unexpected deployment work path')
    for root_path in (WORK, directory.parent):
        info = root_path.lstat()
        if not stat.S_ISDIR(info.st_mode) or info.st_uid != 0 or info.st_mode & 0o022:
            raise ValueError('Unsafe work directory')
    user = pwd.getpwnam('odoo')
    info = directory.lstat()
    if not stat.S_ISDIR(info.st_mode) or info.st_uid != user.pw_uid or info.st_mode & 0o077:
        raise ValueError('Unexpected app directory owner/permissions')
    command = (
        'from odoo.addons.tacare_website.tools.data_transfer import import_bundle\n'
        f'result = import_bundle(env, {str(directory / "data-bundle.json")!r})\n'
        'env.cr.commit()\n'
        'print("TA.CARE DATA OK", result)\n'
    ).encode()
    for name, content in (('data-bundle.json', raw), ('import-command.py', command)):
        path = directory / name
        # Unlink only the directory entry; never follow a previous stage's symlink.
        try:
            path.unlink()
        except FileNotFoundError:
            pass
        write_exclusive(path, content, user.pw_uid, user.pw_gid)


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest='command', required=True)
    admit = sub.add_parser('approve')
    admit.add_argument('file', type=Path)
    admit.add_argument('sha256')
    inspect = sub.add_parser('inspect')
    inspect.add_argument('sha256')
    stage = sub.add_parser('prepare')
    stage.add_argument('sha256')
    stage.add_argument('directory', type=Path)
    args = parser.parse_args()
    if os.geteuid() != 0:
        raise ValueError('Administrator approval is required')
    if args.command == 'approve':
        raw = read_file(args.file)
        report = verify(raw, args.sha256)
        private_directory(STORE, create=True)
        destination = STORE / (args.sha256 + '.json')
        if destination.exists():
            if approved(args.sha256) != raw:
                raise ValueError('Existing approved bundle differs')
        else:
            write_exclusive(destination, raw, 0, 0, 0o400)
        print(json.dumps(report))
    elif args.command == 'inspect':
        print(json.dumps(verify(approved(args.sha256), args.sha256)))
    else:
        prepare(args.sha256, args.directory)


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        # Never dump the input payload or credential hashes.
        print('DATA GATE ERROR: ' + type(exc).__name__ + ': ' + str(exc), file=sys.stderr)
        sys.exit(1)
