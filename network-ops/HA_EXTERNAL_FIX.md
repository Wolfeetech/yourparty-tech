# 🎯 Home Assistant Extern - Diagnose

## ✅ Was funktioniert:

1. **Proxy-Host existiert** in NPM:
   - Domain: `home.prinz-stockenweiler.de`
   - Forward: `192.168.178.67:8123`
   - SSL: Let's Encrypt ✅
   - Websockets: ✅
   - Force SSL: ✅

2. **DNS-Auflösung funktioniert**:
   ```
   home.prinz-stockenweiler.de → yourparty.tech → 91.14.33.77
   ```

3. **Home AssistantLokal erreichbar**:
   - `http://192.168.178.67:8123` → Status 200 ✅

## ❌ Das Problem:

**Port Forwarding fehlt oder ist falsch**!

Die FritzBox leitet Ports 80/443 aktuell nicht auf `192.168.178.175` (NPM) weiter.

## 🔧 Fix: FritzBox Port-Forwarding prüfen

### Erwartete Konfiguration:

| Service | Extern | → | Intern | Gerät |
|:--------|:-------|:-:|:-------|:------|
| HTTP | 80 | → | 80 | 192.168.178.175 (NPM) |
| HTTPS | 443 | → | 443 | 192.168.178.175 (NPM) |

### Anleitung:

1. FritzBox UI: `http://192.168.178.1`
2. **Internet → Freigaben → Portfreigaben**
3. Prüfen ob existiert:
   - "HTTP" → 80 → 192.168.178.175
   - "HTTPS" → 443 → 192.168.178.175

4. Falls **NICHT vorhanden** → Anlegen:
   - Neue Portfreigabe
   - Gerät: NPM (`.175`)
   - Port: 80 (extern) → 80 (intern)
   - Port: 443 (extern) → 443 (intern)

5. **DynDNS** prüfen:
   - Ist `yourparty.tech` mit aktueller WAN-IP konfiguriert?
   - MyFritz oder Cloudflare?

---

## Alternative Test (von außen):

Kannst du vom **Handy-Hotspot** (nicht im WLAN) testen:
```
https://home.prinz-stockenweiler.de
```

Wenn das nicht geht → Port-Forwarding fehlt definitiv.
