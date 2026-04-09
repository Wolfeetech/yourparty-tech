
# Deployment Instructions - 19.12.2025

## 1. Fix "Loading Station..." & "Tag Vibe" (Critical)
The API (CT 211) works, but the WordPress Proxy is pointing to the wrong place (`api.yourparty.tech` which is 502).

**Action**: Edit `wp-config.php` on the Server (CT 207) and ensure this line matches:
```php
define('YOURPARTY_API_URL', 'http://192.168.178.211:8000');
```
*Note: The local file is correct, but the server likely defaults to `https://api.yourparty.tech` if this line is missing.*

## 2. Restore Content (Missing File)
The content configuration was missing, causing empty text.

**Action**: Upload the entire `yourparty-tech` theme folder again, or specifically:
- `inc/content-config.php` (NEW - Created during this session)
- `front-page.php` (CLEANED - Duplicate script removed)

## 3. Proxmox Cleanup (Space Issue)
Your storage `local-lvm` is 93% full. 

**Safe to Delete (Verified):**
- CT 100 (Old Radio API) - *If still present*
- Snapshots/Backups on local storage (Move to HDD)

**Review Needed (Candidates):**
- CT 106 (WireGuard): 94% Full. Check `/var/log` or backups inside.
- CT 110 (n8n), 120 (Fileserver), 130 (Mail-Relay): Are these used? If not, Stop -> Backup -> Remove.

## 4. Verify
After deploying the theme and updating `wp-config.php`:
1. Open `https://yourparty.tech`.
2. "Loading Station..." should disappear.
3. Click "TAG VIBE". The dialog should open and submit successfully.
