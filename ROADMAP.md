# Roadmap - YourParty.tech

## 🚨 KRITISCH - SOFORT

### 1. Proxmox Speicher entlasten
- **Problem**: Thin Pool bei 96.6% - System instabil
- **Lösungsansätze**:
  - [x] **ERLEDIGT**: 1TB HDD als Proxmox Storage 'hdd-backup' eingerichtet (646GB frei)
  - [ ] Container-Größen optimieren (brauchen die alle soviel?)
  - [ ] CT 100 (alte radio-api, inaktiv) löschen → ~8GB frei
  - [ ] Nicht benötigte Container identifizieren

### 2. Visualizer richtig umsetzen
- **Probleme**:
  - [ ] Nur eine Hälfte sichtbar (muss volle Breite sein)
  - [x] CSS für Visualizer-Container hinzugefügt und deployt
  - [ ] Fullscreen Player komplett verloren gegangen
- **Ziel**: Professionelle, vollständige Visualizer-Implementierung

---

## 🔧 HOCH - Track-Datenbank & Musik-Management

### Zentrale Musik-Verwaltung (NEU)
**Ziel**: Alle Tracks zentral verwalten, von überall zugreifbar

#### Anforderungen:
1. **Cloud/Server-basiert**
   - [ ] Zugriff auf AzuraCast 2TB HDD von StudioPC
   - [ ] Einheitlicher Pfad für Musik auf allen Geräten
   - [ ] Nicht lokal auf einzelnen Geräten, sondern zentralisiert

2. **AzuraCast Integration**
   - [ ] One-Click "Nächster Track" direkt in AzuraCast Queue
   - [ ] Tracks durchsuchen und abspielen lassen
   - [ ] Playlist-Management

3. **Bewertungen & Tags aus Radio LIVE in Dateien schreiben**
   - [ ] Wenn Track im Radio 5 Sterne bekommt → in ID3-Tag schreiben
   - [ ] Rekordbox-kompatibel (Rating in POPM Frame)
   - [ ] Mood-Tags ebenfalls in ID3 speichern
   - [ ] Bidirektionale Sync: Radio-Bewertung ↔ Datei-Tag

#### Technische Umsetzung:
- **SMB/NFS Share** von AzuraCast HDD zum StudioPC
- **Backend-Service** der auf Rating-Events lauscht
- **ID3-Tag Writer** (mutagen/eyeD3) für Rating-Sync
- **Web-Interface** oder lokale App für Track-Verwaltung

---

## 📋 MITTEL - Website & Design

### Radio Player Design
- **Stil**: NTS Radio inspired - brutalistisch, typografisch
- [ ] Aktuellen Hintergrund beibehalten (kein schwarz)
- [ ] Eckiges Design (keine Rundungen)
- [ ] Visualizer volle Breite
- [ ] Alle Visualizer-Modi wiederherstellen:
  - Pro Spectrum
  - Precision Waveform
  - Particle Field
  - Frequency Rings
  - Energy Matrix

### Hero Section
- [x] Headline geändert: "." (authentisch, nicht aufgeblasen)

### Backend API
- [x] REST-API gibt 200 zurück
- [x] Track-Daten werden geladen
- [ ] History Endpoint verifizieren

---

## 📊 SYSTEM STATUS

| Komponente | Container | Größe | Status |
|------------|-----------|-------|--------|
| WordPress | CT 207 | 20GB | ✅ Läuft |
| MariaDB | CT 208 | 15GB | ✅ Läuft |
| Radio API (neu) | CT 211 | 20GB | ✅ Aktiv |
| Radio API (alt) | CT 100 | 8GB | ❌ Inaktiv - LÖSCHEN? |
| AzuraCast | VM 210 | 64GB + 2TB HDD | ✅ Läuft |
| MongoDB | CT 202 | 15GB | ✅ Läuft |
| Fileserver | CT 120 | 32GB | ? Prüfen |
| NPM | CT 103 | 10GB | ✅ Läuft |
| AdGuard | CT 101 | 8GB | ✅ Läuft |
| Vaultwarden | CT 108 | 10GB | ✅ Läuft |
| PBS | CT 109 | 20GB | ✅ Läuft |
| n8n | CT 110 | 10GB | ✅ Läuft |
| Mail-Relay | CT 130 | 16GB | ? Prüfen |
| **Thin Pool** | pve/data | 157GB | ⚠️ 96.6% voll |

---

## 🎯 NÄCHSTE SCHRITTE

1. **JETZT**: Speicher analysieren - welche Container können verkleinert/gelöscht werden?
2. **DANN**: SMB-Share von AzuraCast HDD einrichten
3. **DANN**: Visualizer komplett neu implementieren
4. **DANN**: Rating-to-ID3-Sync Backend bauen

---
*Zuletzt aktualisiert: 2024-12-07 23:00*
