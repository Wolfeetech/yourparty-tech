---
description: Deploy changes to yourparty.tech production servers
---

# Deployment Workflow

## Pre-Deployment Checklist

- [ ] Changes tested locally?
- [ ] No syntax errors in files?
- [ ] Git status clean or changes committed?

## Option A: Deploy WordPress Theme

### 1. Prepare files
// turbo
```powershell
cd c:\Users\StudioPC\yourparty-tech
git status
```

### 2. Copy to server
```powershell
# Full theme deployment
scp -r apps/web/* pve:/tmp/theme/
ssh pve "pct push 207 /tmp/theme /var/www/html/wp-content/themes/yourparty-tech/ --recursive"
```

### 3. Fix permissions
// turbo
```bash
ssh pve "pct exec 207 -- chown -R www-data:www-data /var/www/html/wp-content/themes/yourparty-tech"
ssh pve "pct exec 207 -- systemctl reload apache2"
```

### 4. Verify
// turbo
```bash
curl -s https://yourparty.tech/ | head -20
```

## Option B: Deploy FastAPI Backend

### 1. Copy files
```powershell
scp apps/api/*.py pve:/tmp/api/
ssh pve "pct push 211 /tmp/api /app/ --recursive"
```

### 2. Restart service
// turbo
```bash
ssh pve "pct exec 211 -- systemctl restart radio-api"
```

### 3. Verify
// turbo
```bash
# Wait 3 seconds for startup
sleep 3
curl https://api.yourparty.tech/
ssh pve "pct exec 211 -- systemctl status radio-api"
```

## Option C: Quick Single-File Deploy

### WordPress PHP file
```powershell
# Example: Deploy api.php
scp apps/web/inc/api.php pve:/tmp/
ssh pve "pct push 207 /tmp/api.php /var/www/html/wp-content/themes/yourparty-tech/inc/api.php"
ssh pve "pct exec 207 -- chown www-data:www-data /var/www/html/wp-content/themes/yourparty-tech/inc/api.php"
```

### Python file
```powershell
# Example: Deploy api.py
scp apps/api/api.py pve:/tmp/
ssh pve "pct push 211 /tmp/api.py /app/api.py"
ssh pve "pct exec 211 -- systemctl restart radio-api"
```

## Rollback

### WordPress
```bash
# Restore from backup
ssh pve "pct exec 207 -- cp -r /var/www/html/wp-content/themes/yourparty-tech.bak /var/www/html/wp-content/themes/yourparty-tech"
```

### FastAPI
```bash
# Restore from git
ssh pve "pct exec 211 -- cd /app && git checkout api.py"
ssh pve "pct exec 211 -- systemctl restart radio-api"
```

## Post-Deployment Verification

// turbo
1. Check website loads: `curl -I https://yourparty.tech/`
2. Check API responds: `curl https://api.yourparty.tech/status`
3. Check control panel: Open https://yourparty.tech/control/ in browser
4. Check no console errors in browser DevTools
