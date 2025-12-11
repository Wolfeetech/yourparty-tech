# 📊 Netzwerk-Härtung: Fortschritt

## ✅ Phase 1: Abgeschlossen

- [x] Netzwerk-Inventar (49 Geräte)
- [x] Sicherheitsaudit
- [x] Tailscale VPN installiert
- [x] Grafana gestartet
- [x] n8n installiert & konfiguriert
- [x] Container-Status dokumentiert

---

## 🔄 Phase 2: In Arbeit

### Fix #1: Home Assistant Extern ⚠️
- [x] NPM Proxy-Host verifiziert (existiert!)
- [x] Port-Forwarding verifiziert (existiert!)
- [ ] **Problem noch unklar** - evtl. SSL-Zertifikat oder HA-Konfiguration
  - *Status*: Funktioniert lokal, extern noch Testing nötig

### Fix #2: DHCP-Reservierungen 🟡
- [ ] Dokumentation erstellt → `DHCP_RESERVATIONS.md`
- [ ] **User-Action**: Manuell in FritzBox setzen
  - Proxmox (.25)
  - Home Assistant (.67)
  - routerschrankshelly (.21)
  - NPM (.175)

### Fix #3: MySQL Ports schließen 🔴
- [ ] Port 3306 nur auf localhost binden
- [ ] Betroffene Container:
  - 192.168.178.67 (HA)
  - 192.168.178.110 (n8n)
  - 192.168.178.200+

---

## 📋 Noch offen (Mittelfristig)

- [ ] VLAN-Segmentierung (IoT trennen)
- [ ] Fail2Ban auf NPM
- [ ] Shelly Firmware-Updates
- [ ] Unbekannte Geräte identifizieren

---

**Nächster Schritt**: Soll ich Fix #3 (MySQL Ports) automatisch durchführen?
