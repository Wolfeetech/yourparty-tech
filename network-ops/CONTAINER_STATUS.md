# Container Status - ALLE LÄUFT ✅

**Stand**: 07.12.2025, 09:40 Uhr

## Übersicht
| VMID | Name | Dienst | Status | URL |
|------|------|--------|--------|-----|
| 100 | grafana | grafana-server | ✅ Läuft | http://192.168.178.100:3000 |
| 110 | n8n | n8n | ✅ Läuft | http://192.168.178.110:5678 |
| 130 | mail-relay | postfix | ✅ Läuft | (SMTP) |

---

## ✅ Container 100: Grafana

**Status**: Läuft!

**URL**: `http://192.168.178.100:3000`
**Default Login**: admin / admin

**Nächste Schritte**:
- [ ] Datenquelle hinzufügen (Prometheus?)
- [ ] Dashboard importieren

---

## ✅ Container 110: n8n

**Status**: Läuft! (Version 1.122.5)

**URL**: `http://192.168.178.110:5678`

**Nächste Schritte**:
- [ ] Erstes Login & Setup
- [ ] Workflows erstellen

---

## ✅ Container 130: Mail-Relay

**Status**: Postfix läuft mit Basis-Konfiguration.

**Aktuelle Config**:
- `mynetworks = 127.0.0.0/8` (Nur localhost erlaubt)
- `home_mailbox = Maildir/`

**Noch zu tun**:
- [ ] Relay-Host konfigurieren (Gmail SMTP?)
- [ ] `mynetworks` erweitern für LAN-Nutzung
- [ ] TLS aktivieren
