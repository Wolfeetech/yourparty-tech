# Studio Laptop VPN Integration

## ✅ Status: WireGuard Server läuft!

Der WireGuard Server auf Container 106 ist **aktiv** und funktioniert. Ich habe die Config erfolgreich abgerufen.

## 📋 Was du brauchst

### 1. Generiere einen neuen Client-Key auf dem Studio Laptop

```bash
# Auf Ubuntu Studio:
sudo apt install wireguard-tools
wg genkey | tee privatekey | wg pubkey > publickey
```

Das erzeugt zwei Dateien:
- `privatekey` → Kommt in deine Client-Config
- `publickey` → Muss auf dem Server hinzugefügt werden

### 2. Client-Config erstellen

Erstelle auf dem Laptop: `/etc/wireguard/wg0.conf`

```ini
[Interface]
Address = 10.0.0.10/24
PrivateKey = <INHALT_VON_privatekey>
DNS = 192.168.178.1

[Peer]
PublicKey = Lo2CU0DoAIB8J25bNc6M4Rg=
Endpoint = yourparty.tech:51820
AllowedIPs = 192.168.178.0/24, 10.0.0.0/24
PersistentKeepalive = 25
```

**Ersetze** `<INHALT_VON_privatekey>` mit dem Inhalt deiner generierten `privatekey` Datei.

### 3. Server-Config aktualisieren

Auf dem **Server** (via SSH):

```bash
ssh root@192.168.178.25
pct exec 106 -- nano /etc/wireguard/wg0.conf
```

Füge am Ende hinzu:

```ini
[Peer]
# Studio Laptop
PublicKey = <INHALT_VON_publickey>
AllowedIPs = 10.0.0.10/32
```

**Ersetze** `<INHALT_VON_publickey>` mit dem Inhalt deiner generierten `publickey` Datei.

Dann WireGuard neu starten:

```bash
pct exec 106 -- wg-quick down wg0
pct exec 106 -- wg-quick up wg0
```

### 4. Verbindung auf dem Laptop starten

```bash
sudo wg-quick up wg0
```

Teste die Verbindung:

```bash
ping 192.168.178.25  # Proxmox Host
ping 10.0.0.1        # WireGuard Server
```

## 🔥 Wichtig: Portfreigabe

Der Port **51820 UDP** muss in der FritzBox auf `192.168.178.25` (Proxmox) weitergeleitet sein, damit du von außen verbinden kannst.

## ✅ Fertig!

Sobald die Verbindung steht, hast du vollen Zugriff auf das gesamte Netzwerk (192.168.178.0/24).

---

**Alternative**: Wenn du Tailscale schon installiert hast (siehe `VPN_ACCESS.md`), brauchst du WireGuard eigentlich nicht mehr. Tailscale ist einfacher und braucht keine Portfreigabe.
