$ErrorActionPreference = "Stop"

# Load Configuration
$ScriptDir = Split-Path $MyInvocation.MyCommand.Path
. "$ScriptDir\config.ps1"

# Files changed in this session that need deployment
$API_FILES = @(
    "azuracast_client.py",
    "api.py",
    "mood_scheduler.py",
    "audio_science.py",
    "library_service.py",
    "playlist_service.py",
    "enrich_ratings.py",
    "manager.py",
    "mongo_client.py",
    "routers/interactive.py",
    "requirements.txt"
)

$WEB_FILES = @(
    "assets/app.js",
    "assets/js/ControlPanel.js",
    "assets/mood-dialog.js",
    "inc/api.php",
    "templates/page-control.php",
    "functions.php",
    "front-page.php"
)

Write-Host "=== YourParty Full Stack Deployment ===" -ForegroundColor Cyan

# --- API Deployment (CT 211) ---
Write-Host "`n[1/3] Deploying API files to CT $CT_API_ID..." -ForegroundColor Yellow

foreach ($file in $API_FILES) {
    $localPath = "apps/api/$file"
    if (Test-Path $localPath) {
        Write-Host "  Uploading $file..."
        
        $fileName = Split-Path $file -Leaf
        $remoteTmp = "/tmp/$fileName"
        
        # SCP to Host
        scp $SSH_OPTS $localPath "${SSH_USER}@${PVE_HOST}:${remoteTmp}"
        
        # Push to Container
        $destPath = "$REMOTE_API_PATH/$file"
        
        # Ensure destination directory exists (e.g. for routers/)
        $destDir = Split-Path $destPath -Parent
        ssh $SSH_OPTS "${SSH_USER}@${PVE_HOST}" "pct exec $CT_API_ID -- mkdir -p $destDir"

        ssh $SSH_OPTS "${SSH_USER}@${PVE_HOST}" "pct push $CT_API_ID $remoteTmp $destPath && rm $remoteTmp"
    }
    else {
        Write-Host "  [SKIP] $file not found locally" -ForegroundColor DarkGray
    }
}

# --- Frontend Deployment (CT 207) ---
Write-Host "`n[2/3] Deploying Frontend files to CT $CT_WEB_ID..." -ForegroundColor Yellow

foreach ($file in $WEB_FILES) {
    $localPath = "apps/web/$file"
    # Map local "apps/web/..." to remote theme path
    $relPath = $file 
    $remotePath = "$REMOTE_THEME_PATH/$relPath"
    
    if (Test-Path $localPath) {
        Write-Host "  Uploading $file..."
        $fileName = Split-Path $file -Leaf
        $remoteTmp = "/tmp/$fileName"
        
        scp $SSH_OPTS $localPath "${SSH_USER}@${PVE_HOST}:${remoteTmp}"
        ssh $SSH_OPTS "${SSH_USER}@${PVE_HOST}" "pct push $CT_WEB_ID $remoteTmp $remotePath && rm $remoteTmp"
    }
    else {
        Write-Host "  [SKIP] $file not found locally" -ForegroundColor DarkGray
    }
}

# --- Restart Services ---
Write-Host "`n[3/3] Restarting Services..." -ForegroundColor Yellow

# Install dependencies first
Write-Host "  Installing dependencies..."
ssh $SSH_OPTS "${SSH_USER}@${PVE_HOST}" "pct exec $CT_API_ID -- pip install -r $REMOTE_API_PATH/apps/api/requirements.txt"

ssh $SSH_OPTS "${SSH_USER}@${PVE_HOST}" "pct exec $CT_API_ID -- systemctl restart radio-api"
Write-Host "  radio-api restarted."

Write-Host "`n=== Deployment Complete ===" -ForegroundColor Green
