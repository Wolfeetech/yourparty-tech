# Roadmap - YourParty.tech

## 🚨 KRITISCH - SOFORT

### 0. Database Connection Error (SOLVED ✅)
- **Status**: ✅ FIXED via MariaDB Grant Flush (User `wp_user` from `192.168.178.207` allowed).
- **Verification**: Site returns HTTP 200.

### 0.1 Critical Loose Ends (MUST FIX NEXT)
- [x] **NPM Proxy 502**: `api.yourparty.tech` returns 502. FIXED via Config Update (Upstream: `192.168.178.211:8000`).
- [x] **Content Verification**: Validate Impressum/Datenschutz pages verified Live (Content visible). ✅ FIXED via UTF-8 Script
- [x] **Frontend Refactor**: Fixed Homepage Spacing & Voting UI Redundancy.

### 0.2 Frontend & Theme Cleanup
- [ ] **Fix Theme Root**: Remove artifacts (`README.md`, `SERVER_INFO.md`, `main.js`) from `/wp-content/themes/yourparty-tech/`.
- [x] **Verified `main.js`**: Ensure `src/js/main.js` is reachable.
- [x] **Mobile-perfect Control Dashboard**: Final touch for "Admin on the Dancefloor" (Responsive UI). ✅ STACKED FOOTER

### 0.3 Backend Hardening
- [x] **Secrets Management**: Audit `api.py` (Fixed).
- [x] **Dependency Management**: Locked `requirements.txt`.
- [ ] **API Security**: Global Exception Handler.

---

## 🔧 HOCH - Track-Datenbank & Musik-Management

### Zentrale Musik-Verwaltung (NEU)
**Ziel**: Alle Tracks zentral verwalten, von überall zugreifbar

#### 4. CONTENT & LIBRARY (Der Inhalt)
- [ ] **Mass Import & Access (CRITICAL)**:
    - [x] **FEHLEND**: API Container (CT 211) sieht die Musik nicht (`/var/radio/music` leer) ✅ FIXED (NFS Mount)
    - [x] 2TB HDD (in VM 210) via NFS/SMB an API (CT 211) freigeben ✅
    - [x] Musik-Sammlung verifizieren (Genres mit neuen "Vibe" Tags strukturieren).
    - [x] Auto-Tagging Script deployed and tested on CT 211 (venv ready).
    - [ ] **Drive M: Mounting (LOSE ENDE)**: Configuration in `smb.conf` on VM 210 finished, but service restart and final `net use` mount on StudioPC pending.
    - [ ] **API Access Fix (LOSE ENDE)**: AzuraCast API Key permissions need upgrade (current 403 for file list).
- [ ] **Playlisten-Design**:
    - [ ] Definieren: Was läuft morgens? Was läuft abends? (Smart Playlists in AzuraCast).
    - [ ] **Library Sync (LOSE ENDE)**: Execute `sync_library.py` after M: drive is up and API permissions are fixed.

## 5. FRONTEND POLISH (Das Gesicht)
- [x] Visualizer (Deep Space Background).
- [x] Brand Copywriting ("Sonay Audio Engineering").
- [x] Admin Dashboard (Mission Control) wired to Python Backend.
- [x] **Mobile Optimierung**: Mobile Grid fixed, Voting UI consolidated, Control Panel Footer stacked.
- [ ] **JS Standardisierung**:
    - [ ] Remove remaining `[DEBUG]` logs from `app.js` and modules.
    - [ ] Standardize DOM IDs (Clean up `immersive-` fallbacks).
    - [ ] Review `style.css` for orphaned classes (Reduce 38KB size).

### Backend API
- [x] REST-API gibt 200 zurück
- [x] Track-Daten werden geladen
- [x] History Endpoint verifizieren✅ Mock data is live

---

## 📊 SYSTEM STATUS

| Komponente | Container | Größe | Status |
|------------|-----------|-------|--------|
| WordPress | CT 207 | 20GB | ✅ Läuft (Content Updated) |
| MariaDB | CT 208 | 15GB | ✅ Läuft |
| Radio API (neu) | CT 211 | 20GB | ✅ Aktiv (Connected to DB) |
| Radio API (alt) | CT 100 | 8GB | 🗑️ DELETED |
| AzuraCast | VM 210 | 64GB + 2TB HDD | ✅ Läuft |
| MongoDB | CT 202 | 15GB | ✅ Läuft (Storing Ratings) |
| **Thin Pool** | pve/data | 157GB | ⚠️ 88.07% voll |
| **PVE Control** | Host | Script | ✅ Active (Cron) |
| **VM 103/106** | Disk | 10G/5G | 🚨 >94% VOLL |

