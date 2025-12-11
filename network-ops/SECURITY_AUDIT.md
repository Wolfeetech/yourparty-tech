# 🔴 NETZWERK-SICHERHEITSAUDIT
**Datum**: 07.12.2025
**Scope**: 49 Geräte im 192.168.178.0/24

---

## 🚨 KRITISCHE SCHWACHSTELLEN

### 1. **Keine Netzwerk-Segmentierung**
**Risiko**: KRITISCH ⚠️⚠️⚠️

Alle Geräte (IoT, Server, Clients, Smart Home) hängen im selben Flat Network:
- **15+ Shelly-Geräte** (Smart Home) → Port 80 (HTTP unverschlüsselt)
- **Proxmox Server** (.25) → Port 8006, 22, 443 offen
- **Home Assistant** (.67) → Port 8123 offen
- **Produktions-Server** (LXC Container) → Alle im gleichen LAN

**Problem**: Wenn ein Shelly kompromittiert wird (z.B. veraltete Firmware), hat der Angreifer direkten Zugriff auf:
- Proxmox (kann VMs/Container stoppen)
- Home Assistant (kann Türschlösser/Alarme deaktivieren)
- Produktions-Datenbanken (Port 3306 offen auf mehreren Hosts)

**Best Practice**: 
- VLAN 10: Kritische Infrastruktur (Proxmox, NPM, DNS)
- VLAN 20: IoT/Smart Home (Shellys, Google Home)
- VLAN 30: Clients (PCs, Tablets, Phones)

---

### 2. **Home Assistant Extern** 
**Risiko**: HOCH ⚠️⚠️

**Domain**: `home.prinz-stockenweiler.de`
**Status**: ⚠️ Proxy-Host existiert, aber extern nicht erreichbar
**Problem**: 
- NPM Proxy-Host ist korrekt konfiguriert ✅
- DNS funktioniert (`home.prinz-stockenweiler.de` → `91.14.33.77`) ✅
- **ABER**: FritzBox Port-Forwarding fehlt oder zeigt auf falsche IP!

**Erwartung**: Ports 80/443 → 192.168.178.175 (NPM)

**Auswirkung**: 
- Keine Remote-Wartung für die Eltern möglich
- Heizungssteuerung von unterwegs funktioniert nicht

**Fix**: FritzBox Portfreigaben prüfen (siehe `HA_EXTERNAL_FIX.md`)iert
**Problem**: 
- Domain zeigt auf `yourparty.tech` (91.14.33.77)
- Aber NPM hat keinen Proxy für diese Domain
- → DNS funktioniert, Proxy fehlt

**Auswirkung**: 
- Keine Remote-Wartung für die Eltern möglich
- Heizungssteuerung von unterwegs funktioniert nicht

**Fix**: NPM Proxy-Host anlegen:
```
Domain: home.prinz-stockenweiler.de
Forward: 192.168.178.67:8123
SSL: Let's Encrypt
```

---

### 3. **Unverschlüsselte IoT-Kommunikation**
**Risiko**: MITTEL ⚠️

**Betroffene Geräte**: 15 Shellys
- Alle nur Port 80 (HTTP) offen
- Keine HTTPS-Unterstützung
- Credentials im Klartext übertragbar

**Beispiel**:
```
192.168.178.21 - routerschrankshelly (KRITISCHER POWER-SWITCH!)
192.168.178.20-52 - Weitere Shellys
```

**Problem**: Wer im WLAN ist, kann:
- Passwörter mitlesen (Wireshark)
- Shellys übernehmen
- routerschrankshelly ausschalten → Internet tot

**Mitigation (da HTTPS nicht möglich)**:
- Starke WLAN-Passwörter (WPA3 wenn möglich)
- Shellys auf separates IoT-WLAN/VLAN
- Firmware aktuell halten

---

### 4. **Offene Management-Ports**
**Risiko**: HOCH ⚠️⚠️

