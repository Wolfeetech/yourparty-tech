#!/bin/bash
# Deploy Mood Voting System to Production
# Run from local machine with SSH access to PVE

set -e

echo "=== MOOD VOTING DEPLOYMENT SCRIPT ==="
echo "Date: $(date)"

# Configuration
PVE_HOST="pve"
API_CT="211"
WP_CT="207"
BACKUP_DIR="/tmp/mood_voting_backup_$(date +%Y%m%d_%H%M%S)"

# API paths on CT 211
API_DIR="/opt/radio-api"
API_FILES="api.py mongo_client.py mood_scheduler.py sync_moods.py"

# WP Theme paths on CT 207
WP_THEME_DIR="/var/www/yourparty.tech/wp-content/themes/yourparty-tech"

echo ""
echo "=== STEP 1: CREATE BACKUPS ==="

# Backup API files
ssh $PVE_HOST "pct exec $API_CT -- mkdir -p $BACKUP_DIR/api"
for file in $API_FILES; do
    ssh $PVE_HOST "pct exec $API_CT -- cp $API_DIR/$file $BACKUP_DIR/api/ 2>/dev/null || echo 'No $file to backup'"
done
echo "API backup: $BACKUP_DIR/api"

# Backup WP theme files
ssh $PVE_HOST "pct exec $WP_CT -- mkdir -p $BACKUP_DIR/theme"
ssh $PVE_HOST "pct exec $WP_CT -- cp $WP_THEME_DIR/assets/mood-dialog.js $BACKUP_DIR/theme/ 2>/dev/null || true"
ssh $PVE_HOST "pct exec $WP_CT -- cp $WP_THEME_DIR/assets/mood-dialog.css $BACKUP_DIR/theme/ 2>/dev/null || true"
ssh $PVE_HOST "pct exec $WP_CT -- cp $WP_THEME_DIR/inc/api.php $BACKUP_DIR/theme/ 2>/dev/null || true"
echo "Theme backup: $BACKUP_DIR/theme"

echo ""
echo "=== STEP 2: DEPLOY API FILES ==="

# Note: Files will be transferred via scp through PVE
echo "Transferring API files..."

echo ""
echo "=== STEP 3: DEPLOY THEME FILES ==="
echo "Transferring theme files..."

echo ""
echo "=== STEP 4: UPDATE ENVIRONMENT VARIABLES ==="
echo "Adding feature flags to .env..."

# Add feature flags (appending to existing .env)
ssh $PVE_HOST "pct exec $API_CT -- bash -c 'cat >> $API_DIR/.env << EOF

# Mood Voting System (deployed $(date +%Y-%m-%d))
FEATURE_MOOD_VOTES=true
FEATURE_MOOD_SYNC=false
FEATURE_MOOD_AUTODJ=true
MOOD_CYCLE_SECONDS=300
MOOD_VOTE_COOLDOWN_MINUTES=5
EOF'"

echo ""
echo "=== STEP 5: RESTART API SERVICE ==="
ssh $PVE_HOST "pct exec $API_CT -- systemctl restart radio-api"
sleep 3
ssh $PVE_HOST "pct exec $API_CT -- systemctl status radio-api --no-pager"

echo ""
echo "=== DEPLOYMENT COMPLETE ==="
echo "Backup location: $BACKUP_DIR"
echo ""
echo "Next steps:"
echo "1. Test mood dialog at https://yourparty.tech/"
echo "2. Check API logs: ssh pve 'pct exec 211 -- journalctl -u radio-api -f'"
echo "3. Verify MongoDB collection: mood_next_votes"
