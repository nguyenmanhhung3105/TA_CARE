"""Run ONLY in a disposable Linux container, with --network none and /qa read-only.

Uses fixed deployment paths inside that container; never run on the real server.
"""
import hashlib
import json
import os
from pathlib import Path
import pwd
import subprocess
import sys
import tempfile

assert os.geteuid() == 0 and Path('/.dockerenv').exists(), 'Disposable container only'
assert Path('/qa/tests/worker_contract_fixture.sh').exists()
ROOT = Path('/usr/local/lib/tacare-deploy')
assert not ROOT.exists(), 'Refuse an environment with existing deployment scripts'
ROOT.mkdir(parents=True)
(ROOT / 'worker.sh').write_bytes(Path('/qa/tests/worker_contract_fixture.sh').read_bytes())
(ROOT / 'deploy.sh').write_text('#!/usr/bin/env bash\nexit 0\n')
for file in ROOT.iterdir():
    file.chmod(0o755)


def run(*args, ok=True):
    result = subprocess.run([sys.executable, *args], capture_output=True, text=True)
    assert (result.returncode == 0) == ok, result.stderr
    return result


old = (ROOT / 'worker.sh').read_bytes()
run('/qa/server/install_modes.py')
assert (ROOT / 'worker.sh').read_bytes() == old, 'Preview changed scripts'
run('/qa/server/install_modes.py', '--install')
new = (ROOT / 'worker.sh').read_bytes()
assert new != old and b'run_data_import stage' in new
run('/qa/server/install_modes.py', '--install')
assert (ROOT / 'worker.sh').read_bytes() == new
backups = list(ROOT.glob('data-modes-backup-*'))
assert len(backups) == 1 and (backups[0] / 'worker.sh').read_bytes() == old
assert backups[0].stat().st_mode & 0o777 == 0o700

gate = str(ROOT / 'data_bundle.py')
source = Path('/tmp/private-bundle.json')
raw = json.dumps({'format': 'tacare.demo.v1', 'accounts': [{}], 'records': [{}]}).encode()
source.write_bytes(raw)
source.chmod(0o600)
sha = hashlib.sha256(raw).hexdigest()
run(gate, 'approve', str(source), sha)
run(gate, 'approve', str(source), sha)
approved = Path('/var/lib/tacare-deploy/data') / (sha + '.json')
assert approved.stat().st_mode & 0o777 == 0o400 and approved.stat().st_uid == 0
run(gate, 'inspect', sha)
run(gate, 'inspect', '../bad', ok=False)
source.chmod(0o644)
run(gate, 'approve', str(source), sha, ok=False)
source.chmod(0o600)
symlink = Path('/tmp/bundle-link')
symlink.symlink_to(source)
run(gate, 'approve', str(symlink), sha, ok=False)

workroot = Path('/var/lib/tacare-deploy/work')
workroot.mkdir(mode=0o711)
work = Path(tempfile.mkdtemp(prefix='deploy-', dir=workroot))
work.chmod(0o711)
app = work / 'app'
app.mkdir(mode=0o700)
odoo = pwd.getpwnam('odoo')
os.chown(app, odoo.pw_uid, odoo.pw_gid)
run(gate, 'prepare', sha, str(app))
assert (app / 'data-bundle.json').read_bytes() == raw
assert (app / 'data-bundle.json').stat().st_uid == odoo.pw_uid
assert (app / 'data-bundle.json').stat().st_mode & 0o777 == 0o600
sentinel = Path('/tmp/unchanged-sentinel')
sentinel.write_bytes(b'unchanged')
(app / 'data-bundle.json').unlink()
(app / 'data-bundle.json').symlink_to(sentinel)
run(gate, 'prepare', sha, str(app))
assert sentinel.read_bytes() == b'unchanged'
assert not (app / 'data-bundle.json').is_symlink()
run(gate, 'prepare', sha, '/tmp', ok=False)
approved.chmod(0o600)
run(gate, 'inspect', sha, ok=False)
approved.chmod(0o400)
approved.write_bytes(b'tampered')
run(gate, 'inspect', sha, ok=False)
print('PASS disposable Linux: installer preview/apply/backup/idempotence; root-owned approval, '
      'hash, permissions, work-path and symlink protections. No systemd, Odoo or database action.')
