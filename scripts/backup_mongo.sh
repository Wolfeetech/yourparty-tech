#!/bin/bash
# MongoDB Daily Backup Script
# Install on: CT 202 (mongodb-primary)
# Path: /root/backup_mongo.sh
# Cron: 0 3 * * * /root/backup_mongo.sh >> /var/log/backup.log 2>&1

set -e

BACKUP_DIR="/mnt/nas/backups/mongodb"
DATE=$(date +%Y%m%d_%H%M)
RETENTION_DAYS=7

# Load environment
source /root/.env 2>/dev/null || true

echo "[$(date)] Starting MongoDB backup..."

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Run mongodump
if [ -n "$MONGO_URI" ]; then
    mongodump --uri="$MONGO_URI" --out="$BACKUP_DIR/$DATE" --gzip
else
    mongodump --out="$BACKUP_DIR/$DATE" --gzip
fi

# Verify backup
if [ -d "$BACKUP_DIR/$DATE" ]; then
    SIZE=$(du -sh "$BACKUP_DIR/$DATE" | cut -f1)
    echo "[$(date)] Backup completed: $BACKUP_DIR/$DATE ($SIZE)"
else
    echo "[$(date)] ERROR: Backup failed!"
    exit 1
fi

# Cleanup old backups
find "$BACKUP_DIR" -maxdepth 1 -type d -mtime +$RETENTION_DAYS -exec rm -rf {} \;
echo "[$(date)] Cleaned up backups older than $RETENTION_DAYS days"

echo "[$(date)] MongoDB backup complete."
