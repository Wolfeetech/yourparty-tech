# Roadmap - YourParty.tech

## 🚨 KRITISCH - SOFORT

### 1. Proxmox Speicher entlasten
- **Problem**: Thin Pool bei 96.6% - System instabil (Muss noch geprüft werden)
- **Lösungsansätze**:
  - [x] **ERLEDIGT**: 1TB HDD als Proxmox Storage 'hdd-backup' eingerichtet (646GB frei)
  - [x] Container-Größen optimieren (brauchen die alle soviel?)
  - [x] CT 100 (alte radio-api, inaktiv) löschen → ~8GB frei
  - [x] Nicht benötigte Container identifizieren (CT 100 gone)
  - [/] Migration WordPress CT 207 (Failed - Volume Error)

### 2. Frontend Integration (CRITICAL / BROKEN)
- **Status**: ✅ FIXED via modularization
- **Current Issues**:
    - [x] **API Proxy**: Fixed (`/api/` -> `211`) via Apache config. Data available.
    - [x] **"Station Loading" Bug**: Fixed via StatusManager.js.
    - [x] **Interactive Features**: Visualizer Pro & Mood Tagging active.
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
- [x] **Mobile Optimierung**: Tested on iPhone X viewport (375x812).

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
| **Thin Pool** | pve/data | 157GB | ⚠️ 92.79% voll |
| **PVE Control** | Host | Script | ✅ Active (Cron) |

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
    - [x] "Playlist Generator" testen (AzuraCast native .m3u export verified).
    - [x] **Stream Stability**: Rewrite of `StreamController.js` to fix paused states.

---
*Zuletzt aktualisiert: 2025-12-15 07:13*
