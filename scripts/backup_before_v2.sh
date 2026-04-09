#!/bin/bash
# ============================================================
# PRE-V2 MIGRATION BACKUP SCRIPT
# YourParty.tech - Project "Renovate"
# 
# This script creates a comprehensive backup before V2 migration:
# 1. MongoDB full dump (all databases)
# 2. File inventory of music library
# 3. AzuraCast configuration export
# 4. Current Docker volume state
#
# Run this BEFORE starting any V2 migration work!
# ============================================================

set -e

# Configuration
BACKUP_DIR="${BACKUP_DIR:-/mnt/nas/backups/v2_migration}"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_PATH="${BACKUP_DIR}/${DATE}"
LOG_FILE="${BACKUP_PATH}/backup.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[$(date '+%H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

warn() {
    echo -e "${YELLOW}[$(date '+%H:%M:%S')] WARNING:${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[$(date '+%H:%M:%S')] ERROR:${NC} $1" | tee -a "$LOG_FILE"
    exit 1
}

# Load environment
if [ -f /root/.env ]; then
    source /root/.env
elif [ -f .env ]; then
    source .env
fi

# Create backup directory
mkdir -p "$BACKUP_PATH"
log "Starting V2 Migration Backup to: $BACKUP_PATH"

# ============================================================
# 1. MONGODB BACKUP
# ============================================================
log "=== MongoDB Backup ==="

MONGO_BACKUP_DIR="${BACKUP_PATH}/mongodb"
mkdir -p "$MONGO_BACKUP_DIR"

if [ -n "$MONGO_URI" ]; then
    log "Using MONGO_URI from environment"
    mongodump --uri="$MONGO_URI" --out="$MONGO_BACKUP_DIR" --gzip 2>&1 | tee -a "$LOG_FILE"
else
    # Construct from parts
    MONGO_HOST="${MONGO_HOST:-192.168.178.222}"
    MONGO_PORT="${MONGO_PORT:-27017}"
    MONGO_USER="${MONGO_INITDB_ROOT_USERNAME:-root}"
    MONGO_PASS="${MONGO_INITDB_ROOT_PASSWORD:-}"
    
    if [ -n "$MONGO_PASS" ]; then
        log "Using constructed URI: mongodb://${MONGO_USER}:****@${MONGO_HOST}:${MONGO_PORT}"
        mongodump --uri="mongodb://${MONGO_USER}:${MONGO_PASS}@${MONGO_HOST}:${MONGO_PORT}/?authSource=admin" \
            --out="$MONGO_BACKUP_DIR" --gzip 2>&1 | tee -a "$LOG_FILE"
    else
        log "Using unauthenticated connection to ${MONGO_HOST}:${MONGO_PORT}"
        mongodump --host="${MONGO_HOST}" --port="${MONGO_PORT}" \
            --out="$MONGO_BACKUP_DIR" --gzip 2>&1 | tee -a "$LOG_FILE"
    fi
fi

# Verify MongoDB backup
if [ -d "$MONGO_BACKUP_DIR" ] && [ "$(ls -A $MONGO_BACKUP_DIR)" ]; then
    MONGO_SIZE=$(du -sh "$MONGO_BACKUP_DIR" | cut -f1)
    log "MongoDB backup complete: $MONGO_SIZE"
else
    error "MongoDB backup failed or empty!"
fi

# ============================================================
# 2. MUSIC LIBRARY INVENTORY
# ============================================================
log "=== Music Library Inventory ==="

LIBRARY_PATH="${LIBRARY_ROOT_LINUX:-/var/radio/music/yourparty_Libary}"
INVENTORY_FILE="${BACKUP_PATH}/library_inventory.txt"
INVENTORY_JSON="${BACKUP_PATH}/library_inventory.json"

if [ -d "$LIBRARY_PATH" ]; then
    log "Scanning library at: $LIBRARY_PATH"
    
    # Create detailed inventory
    find "$LIBRARY_PATH" -type f \( -name "*.mp3" -o -name "*.flac" -o -name "*.m4a" -o -name "*.wav" \) \
        -printf '%s\t%T@\t%p\n' | sort -k3 > "$INVENTORY_FILE"
    
    FILE_COUNT=$(wc -l < "$INVENTORY_FILE")
    TOTAL_SIZE=$(du -sh "$LIBRARY_PATH" 2>/dev/null | cut -f1)
    
    log "Found $FILE_COUNT audio files ($TOTAL_SIZE total)"
    
    # Create JSON summary
    cat > "$INVENTORY_JSON" << EOF
{
  "timestamp": "$(date -Iseconds)",
  "library_path": "$LIBRARY_PATH",
  "file_count": $FILE_COUNT,
  "total_size": "$TOTAL_SIZE",
  "file_types": {
    "mp3": $(grep -c '\.mp3$' "$INVENTORY_FILE" || echo 0),
    "flac": $(grep -c '\.flac$' "$INVENTORY_FILE" || echo 0),
    "m4a": $(grep -c '\.m4a$' "$INVENTORY_FILE" || echo 0),
    "wav": $(grep -c '\.wav$' "$INVENTORY_FILE" || echo 0)
  }
}
EOF
else
    warn "Library path not found: $LIBRARY_PATH"
    echo "[]" > "$INVENTORY_JSON"
