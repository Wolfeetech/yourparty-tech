# Network Hardening - Fixes

## Fix #1: Home Assistant Proxy einrichten

**Problem**: `home.prinz-stockenweiler.de` hat keinen NPM Proxy-Host

**Manuelle Schritte** (NPM Web UI):
1. Öffne Nginx Proxy Manager: `http://192.168.178.103:81`
2. Login (Admin Credentials)
3. **Proxy Hosts** → **Add Proxy Host**
4. Konfiguration:
   ```
   Domain Names: home.prinz-stockenweiler.de
   Scheme: http
   Forward Hostname/IP: 192.168.178.67
   Forward Port: 8123
   Block Common Exploits: ✅
   Websockets Support: ✅ (WICHTIG für HA!)
   
   SSL Tab:
   - SSL Certificate: Request new Let's Encrypt
   - Force SSL: ✅
   - HTTP/2: ✅
   ```
5. Save

**Alternative** (wenn NPM UI nicht erreichbar):
Ich kann die Config direkt auf dem Server anlegen.

---

## Fix #2: DHCP-Reservierungen (FritzBox)

**Kritische IPs** die statisch werden müssen:

| IP | Hostname | MAC | Funktion |
|:---|:---------|:----|:---------|
| 192.168.178.25 | pve | 10-62-e5-14-97-ed | Proxmox Server |
| 192.168.178.67 | homeassistant | bc-24-11-8e-fa-a9 | Home Assistant |
| 192.168.178.21 | routerschrankshelly | d4-d4-da-ed-1b-64 | POWER SWITCH! |
| 192.168.178.100 | grafana | bc-24-11-7b-84-c1 | Monitoring |
| 192.168.178.110 | n8n | bc-24-11-6f-2b-f3 | Automation |

**Anleitung**:
1. FritzBox UI: `http://192.168.178.1`
2. Heimnetz → Netzwerk → Netzwerkeinstellungen
3. Bei jedem Gerät: "Diesem Netzwerkgerät immer die gleiche IPv4-Adresse zuweisen" ✅

---

## Fix #3: MySQL Ports schließen

**Container mit offenen MySQL Ports**:
- 192.168.178.67 (HA)
- 192.168.178.110 (n8n)  
- 192.168.178.200+

**Fix**: MySQL nur auf localhost binden.

Soll ich mit Fix #1 anfangen?
