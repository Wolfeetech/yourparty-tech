$Server = "192.168.178.210"
$User = "root"
$Pass = "yourparty" # Recovered/Reset password
$Drive = "M:"

$Shares = @("music", "music_hdd", "station_media", "azuracast", "share", "public", "data", "files", "radio", "mp3", "media", "station1", "station_1")

# Clean up
net use $Drive /delete /y 2>$null
net use \\$Server /delete /y 2>$null

# Authenticate IPC$
Write-Host "Authenticating..."
net use \\$Server /USER:$User $Pass
if (!$?) { Write-Error "Authentication failed"; exit }

foreach ($Share in $Shares) {
    $Path = "\\$Server\$Share"
    Write-Host "Trying $Path..."
    net use $Drive $Path /PERSISTENT:YES
    if ($?) {
        Write-Host "SUCCESS! Mounted $Path to $Drive" -ForegroundColor Green
        exit 0
    }
}
Write-Host "All guesses failed." -ForegroundColor Red
