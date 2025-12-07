# Netzwerk-Vorbereitung "Alopri" & Stockenweiler
**Ziel**: Robustes, fernwartbares Netzwerk für Eltern (Rentner) nach Auszug.
**Zeitrahmen**: 2 Monate bis Auszug.

## 1. Remote-Zugang (Connectivity)
Das Wichtigste ist der Zugang. Wenn dieser ausfällt, ist keine Fernwartung möglich.
- [ ] **Primärer Zugang (WireGuard)**: Besteht bereits/in Arbeit. Muss stabil laufen.
- [ ] **Notfall-Zugang (Backup)**: Installation von **Tailscale** oder **Cloudflare Tunnel** auf dem Home Assistant oder Server.
    - *Warum?* Wenn WireGuard config kaputt geht oder Port-Forwarding spinnt, braucht man einen Weg rein, der keine Portfreigaben benötigt.
- [ ] **DynDNS Stabilisierung**: Sicherstellen, dass die externe IP immer aktuell ist (MyFritz oder Cloudflare Updater).

## 2. Hardware & Ausfallsicherheit (Self-Healing)
Eltern können keine komplexen Restarts durchführen.
- [ ] **Automatischer Reboot**: Cronjobs für regelmäßige Reboots (falls nötig) oder Health-Checks.
- [ ] **"Not-Aus" / Hard Reset**:
    - Hast du smarte Steckdosen (Zigbee/WiFi) vor dem Server/Router?
    - *Idee*: Eine Steckdose, die sich *automatisch* aus- und wieder einschaltet, wenn das Internet weg ist (Ping Watchdog).
- [ ] **USV (UPS)**: Gibt es eine Notstromversorgung? Falls nein, prüfen ob sinnvoll für kurzen Brownout-Schutz.

## 3. Home Assistant (HA)
- [ ] **Backups**: "Home Assistant Google Drive Backup" Add-on einrichten.
    - Sichert Snapshots automatisch in die Cloud. Lebensretter!
- [ ] **Remote UI**: Nabu Casa oder Cloudflare Tunnel für Zugriff auf HA App ohne VPN (für die Eltern unterwegs/dich).
- [ ] **Updates**: Auto-Update deaktivieren? (Lieber kontrolliert updaten als kaputtes Update automatisch laden).

## 4. Dokumentation & "Parent-Friendly" Interface
- [ ] **Physischer "Notfall-Zettel"**: 
    - Welche Stecker dürfen gezogen werden?
    - Welche Lampen müssen leuchten?
- [ ] **Vereinfachtes Dashboard**: Hat HA ein einfaches Dashboard für die Eltern?

## 5. Inventur
Aktueller Status:
- **Router**: FritzBox? IP: 192.168.178.1
- **Server**: Proxmox? IP: 192.168.178.xxx
- **Dienste**: HomeAssistant, AdGuard/PiHole?

---
## Nächste Schritte
1. Backup-VPN (Tailscale) einrichten.
2. HA Cloud Backups prüfen.
3. Inventurliste vervollständigen.
