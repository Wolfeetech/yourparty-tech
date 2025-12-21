# YourParty.tech Deployment Guide

## ⚠️ IMPORTANT: Hardcoded URLs to Change

The following files contain hardcoded IP addresses and URLs that **MUST be updated** for a new server:

### Files with Hardcoded IPs

| File | Line | Current Value | Purpose |
|------|------|---------------|---------|
| `inc/api.php` | 19 | `192.168.178.210` | AzuraCast internal IP |
| `inc/api.php` | 556, 605, 965 | `192.168.178.211:8000` | FastAPI backend |
| `inc/api.php` | 680 | `192.168.178.211:8080` | Vote-next endpoint |
| `inc/api.php` | 856, 868, 880 | `192.168.178.211:8000` | Ratings/Moods/Steer |
| `inc/admin-dashboard.php` | 13 | `192.168.178.211:8000` | API base |
| `templates/page-control.php` | 631 | `192.168.178.211:8000` | Mood fetch |
| `assets/app.js` | 24 | `192.168.178.210` | Internal IP check |
| `functions.php` | 26, 41, 351 | `radio.yourparty.tech` | AzuraCast public URL |

---

## 🔑 Required Credentials & Services

### 1. AzuraCast Radio Server
- **URL:** `https://radio.yourparty.tech` (or your domain)
- **Internal IP:** `192.168.178.210` (change to your AzuraCast IP)
- **API Key:** Get from AzuraCast Admin → Station → API Keys
- **Station ID:** Usually `1`

### 2. FastAPI Backend (Rating/Mood Service)
- **URL:** `http://192.168.178.211:8000` (change to your backend IP)
- **Endpoints used:**
  - `/vote-mood` - Submit mood votes
  - `/mood-tag` - Tag tracks with moods
  - `/ratings` - Get track ratings
  - `/moods` - Get mood statistics
  - `/control/steer` - Vibe steering

### 3. MongoDB Database
- **URI:** `mongodb://192.168.178.202:27017/yourparty`
- **Used by:** FastAPI backend (not directly by WordPress)

### 4. WordPress Database
- **Create new MySQL database** on target server
- **Credentials needed:** DB_NAME, DB_USER, DB_PASSWORD, DB_HOST

---

## 📦 Quick Deployment Steps

```bash
# 1. Clone repository
git clone https://github.com/Wolfeetech/yourparty-tech.git
cd yourparty-tech

# 2. Copy theme to WordPress
cp -r yourparty-tech/* /var/www/html/wp-content/themes/yourparty-tech/

# 3. Update hardcoded IPs (use sed or manual edit)
# Replace 192.168.178.210 with your AzuraCast IP
# Replace 192.168.178.211 with your FastAPI IP
# Replace radio.yourparty.tech with your domain

# 4. Set file permissions
chown -R www-data:www-data /var/www/html/wp-content/themes/yourparty-tech/
chmod -R 755 /var/www/html/wp-content/themes/yourparty-tech/
```

---

## 🔧 Post-Deployment Checklist

- [ ] Update all hardcoded IPs (see table above)
- [ ] WordPress Admin → Appearance → Activate "YourParty.tech" theme
- [ ] WordPress Admin → Settings → Reading → Homepage = "Front Page"
- [ ] Create page "Control" with template "Radio Control Dashboard"
- [ ] Test: Stream plays when clicking play button
- [ ] Test: TAG VIBE dialog opens and closes
- [ ] Test: Control Panel shows mood data

---

## 🏗️ External Services to Set Up

If starting from scratch, you need:

1. **AzuraCast** - Radio automation software
   - Install: https://docs.azuracast.com/
   - Add your music library
   - Create station

2. **FastAPI Backend** (optional for voting)
   - Located in: `backend/` folder (if present)
   - Requires: Python 3.9+, MongoDB
   - Run: `uvicorn main:app --host 0.0.0.0 --port 8000`

3. **MongoDB** (optional for voting)
   - Install MongoDB 6.0+
   - Create database: `yourparty`

---

## 📁 File Structure

```
yourparty-tech/
├── front-page.php          # Homepage with player + mood dialog
├── functions.php           # Theme setup, URL configs
├── inc/
│   ├── api.php             # ⚠️ Contains most hardcoded IPs
│   └── admin-dashboard.php # Admin widget
├── templates/
│   └── page-control.php    # ⚠️ Has hardcoded IP for mood fetch
├── assets/
│   ├── js/modules/         # ES6 modules
│   └── app.js              # ⚠️ Has internal IP check
├── main.js                 # App entry point
├── .env.example            # Config template
└── DEPLOYMENT.md           # This file
```
