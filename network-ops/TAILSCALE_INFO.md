# Tailscale Netzwerk-Konfiguration

## Gerät: pve (Proxmox Server)
- **Tailscale IP**: `100.73.11.7`
- **LAN IP**: `192.168.178.25`
- **Funktion**: Subnet Router für `192.168.178.0/24`

## Zugriff von außen
1. **Tailscale auf Windows installieren**: [Download](https://tailscale.com/download/windows)
2. Mit dem gleichen Account einloggen (`wwolfitec@gmail.com`)
3. Sobald verbunden, kannst du auf **alle** Geräte im Heimnetz zugreifen:
   - Proxmox Web UI: `https://192.168.178.25:8006`
   - FritzBox: `http://192.168.178.1`
   - Home Assistant: `http://192.168.178.XX` (IP noch zu ermitteln)
   - Alle Shellys über ihre lokalen IPs

## Vorteile
- **Kein Portforwarding** nötig
- **Verschlüsselt** (WireGuard-Protokoll)
- **Funktioniert überall**: Auch wenn die FritzBox die WireGuard-Ports blockiert
- **Mesh-Netzwerk**: Alle deine Geräte (Laptop, Handy, Server) können sich direkt erreichen

## Notfall-Zugang
Wenn du ausgesperrt bist:
1. Tailscale auf dem Handy öffnen
2. SSH zu `100.73.11.7` (pve)
3. Von dort aus alles reparieren

## Nächste Schritte
- [ ] Tailscale auf dem StudioPC installieren (für Tests)
- [ ] Tailscale auf dem Handy installieren (Notfall-Zugang)
- [ ] Optional: Tailscale auf einem Raspberry Pi als "Always-On" Backup
