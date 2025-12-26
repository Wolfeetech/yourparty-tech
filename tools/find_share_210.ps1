$Server = "192.168.178.210"
$User = "root" 
$Pass = "yourparty"
$Drive = "Y:"

$Shares = @("music", "music_hdd", "station_media", "azuracast", "share", "public", "data", "files", "radio", "mp3", "media", "station1", "station_1")

# Clean up
net use $Drive /delete /y 2>$null
net use \\$Server /delete /y 2>$null

Write-Host "Attempting to connect to $Server..."

foreach ($Share in $Shares) {
    $Path = "\\$Server\$Share"
    Write-Host "Trying $Path..."
    net use $Drive $Path /USER:$User $Pass 2>$null
    if ($?) {
        Write-Host "SUCCESS! Mounted $Path to $Drive" -ForegroundColor Green
        exit 0
    }
    
    # Try without auth (Guest)
    net use $Drive $Path 2>$null
    if ($?) {
        Write-Host "SUCCESS (Guest)! Mounted $Path to $Drive" -ForegroundColor Green
        exit 0
    }
}
Write-Host "All guesses failed." -ForegroundColor Red
exit 1
