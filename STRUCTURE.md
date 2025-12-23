# 🗺️ YourParty.tech - New Repository Structure

**Quick Reference Guide**

---

## 📁 Directory Structure

```
yourparty-tech/
│
├── apps/                    # Application Code
│   ├── api/                # Backend (FastAPI + Python)
│   │   ├── api.py          # Main FastAPI application
│   │   ├── main.py         # Alternative entry point
│   │   ├── mongo_client.py # MongoDB integration
│   │   ├── requirements.txt
│   │   └── .env            # Backend environment config
│   │
│   └── web/                # Frontend (WordPress Theme)
│       ├── functions.php   # Theme functions
│       ├── style.css       # Main stylesheet
│       ├── front-page.php  # Homepage template
│       ├── assets/         # CSS, JS, images
│       └── .env            # Theme environment config
│
├── infrastructure/          # Deployment & Configuration
│   ├── nginx/              # Web server configs
│   ├── docker/             # Docker Compose
│   │   └── docker-compose.yml
│   └── systemd/            # Service definitions
│
├── database/                # Database Management
│   ├── migrations/         # SQL migration scripts
│   └── backups/            # Database backups
│
├── docs/                    # Documentation
│   ├── planning/           # Project planning docs
│   ├── ops/                # Operations & deployment
│   ├── network/            # VPN & network configs
│   └── ssl/                # SSL/TLS documentation
│
├── scripts/                 # Utility scripts
├── tools/                   # Development tools
├── tests/                   # Test suites
└── _archive/                # Archived/deprecated code
```

---

## 🎯 Common Tasks

### Starting the Application

```bash
# Start all services
cd infrastructure/docker
docker-compose up -d

# Or manually:
# Backend
cd apps/api
python api.py

# Frontend (WordPress)
# Deploy apps/web/ to WordPress themes directory
```

### Environment Configuration

```bash
# Backend
cp apps/api/.env.example apps/api/.env
# Edit apps/api/.env with your settings

# Frontend
cp apps/web/.env.example apps/web/.env
# Edit apps/web/.env with your settings
```

### Deployment

```bash
# See deployment documentation
cat docs/ops/DEPLOY_INSTRUCTIONS.md
cat docs/ops/SERVER_INFO.md
```

---

## 🔍 Finding Things

| What | Where |
|------|-------|
| Backend API code | `apps/api/` |
| WordPress theme | `apps/web/` |
| Nginx configs | `infrastructure/nginx/` |
| Docker setup | `infrastructure/docker/` |
| SQL migrations | `database/migrations/` |
| Planning docs | `docs/planning/` |
| Deployment guides | `docs/ops/` |
| VPN configs | `docs/network/` |
| Utility scripts | `scripts/` |
| Tests | `tests/` |

---

## ⚠️ Important Notes

### Path Changes
- **Backend:** `backend/` → `apps/api/`
- **Theme:** `yourparty-tech/` → `apps/web/`
- **Docker:** `docker-compose.yml` → `infrastructure/docker/docker-compose.yml`

### Update Required
If you have existing deployments or scripts, update these paths:
1. Docker Compose volume mounts
2. Deployment scripts
3. CI/CD pipelines
4. Import statements (if using relative paths)

---

## 🚀 Quick Commands

```bash
# View backend logs
docker logs radio-api

# View frontend (WordPress)
# Access via web browser at configured domain

# Run backend tests
cd apps/api
pytest

# Check nginx config
nginx -t

# Restart services
docker-compose restart
```

---

**Last Updated:** 2025-12-23  
**Structure Version:** 2.0 (Monorepo)
