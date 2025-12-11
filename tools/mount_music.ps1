# Mount AzuraCast Music Folder to Drive M:
$Server = "192.168.178.210"
$Share = "music"
$Drive = "M:"
$Path = "\\$Server\$Share"

Write-Host "Attempting to connect to AzuraCast Music Storage ($Path)..." -ForegroundColor Cyan

# Check if drive exists
if (Get-PSDrive -Name $Drive.TrimEnd(':') -ErrorAction SilentlyContinue) {
    Write-Host "Drive $Drive is already mapped. Removing old mapping..." -ForegroundColor Yellow
    Remove-PSDrive -Name $Drive.TrimEnd(':') -Force -ErrorAction SilentlyContinue
    net use $Drive /delete /y | Out-Null
}

# Test connection
if (!(Test-Connection -ComputerName $Server -Count 1 -Quiet)) {
    Write-Host "Error: Server $Server is not reachable. Check VPN or Network." -ForegroundColor Red
    exit
}

# Attempt Mount (Try Guest first/Current Creds)
Write-Host "Mounting $Path to $Drive..."
try {
    New-PSDrive -Name $Drive.TrimEnd(':') -PSProvider FileSystem -Root $Path -Persist -ErrorAction Stop | Out-Null
    Write-Host "Success! Connected to $Drive" -ForegroundColor Green
    Invoke-Item $Drive
} catch {
    Write-Host "Authentication required." -ForegroundColor Yellow
    $Creds = Get-Credential -Message "Enter Credentials for $Server (e.g. user/pass)"
    try {
        New-PSDrive -Name $Drive.TrimEnd(':') -PSProvider FileSystem -Root $Path -Credential $Creds -Persist -ErrorAction Stop | Out-Null
        Write-Host "Success! Connected to $Drive with provided credentials." -ForegroundColor Green
         Invoke-Item $Drive
    } catch {
        Write-Host "Failed to map drive: $($_.Exception.Message)" -ForegroundColor Red
    }
}
