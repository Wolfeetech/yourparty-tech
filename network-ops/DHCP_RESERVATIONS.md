# DHCP-Reservierungen - Kritische IPs fixieren

## ⚠️ Warum wichtig?

Wenn kritische Server ihre IP ändern:
- Alle Proxy-Hosts in NPM brechen
- Home Assistant Automationen finden Geräte nicht mehr
- n8n Workflows schlagen fehl

## 📋 IPs die STATISCH werden müssen:

| Priorität | IP | Hostname | MAC | Funktion |
|:----------|:---|:---------|:----|:---------|
| 🔴 KRITISCH | 192.168.178.25 | pve | 10-62-e5-14-97-ed | **Proxmox Server** |
| 🔴 KRITISCH | 192.168.178.67 | homeassistant | bc-24-11-8e-fa-a9 | **Home Assistant** |
| 🔴 KRITISCH | 192.168.178.21 | routerschrankshelly | d4-d4-da-ed-1b-64 | **POWER SWITCH!** |
| 🟡 WICHTIG | 192.168.178.175 | npm | bc-24-11-91-4e-6e | Nginx Proxy Manager |
| 🟡 WICHTIG | 192.168.178.100 | grafana | (ermitteln) | Monitoring |
| 🟡 WICHTIG | 192.168.178.110 | n8n | bc-24-11-6f-2b-f3 | Automation |
| 🟢 OPTIONAL | 192.168.178.210 | azuracast | bc-24-11-de-76-67 | Radio Server |
| 🟢 OPTIONAL | 192.168.178.211 | radio-api | bc-24-11-dc-21-af | FastAPI Backend |

---

## 🔧 Anleitung: FritzBox DHCP-Reservierung

### Schritt-für-Schritt:

1. **FritzBox öffnen**: `http://192.168.178.1`
2. **Login** mit Admin-Passwort
3. Navigation: **Heimnetz** → **Netzwerk** → **Netzwerkeinstellungen**
4. **Jedes Gerät einzeln konfigurieren**:

   **Beispiel für Proxmox (.25)**:
   - Gerät in der Liste finden: `pve` oder `schreibtischshelly` (MAC: 10-62-e5-14-97-ed)
   - Bearbeiten-Stift klicken
   - ✅ **Diesem Netzwerkgerät immer die gleiche IPv4-Adresse zuweisen**
   - IP-Ad IP bestätigen: `192.168.178.25`
   - Speichern

5. **Wiederholen für alle IPs in der Tabelle oben**

---

## ⚙️ Alternative: Statische IPs auf den Servern selbst

Für LXC-Container kannst du auch direkt die Netzwerk-Config anpassen.

**Beispiel Proxmox Container**:
```bash
ssh pve "pct set 103 -net0 name=eth0,bridge=vmbr0,firewall=1,hwaddr=BC:24:11:91:4E:6E,ip=192.168.178.175/24,gw=192.168.178.1,type=veth"
```

**Vorteil**: Unabhängig von DHCP  
**Nachteil**: Mehr Verwaltungsaufwand

---

## ✅ Prüfung nach der Änderung:

Nach dem Speichern:
1. **Warte 2 Minuten**
2. **Ping-Test**:
   ```powershell
   ping 192.168.178.25  # Proxmox
   ping 192.168.178.67  # Home Assistant
   ping 192.168.178.21  # Shelly
   ```
3. **NPM-Test**: `http://192.168.178.175:81` noch erreichbar?
4. **HA-Test**: `http://192.168.178.67:8123` noch erreichbar?

---

**Soll ich die Reservierungen via SSH automatisch setzen (für die LXC Container)?**