fi

# ============================================================
# 3. AZURACAST CONFIG EXPORT
# ============================================================
log "=== AzuraCast Configuration ==="

AZURA_BACKUP_DIR="${BACKUP_PATH}/azuracast"
mkdir -p "$AZURA_BACKUP_DIR"

AZURACAST_URL="${AZURACAST_URL:-https://radio.yourparty.tech}"
AZURACAST_API_KEY="${AZURACAST_API_KEY:-}"

if [ -n "$AZURACAST_API_KEY" ]; then
    log "Exporting AzuraCast station configs..."
    
    # Export station 1 config
    curl -s -H "X-API-Key: $AZURACAST_API_KEY" \
        "${AZURACAST_URL}/api/station/1" > "$AZURA_BACKUP_DIR/station_1.json" 2>/dev/null || warn "Failed to export station 1"
    
    # Export playlists
    curl -s -H "X-API-Key: $AZURACAST_API_KEY" \
        "${AZURACAST_URL}/api/station/1/playlists" > "$AZURA_BACKUP_DIR/playlists.json" 2>/dev/null || warn "Failed to export playlists"
    
    # Export storage locations
    curl -s -H "X-API-Key: $AZURACAST_API_KEY" \
        "${AZURACAST_URL}/api/station/1/storage-locations" > "$AZURA_BACKUP_DIR/storage.json" 2>/dev/null || warn "Failed to export storage"
    
    log "AzuraCast config exported"
else
    warn "AZURACAST_API_KEY not set, skipping AzuraCast export"
fi

# ============================================================
# 4. DOCKER STATE SNAPSHOT
# ============================================================
log "=== Docker State Snapshot ==="

DOCKER_BACKUP_DIR="${BACKUP_PATH}/docker"
mkdir -p "$DOCKER_BACKUP_DIR"

# List all containers
docker ps -a --format '{{json .}}' > "$DOCKER_BACKUP_DIR/containers.json" 2>/dev/null || warn "Docker not available"

# List all volumes
docker volume ls --format '{{json .}}' > "$DOCKER_BACKUP_DIR/volumes.json" 2>/dev/null || true

# Export current docker-compose if exists
if [ -f /opt/yourparty-tech/infrastructure/docker/docker-compose.yml ]; then
    cp /opt/yourparty-tech/infrastructure/docker/docker-compose.yml "$DOCKER_BACKUP_DIR/docker-compose.v1.yml"
    log "Copied current docker-compose.yml"
fi

# ============================================================
# 5. SUMMARY
# ============================================================
log "=== Backup Summary ==="

TOTAL_BACKUP_SIZE=$(du -sh "$BACKUP_PATH" | cut -f1)

cat > "${BACKUP_PATH}/MANIFEST.json" << EOF
{
  "backup_id": "${DATE}",
  "timestamp": "$(date -Iseconds)",
  "version": "pre-v2",
  "total_size": "$TOTAL_BACKUP_SIZE",
  "components": {
    "mongodb": $([ -d "$MONGO_BACKUP_DIR" ] && echo "true" || echo "false"),
    "library_inventory": $([ -f "$INVENTORY_FILE" ] && echo "true" || echo "false"),
    "azuracast": $([ -d "$AZURA_BACKUP_DIR" ] && echo "true" || echo "false"),
    "docker": $([ -d "$DOCKER_BACKUP_DIR" ] && echo "true" || echo "false")
  },
  "restore_instructions": "See RESTORE.md in this directory"
}
EOF

# Create restore instructions
cat > "${BACKUP_PATH}/RESTORE.md" << 'EOF'
# Restore Instructions

## MongoDB Restore
```bash
mongorestore --uri="$MONGO_URI" --gzip ./mongodb/
```

## Verify Library
Compare `library_inventory.txt` with current state to identify missing files.

## AzuraCast
Import configs via AzuraCast admin panel or API.

## Docker
Use `docker-compose.v1.yml` to restore original V1 setup if needed.
EOF

log "============================================"
log "BACKUP COMPLETE!"
log "Location: $BACKUP_PATH"
log "Total Size: $TOTAL_BACKUP_SIZE"
log "============================================"

# Print manifest
cat "${BACKUP_PATH}/MANIFEST.json"
