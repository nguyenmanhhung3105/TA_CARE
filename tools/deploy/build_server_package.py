#!/usr/bin/env python3
"""Package only reviewed server scripts; never include data or credentials."""
import hashlib
from pathlib import Path
import tarfile

root = Path(__file__).resolve().parents[2]
output = root / 'runtime/releases/tacare-deploy-modes-v1.tar.gz'
output.parent.mkdir(parents=True, exist_ok=True)
with tarfile.open(output, 'w:gz') as archive:
    for name in ('install_modes.py', 'deploy.sh', 'worker_extension.sh', 'data_bundle.py'):
        archive.add(root / 'tools/deploy/server' / name, arcname=name, recursive=False)
print('SERVER PACKAGE:', output)
print('SHA256:', hashlib.sha256(output.read_bytes()).hexdigest())
