$ErrorActionPreference = "Stop"

Write-Host "Uploading API fix..."
scp -o BatchMode=yes -o ConnectTimeout=5 backend/api.py root@192.168.178.25:/tmp/api.py

Write-Host "Executing remote maintenance..."
# Construct command as single line to avoid CRLF issues
$remoteCmd = "echo '[INFO] Trimming LXC Containers...'; " +
"pct fstrim 103 || echo 'Failed to trim 103'; " +
"pct fstrim 106 || echo 'Failed to trim 106'; " +
"pct fstrim 110 || echo 'Failed to trim 110'; " +
"echo '[INFO] Trimming AzuraCast VM...'; " +
"qm guest exec 210 -- fstrim -va || echo 'Failed to trim VM 210'; " +
"echo '[INFO] Deploying API Fix to CT 211...'; " +
"pct push 211 /tmp/api.py /opt/radio-api/api.py; " +
"echo '[INFO] Restarting Radio API...'; " +
"pct exec 211 -- systemctl restart radio-api || pct exec 211 -- pkill -f uvicorn; " +
"echo '[INFO] Cleaning up...'; " +
"rm /tmp/api.py; " +
"echo '[INFO] Final Storage Check:'; " +
"lvs -a -o name,data_percent | grep data"

ssh -o BatchMode=yes -o ConnectTimeout=5 root@192.168.178.25 $remoteCmd
