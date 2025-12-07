$subnet = "192.168.178."
$start = 1
$end = 254
$ports = @(21, 22, 53, 80, 443, 8000, 8006, 8080, 8123)

Write-Output "Scanning $subnet$start - $subnet$end ..."

$results = @()

# Use parallel-ish approach with Test-Connection if possible, or just loop fast
1..254 | ForEach-Object {
    $ip = "$subnet$_"
    if (Test-Connection -ComputerName $ip -Count 1 -Quiet) {
        $hostname = "Unknown"
        try {
            $hostname = ([System.Net.Dns]::GetHostEntry($ip)).HostName
        } catch {}
        
        $openPorts = @()
        foreach ($port in $ports) {
            try {
                $tcp = New-Object System.Net.Sockets.TcpClient
                $connect = $tcp.BeginConnect($ip, $port, $null, $null)
                $wait = $connect.AsyncWaitHandle.WaitOne(100, $false)
                if ($wait -and $tcp.Connected) {
                    $openPorts += $port
                    $tcp.Close()
                }
            } catch {}
        }
        
        $obj = [PSCustomObject]@{
            IP = $ip
            Hostname = $hostname
            OpenPorts = ($openPorts -join ", ")
        }
        $results += $obj
        Write-Output "Found: $ip ($hostname) - Ports: $($obj.OpenPorts)"
    }
}

$results | ConvertTo-Json | Set-Content ".\network_inventory.json"
Write-Output "Scan Complete."
