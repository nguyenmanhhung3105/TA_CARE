#!/usr/bin/env bash
# tacare-data-modes-v1: code-only remains the default for existing Actions.
set -Eeuo pipefail
[[ $EUID -eq 0 ]] || { echo 'Run through sudo.'; exit 1; }
if [[ $# == 1 && ( $1 == --check || $1 == --recover ) ]]; then
    exec /usr/local/lib/tacare-deploy/worker.sh "$1"
fi
[[ $# == 1 || $# == 3 ]] || { echo 'Usage: deploy.sh SHA [--with-data BUNDLE_SHA256] | --check | --recover'; exit 1; }
[[ $1 =~ ^[0-9a-f]{40}$ ]] || { echo 'Invalid commit SHA.'; exit 1; }
if [[ $# == 3 ]]; then
    [[ $2 == --with-data && $3 =~ ^[0-9a-f]{64}$ ]] || { echo 'Invalid data selection.'; exit 1; }
fi
systemd-run --quiet --wait --pipe --collect --service-type=exec \
    --unit="tacare-deploy-$(date -u +%Y%m%d%H%M%S)-$$" \
    -p User=root -p Group=root -p KillMode=control-group -p TimeoutStopSec=120 \
    /usr/local/lib/tacare-deploy/worker.sh "$@"
