# YourParty.tech Server Info Sheet

> Last Updated: 2025-12-17

---

## 🚨 SECURITY ISSUES (CRITICAL)

### 1. Compromised WordPress User
| User | Email | Risk |
|------|-------|------|
| `adminbockup` (ID 5) | adminbockup@wordpress.org | **REMOVE IMMEDIATELY** - Likely attacker account |

### 2. Weak Database Password
```
DB_PASSWORD = 'SimplePass123'  ← CHANGE THIS!
```

### 3. Active Malware Attack
- `index.php` repeatedly infected with obfuscated PHP (`goto` chains)
- Watchdog scripts installed to auto-restore (workaround, not fix)
- Root cause: Unknown, possibly compromised WP admin or exploit

### 4. File Permissions
- All files have 777 permissions (unprivileged LXC limitation)
- Cannot use `chattr +i` (filesystem doesn't support it)

---

## 🖥️ INFRASTRUCTURE OVERVIEW

### Proxmox Host
| Property | Value |
|----------|-------|
| Hostname | `pve` |
| IP | `192.168.178.172` |
| SSH | `root@pve` (port 22) |

### LXC Containers (Proxmox)

| VMID | Name | IP | Purpose |
|------|------|-----|---------|
| 101 | adguard | - | DNS/Ad blocking |
| 103 | npm | - | Nginx Proxy Manager |
| 106 | wireguard | - | VPN server |
| 108 | vaultwarden | - | Password manager |
| 109 | pbs | - | Proxmox Backup Server |
| 110 | n8n | - | Automation |
| 120 | fileserver | - | File storage |
| 130 | mail-relay | - | Email relay |
| **202** | **mongodb-primary** | **192.168.178.222** | MongoDB for mood/ratings |
| **207** | **radio-wordpress-prod** | **192.168.178.207** | WordPress + Theme |
| **208** | **mariadb-server** | **192.168.178.228** | WordPress Database |
| **211** | **radio-api** | **192.168.178.211** | FastAPI Backend |

### Virtual Machines

| VMID | Name | IP | Purpose |
|------|------|-----|---------|
| **210** | azuracast-vm | ~192.168.178.210 | AzuraCast Radio |
| 360 | homeassistant-eltern | - | Home Assistant |

---

## 🎵 YOURPARTY.TECH SERVICES

### WordPress (CT 207)
| Property | Value |
|----------|-------|
| IP | `192.168.178.207` |
| Web Server | Apache 2.4 |
| PHP Version | 8.x |
| Theme | `yourparty-tech` |
| Ports | 80 (HTTP), 3000 (Docker), 9090 (Docker) |

### FastAPI Backend (CT 211)
| Property | Value |
|----------|-------|
| IP | `192.168.178.211` |
| Port | `8000` |
| Endpoints | `/vote-mood`, `/mood-tag`, `/ratings`, `/moods` |

### MongoDB (CT 202)
| Property | Value |
|----------|-------|
| IP | `192.168.178.222` |
| Port | `27017` |
| Database | `yourparty` |

### MariaDB (CT 208)
| Property | Value |
|----------|-------|
| IP | `192.168.178.228` |
| Database | `wordpress_db` |
| User | `wp_user` |
| Password | `YpRd!2024#SecureDB` ✅ UPDATED 2024-12-17 |

### AzuraCast (VM 210)
| Property | Value |
|----------|-------|
| IP | ~`192.168.178.210` |
| URL | `https://radio.yourparty.tech` |
| Station ID | `1` |

---

## 👤 WORDPRESS USERS

| ID | Username | Email | Password | Role |
|----|----------|-------|----------|------|
| 1 | admin | admin@yourparty.tech | `YpAdmin2024!` | Administrator |
| 2 | Wolf | wolf@yourparty.tech | `YpWolf2024!` | Administrator |
| 3 | Franz | franz@yourparty.tech | `YpFranz2024!` | Administrator |
| 4 | trumpweiss | yourpartycr@gmail.com | *unchanged* | Administrator |

---

## 📁 THEME STRUCTURE

```
/var/www/html/wp-content/themes/yourparty-tech/
├── front-page.php      # Homepage + Mood Dialog
├── functions.php       # Theme setup, API config
├── inc/
│   ├── api.php         # REST API endpoints
│   └── admin-dashboard.php
├── templates/
│   └── page-control.php # Control Panel
├── assets/
│   └── js/modules/     # ES6 modules
└── DEPLOYMENT.md       # Setup guide
```

---

## 🔧 CONFIGURATION VALUES

### wp-config.php (WordPress)
```php
define('DB_NAME', 'wordpress_db');
define('DB_USER', 'wp_user');
define('DB_PASSWORD', 'SimplePass123');  // CHANGE!
define('DB_HOST', '192.168.178.228');
```

### Required Constants (add to wp-config.php)
```php
define('YOURPARTY_AZURACAST_URL', 'https://radio.yourparty.tech');
define('YOURPARTY_API_URL', 'http://192.168.178.211:8000');
```

---

## 🛡️ SECURITY SCRIPTS INSTALLED

| Script | Path | Schedule | Purpose |
|--------|------|----------|---------|
| wp-core-check.sh | /usr/local/bin/ | */5 * * * * | Restore WP core files |
| wp-index-watchdog.sh | /usr/local/bin/ | * * * * * | Detect malware in index.php |

Logs:
- `/var/log/wp-core-check.log`
- `/var/log/wp-index-watchdog.log`

---

## ✅ RECOMMENDED FIXES

### Immediate Actions
1. [ ] Delete WordPress user `adminbockup` (ID 5)
2. [ ] Change DB password from `SimplePass123`
3. [ ] Change all WordPress admin passwords
4. [ ] Review user `trumpweiss` legitimacy

### Short-term
1. [ ] Install Wordfence security plugin
2. [ ] Enable 2FA for all admin accounts
3. [ ] Update wp-config.php with new DB password

### Long-term
1. [ ] Migrate to new container (cleanest solution)
2. [ ] Use docker-compose for deployment
3. [ ] Set up proper backups
4. [ ] Consider Cloudflare for DDoS protection

---

## 📋 REBUILD CHECKLIST

For fresh server setup:

1. **Proxmox**
   - Create LXC containers for: WordPress, MariaDB, MongoDB, FastAPI
   - Use VMID scheme: 207, 208, 202, 211

2. **Clone Repository**
   ```bash
   git clone https://github.com/Wolfeetech/yourparty-tech.git
   ```

3. **Use Docker Compose** (recommended)
   ```bash
   cd yourparty-tech
   cp .env.example .env
   # Edit .env with new passwords
   docker-compose up -d
   ```

4. **Or Manual Setup**
   - Follow `yourparty-tech/DEPLOYMENT.md`
   - Update hardcoded IPs in theme files

5. **AzuraCast**
   - Install separately: https://docs.azuracast.com/
   - Configure station and get API key

---

## 📞 DOMAINS & DNS

| Domain | Points To | Service |
|--------|-----------|---------|
| yourparty.tech | 192.168.178.207 (via NPM) | WordPress |
| radio.yourparty.tech | 192.168.178.210 | AzuraCast |
| api.yourparty.tech | 192.168.178.211 | FastAPI |
