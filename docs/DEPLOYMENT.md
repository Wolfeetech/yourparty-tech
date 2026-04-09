# YourParty.tech Deployment Guide

> **Last Updated:** December 30, 2024  
> **Maintainer:** DevOps Team

---

## Architecture Overview

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Windows Dev    │────▶│   PVE Host      │────▶│   Containers    │
│  (yourparty-    │ SCP │   (pve)         │ pct │                 │
│   tech repo)    │     │                 │push │  207: WordPress │
└─────────────────┘     └─────────────────┘     │  211: FastAPI   │
                                                │  202: MongoDB   │
                                                │  208: MariaDB   │
                                                └─────────────────┘
```

---

## Standard Deployment Workflow

### 1. Make Changes Locally
```powershell
# Edit files in: C:\Users\StudioPC\yourparty-tech\
code apps/api/routers/interactive.py
```

### 2. Copy to PVE Host
```powershell
scp C:\Users\StudioPC\yourparty-tech\apps\api\routers\interactive.py pve:/tmp/
```

### 3. Push to Container
```bash
# FastAPI (CT 211)
ssh pve "pct push 211 /tmp/interactive.py /app/routers/interactive.py"

# WordPress (CT 207)
ssh pve "pct push 207 /tmp/api.php /var/www/html/wp-content/themes/yourparty-tech/inc/api.php"
ssh pve "pct exec 207 -- chown www-data:www-data /var/www/html/wp-content/themes/yourparty-tech/inc/api.php"
```

### 4. Restart Services
```bash
# FastAPI
ssh pve "pct exec 211 -- systemctl restart radio-api"

# WordPress (if PHP-FPM issues)
ssh pve "pct exec 207 -- systemctl restart apache2"
```

### 5. Verify Deployment
```bash
# Health Check
curl https://api.yourparty.tech/health

# FastAPI Logs
ssh pve "pct exec 211 -- journalctl -u radio-api -n 50 --no-pager"
```

---

## Quick Commands Cheatsheet

| Task | Command |
|------|---------|
| List containers | `ssh pve "pct list"` |
| Enter container shell | `ssh pve "pct enter 211"` |
| Check API status | `curl https://api.yourparty.tech/health` |
| View logs | `ssh pve "pct exec 211 -- journalctl -u radio-api -f"` |
| Restart API | `ssh pve "pct exec 211 -- systemctl restart radio-api"` |

---

## Rollback Procedure

If a deployment causes issues:

### 1. Identify Last Working Version
```bash
# Check git log
git log --oneline -10
```

### 2. Restore Previous File
```powershell
# Checkout previous version
git checkout HEAD~1 -- apps/api/routers/interactive.py

# Deploy the rollback
scp apps/api/routers/interactive.py pve:/tmp/
ssh pve "pct push 211 /tmp/interactive.py /app/routers/interactive.py"
ssh pve "pct exec 211 -- systemctl restart radio-api"
```

### 3. Verify Rollback
```bash
curl https://api.yourparty.tech/health
```

---

## Environment Variables (CT 211)

The API requires these environment variables in `/app/.env`:

```bash
MONGO_URI=mongodb://...
AZURACAST_API_URL=https://radio.yourparty.tech/api
AZURACAST_API_KEY=...
```

To update:
```bash
ssh pve "pct exec 211 -- nano /app/.env"
ssh pve "pct exec 211 -- systemctl restart radio-api"
```

---

## Backup Verification

Daily backups run automatically at:
- **MongoDB:** 03:00 UTC (CT 202)
- **MariaDB:** 04:00 UTC (CT 208)

Check backup status:
```bash
ssh pve "pct exec 202 -- ls -la /mnt/nas/backups/mongodb/"
ssh pve "pct exec 208 -- ls -la /mnt/nas/backups/mariadb/"
```

---

## Troubleshooting

### API Not Responding
```bash
# Check if service is running
ssh pve "pct exec 211 -- systemctl status radio-api"

# Check for errors in logs
ssh pve "pct exec 211 -- journalctl -u radio-api -n 100 --no-pager"

# Verify MongoDB connection
ssh pve "pct exec 211 -- curl -s http://localhost:8000/health"
```

### WordPress 500 Errors
```bash
# Check Apache error log
ssh pve "pct exec 207 -- tail -50 /var/log/apache2/error.log"

# Verify file permissions
ssh pve "pct exec 207 -- ls -la /var/www/html/wp-content/themes/yourparty-tech/inc/"
```
