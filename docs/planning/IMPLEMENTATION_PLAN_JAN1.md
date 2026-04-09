# MASTER IMPLEMENTATION PLAN - DEADLINE: JAN 01
**Status**: � IN PROGRESS (On Track for Jan 1)
**Objective**: Hardened, stable, and unified "YourParty.tech" system (Radio + Website + Control).

## 🚨 PHASE 1: CRISIS MANAGEMENT & SECURITY (IMMEDIATE)
**Goal**: Stop the bleeding. Prevent hacks. Ensure uptime.

1.  **[CRITICAL] SECURE CREDENTIALS**
    *   [x] Audit `functions.php`: Remove exposed AzuraCast API Key.
    *   [x] Audit `enrich_ratings.py`: Removed hardcoded MongoDB password and API key.
    *   [x] Audit `backend/api.py`: Removed 5 hardcoded IP fallbacks.
    *   [x] Created `.env.example` template for all secrets.
    *   [x] Action: Deployed `.env` file to CT 211 (`/opt/radio-api/.env`).

2.  **[CRITICAL] BACKEND STABILITY**
    *   [x] **Dependency Lock**: Generated strict `requirements.txt` (63 packages locked).
    *   [x] **Async Processing**: Refactor `api.py` /scan endpoint to use BackgroundTasks. ✅ *Refactored AzuraCastClient to async.*
    *   [x] **Error Handling**: Add global exception handlers to prevent "Internal Server Error" white screens. ✅ *Global handler implemented in api.py.*

3.  **[INFRA] STORAGE EMERGENCY (PVE)**
    *   [x] PVE Thin Pool at **59%** usage - ✅ No emergency!
    *   [x] CT 100 (Old Radio API) - **Already removed**.
    *   [ ] **Action**: Rotate/Truncate logs on `CT 211` (if needed).

## 🛠 PHASE 2: UNIFICATION (WEEK 2)
**Goal**: Make the Frontend and Backend talk the same language.

1.  **API UNIFICATION**
    *   Ensure `api.yourparty.tech` points correctly to the Python Backend.
    *   Ensure WordPress `page-control.php` uses ONLY the Python API, not direct AzuraCast calls (Single Source of Truth paradigm).

2.  **FRONTEND POLISH (React)**
    *   [ ] Remove inline styles in `App.jsx`.
    *   [ ] Implement "Deep Space" theme variables globally.
    *   [ ] Fix "Mongo Integration" UI to be less cluttered.

## ✨ PHASE 3: "WOW" FACTOR & LAUNCH (WEEK 3)
**Goal**: Visual excellence and smooth UX.

1.  **PUBLIC SITE (WordPress)**
    *   [ ] **Performance**: Configure caching (W3 Total Cache or FastCGI Cache).
    *   [ ] **SEO**: Add OpenGraph tags for WhatsApp/Discord sharing.
    *   [ ] **History**: Fix the "Tracks History" widget to be real-time.

2.  **CONTROL DASHBOARD**
    *   [ ] Make it mobile-perfect for the "Admin on the Dancefloor".

## 🛡️ PHASE 4: INFRASTRUCTURE HARDENING (PROFESSIONALIZATION)
**Goal**: Move from "Fragile Home Lab" to "Production Grade Infrastructure".

1.  **STORAGE ARCHITECTURE (Circular Dependency Fix)**
    *   [ ] **Current**: PVE Host mounts NFS from AzuraCast VM (210). ❌ *Risk: Host freezes if VM dies.*
    *   [ ] **Target**: PVE Host exports `/mnt/storage` (NFSv4), AzuraCast VM mounts it. ✅ *Stable.*
    *   [ ] **Action**: Create "Bind Mount" or Host-level NFS share plan.

2.  **DISASTER RECOVERY (Backups)**
    *   [ ] **Gap**: Critical systems (HA, AzuraCast, Proxy) have NO backups.
    *   [ ] **Action**: Add IDs `103`, `210`, `211`, `360` to daily `vzdump` schedule.

3.  **NETWORK PROFESSIONALIZATION**
    *   [ ] **Static IPs**: Remove hardcoded IPs from code, move to DNS/Env Vars or strict Sticky Static implementations.
    *   [ ] **NPM hardening**: Move from manual DB edits to "Configuration as Code" or at least `docker-compose` with persistent volume management.

## 🚀 LIVE DEVELOPMENTS (ADDED SCOPE)
1.  **MULTI-CHANNEL CAPABILITY**
    *   [x] **Backend**: `station_id` support added to `AzuraCastClient`.
    *   [x] **Logic**: Foundation for independent radio stations implemented.
2.  **SOCIAL FEATURES (SHOUTOUTS)**
    *   [x] **API**: `/shoutout` endpoints implemented.
    *   [ ] **Frontend**: Integration into `footer.php` and `ShoutoutModule.js`.

---
*This document is the Single Source of Truth for the Jan 1st Launch.*
