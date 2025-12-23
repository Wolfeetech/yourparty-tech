# VPN Zugang für Ubuntu Studio Laptop

Da du dringend Zugang brauchst, ist **Tailscale** die schnellste und stabilste Methode, da es bereits auf dem Proxmox-Server (`pve`) eingerichtet ist und das lokale Netzwerk (`192.168.178.0/24`) routet.

## Option A: Tailscale (Empfohlen & Schnellste)

Tailscale ist auf dem Server bereits konfiguriert (`TAILSCALE_INFO.md`) und erlaubt sofortigen Zugriff auf alles (Proxmox, SSH, FritzBox) ohne komplexe Config-Dateien.

### 1. Installation auf Ubuntu Studio
Öffne ein Terminal auf deinem Laptop und führe aus:

```bash
curl -fsSL https://tailscale.com/install.sh | sh
```

### 2. Verbinden
Starte Tailscale und logge dich ein:

```bash
sudo tailscale up
```

- Klicke auf den Link im Terminal.
- Logge dich mit **`wwolfitec@gmail.com`** ein (derselbe Account wie auf dem Server).
- **Wichtig**: Akzeptiere das Gerät im Admin-Panel, falls gefragt (meist aber automatisch).

### 3. Fertig!
Du solltest nun direkten Zugriff auf alle IP-Adressen haben, als wärst du zuhause:
- **Proxmox**: `https://192.168.178.25:8006`
- **SSH**: `ssh request@192.168.178.25`
- **Apps**: Alle Dienste unter ihren normalen IPs.

---

## Option B: WireGuard (Falls zwingend erforderlich)

Der WireGuard Container läuft auf **LXC 106**. 
**Problem**: Die Config-Datei (`.conf`) liegt auf dem Server, und wir haben von hier keinen Zugriff darauf.

**Lösung**:
1.  Verbinde dich zuerst via **Tailscale** (siehe oben).
2.  Logge dich in Proxmox ein (`https://192.168.178.25:8006`).
3.  Öffne die Konsole von Container **106 (wireguard)**.
4.  Generiere einen neuen Client oder zeige einen existierenden an:
    ```bash
    # Beispiel (befehl kann abweichen, checke /root oder /etc/wireguard)
    cat /etc/wireguard/peer_studio.conf 
    # oder
    pivpn add  # falls PiVPN genutzt wurde
    ```
5.  Kopiere den Inhalt in eine Datei auf deinem Laptop (z.B. `wg0.conf`).

> **Meine Empfehlung**: Bleib bei Tailscale. Es ist robuster gegen wechselnde IPs und Firewalls.
