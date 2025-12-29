$ErrorActionPreference = "Stop"
$PVE_HOST = "192.168.178.25"

Write-Host "--- Deploying Shoutout Backend ---"

# 1. mongo_client.py
Write-Host "Deploying mongo_client.py..."
if (Test-Path "apps/api/mongo_client.py") {
    scp -o BatchMode=yes "apps/api/mongo_client.py" "root@${PVE_HOST}:/tmp/mongo_client.py"
    ssh root@$PVE_HOST "pct push 211 /tmp/mongo_client.py /opt/radio-api/mongo_client.py && rm /tmp/mongo_client.py"
    Write-Host "  OK."
} else {
    Write-Error "apps/api/mongo_client.py not found!"
}

# 2. interactive.py (routers)
Write-Host "Deploying routers/interactive.py..."
if (Test-Path "apps/api/routers/interactive.py") {
    scp -o BatchMode=yes "apps/api/routers/interactive.py" "root@${PVE_HOST}:/tmp/interactive.py"
    ssh root@$PVE_HOST "pct push 211 /tmp/interactive.py /opt/radio-api/routers/interactive.py && rm /tmp/interactive.py"
    Write-Host "  OK."
} else {
    Write-Error "apps/api/routers/interactive.py not found!"
}

# 3. Restart Service
Write-Host "Restarting radio-api service..."
ssh root@$PVE_HOST "pct exec 211 -- systemctl restart radio-api"

Write-Host "Deployment Complete."
