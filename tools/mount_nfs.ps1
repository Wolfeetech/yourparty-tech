# Versuch, NFS Share zu mounten (Passwortlos)
$Server = "192.168.178.210"
$SharePath = "/mnt/music_hdd" # NFS Export Path
$Drive = "M:"

Write-Host "Versuche NFS Mount auf $Server..." -ForegroundColor Cyan

# Check if NFS Client is installed
if (Get-Command "mount" -ErrorAction SilentlyContinue) {
    Write-Host "NFS Client gefunden." -ForegroundColor Green
    
    # Unmap existing
    if (Get-PSDrive -Name "M" -ErrorAction SilentlyContinue) {
        net use M: /delete /y | Out-Null
    }
    
    # Mount
    # Syntax: mount -o anon \\192.168.178.210\mnt\music_hdd M:
    # Note: Windows NFS requires mapping / to \ in path usually
    $NfsPath = "\\$Server$($SharePath.Replace('/','\'))"
    
    Write-Host "Mounte $NfsPath auf $Drive..."
    
    cmd /c "mount -o anon $Server`:$SharePath $Drive"
    
    if ($?) {
        Write-Host "✅ Erfolg! M: ist via NFS verbunden." -ForegroundColor Green
    }
    else {
        Write-Host "❌ NFS Mount fehlgeschlagen. Prüfen Sie, ob 'Client für NFS' in Windows Features aktiv ist." -ForegroundColor Red
        Write-Host "Alternativ: Nutzen Sie WinSCP oder FileZilla."
    }
}
else {
    Write-Host "❌ 'mount' Befehl nicht gefunden." -ForegroundColor Red
    Write-Host "Bitte aktivieren Sie das Feature 'Client für NFS' in Windows:"
    Write-Host "1. Start -> 'Windows-Features aktivieren oder deaktivieren'"
    Write-Host "2. 'Dienste für NFS' -> 'Client für NFS' anhaken -> OK"
}
