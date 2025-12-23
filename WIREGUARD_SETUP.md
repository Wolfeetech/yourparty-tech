# WireGuard Neuerstellung (Emergency Kit)

Da die alten Keys im LXC Container eingeschlossen sind, ist hier der schnellste Weg, eine **neue, funktionierende WireGuard-Instanz** aufzusetzen, die wir sofort kontrollieren können.

Wir nutzen **WG-Easy** (Docker), da es eine Web-Oberfläche hat, wo du die Config für deinen Laptop einfach herunterladen kannst.

## 1. Voraussetzungen
Du musst dich **einmalig** via Tailscale oder direktem Netzwerk auf einen Docker-fähigen Host verbinden (z.B. VM 207 - WordPress Server, oder VM 210).

## 2. Setup (auf dem Server)
Erstelle einen Ordner und eine `docker-compose.yml`:

```bash
mkdir -p ~/wireguard
cd ~/wireguard
nano docker-compose.yml
```

Füge diesen Inhalt ein:

```yaml
version: "3.8"
services:
  wg-easy:
    environment:
      # ⚠️ Ersetze 'DEINE_PUBLIC_IP' mit deiner WAN IP oder Dyndns (z.B. yourparty.tech)
      - WG_HOST=yourparty.tech
      - PASSWORD=DeinSicheresPasswort123
      - WG_PORT=51820
      - WG_DEFAULT_ADDRESS=10.8.0.x
      - WG_DEFAULT_DNS=1.1.1.1
    image: ghcr.io/wg-easy/wg-easy
    container_name: wg-easy
    volumes:
      - .:/etc/wireguard
    ports:
      - "51820:51820/udp"
      - "51821:51821/tcp"
    restart: unless-stopped
    cap_add:
      - NET_ADMIN
      - SYS_MODULE
    sysctls:
      - net.ipv4.ip_forward=1
      - net.ipv4.conf.all.src_valid_mark=1
```

Starte den Server:
```bash
docker-compose up -d
```

## 3. Config herunterladen
1. Öffne im Browser: `http://<SERVER-IP>:51821`
2. Logge dich ein mit dem Passwort (`DeinSicheresPasswort123`).
3. Klicke auf **"New Client"** -> Name: `StudioLaptop`.
4. Klicke auf das **Download-Icon** ⬇️.
5. Du erhältst eine `.conf` Datei.

## 4. Auf Ubuntu Studio einrichten
Kopiere die `.conf` Datei auf deinen Laptop und importiere sie:

```bash
# Entweder via GUI im Network Manager importieren
# ODER via Terminal:
sudo apt install wireguard
sudo cp StudioLaptop.conf /etc/wireguard/wg0.conf
sudo wg-quick up wg0
```

## 🔥 WICHTIG: Portfreigabe
Damit das funktioniert, muss im Router (FritzBox) der Port **51820 UDP** an die IP des Servers weitergeleitet werden, auf dem dieser Docker-Container läuft!

---

**Alternative**: Wenn du Tailscale schon hast (wie in `VPN_ACCESS.md` beschrieben), brauchst du das hier eigentlich nicht. Tailscale ist einfacher und braucht keine Portfreigabe.
