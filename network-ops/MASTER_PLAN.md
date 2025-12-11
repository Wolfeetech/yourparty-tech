# 📡 Operation: Fortress Stockenweiler
**Ziel**: Ein absolut wartungsfreies, sicheres und selbsterhaltendes Netzwerk für die Eltern.
**Status**: Initialisierung
**Verzeichnis**: `/network-ops/`

---

## 🛑 Phase 1: Sofort-Maßnahmen (Critical Fixes)
Sicherung des Zugangs und Behebung akuter Risiken aus dem Audit.

- [x] **1. Identitäts-Krise lösen (Hostnamen)**
    - [x] Server-Check: `/etc/hostname` ist korrekt (`pve`).
    - [ ] **FritzBox-Check**: FritzBox nennt ihn immer noch `schreibtischshelly`.
        - *Action*: Bitte in FritzBox UI einloggen -> Heimnetz -> Bearbeiten -> Name ändern.
- [x] **2. "Hintertür" einbauen (Backup Access)**
    - [x] **Tailscale** auf Proxmox installiert & Verbunden (`pve`).
    - [x] Subnet Routes (`192.168.178.0/24`) annouced.
    - [x] Tailscale IP: `100.73.11.7`
    - [ ] **Optional**: Tailscale auf StudioPC/Handy installieren für Tests.
- [x] **3. Shelly "Kill Switch" Validierung**
    - [x] **Bestätigt**: `routerschrankshelly` schaltet nach 1s automatisch wieder an.
    - [ ] Beschriftung in FritzBox anpassen: `CRITICAL-ROUTER-POWER`.

## 🛡️ Phase 2: System-Härtung (Hardening)
Vorbereitung auf 6 Monate ohne Admin vor Ort.

- [ ] **4. Server Updates & Reinigung**
    - [x] `apt update && apt upgrade` auf Proxmox (10 Pakete aktualisiert).
    - [ ] Container-Inventar erstellt (14 LXC, 1 VM). Siehe `PROXMOX_INVENTORY.md`.
    - [ ] Container korrekt initialisieren (Grafana, n8n, mail-relay).
    - [ ] "Unattended Upgrades" aktivieren? (Sicherheitsupdates automatisch).
- [ ] **5. Home Assistant Stabilisierung**
    - [x] **IP ermittelt**: `192.168.178.67` (homeassistant.fritz.box)
    - [ ] **Cloud Backup**: Google Drive Backup Add-on einrichten (Daily Snapshots).
    - [ ] **Datenbank**: Recorder bereinigen (damit SSD nicht volläuft).
    - [ ] **Watchdog**: Automation "Wenn Internet weg > Reboot Router" (Vorsicht!).

## 📄 Phase 3: "Parent-Proofing" (Usability)
Damit die Eltern nicht anrufen müssen.

- [ ] **6. Das "Eltern-Tablet"**
    - [ ] Simples HA-Dashboard bauen: Nur Licht, Heizung, Wetter. Keine Graphen, keine Logs.
    - [ ] "Alles Aus" Button (groß und rot).
- [ ] **7. Physischer Notfall-Plan**
    - [ ] Einlaminierter Zettel am Router:
        1. "Wenn gar nichts mehr geht: Stecker X ziehen, bis 10 zählen, wieder rein."
        2. "Wenn Lampe Y rot Blinkt: Sohn anrufen."

## 🧪 Phase 4: Der "Chaos Monkey" Test
Wir simulieren den Ernstfall.

- [ ] **8. Der "Stecker-Test"**
    - [ ] Wir trennen die Internet-Verbindung (WAN).
    - [ ] Wir booten den Router neu.
    - [ ] Kommt alles automatisch wieder hoch? (VPN, Server, HA, Shellys).
- [ ] **9. Der "Remote-Test"**
    - [ ] Du gehst mit dem Laptop in einen Hotspot (Handy).
    - [ ] Versuchst dich "von außen" einzuloggen.
        - Via WireGuard?
        - Via Tailscale (Backup)?
        - Kommst du auf HA? Kommst du auf die Proxmox Konsole?

---
## 🏃 Aktueller Fokus
Bitte wähle den ersten Task aus **Phase 1**. Empfehlung: **Task 2 (Tailscale)**, da dies unsere Lebensversicherung gegen Aussperren ist.
