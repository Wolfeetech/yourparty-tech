# YourParty.tech Deployment Guide

## Quick Deployment Steps

### 1. Server Requirements
- **OS:** Debian 12 / Ubuntu 22.04+
- **Web Server:** Apache 2.4+ with mod_php or Nginx + PHP-FPM
- **PHP:** 8.1+ with extensions: curl, json, mysqli, mbstring
- **Database:** MySQL 8.0+ or MariaDB 10.5+
- **WordPress:** 6.7+

### 2. Files to Deploy

```bash
# Clone repository
git clone https://github.com/Wolfeetech/yourparty-tech.git

# Theme goes to:
/var/www/html/wp-content/themes/yourparty-tech/

# Only copy the inner yourparty-tech folder contents, NOT the outer wrapper
cp -r yourparty-tech/yourparty-tech/* /var/www/html/wp-content/themes/yourparty-tech/
```

### 3. Required WordPress Plugins
- None required (all functionality is in theme)

### 4. External Services
| Service | URL | Purpose |
|---------|-----|---------|
| AzuraCast | https://radio.yourparty.tech | Radio stream + metadata |
| FastAPI Backend | http://192.168.178.211:8000 | Mood voting, ratings |
| MongoDB | 192.168.178.202:27017 | Vote storage |

### 5. Configuration
Set these in `wp-config.php` or theme options:
```php
// No additional configuration needed - URLs are in inc/api.php
```

### 6. Post-Deployment Checklist
- [ ] Set WordPress Reading Settings: Homepage = Front Page
- [ ] Create page "Control" using template "Radio Control Dashboard"
- [ ] Verify AzuraCast connectivity
- [ ] Test mood voting via TAG VIBE button
- [ ] Verify WebSocket connection (optional, has polling fallback)

### 7. Security
- Remove debug.php, phpinfo.php if present
- Set proper file permissions (644 files, 755 directories)
- Install Wordfence or similar security plugin

---
## File Structure
```
yourparty-tech/
├── front-page.php      # Homepage with player + mood dialog
├── functions.php       # Theme setup, enqueuing, rewrite rules
├── inc/api.php         # REST API endpoints, AzuraCast proxy
├── templates/
│   └── page-control.php # Control Panel dashboard
├── assets/
│   ├── js/modules/     # ES6 modules (StatusModule, MoodModule, etc.)
│   └── css/            # Stylesheets
└── main.js             # App entry point
```
