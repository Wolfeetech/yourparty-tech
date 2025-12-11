$ErrorActionPreference = "Stop"

function Write-Color($text, $color) {
    Write-Host $text -ForegroundColor $color
}

Write-Color "=== YourParty.tech Radio Connection Setup ===" "Cyan"
Write-Color "Dieses Skript stellt die Verbindung zum AzuraCast Server und zur Datenbank her." "Cyan"
Write-Color "" "White"

# 1. SMB Connection (Music Folder)
$SmbServer = "192.168.178.210"
$SmbShare = "music"
$Drive = "M:"

Write-Color "1. Verbinde Netzlaufwerk $Drive nach \\$SmbServer\$SmbShare..." "Yellow"

# Clean up
try { net use $Drive /delete /y 2>$null | Out-Null } catch {}

# Ask for creds
$Creds = Get-Credential -Message "Bitte geben Sie Benutzer/Passwort für den AzuraCast Server ein (z.B. root oder azuracast)"

try {
    New-PSDrive -Name "M" -PSProvider FileSystem -Root "\\$SmbServer\$SmbShare" -Credential $Creds -Persist | Out-Null
    Write-Color "✅ Laufwerk M: erfolgreich verbunden!" "Green"
}
catch {
    Write-Color "❌ Fehler beim Verbinden von M:: $($_.Exception.Message)" "Red"
    Write-Color "Überprüfen Sie das Passwort. Versuchen Sie es erneut." "Red"
    exit
}

# 2. MongoDB Connection
Write-Color "`n2. Konfiguriere Datenbank-Verbindung..." "Yellow"

$MongoHost = "192.168.178.222"
$MongoPort = "27017"

$MongoUser = Read-Host "MongoDB Benutzer (Enter für 'root')"
if (-not $MongoUser) { $MongoUser = "root" }

$MongoPass = Read-Host "MongoDB Passwort (Enter für leer)"
if ($MongoPass) {
    $MongoUri = "mongodb://$($MongoUser):$($MongoPass)@$($MongoHost):$($MongoPort)/?authSource=admin"
}
else {
    $MongoUri = "mongodb://$($MongoHost):$($MongoPort)/"
}

# Test Mongo Connection via Python script (simplest way since we have python)
$TestScript = @"
import sys
from pymongo import MongoClient
try:
    client = MongoClient('$MongoUri', serverSelectionTimeoutMS=2000)
    client.server_info()
    print('SUCCESS')
except Exception as e:
    print(f'FAIL: {e}')
    sys.exit(1)
"@

$TestFile = "test_mongo.py"
Set-Content $TestFile $TestScript

Write-Color "Teste Verbindung zu MongoDB..." "Gray"
try {
    $Result = python $TestFile
    if ($Result -match "SUCCESS") {
        Write-Color "✅ Datenbank-Verbindung erfolgreich!" "Green"
    }
    else {
        throw "Verbindung fehlgeschlagen: $Result"
    }
}
catch {
    Write-Color "❌ Datenbank-Fehler: $_" "Red"
    Write-Color "Bitte überprüfen Sie die Zugangsdaten." "Red"
    Remove-Item $TestFile -ErrorAction SilentlyContinue
    exit
}
Remove-Item $TestFile -ErrorAction SilentlyContinue

# 3. Save Configuration to .env
Write-Color "`n3. Speichere Konfiguration..." "Yellow"
$EnvContent = @"
MONGO_URI="$MongoUri"
AZURACAST_URL="http://192.168.178.210"
AZURACAST_API_KEY="9199dc63da6223190:c9f8c3a22e25932753dd3f4d57fa0d9c"
MONGO_HOST="$MongoHost"
MONGO_PORT="$MongoPort"
MONGO_INITDB_ROOT_USERNAME="$MongoUser"
MONGO_INITDB_ROOT_PASSWORD="$MongoPass"
"@

# Save to backend AND tools
Set-Content "backend\.env" $EnvContent
Set-Content "tools\.env" $EnvContent

Write-Color "✅ Konfiguration gespeichert in backend\.env" "Green"

# 4. Initial Sync
Write-Color "`n4. Starte initiale Synchronisierung der Bibliothek..." "Yellow"
python tools/sync_library.py

Write-Color "`n=== SETUP ABGESCHLOSSEN ===" "Cyan"
Write-Color "Sie können nun Tracks auf M: verwalten." "White"
Write-Color "Die Synchronisation läuft automatisch im Hintergrund (geplanter Task empfohlen)." "White"
Pause
