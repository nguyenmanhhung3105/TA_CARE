#!/usr/bin/env bash
# Produces a PRIVATE ignored JSON bundle; no git push or server connection.
set -Eeuo pipefail
repo_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$repo_dir"
bundle_name="release-demo-$(date -u +%Y%m%dT%H%M%S)-$$.json"
docker compose exec -T tacare python /opt/odoo/odoo-server/odoo-bin shell \
    -c /etc/odoo/local.conf -d tacare_local --no-http --max-cron-threads=0 <<PY
from odoo.addons.tacare_website.tools.data_transfer import export_demo
env.cr.execute('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ')
print('EXPORTED', export_demo(env, '/var/lib/odoo/$bundle_name'))
env.cr.rollback()
PY
python3 - "$repo_dir/runtime/tacare/$bundle_name" <<'PY'
import hashlib
from pathlib import Path
import sys
path = Path(sys.argv[1])
print('PRIVATE FILE:', path)
print('SHA256:', hashlib.sha256(path.read_bytes()).hexdigest())
print('Do not commit or paste the bundle: it contains portal password hashes.')
PY
