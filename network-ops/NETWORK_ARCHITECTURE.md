# 🏗️ Netzwerk-Architektur Plan (Best Practice)

## Ausgangslage

**Aktuell**: Flat Network (192.168.178.0/24)
- 49 Geräte in einem Netz
- IoT, Server, Clients, Smart Home alles gemischt
- Keine Segmentierung

---

## 📐 Ziel-Architektur: Segmentiertes Netzwerk

### VLAN-Struktur

| VLAN ID | Netzwerk | Name | Zweck | Geräte |
|:--------|:---------|:-----|:------|:-------|
| **1** | 192.168.178.0/24 | MGMT | Management & Clients | FritzBox, StudioPC, Laptops, Tablets |
| **10** | 10.10.10.0/24 | INFRASTRUKTUR | Kritische Server | Proxmox Host, PBS Backup |
| **20** | 10.10.20.0/24 | DMZ | Öffentlich erreichbare Dienste | NPM, WordPress, AzuraCast, Radio-API |
| **30** | 10.10.30.0/24 | IOT | Smart Home Geräte | Shellys (15+), Google Home |
| **40** | 10.10.40.0/24 | INTERN | Interne Dienste | Home Assistant, Grafana, n8n, Vaultwarden |
| **50** | 10.10.50.0/24 | DATABASE | Datenbanken | MariaDB, MongoDB |

---

## 🔒 Firewall-Regeln (Inter-VLAN)

### DMZ (VLAN 20) - Öffentlich
```
IN:  Internet → DMZ:80,443 (ALLOW)
OUT: DMZ → DATABASE:3306,27017 (ALLOW)
OUT: DMZ → INTERN:8123 (DENY - HA nicht direkt erreichbar)
OUT: DMZ → MGMT (DENY)
OUT: DMZ → IOT (DENY)
```

### IOT (VLAN 30) - Isoliert
```
IN:  INTERN:HA → IOT:* (ALLOW - HA steuert Shellys)
OUT: IOT → Internet (ALLOW - Firmware Updates)
OUT: IOT → MGMT (DENY)
OUT: IOT → DMZ (DENY)
OUT: IOT → DATABASE (DENY)
```

### INTERN (VLAN 40) - Vertrauenswürdig
```
IN:  MGMT → INTERN:* (ALLOW - Admins)
OUT: INTERN → DATABASE (ALLOW)
OUT: INTERN → IOT (ALLOW - HA steuert)
OUT: INTERN → DMZ (DENY)
```

### DATABASE (VLAN 50) - Geschützt
```
IN:  DMZ:API → DATABASE:3306,27017 (ALLOW)
IN:  INTERN:HA,Grafana → DATABASE (ALLOW)
OUT: DATABASE → * (DENY - keine Verbindungen nach außen)
```

---

## 🗺️ Geräte-Zuordnung

### VLAN 1 - MGMT (192.168.178.0/24)
| IP | Gerät | Funktion |
|:---|:------|:---------|
| .1 | fritz.box | Gateway/Router |
| .33 | wolfstudioPC | Admin Workstation |
| .40 | Pixel-8a | Smartphone |
| .35/.38/.136 | fritz.repeater | WLAN Repeater |
| .24 | brother-drucker | Drucker |

### VLAN 10 - INFRASTRUKTUR (10.10.10.0/24)
| IP | Gerät | Funktion |
|:---|:------|:---------|
| .1 | pve | Proxmox VE Host |
| .2 | pbs | Proxmox Backup Server |

### VLAN 20 - DMZ (10.10.20.0/24)
| IP | Gerät | Funktion |
|:---|:------|:---------|
| .1 | npm | Nginx Proxy Manager |
| .2 | radio-wordpress | WordPress Site |
| .3 | azuracast | Radio Server |
| .4 | radio-api | FastAPI Backend |

### VLAN 30 - IOT (10.10.30.0/24)
| IP | Gerät | Funktion |
|:---|:------|:---------|
| .1 | routerschrankshelly | 🔴 KRITISCH - Power Switch |
| .2-20 | shellyplugsg3-* | Smart Plugs |
| .21 | Google-Home-Mini | Voice Assistant |

### VLAN 40 - INTERN (10.10.40.0/24)
| IP | Gerät | Funktion |
|:---|:------|:---------|
| .1 | homeassistant | Home Assistant |
| .2 | grafana | Monitoring |
| .3 | n8n | Automation |
| .4 | vaultwarden | Password Manager |
| .5 | adguard | DNS/AdBlocker |
| .6 | wireguard | VPN Server |
| .7 | fileserver | NAS |

### VLAN 50 - DATABASE (10.10.50.0/24)
| IP | Gerät | Funktion |
|:---|:------|:---------|
| .1 | mariadb-server | MariaDB |
| .2 | mongodb-primary | MongoDB |

---

## ⚠️ Einschränkungen: FritzBox

**Problem**: Die FritzBox unterstützt **KEINE VLANs** nativ!

### Optionen:

#### Option A: Managed Switch + Proxmox VLANs
1. **Managed Switch** (z.B. TP-Link TL-SG108E ~30€) zwischen FritzBox und Proxmox
2. Proxmox konfiguriert VLANs auf `vmbr0`
3. FritzBox bleibt Default Gateway für Gäste/Clients
4. Proxmox routet zwischen VLANs

**Aufwand**: Mittel | **Kosten**: ~30€ | **Empfohlen**: ✅

#### Option B: Separate physische Netze
1. Zweite Netzwerkkarte im Proxmox
2. Ein Netz für IoT, eins für Server
3. FritzBox routet zwischen beiden

**Aufwand**: Hoch | **Kosten**: ~20€ | **Empfohlen**: ❌

#### Option C: Software-basiert (Firewall-only)
1. Keine echten VLANs
2. Proxmox Firewall regelt Traffic zwischen Containern
3. IoT bleibt im gleichen Netz, aber Firewall-Regeln einschränken

**Aufwand**: Niedrig | **Kosten**: 0€ | **Empfohlen für jetzt**: ✅

---

## 🚀 Implementierungs-Plan

### Phase 1: Software-Firewall (SOFORT)
- [x] Home Assistant extern gefixt ✅
- [ ] Proxmox Firewall aktivieren
- [ ] Firewall-Regeln für Container (DMZ, DB, etc.)
- [ ] DHCP-Reservierungen für kritische IPs

### Phase 2: VLAN-Vorbereitung (Diese Woche)
- [ ] Proxmox vmbr0 für VLAN-Tagging konfigurieren
- [ ] Container in VLANs gruppieren
- [ ] Inter-VLAN Routing testen

### Phase 3: Hardware (Optional, vor Auszug)
- [ ] Managed Switch kaufen
- [ ] FritzBox -> Switch -> Proxmox verkabeln
- [ ] VLANs auf Switch konfigurieren
- [ ] IoT-Geräte migrieren

---

## 📋 Sofort umsetzbar (Heute)

1. **Proxmox Firewall für LXC Container aktivieren**
2. **Firewall-Regeln für DMZ-Server (WordPress, API)**
3. **MySQL/MongoDB nur für erlaubte Container**
4. **DHCP-Reservierungen in FritzBox**

Soll ich mit der **Software-Firewall** anfangen?
