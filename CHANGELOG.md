# Changelog

## [v1.0.9] - 2025-12-26
### Added
- **Vote Next Vibe (MTV Style)**: Users can vote for the next track's mood (energy/chill/groove/dark).
  - Visual trend feedback shows which mood is "winning" in real-time.
  - Pulsing animation highlights the trending button.
- **Auto-DJ Integration**: Backend scheduler (`mood_scheduler.py`) now reads from `mood_next_votes` and selects tracks accordingly.
- **Unified Database**: All collections now in single `yourparty` MongoDB database.

### Fixed
- **Database Fragmentation**: Resolved split between `radio_ratings` and `yourparty` databases.
- **Missing Imports**: Fixed `get_library_service` function in `library_service.py`.
- **PHP Syntax Error**: Removed duplicate `);` in `inc/api.php` that caused site outage.
- **API Startup**: Added `Depends` import to `api.py` for FastAPI dependency injection.

### Infrastructure
- Storage baseline captured: local-lvm at 85.02%.
- All 12 containers verified healthy.

## [v1.0.8] - 2025-12-18
### Fixed
- **Critical**: WordPress Core repariert (`class-wp-html-doctype-info.php` fehlte).
- **Security**: Wordfence 8.1.3 neu installiert (war beschädigt).

### Infrastructure
- Thin Pool von 92.79% auf 87.97% reduziert.
- Alle Container verifiziert und laufend.

## [v1.0.7] - 2025-12-17
### Security
- **Critical**: Deleted malicious WordPress user `adminbockup` (ID 5).
- **Database**: Changed weak password (`SimplePass123` → `YpRd!2024#SecureDB`).
- **WordPress**: Reset admin passwords for admin, Wolf, Franz users.
- **Protection**: Installed Wordfence 8.1.3 security plugin.
- **Auto-Heal**: Added watchdog scripts (`wp-core-check.sh`, `wp-index-watchdog.sh`).
- **Documentation**: Created `SERVER_INFO.md` with complete infrastructure reference.

### Infrastructure
- Documented all 12 LXC containers and 2 VMs with IP addresses.
- Added `docker-compose.yml` with WordPress, MariaDB, MongoDB, FastAPI, Nginx.
- Created `.env.example` with all configuration variables.
- Centralized API URLs via `yourparty_api_base_url()` function.

## [v1.0.6] - 2025-12-15
### Fixed
- **Critical**: Resolved broken "Tag Vibe" button and module loading failures.
    - Root Cause 1: Nested directory structure (`yourparty-tech/yourparty-tech/`) caused stale files.
    - Root Cause 2: Nginx blocked direct access to `/modules/*.js` files.
    - Root Cause 3: WordPress canonical redirect added trailing slashes, breaking ES6 imports.
- **Module Proxy**: Implemented PHP-based module proxy in `functions.php` to serve JS modules via WordPress routing.
- **Canonical Redirect Bypass**: Added filter to disable `redirect_canonical` for module requests.
- **Deployment Fix**: Forced file copy from nested subdirectory to theme root on server.

### Infrastructure
- **Storage Report**: Thin-pool at 92.79% (CT 207 already on HDD, CT 100 destroyed).
- **Apache**: Reloaded after deployment to clear caches.

## [v1.0.5] - 2025-12-14
### Added
- **Optimization**: PVE Monitoring Integration.
    - Added `tools/pve_monitor.py` to host (scheduled via cron).
    - Added `/yourparty/v1/control` endpoint to fetch PVE status.
- **Visuals**: Replaced "over-the-top" drone banner with realistic Bodensee footage in Services section.
- **Visuals**: Updated Hero Banner to "Stage" image.

### Fixed
- **CSS**: Resolved merge conflicts in `style.css` (Startpage/Radio Card).
- **Cleanup**: Removed temporary debug headers.


## [1.0.0] - 2025-12-12
### Optimization Phase
- **Infrastructure**:
  - Analyzed Proxmox storage (91% utilization).
  - Cleaned up legacy Container 100 (confirmed missing).
  - Attempted migration of CT 207 (postponed due to volume error).
- **Control Panel**:
  - Deployed `/yourparty/v1/control` plugin to WordPress (CT 207).
  - Implemented mock status endpoint returning container inventory.
  - Added action logging to `wp-content/uploads/yourparty_control.log`.
- **Frontend**:
  - Full modularization (ES6).
  - Visualizer Pro upgrades.
  - Mood Tagging fixes.
