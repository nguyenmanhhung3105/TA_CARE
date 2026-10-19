# tacare-data-modes-v1
DATA_SHA=

run_data_import() {
    local mode=$1 config=$2
    [[ -n "$DATA_SHA" ]] || return 0
    log "Import selected demo data into $mode (sha256=$DATA_SHA)"
    /usr/bin/python3 "$ROOT/data_bundle.py" prepare "$DATA_SHA" "$WORK/app"
    if [[ "$mode" == stage ]]; then
        run_stage data-import shell -c "$config" -d "$DB" \
            --no-http --max-cron-threads=0 --workers=0 \
            < "$WORK/app/import-command.py"
    elif [[ "$mode" == live ]]; then
        systemd-run --quiet --wait --pipe --collect --service-type=exec \
            --unit="tacare-live-$ID-data-import" "${SANDBOX[@]}" -p RuntimeMaxSec=1800 \
            -p "ReadWritePaths=$WORK/app $DATA" -p "InaccessiblePaths=$BACKUPS $WORK/pgdata" \
            -- "$PY" "$ODOO/odoo-bin" shell -c "$config" -d "$DB" \
            --no-http --max-cron-threads=0 --workers=0 \
            < "$WORK/app/import-command.py"
    else
        die 'Unknown import environment.'
    fi
}

