#!/usr/bin/env python3
"""Explicit release selection. Creates a release commit and PUSHES main.

code: normal code/schema update; with-data: also select an approved bundle hash.
Never invoked automatically by Codex or by ordinary Git hooks.
"""
import argparse
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[2]


def git(*args, capture=False):
    return subprocess.run(['git', *args], cwd=ROOT, check=True, text=True,
                          stdout=subprocess.PIPE if capture else None).stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('code', 'with-data'))
    parser.add_argument('--data-sha256', default='')
    args = parser.parse_args()
    if args.mode == 'with-data' and not re.fullmatch(r'[0-9a-f]{64}', args.data_sha256):
        parser.error('with-data requires --data-sha256 (the server-approved bundle)')
    if args.mode == 'code' and args.data_sha256:
        parser.error('code does not accept a data bundle')
    if git('branch', '--show-current', capture=True).strip() != 'main':
        raise SystemExit('Release from main only')
    if git('status', '--porcelain', capture=True).strip():
        raise SystemExit('Commit your code changes first; the release command never stages files')
    title = 'chore: release code and selected demo data' if args.mode == 'with-data' else 'chore: release code only'
    command = ['commit', '--allow-empty', '-m', title]
    if args.mode == 'with-data':
        command += ['-m', 'Tacare-Data-SHA256: ' + args.data_sha256]
    git(*command)
    # Do not force-push, merge, reset or change remote configuration.
    git('push', 'origin', 'HEAD:main')


if __name__ == '__main__':
    main()
