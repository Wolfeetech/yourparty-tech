#!/bin/bash
# MariaDB Daily Backup Script
# Install on: CT 208 (mariadb-server)
# Path: /root/backup_mariadb.sh
# Cron: 0 4 * * * /root/backup_mariadb.sh >> /var/log/backup.log 2>&1

set -e

BACKUP_DIR="/mnt/nas/backups/mariadb"
DATE=$(date +%Y%m%d_%H%M)
RETENTION_DAYS=7

echo "[$(date)] Starting MariaDB backup..."

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Dump all databases (uses ~/.my.cnf for credentials)
mysqldump --all-databases --single-transaction --quick | gzip > "$BACKUP_DIR/all_databases_$DATE.sql.gz"

# Verify backup
if [ -f "$BACKUP_DIR/all_databases_$DATE.sql.gz" ]; then
    SIZE=$(du -sh "$BACKUP_DIR/all_databases_$DATE.sql.gz" | cut -f1)
    echo "[$(date)] Backup completed: all_databases_$DATE.sql.gz ($SIZE)"
else
    echo "[$(date)] ERROR: Backup failed!"
    exit 1
fi

# Cleanup old backups
find "$BACKUP_DIR" -name "*.sql.gz" -mtime +$RETENTION_DAYS -delete
echo "[$(date)] Cleaned up backups older than $RETENTION_DAYS days"

echo "[$(date)] MariaDB backup complete."
