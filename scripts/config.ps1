# YourParty Tech - Centralized Configuration (SSOT)

# Local Network
$PVE_HOST = "192.168.178.25"
$SSH_USER = "root"

# Container IDs
$CT_WEB_ID = "207"
$CT_API_ID = "211"

# Remote Paths
$THEME_DIR_NAME = "yourparty-tech"
$REMOTE_THEME_PATH = "/var/www/html/wp-content/themes/$THEME_DIR_NAME"
$REMOTE_API_PATH = "/opt/radio-api"

# SSH Options
$SSH_OPTS = @("-o", "BatchMode=yes", "-o", "ConnectTimeout=5")

Write-Host "Loaded Configuration: PVE=$PVE_HOST | API=$CT_API_ID | WEB=$CT_WEB_ID" -ForegroundColor DarkGray
