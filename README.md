# YourParty.tech 🎵

Community-driven radio web application with mood-based playlists.

> **⚠️ NEW STRUCTURE:** This repository has been reorganized into a clean monorepo.
> - **Backend (FastAPI):** `/apps/api`
> - **Frontend (WordPress Theme):** `/apps/web`
> - **Infrastructure:** `/infrastructure` (nginx, docker, systemd)
> - **Documentation:** `/docs` (planning, ops, network, ssl)

## Features ✨

- 🎶 **Live Radio Streaming** via AzuraCast
- ⭐ **Community Ratings** (1-5 stars with averages)
- 🎛️ **Mood-Based Auto-DJ** (Energy/Chill/Groove/Dark modes)
- 🗳️ **Live Voting** for next track
- 🔐 **JWT Authentication** for admin endpoints
- 🛡️ **Rate Limiting** on public endpoints
- 📊 **Real-time WebSocket** updates

## Quick Start (Docker)

```bash
# 1. Clone repository
git clone https://github.com/Wolfeetech/yourparty-tech.git
cd yourparty-tech

# 2. Configure environment
cp apps/api/.env.example apps/api/.env
cp apps/web/.env.example apps/web/.env
# Edit .env files with your credentials

# 3. Start all services
cd infrastructure/docker
docker-compose up -d

# 4. Access services
# WordPress: http://localhost:8080
# API: http://localhost:8000
```

## Architecture

```
┌─────────────────┐     ┌─────────────────┐
│   WordPress     │────▶│   FastAPI       │
│   (/apps/web)   │     │   (/apps/api)   │
└────────┬────────┘     └────────┬────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐     ┌─────────────────┐
│   MariaDB       │     │   MongoDB       │
│   (WP Data)     │     │   (Mood/Votes)  │
└─────────────────┘     └─────────────────┘
                               │
                               ▼
                  ┌─────────────────┐
                  │   AzuraCast     │
                  │   (Radio)       │
                  └─────────────────┘
```

## API Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/token` | POST | - | Login (returns JWT) |
| `/rate` | POST | - | Submit track rating |
| `/vote-mood` | POST | - | Vote for mood/track |
| `/vote-next-candidates` | GET | - | Get voting candidates |
| `/vote-next-track` | POST | - | Vote for specific track |
| `/now-playing` | GET | - | Current track info |
| `/library/all` | GET | Auth | Full library metadata |
| `/control/steer` | POST | Auth | Set Auto-DJ mode |

## Services

| Service | Port | Purpose |
|---------|------|---------|
| WordPress | 8080 | Main website |
| FastAPI | 8000 | Mood/Rating API |
| Nginx | 80/443 | Reverse proxy |
| MariaDB | 3306 | WordPress DB |
| MongoDB | 27017 | Mood data |

## Configuration

See documentation in `/docs`:
- **Deployment:** [docs/ops/DEPLOY_INSTRUCTIONS.md](docs/ops/DEPLOY_INSTRUCTIONS.md)
- **Server Info:** [docs/ops/SERVER_INFO.md](docs/ops/SERVER_INFO.md)
- **Planning:** [docs/planning/](docs/planning/)
- **Network/VPN:** [docs/network/](docs/network/)

## External Dependencies

- **AzuraCast** - Radio automation (install separately)
  - https://docs.azuracast.com/

## License

MIT

