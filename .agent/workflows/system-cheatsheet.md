---
description: Quick reference for yourparty.tech architecture, endpoints, and common tasks
---

# YourParty.tech - System Cheatsheet

## Architecture Overview

```
┌────────────────────────────────────────────────────────────────────┐
│                         PRODUCTION STACK                            │
├────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐   │
│   │  WordPress  │───▶│  FastAPI    │───▶│  MongoDB + AzuraCast│   │
│   │  yourparty  │    │  api.       │    │  (Proxmox VE)       │   │
│   │   .tech     │    │  yourparty  │    │                     │   │
│   │   (CT 207)  │    │   .tech     │    │                     │   │
│   │             │    │   (CT 211)  │    │                     │   │
│   └─────────────┘    └─────────────┘    └─────────────────────┘   │
│                                                                     │
└────────────────────────────────────────────────────────────────────┘
```

## Key Files

| Purpose | Path |
|---------|------|
| Backend Entry Point | `apps/api/api.py` |
| API Routers | `apps/api/routers/` |
| API Models | `apps/api/models/schemas.py` |
| Backend MongoDB Client | `apps/api/mongo_client.py` |
| WordPress API Proxy | `apps/web/inc/api.php` |
| Frontend JavaScript | `apps/web/assets/app.js` |
| Main Stylesheet | `apps/web/style.css` |

## API Endpoints (api.yourparty.tech)

### Core Endpoints
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/` | Health check |
| GET | `/status` | Now playing + steering |
| GET | `/ratings` | All track ratings |
| GET | `/moods` | All mood tags |
| GET | `/queue` | AzuraCast queue proxy |

### Interaction Endpoints
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/rate` | Submit track rating |
| POST | `/mood-tag` | Tag track with mood |
| POST | `/vote-next` | Vote for next vibe |
| POST | `/vote-next-mood` | Vote mood for next track |
| POST | `/vote-next-track` | Vote for specific track |
| GET | `/vote-next-candidates` | Get 3 voting candidates |

### Admin Endpoints
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET/POST | `/control/steer` | Get/Set steering mode |
| POST | `/library/sync` | Sync music directory |
| POST | `/library/cleanup` | Remove missing tracks |
| GET | `/docs` | Swagger UI |

## Quick Commands

### Check Production Status
```bash
# API health
curl https://api.yourparty.tech/

# Current track
curl https://api.yourparty.tech/status

# AzuraCast direct
curl https://radio.yourparty.tech/api/nowplaying/1
```

### Deploy to Server
```powershell
# WordPress theme
scp -r apps/web/* user@yourparty.tech:/var/www/html/wp-content/themes/yourparty-tech/

# FastAPI (via PVE)
ssh pve "pct exec 211 -- systemctl restart radio-api"
```

### Database Access
```bash
# MongoDB on server
ssh pve "pct exec 210 -- mongosh yourparty"

# Common queries
db.ratings.find().limit(5)
db.moods.find({tag: "energy"})
db.song_metadata.countDocuments()
```

## Known Issues (as of 2025-12-26)

1. **Two API files exist**: `api.py` (production) vs `main.py` (unused features)
2. **Some ratings have "Unknown" metadata**: Test entries in DB
3. **WebSocket not available**: Only in `main.py`, not `api.py`
4. **Vote-next-mood returns 400**: Parameter mismatch in WordPress proxy

## WordPress API Proxy Routes

All frontend calls go through WordPress (`/wp-json/yourparty/v1/...`) which proxies to FastAPI:

| WP Route | Proxies To | Method |
|----------|------------|--------|
| `/status` | AzuraCast `/api/nowplaying` | GET |
| `/rate` | FastAPI `/rate` | POST |
| `/mood-tag` | FastAPI `/mood-tag` | POST |
| `/vote-next` | FastAPI `/control/vote-next` | POST |
| `/vote-next-candidates` | FastAPI `/vote-next-candidates` | GET |
| `/vote-next-track` | FastAPI `/vote-next-track` | POST |
