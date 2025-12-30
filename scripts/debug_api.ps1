$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path $MyInvocation.MyCommand.Path
. "$ScriptDir\config.ps1"

Write-Host "Checking radio-api status on CT $CT_API_ID..."
ssh $SSH_OPTS "${SSH_USER}@${PVE_HOST}" "pct exec $CT_API_ID -- systemctl status radio-api"

Write-Host "`nFetching recent logs..."
ssh $SSH_OPTS "${SSH_USER}@${PVE_HOST}" "pct exec $CT_API_ID -- journalctl -u radio-api -n 50 --no-pager"
