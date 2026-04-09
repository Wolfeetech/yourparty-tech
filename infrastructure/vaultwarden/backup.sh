#!/usr/bin/env bash
set -euo pipefail

TS=$(date +"%Y%m%d-%H%M%S")
TARGET_DIR="${1:-./backups}"
SRC="./data"

mkdir -p "$TARGET_DIR"
tar -C "$SRC" -czf "$TARGET_DIR/vaultwarden-${TS}.tar.gz" .
find "$TARGET_DIR" -type f -name "vaultwarden-*.tar.gz" -mtime +30 -delete
echo "Backup written to $TARGET_DIR/vaultwarden-${TS}.tar.gz"
