# Changelog

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
