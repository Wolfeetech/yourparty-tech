# YourParty.tech 🎵

Community-driven radio web application with mood-based playlists.

## Quick Start (Docker)

```bash
# 1. Clone repository
git clone https://github.com/Wolfeetech/yourparty-tech.git
cd yourparty-tech

# 2. Configure environment
cp .env.example .env
# Edit .env with your credentials

# 3. Start all services
docker-compose up -d

# 4. Access services
# WordPress: http://localhost:8080
# API: http://localhost:8000
```

## Architecture

```
┌─────────────────┐     ┌─────────────────┐
│   WordPress     │────▶│   FastAPI       │
│   (Theme)       │     │   (Backend)     │
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

## Services

| Service | Port | Purpose |
|---------|------|---------|
| WordPress | 8080 | Main website |
| FastAPI | 8000 | Mood/Rating API |
| Nginx | 80/443 | Reverse proxy |
| MariaDB | 3306 | WordPress DB |
| MongoDB | 27017 | Mood data |

## Configuration

See [DEPLOYMENT.md](yourparty-tech/DEPLOYMENT.md) for:
- Required credentials
- Hardcoded IPs to change
- Post-deployment checklist

## External Dependencies

- **AzuraCast** - Radio automation (install separately)
  - https://docs.azuracast.com/

## License

MIT
