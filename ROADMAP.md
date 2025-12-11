# Roadmap - YourParty.tech

## 🚨 KRITISCH - SOFORT

### 1. Proxmox Speicher entlasten
- **Problem**: Thin Pool bei 96.6% - System instabil (Muss noch geprüft werden)
- **Lösungsansätze**:
  - [x] **ERLEDIGT**: 1TB HDD als Proxmox Storage 'hdd-backup' eingerichtet (646GB frei)
  - [ ] Container-Größen optimieren (brauchen die alle soviel?)
  - [ ] CT 100 (alte radio-api, inaktiv) löschen → ~8GB frei
  - [ ] Nicht benötigte Container identifizieren

### 2. Frontend Integration (CRITICAL / BROKEN)
- **Status**: ⚠️ PARTIALLY BROKEN - Handover Phase
- **Current Issues**:
    - [x] **API Proxy**: Fixed (`/api/` -> `211`) via Apache config. Data available.
    - [ ] **"Station Loading" Bug**: JS fails to bind API data to DOM elements. (Suspect ID mismatch).
    - [ ] **Interactive Features**: Ratings and Visualizer dead due to JS init failure.
    - [x] **Control Dashboard**: CSS styling fixed and deployed.

---

## 🔧 HOCH - Track-Datenbank & Musik-Management

### Zentrale Musik-Verwaltung (NEU)
**Ziel**: Alle Tracks zentral verwalten, von überall zugreifbar

#### 4. CONTENT & LIBRARY (Der Inhalt)
- [ ] **Mass Import & Access (CRITICAL)**:
    - [x] **FEHLEND**: API Container (CT 211) sieht die Musik nicht (`/var/radio/music` leer) ✅ FIXED (NFS Mount)
    - [x] 2TB HDD (in VM 210) via NFS/SMB an API (CT 211) freigeben ✅
    - [x] Musik-Sammlung verifizieren (Genres mit neuen "Vibe" Tags strukturieren).
    - [ ] Auto-Tagging Script laufen lassen.
- [ ] **Playlisten-Design**:
    - [ ] Definieren: Was läuft morgens? Was läuft abends? (Smart Playlists in AzuraCast).

## 5. FRONTEND POLISH (Das Gesicht)
- [x] Visualizer (Deep Space Background).
- [x] Brand Copywriting ("Sonay Audio Engineering").
- [x] Admin Dashboard (Mission Control) wired to Python Backend.
- [ ] **Mobile Optimierung**: Testen auf iPhone/Android.

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
| Radio API (alt) | CT 100 | 8GB | ❌ Inaktiv - LÖSCHEN? |
| AzuraCast | VM 210 | 64GB + 2TB HDD | ✅ Läuft |
| MongoDB | CT 202 | 15GB | ✅ Läuft (Storing Ratings) |
| **Thin Pool** | pve/data | 157GB | ⚠️ 96.6% voll |

---

## 🎯 NÄCHSTE SCHRITTE (PRIORITÄT)

1.  **🔥 Cleanup & Stability**:
    - [x] **Backup**: Full Server Snapshot (`.tar.gz`) for Backend/Frontend stored offline.
    - [ ] **Proxmox Space**: Delete unused CTs immediately.

2.  **💾 Datenbank Persistence (Kein Mock mehr)**:
    - [x] `/rate` Endpoint an MongoDB anschließen✅ (Verified functionality)
    - [x] `/mood-tag` Endpoint an MongoDB anschließen✅ (Verified functionality)
    - [x] **Verified**: Lifecycle Test passed. Ratings submitted -> API -> DB -> ID3 Tag.

3.  **🔄 Mission Control**:
    - [x] Dashboard zeigt jetzt Live-Daten aus der API.
    - [ ] "Playlist Generator" testen (exportiert .m3u für AzuraCast).
    - [x] **Stream Stability**: Rewrite of `StreamController.js` to fix paused states.

---
*Zuletzt aktualisiert: 2024-12-11 05:15*
