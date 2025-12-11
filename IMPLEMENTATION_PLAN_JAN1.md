# MASTER IMPLEMENTATION PLAN - DEADLINE: JAN 01
**Status**: 🔴 IN PROGRESS
**Objective**: Hardened, stable, and unified "YourParty.tech" system (Radio + Website + Control).

## 🚨 PHASE 1: CRISIS MANAGEMENT & SECURITY (IMMEDIATE)
**Goal**: Stop the bleeding. Prevent hacks. Ensure uptime.

1.  **[CRITICAL] SECURE CREDENTIALS**
    *   [x] Audit `functions.php`: Remove exposed AzuraCast API Key.
    *   [ ] Audit `api.py`: Remove hardcoded IP addresses.
    *   [ ] Action: Move secrets to System Environment Variables or `wp-config.php`.

2.  **[CRITICAL] BACKEND STABILITY**
    *   [ ] **Dependency Lock**: Generate strict `requirements.txt` to prevent random crashes on updates.
    *   [ ] **Async Processing**: Refactor `api.py` /scan endpoint to use BackgroundTasks. *Current usage blocks the entire server.*
    *   [ ] **Error Handling**: Add global exception handlers to prevent "Internal Server Error" white screens.

3.  **[INFRA] STORAGE EMERGENCY (PVE)**
    *   *Observation*: PVE Thin Pool is at 96% usage.
    *   [ ] **Action**: Identify and purge `CT 100` (Old Radio API) if confirmed unused.
    *   [ ] **Action**: Rotate/Truncate logs on `CT 211`.

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

---
*This document is the Single Source of Truth for the Jan 1st Launch.*
