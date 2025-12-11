$subnet = "192.168.178."
$commonPorts = @(21, 22, 23, 53, 80, 443, 445, 554, 1883, 3000, 3306, 5000, 5678, 8000, 8006, 8080, 8123, 8443, 9090)
$results = @()

# Get all IPs from ARP cache first
$arpEntries = arp -a | Select-String "192\.168\.178\.\d+" | ForEach-Object {
    if ($_ -match "(\d+\.\d+\.\d+\.\d+)\s+([a-f0-9-]+)\s+(\w+)") {
        @{
            IP   = $matches[1]
            MAC  = $matches[2]
            Type = $matches[3]
        }
    }
}

Write-Output "Scanning $($arpEntries.Count) devices..."
Write-Output "============================================"

foreach ($entry in $arpEntries) {
    $ip = $entry.IP
    if ($ip -eq "192.168.178.255") { continue }
    
    # DNS Lookup
    $hostname = "Unknown"
    try {
        $hostname = ([System.Net.Dns]::GetHostEntry($ip)).HostName
    }
    catch {}
    
    # Port Scan
    $openPorts = @()
    foreach ($port in $commonPorts) {
        try {
            $tcp = New-Object System.Net.Sockets.TcpClient
            $connect = $tcp.BeginConnect($ip, $port, $null, $null)
            $wait = $connect.AsyncWaitHandle.WaitOne(50, $false)
            if ($wait -and $tcp.Connected) {
                $openPorts += $port
            }
            $tcp.Close()
        }
        catch {}
    }
    
    # Determine device type based on MAC prefix
    $macPrefix = $entry.MAC.Substring(0, 8).ToUpper().Replace("-", ":")
    $vendor = switch -Wildcard ($macPrefix) {
        "8C:BF:EA*" { "Shelly" }
        "D4:D4:DA*" { "Shelly" }
        "34:CD:B0*" { "Shelly" }
        "AC:15:18*" { "Shelly" }
        "BC:24:11*" { "Proxmox/LXC" }
        "E0:08:55*" { "AVM/FritzBox" }
        "10:62:E5*" { "Intel Server" }
        "48:D6:D5*" { "Google" }
        "C8:94:02*" { "Brother" }
        "E4:B0:63*" { "Samsung" }
        default { "Unknown" }
    }
    
    # Determine function
    $function = switch ($hostname) {
        { $_ -like "*fritz.box*" -and $ip -eq "192.168.178.1" } { "GATEWAY/ROUTER" }
        { $_ -like "*shelly*" } { "Smart Home Switch" }
        { $_ -like "*repeater*" } { "WiFi Repeater" }
        { $_ -like "*home*assistant*" } { "HOME ASSISTANT" }
        { $_ -like "*drucker*" -or $_ -like "*printer*" } { "Printer" }
        { $_ -like "*Google*" } { "Smart Speaker" }
        { $_ -like "*Pixel*" } { "Smartphone" }
        default { "Unknown" }
    }
    
    $obj = [PSCustomObject]@{
        IP        = $ip
        Hostname  = $hostname
        MAC       = $entry.MAC
        Vendor    = $vendor
        OpenPorts = ($openPorts -join ", ")
        Function  = $function
        Type      = $entry.Type
    }
    $results += $obj
    
    $portStr = if ($openPorts.Count -gt 0) { $openPorts -join "," } else { "-" }
    Write-Output "$ip | $hostname | $vendor | Ports: $portStr"
}

# Sort by IP
$results = $results | Sort-Object { [version]$_.IP }

# Export to JSON
$results | ConvertTo-Json | Set-Content ".\network-ops\full_inventory.json"

# Export to Markdown table
$mdOutput = @"
# Vollständiges Netzwerk-Inventar
**Scan-Datum**: $(Get-Date -Format "yyyy-MM-dd HH:mm")
**Geräte gefunden**: $($results.Count)

## Alle Geräte

| IP | Hostname | Vendor | Ports | Funktion | MAC |
|:---|:---------|:-------|:------|:---------|:----|
"@

foreach ($r in $results) {
    $mdOutput += "`n| $($r.IP) | $($r.Hostname) | $($r.Vendor) | $($r.OpenPorts) | $($r.Function) | $($r.MAC) |"
}

$mdOutput | Set-Content ".\network-ops\FULL_NETWORK_INVENTORY.md"

Write-Output ""
Write-Output "============================================"
Write-Output "Scan complete. Results saved to:"
Write-Output "- network-ops/full_inventory.json"
Write-Output "- network-ops/FULL_NETWORK_INVENTORY.md"
