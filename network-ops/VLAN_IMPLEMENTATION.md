# Proxmox VLAN & Firewall Implementation

## Container-Klassifizierung

### VLAN 20 - DMZ (Öffentlich erreichbar)
- CT 103: npm (.175) - Reverse Proxy
- CT 130: mail-relay - SMTP
- CT 207: radio-wordpress-prod (.207)
- CT 211: radio-api (.211)

### VLAN 40 - INTERN (Nur intern erreichbar)
- CT 100: grafana (.100)
- CT 108: vaultwarden (.108)
- CT 110: n8n (.110)
- CT 120: fileserver
- VM 360: homeassistant (.67)

### VLAN 50 - DATABASE (Nur von DMZ/INTERN)
- CT 202: mongodb-primary (.222)
- CT 208: mariadb-server (.228)

### VLAN 10 - INFRASTRUKTUR (Management)
- CT 101: adguard (.174) - DNS für alle
- CT 106: wireguard (.186) - VPN
- CT 109: pbs (.109) - Backup

---

## Firewall-Gruppen

### Gruppe: dmz-servers
Erlaubt:
- IN: 80, 443 (HTTP/S)
- OUT: 3306, 27017 (zu Datenbanken)
Verboten:
- Zugriff auf INTERN/INFRASTRUKTUR

### Gruppe: database-servers
Erlaubt:
- IN: 3306, 27017 (von DMZ, INTERN)
Verboten:
- Alle ausgehenden Verbindungen
- Direkter Internetzugang

### Gruppe: internal-servers
Erlaubt:
- IN: Alle Ports von MGMT
- OUT: Database, Internet
Verboten:
- Direkte eingehende Verbindungen von außen

---

## Implementierung

Da alle Container auf demselben vmbr0 sind, nutzen wir:
1. **Proxmox Firewall** (bereits aktiv: enable=1)
2. **Security Groups** für Regelsets
3. **Container-spezifische Firewalls**

Keine VLAN-Tags nötig, da Software-Firewall ausreichend ist.
