# Netzwerk-Inventar & Hacker-Audit
**Stand**: 07.12.2025
**Scope**: 192.168.178.0/24 (FritzBox LAN)

## 🚨 Kritische Funde ("Hacker-Report")
1.  **Identity Crisis**: Host `192.168.178.25` meldet sich als `schreibtischshelly.fritz.box`, aber Ports 8006 (Proxmox), 22 (SSH) sind offen.
    *   **Risiko**: Verwirrung bei Wartung. Man denkt, man rebootet eine Shelly, tötet aber den Server.
    *   **Maßnahme**: Hostname in FritzBox und am Server korrigieren!
2.  **IoT-Schwemme**: Viele Smart-Home Geräte (Shellys) hängen direkt im Hauptnetz mit offenem Port 80 (HTTP).
    *   `routerschrankshelly` (.21), `shellyplugsg3` (.20), etc.
    *   **Risiko**: Kein HTTPS. PW/Token fliegen im Klartext. Wenn ein Gerät kompromittiert wird, ist das ganze Netz offen.
    *   **Maßnahme**: IoT-VLAN (Langfristig) oder starke WLAN-Passwörter und Firmware-Updates (Kurzfristig).
3.  **Management-Interfaces**:
    *   `switchwozi.fritz.box` (.22): Hat Port 8080 offen. Default Credentials?!

## 🖥️ Core Infrastructure
| IP | Hostname (DNS) | Rolle (Vermutet) | Ports | Notes |
| :--- | :--- | :--- | :--- | :--- |
| **192.168.178.1** | `fritz.box` | **Gateway / Router** | 21, 53, 80, 443 | Zentrale. Zugriff absichern! |
| **192.168.178.25** | `schreibtischshelly` ⚠️ | **Proxmox Server** | **8006**, 22, 80, 443 | **Falscher Hostname!** |
| 192.168.178.33 | `wolfstudioPC` | Admin Workstation | 8000, 8080 | Dev Machine |
| 192.168.178.35 | `fritz.repeater` | WiFi Repeater | 53, 80, 443 | |
| 192.168.178.38 | `fritz.repeater` | WiFi Repeater | 53, 80, 443 | |

## 🏠 Smart Home (Shelly Army)
Wichtig für "Self-Healing":
*   `routerschrankshelly` (192.168.178.21): **Kritisch!** Hängt hier der Router dran?
    *   Wenn ja -> Perfekt für Auto-Reboot Sktipt.
    *   Wenn nein -> Unwichtig.

## 🖨️ Peripherie
*   `brother-drucker` (192.168.178.24): Firmware aktuell halten!

---
## 🛠️ Sofort-Maßnahmen
1.  **Dringend**: Hostname von `192.168.178.25` ändern. Das ist kein Shelly.
2.  **Validieren**: Ist `routerschrankshelly` (.21) wirklich die Stromversorgung vom Router/Modem?
3.  **Connectivity Check**: Tailscale auf .25 (Proxmox) installieren als "Notfall-Hintertür".
