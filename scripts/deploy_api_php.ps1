$ErrorActionPreference = "Stop"
$PVE_HOST = "192.168.178.25"

Write-Host "--- Deploying api.php to CT 207 (yourparty) ---"

$localPath = "apps/web/inc/api.php"
$remoteTmp = "/tmp/api.php"
$paramRemotePath = "/var/www/html/wp-content/themes/yourparty-tech/inc/api.php"

# Try yourparty-tech first (since Z: showed that)
# Wait, if `deploy_full_stack.ps1` used `yourparty`, I should try THAT.
# But `ls` showed `yourpart...`.

# Let's try BOTH locations to be sure.
$paths = @(
    "/var/www/html/wp-content/themes/yourparty/inc/api.php",
    "/var/www/html/wp-content/themes/yourparty-tech/inc/api.php"
)

Write-Host "Uploading api.php to PVE Host..."
scp -o BatchMode=yes $localPath root@${PVE_HOST}:$remoteTmp

foreach ($path in $paths) {
    Write-Host "Pushing to $path ..."
    # Check if dir exists first? No, just try push.
    # pct push fail shouldn't stop us from trying the other.
    try {
        ssh root@$PVE_HOST "pct push 207 $remoteTmp $path"
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  SUCCESS: Deployed to $path" -ForegroundColor Green
        }
        else {
            Write-Host "  FAILED target $path" -ForegroundColor Red
        }
    }
    catch {
        Write-Host "  Error pushing to $path"
    }
}

ssh root@$PVE_HOST "rm $remoteTmp"

Write-Host "Done."