---

## 🎯 NÄCHSTE SCHRITTE (PRIORITÄT)

2.  **🔥 Cleanup & Stability**:
    - [x] **Backup**: Full Server Snapshot (`.tar.gz`) for Backend/Frontend stored offline.
    - [ ] **Proxmox Space**: Delete unused CTs immediately.
    - [x] **Fix DB Connection (LOSE ENDE)**: `yourparty.tech` currently shows Database Error. Check CT 208 Status. (SOLVED)

2.  **💾 Datenbank Persistence (Kein Mock mehr)**:
    - [x] `/rate` Endpoint an MongoDB anschließen✅ (Verified functionality)
    - [x] `/mood-tag` Endpoint an MongoDB anschließen✅ (Verified functionality)
    - [x] **Verified**: Lifecycle Test passed. Ratings submitted -> API -> DB -> ID3 Tag.

3.  **🔄 Mission Control**:
    - [x] Dashboard zeigt jetzt Live-Daten aus der API.
    - [x] "Playlist Generator" testen (AzuraCast native .m3u export verified).
    - [x] **Stream Stability**: Rewrite of `StreamController.js` to fix paused states.
    - [x] **Community Vibe**: Backend Integration & Dislike Display completed.
    - [ ] **Flatten Subdirectories**: Clean up `yourparty-tech/yourparty-tech/` redundancy.
    - [ ] **AzuraCast Sync**: Verify why titles are lagging in frontend.

---

## 🔒 SECURITY (2025-12-17)

| Fix | Status |
|-----|--------|
| Delete malicious user `adminbockup` | ✅ DONE |
| Change DB password (`SimplePass123` → secure) | ✅ DONE |
| Reset WP admin passwords (admin, Wolf, Franz) | ✅ DONE |
| Install Wordfence 8.1.3 | ✅ DONE |
| Auto-protection scripts (watchdog) | ✅ ACTIVE |
| `SERVER_INFO.md` documentation | ✅ CREATED |

---
- [x] **Metadata Enrichment (PARTIAL)**: API fixed, `tracks` collection populated (1636 items), but UI still showing some "Unknowns".
- [ ] **SSL Polling Fix (NEW)**: `radio-api` polling AzuraCast (`192.168.178.210`) fails due to self-signed SSL cert. Need `verify=False` or internal HTTP path.
- [ ] **WebSocket Proxy Fix (NEW)**: `wss://radio.yourparty.tech/ws/radio.yourparty` returns 404/503. Check Nginx `proxy_set_header Upgrade` config.
- [ ] **Library Intel Rendering**: Frontend JS not displaying table data despite API 200 OK. Check `StatusManager.js` data mapping.

---
...
## 7. Website Professional Optimization (Dec 2025)

**Ziel**: Rechtliche Absicherung (GDPR) und professionelle Außendarstellung (Impressum, Datenschutz, Testimonials).

### 7.1 Rechtliche Compliance (Impressum & Datenschutz)
- [x] **Templates erstellt**: `page-impressum.php` und `page-datenschutz.php` im Theme deployed.
- [x] **Daten aktualisiert**: Inhaber Wolfgang Prinz, Stockenweiler 3, Hergensweiler hinterlegt.
- [x] **Seiten erstellt**: WordPress-Seiten "Impressum" (ID 15) und "Datenschutz" (ID 16) via Script erstellt.
- [ ] **Verifizierung (LOSE ENDE)**: Templates wurden zugewiesen, aber Anzeige ist noch blockiert durch Datenbank-Fehler.

### 7.2 GDPR - Cookie Consent Banner
- [x] **Implementation**: Minimalistischer Banner in `inc/cookie-consent.php` implementiert.
- [x] **Hooking**: In `functions.php` via `wp_footer` eingebunden.
- [ ] **Verifizierung (LOSE ENDE)**: Muss in Incognito-Fenster geprüft werden, sobald DB wieder läuft.

