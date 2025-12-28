$ErrorActionPreference = "Stop"
$PVE_HOST = "192.168.178.25"

# Files changed in this session that need deployment
$API_FILES = @(
    "azuracast_client.py",
    "mood_scheduler.py",
    "library_service.py",
    "playlist_service.py",
    "enrich_ratings.py",
    "manager.py"
)

$WEB_FILES = @(
    "assets/app.js"
)

Write-Host "=== YourParty Full Stack Deployment ===" -ForegroundColor Cyan

# --- API Deployment (CT 211) ---
Write-Host "`n[1/3] Deploying API files to CT 211..." -ForegroundColor Yellow

foreach ($file in $API_FILES) {
    $localPath = "apps/api/$file"
    if (Test-Path $localPath) {
        Write-Host "  Uploading $file..."
        scp -o BatchMode=yes $localPath root@${PVE_HOST}:/tmp/$file
        ssh root@$PVE_HOST "pct push 211 /tmp/$file /opt/radio-api/$file && rm /tmp/$file"
    } else {
        Write-Host "  [SKIP] $file not found locally" -ForegroundColor DarkGray
    }
}

# --- Frontend Deployment (CT 207) ---
Write-Host "`n[2/3] Deploying Frontend files to CT 207..." -ForegroundColor Yellow

foreach ($file in $WEB_FILES) {
    $localPath = "apps/web/$file"
    $remotePath = "/var/www/html/wp-content/themes/yourparty/$file"
    if (Test-Path $localPath) {
        Write-Host "  Uploading $file..."
        scp -o BatchMode=yes $localPath root@${PVE_HOST}:/tmp/$(Split-Path $file -Leaf)
        ssh root@$PVE_HOST "pct push 207 /tmp/$(Split-Path $file -Leaf) $remotePath && rm /tmp/$(Split-Path $file -Leaf)"
    } else {
        Write-Host "  [SKIP] $file not found locally" -ForegroundColor DarkGray
    }
}

# --- Restart Services ---
Write-Host "`n[3/3] Restarting Services..." -ForegroundColor Yellow
ssh root@$PVE_HOST "pct exec 211 -- systemctl restart radio-api"
Write-Host "  radio-api restarted."

Write-Host "`n=== Deployment Complete ===" -ForegroundColor Green
