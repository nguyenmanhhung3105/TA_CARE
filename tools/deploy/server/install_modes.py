#!/usr/bin/env python3
"""Review a narrow patch to the inspected Oct 16 worker; --install applies it.

Run manually on the server. No Git fetch, Odoo action or database change here.
"""
import argparse
import difflib
import fcntl
import os
from pathlib import Path
import shutil
import stat
import subprocess
import tempfile
from datetime import datetime, timezone

ROOT = Path('/usr/local/lib/tacare-deploy')
HERE = Path(__file__).resolve().parent
MARKER = '# tacare-data-modes-v1'


def replace_once(text, before, after):
    if text.count(before) != 1:
        raise ValueError('Worker differs from the reviewed version; refusing this patch: ' + before.splitlines()[0])
    return text.replace(before, after, 1)


def patch_worker(text, extension):
    if MARKER in text:
        if text.count(extension) != 1:
            raise ValueError('Installed data extension differs; inspect before updating')
        return text
    for anchor in ('DB=tacare_prod\n', 'PENDING=$BACKUPS/pending.json\n', 'gate_on() {',
                   'rollback() {', 'run_stage() {', 'start_probe() {',
                   "state 'phase=committed'", 'COMMITTED=1\n'):
        if anchor not in text:
            raise ValueError('Unexpected deployment contract')
    text = replace_once(text, '\nmain() {\n', '\n' + extension + '\nmain() {\n')
    text = replace_once(text,
        "    [[ $# == 1 && $1 =~ ^[0-9a-f]{40}$ ]] || die 'Expected a 40-character commit SHA.'\n    SHA=$1\n",
        "    [[ $# == 1 || $# == 3 ]] || die 'Expected SHA [--with-data BUNDLE_SHA256].'\n"
        "    [[ $1 =~ ^[0-9a-f]{40}$ ]] || die 'Expected a 40-character commit SHA.'\n"
        "    SHA=$1\n"
        "    if [[ $# == 3 ]]; then\n"
        "        [[ $2 == --with-data && $3 =~ ^[0-9a-f]{64}$ ]] || die 'Invalid data selection.'\n"
        "        DATA_SHA=$3\n"
        "        /usr/bin/python3 \"$ROOT/data_bundle.py\" inspect \"$DATA_SHA\"\n"
        "    fi\n")
    text = replace_once(text,
        '        "tacare-stage-$GATE_ID-neutralize.service"; do\n',
        '        "tacare-stage-$GATE_ID-neutralize.service" "tacare-stage-$GATE_ID-data-import.service" \\\n'
        '        "tacare-live-$GATE_ID-data-import.service"; do\n')
    text = replace_once(text,
        '    start_probe stage "$WORK/app/stage.conf"\n',
        '    run_data_import stage "$WORK/app/stage.conf"\n'
        '    helper check-logs "$WORK/app/stage.log"\n'
        '    start_probe stage "$WORK/app/stage.conf"\n')
    text = replace_once(text,
        '    start_probe live "$WORK/app/live-probe.conf"\n',
        '    run_data_import live "$WORK/app/live.conf"\n'
        '    helper check-logs "$WORK/app/live-upgrade.log"\n'
        '    start_probe live "$WORK/app/live-probe.conf"\n')
    text = replace_once(text,
        '        "sha=$SHA" "gate_id=$ID" "work=$WORK" "phase=frozen"\n',
        '        "sha=$SHA" "gate_id=$ID" "work=$WORK" "phase=frozen" "data_sha=$DATA_SHA"\n')
    text = replace_once(text,
        '    printf \'%s\\n\' "$SHA" > "$BACKUP/new-commit.txt"\n',
        '    printf \'%s\\n\' "$SHA" > "$BACKUP/new-commit.txt"\n'
        '    printf \'%s\\n\' "${DATA_SHA:-code-only}" > "$BACKUP/data-selection.txt"\n')
    return text


def validate_worker(text):
    subprocess.run(['bash', '-n'], input=text.encode(), check=True)
    if text.count('run_data_import stage "$WORK/app/stage.conf"') != 1 or text.count('run_data_import live "$WORK/app/live.conf"') != 1:
        raise ValueError('Import gates are missing or duplicated')
    if not (text.index('run_data_import stage "$WORK/app/stage.conf"') < text.index("step '4. Freeze production")
            < text.index('run_data_import live "$WORK/app/live.conf"') < text.index("state 'phase=committed'", text.index('main() {'))):
        raise ValueError('Import must stay within the existing staging/rollback boundaries')


def safe_file(path):
    info = path.lstat()
    if not stat.S_ISREG(info.st_mode) or info.st_uid != 0 or info.st_mode & 0o022 or info.st_nlink != 1:
        raise ValueError('Expected a root-owned non-writable regular file: ' + str(path))


def atomic_write(path, raw):
    fd, temporary = tempfile.mkstemp(prefix='.data-modes-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as target:
            os.fchmod(target.fileno(), 0o755)
            target.write(raw)
            target.flush()
            os.fsync(target.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--install', action='store_true')
    args = parser.parse_args()
    if os.geteuid() != 0:
        raise ValueError('Run with sudo (preview is read-only)')
    if ROOT.resolve() != ROOT or ROOT.stat().st_uid != 0 or ROOT.stat().st_mode & 0o022:
        raise ValueError('Unsafe deployment directory')
    fd = os.open('/run/lock/tacare-deploy.lock', os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'w') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if Path('/var/backups/tacare-deploy/pending.json').exists() or Path('/run/systemd/system/odoo-tacare.service.d/95-tacare-deploy.conf').exists():
            raise ValueError('Recover the unfinished deployment before changing deployment scripts')
        safe_file(ROOT / 'worker.sh')
        safe_file(ROOT / 'deploy.sh')
        original = (ROOT / 'worker.sh').read_text()
        worker = patch_worker(original, (HERE / 'worker_extension.sh').read_text())
        validate_worker(worker)
        wrapper = (HERE / 'deploy.sh').read_bytes()
        gate = (HERE / 'data_bundle.py').read_bytes()
        subprocess.run(['bash', '-n'], input=wrapper, check=True)
        compile(gate, 'data_bundle.py', 'exec')
        replacements = {'worker.sh': worker.encode(), 'deploy.sh': wrapper, 'data_bundle.py': gate}
        changes = {}
        for name, content in replacements.items():
            target = ROOT / name
            if target.exists() or target.is_symlink():
                safe_file(target)
                old = target.read_bytes()
            else:
                old = b''
            if old != content:
                changes[name] = (old, content)
                print(''.join(difflib.unified_diff(old.decode().splitlines(True), content.decode().splitlines(True),
                                                 fromfile=str(target), tofile=str(target) + '.new')))
        if not changes:
            print('Two deployment modes are already installed; no files changed.')
            return
        if not args.install:
            print('PREVIEW ONLY. Review the diff, then run again with --install.')
            return
        backup = ROOT / ('data-modes-backup-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'))
        backup.mkdir(mode=0o700)
        for name in changes:
            if (ROOT / name).exists():
                shutil.copy2(ROOT / name, backup / name)
        try:
            for name, (_, content) in changes.items():
                atomic_write(ROOT / name, content)
        except BaseException:
            for name, (old, _) in changes.items():
                if old:
                    atomic_write(ROOT / name, old)
                elif (ROOT / name).exists():
                    (ROOT / name).unlink()
            raise
        print('INSTALLED. Script backup: ' + str(backup))
        print('Odoo and the production database were not changed. Run deploy.sh --check next.')


if __name__ == '__main__':
    main()