### 7.3 Content & Social Proof
- [x] **Kontakt-Email**: Auf `wolf@yourparty.tech` aktualisiert.
- [x] **Content-Refactor**: Content komplett auf "Authentic Quality" umgestellt und Umlaute gefixt (via `deploy_content_utf8.php`).
- [x] **Statische Testimonials**: In `references.php` vorbereitet (Fallback für fehlende Google API).

### [LOSE ENDEN & OFFENE AUFGABEN AUS DIESEM CHAT]
- [x] **Git Identity**: `user.name` "wwolfitec" und `user.email` "wwolfitec@gmail.com" konfiguriert.
- [ ] **🔥 CRITICAL: Database Error**: `yourparty.tech` und `wp-admin` werfen aktuell Datenbank-/WordPress-Fehler. (Muss sofort nach Chat-Archivierung geprüft werden!)
- [ ] **API Security**: Globaler Exception Handler in `backend/api.py` implementiert (geplant).
- [ ] **API Polling**: SSL Verification Problem bei AzuraCast-Abfrage (CT 211 -> VM 210) lösen.
- [ ] **Frontend Rendering**: `StatusManager.js` Datenmapping prüfen (200 OK aber keine Daten-Anzeige).
- [x] **Mission Control Mobile**: UI-Anpassungen für mobile Endgeräte (iPhone X Viewport). ✅ Done

---

## 8. MTV-Style Track Voting Implementation (Dec 2025)

**Ziel**: Ersetze abstrakte "Vibe Tagging" durch direktes Track-Voting (MTV TRL-Style).

### 8.1 Backend API (✅ COMPLETED)
- [x] **Endpoint `/vote-next-candidates`**: Liefert 3 zufällige Track-Kandidaten aus MongoDB
- [x] **Endpoint `/vote-next-track`**: Nimmt User-Votes entgegen und broadcastet via WebSocket
- [x] **Endpoint `/vote-next-winner`**: Berechnet Gewinner und resettet Voting-State
- [x] **VotingState Management**: In-Memory State mit 3-Minuten Refresh-Logik

### 8.2 Frontend UI (✅ COMPLETED)
- [x] **`live-voting.js` Rewrite**: Track-Karten statt Vibe-Buttons
- [x] **`live-voting.css` Update**: Card-Layout mit Hover-Effekten und Vote-Counts
- [x] **Widget Container**: In `front-page.php` hinzugefügt
- [ ] **End-to-End Testing**: Voting-Flow auf Live-Site testen

### 8.3 n8n Automation (⏳ IN PROGRESS)
- [x] **Workflow JSON erstellt**: 4-Node Workflow (Trigger → Candidates → Winner → Queue)
- [ ] **Import in n8n**: Workflow via UI importieren
- [ ] **AzuraCast Credential**: API Key in n8n hinterlegen
- [ ] **Activation**: Workflow aktivieren und testen

### 8.4 Critical Fixes (✅ COMPLETED)
- [x] **Heart Button**: Super-Like Funktionalität (5-Sterne Rating)
- [x] **Queue Time Display**: Echte Dauer-Berechnung statt Schätzungen
- [x] **SSL Certificate**: `radio.yourparty.tech` Cert-Mismatch behoben

**Status**: Backend + Frontend deployed, n8n Import pending

---

## 9. SSL Certificate Incident (Dec 2025)

**Problem**: `radio.yourparty.tech` zeigte `ERR_CERT_COMMON_NAME_INVALID`

### Root Cause Analysis
- **22. Dez 14:05**: Manuell falsches Cert (#14 statt #12) zugewiesen
- **User**: Wolf Prinz (via NPM UI)
- **Impact**: 6h Downtime für AzuraCast-Zugriff

### Resolution
- [x] **NPM UI Disable/Enable**: Config neu generiert mit korrektem Cert
- [x] **Incident Report**: Vollständige Dokumentation mit Prevention-Maßnahmen
- [x] **Audit Log Review**: Change-History analysiert

### Prevention Measures
- [ ] **SSL Monitoring**: Expiry Alerts in NPM aktivieren
- [ ] **Wildcard Cert**: `*.yourparty.tech` evaluieren
- [ ] **Runbook**: Quick Recovery Procedure dokumentiert

**Status**: ✅ Resolved, Dokumentation complete

---
*Zuletzt aktualisiert: 2025-12-23 11:00*
