# Proxmox Container & VM Inventar

## LXC Container (14 aktiv)
| VMID | Name | Funktion | Kritisch? |
|------|------|----------|-----------|
| 100 | grafana | Monitoring Dashboard | Nein |
| 101 | adguard | DNS Ad-Blocker | **JA** (DNS) |
| 103 | npm | Nginx Proxy Manager | **JA** (Reverse Proxy) |
| 106 | wireguard | VPN Server | **JA** (Remote Access) |
| 108 | vaultwarden | Password Manager | Mittel |
| 109 | pbs | Proxmox Backup Server | **JA** (Backups) |
| 110 | n8n | Automation Platform | Nein |
| 120 | fileserver | File Storage | Mittel |
| 130 | mail-relay | Mail Server | Nein |
| 202 | mongodb-primary | Database | **JA** (Radio-API) |
| 206 | nextcloud | Cloud Storage | Mittel |
| 207 | radio-wordpress-prod | WordPress (Radio) | Nein |
| 208 | mariadb-server | Database | **JA** (WordPress) |
| 211 | radio-api | FastAPI Backend | Nein |

## VMs (1 aktiv)
| VMID | Name | RAM | Disk | Funktion | Kritisch? |
|------|------|-----|------|----------|-----------|
| 360 | homeassistant-eltern | 4GB | 42GB | **Home Assistant** | **KRITISCH** |

---

## Optimierungs-Potenzial

### Sofort-Maßnahmen
- [ ] **Home Assistant IP ermitteln**: `ssh root@192.168.178.25 "qm guest cmd 360 network-get-interfaces"`
- [ ] **Backup-Status prüfen**: PBS (109) läuft - sind tägliche Backups konfiguriert?

### Mittelfristig (Phase 2)
- [ ] **Ressourcen-Check**: Grafana (100) wirklich nötig für die Eltern? Oder nur für dich?
- [ ] **Auto-Start validieren**: Alle kritischen Container müssen "Start at boot" haben.
- [ ] **Update-Strategie**: Unattended Upgrades nur für Security-Patches, keine Major-Versions.

### Langfristig
- [ ] **Konsolidierung**: Mail-Relay (130) + n8n (110) - werden die wirklich gebraucht?
