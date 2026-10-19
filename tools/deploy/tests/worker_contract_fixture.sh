#!/usr/bin/env bash
# Reduced fixture of the inspected worker anchors, NOT a deployable worker.
DB=tacare_prod
PENDING=$BACKUPS/pending.json
gate_on() { :; }
rollback() {
    for unit in \
        "tacare-stage-$GATE_ID-neutralize.service"; do
        : "$unit"
    done
}
run_stage() { :; }
start_probe() { :; }
main() {
    [[ $# == 1 && $1 =~ ^[0-9a-f]{40}$ ]] || die 'Expected a 40-character commit SHA.'
    SHA=$1
    printf '%s\n' "$SHA" > "$BACKUP/new-commit.txt"
    start_probe stage "$WORK/app/stage.conf"
    step '4. Freeze production and make a consistent backup'
    state "original_oid=$original_oid" "previous_db=$previous_db" "failed_db=$failed_db" \
        "old_addons=$old_addons" "old_filestore=$old_filestore" "backup=$BACKUP" \
        "sha=$SHA" "gate_id=$ID" "work=$WORK" "phase=frozen"
    start_probe live "$WORK/app/live-probe.conf"
    state 'phase=committed'
    COMMITTED=1
}