**192.168.178.25** (Proxmox Server):
- Port 22 (SSH) → ✅ OK, aber KeyAuth prüfen
- Port 8006 (Proxmox Web UI) → ❌ Von jedem Gerät erreichbar
- Port 3306 (MySQL) → ❌ Warum exposed?

**192.168.178.210** (AzuraCast):
- Port 445 (SMB/CIFS) → ❌ Windows File Sharing offen!
- Ports 3306, 8000, 8006, 8080, 9090 → Viele Services exposed

**Best Practice**:
- Proxmox Web UI nur über VPN (WireGuard/Tailscale) ✅ (hast du!)
- MySQL Port 3306 nur lokal binden
- SMB Port 445 schließen (außer bewusst File-Server)

---

### 5. **DHCP für kritische Infrastruktur**
**Risiko**: MITTEL ⚠️

Alle Geräte nutzen DHCP (Type: dynamisch).

**Problem bei kritischen Servern**:
- **192.168.178.25** (Proxmox) → Wenn IP wechselt, sind alle Proxy-Hosts tot
- **192.168.178.67** (Home Assistant) → Automationen brechen
- **192.168.178.110** (n8n) → Workflows fehlerhaft

**Best Practice**: DHCP-Reservierungen (oder Static IPs) für:
- `.1` - FritzBox (Gateway) ✅ 
- `.25` - Proxmox Server
- `.67` - Home Assistant
- `.100` - Grafana
- `.110` - n8n
- `.21` - **routerschrankshelly** (KRITISCH!)

---

### 6. **Unbekannte Geräte**
**Risiko**: MITTEL ⚠️

Mehrere Geräte ohne Identifikation:
```
192.168.178.28  - Unknown (MAC: b0-4a-39-0e-38-84)
192.168.178.51  - Unknown (MAC: d8-1f-12-da-f8-f7)
192.168.178.137 - Unknown (MAC: da-e5-c4-1f-e0-8b)
192.168.178.140 - Unknown (MAC: 86-bf-2d-32-8a-04)
```

**Problem**: Nicht identifizierte Geräte = potenzielle Sicherheitsrisiken.

**Action**: MAC-Adressen in FritzBox prüfen → Geräte zuordnen oder kicken.

---

### 7. **Fehlende externe Zugangskontrolle**
**Risiko**: MITTEL ⚠️

**Nginx Proxy Manager** (NPM) hat nur 3 aktive Proxies:
- `radio.yourparty.tech`
- `yourparty.tech`
- (Weitere?)

**Problem**:
- Kein Proxy für `home.prinz-stockenweiler.de`
- Keine Fail2Ban-Integration erkennbar
- Keine Rate-Limiting-Konfiguration sichtbar

**Best Practice**:
- Fail2Ban für wiederholte Login-Versuche
- Rate Limiting (max 10 req/s pro IP)
- Geo-Blocking für sensible Services (nur DE erlauben)

---

## ✅ POSITIVE FUNDE

1. **Tailscale VPN** installiert (100.73.11.7) ✅
2. **WireGuard** läuft (Container 106) ✅
3. **Let's Encrypt SSL** auf Proxies ✅
4. **Backups** vorhanden (PBS Container 109) ✅
5. **Auto-On** bei routerschrankshelly konfiguriert ✅

---

## 📋 SOFORT-MAẞNAHMEN (Priorität)

1. ⚠️⚠️⚠️ **Home Assistant Proxy** einrichten (Eltern brauchen Zugriff!)
2. ⚠️⚠️ **DHCP-Reservierungen** für kritische IPs (.25, .67, .21)
3. ⚠️⚠️ **MySQL Port 3306** schließen (nur localhost)
4. ⚠️ **Unbekannte Geräte** identifizieren

## 🔧 MITTELFRISTIG (2 Monate vor Auszug)

5. **VLAN-Segmentierung** planen (IoT trennen)
6. **Firewall-Regeln** verfeinern
7. **Shelly Firmware** auf allen Geräten aktualisieren
8. **Fail2Ban** auf NPM konfigurieren

---

**Bereit für** `NETWORK_HARDENING.md` **mit Step-by-Step Fixes?**
