---
description: Incremental optimisation of YourParty.tech website and control panel (best‑practice, SSOT, logging)
---

# Phase 1 – Analyse & Baseline
1. // turbo
   Run `ssh pve "pvesm status && lvs pve/data --noheadings -o data_percent"` to capture current storage usage.
2. // turbo
   Run `ssh pve "pct list"` and store output as `storage_report.txt`.
3. // turbo
   Run `curl -s -o /dev/null -w "%{http_code}" https://yourparty.tech/` and log HTTP status.

# Phase 2 – Clean‑up Thin‑Pool
4. // turbo
   Stop and migrate WordPress container 207 to `hdd-backup` storage:
   `ssh pve "pct stop 207 && pct move 207 hdd-backup && pct start 207"`
5. // turbo
   Destroy unused container CT 100 (old radio‑api):
   `ssh pve "pct stop 100 && pct destroy 100"`
6. // turbo
   Run `ssh pve "lvs pve/data --noheadings -o data_percent"` again to verify reduction.

# Phase 3 – UI/UX Polish
7. // turbo
   Deploy fresh CSS (already fixed) to CT 207:
   `scp -r c:\Users\StudioPC\.gemini\antigravity\playground\ionized-kepler\yourparty-tech\style.css pve:/tmp/ && ssh pve "pct exec 207 -- cp /tmp/style.css /var/www/html/wp-content/themes/yourparty-tech/ && chown 33:33 /var/www/html/wp-content/themes/yourparty-tech/style.css"`
8. // turbo
   Reload Apache on CT 207: `ssh pve "pct exec 207 -- systemctl reload apache2"`
9. // turbo
   Verify visualizer width and mode buttons via headless curl (fetch page snippet) and log.

# Phase 4 – Control Panel Enhancements
10. // turbo
    Add a lightweight admin endpoint `/wp-json/yourparty/v1/control` that returns JSON with container statuses (implemented via a small WP plugin). Deploy plugin via WP‑CLI.
11. // turbo
    Create a simple log file `control.log` on the host that records each admin action (timestamp, action).

# Phase 5 – Documentation & Logging
12. // turbo
    Append a `CHANGELOG.md` entry summarising each step with timestamps.
13. // turbo
    Update `ROADMAP.md` – mark completed items and add new tasks for final release.
14. // turbo
    Commit all changes to Git with a signed commit.

# Phase 6 – Final Release Prep (by 01.01.26)
15. // turbo
    Run full site smoke test (curl + basic JS check) and store results.
16. // turbo
    Tag the repository `v1.0‑release`.

---

*All commands marked with `// turbo` are safe to run automatically.*
