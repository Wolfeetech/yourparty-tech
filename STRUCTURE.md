# 🗺️ YourParty.tech - Repository Structure

**Quick Reference Guide**

---

## 📁 Directory Structure

```
yourparty-tech/
│
├── apps/                    # Application Code
│   ├── api/                # Backend (FastAPI + Python)
│   │   ├── main.py         # FastAPI entry point
│   │   ├── mongo_client.py # MongoDB integration
│   │   ├── requirements.txt
│   │   ├── .env.example    # Copy to .env — never commit .env!
│   │   ├── models/         # Pydantic data models
│   │   ├── routers/        # FastAPI route handlers
│   │   └── services/       # Business logic layer
│   │
│   └── web/                # Frontend (WordPress Theme)
│       ├── functions.php   # Theme functions
│       ├── style.css       # Main stylesheet
│       ├── front-page.php  # Homepage template
│       ├── assets/         # CSS, JS, images
│       └── .env.example    # Copy to .env — never commit .env!
│
├── infrastructure/          # Deployment & Configuration
│   ├── nginx/              # Web server configs
│   ├── docker/             # Docker Compose
│   │   └── docker-compose.yml
│   └── systemd/            # Service unit definitions
│
├── config/                  # Shared runtime config (non-secret)
│   └── stations.json       # Radio station definitions
│
├── database/                # Database Management
│   ├── migrations/         # SQL migration scripts
│   └── backups/            # Database backups (git-ignored)
│
├── docs/                    # Documentation
│   ├── planning/           # Project planning docs
│   ├── ops/                # Operations & deployment
│   ├── network/            # VPN & network configs
│   └── ssl/                # SSL/TLS documentation
│
├── scripts/                 # Utility & maintenance scripts
│   ├── ops/                # DB recovery, WP setup, server ops
│   └── debug/              # Diagnostic and debug scripts
│
├── tools/                   # Development tools
├── tests/                   # Test suites
└── _archive/                # Archived/deprecated code
    ├── legacy_php/         # Old PHP debug/utility files
    └── frontend/           # Previous React frontend attempt
```

---

## 🔐 Environment / Secrets

**Rule:** Never commit `.env`, `.env.prod`, `.env.production`, or any file containing real credentials.

```bash
# Backend
cp apps/api/.env.example apps/api/.env
# Edit apps/api/.env with your real settings — kept local only

# Frontend
cp apps/web/.env.example apps/web/.env
```

All patterns like `*.env`, `*.env.prod`, `*.env.production` are in `.gitignore`.

---

## 🎯 Common Tasks

### Starting the Application

```bash
# Start all services via Docker
cd infrastructure/docker
docker-compose up -d

# Or manually — Backend only:
cd apps/api
python main.py

# Frontend (WordPress)
# Deploy apps/web/ to the WordPress themes directory on the server
```

### Deployment

```bash
cat docs/ops/DEPLOY_INSTRUCTIONS.md
cat docs/ops/SERVER_INFO.md
```

---

## 🔍 Finding Things

| What | Where |
|------|-------|
| Backend API code | `apps/api/` |
| WordPress theme | `apps/web/` |
| Radio station config | `config/stations.json` |
| Nginx configs | `infrastructure/nginx/` |
| Docker setup | `infrastructure/docker/` |
| Systemd services | `infrastructure/systemd/` |
| SQL migrations | `database/migrations/` |
| Planning docs | `docs/planning/` |
| Deployment guides | `docs/ops/` |
| VPN configs | `docs/network/` |
| DB / WP ops scripts | `scripts/ops/` |
| Debug scripts | `scripts/debug/` |
| Tests | `tests/` |
| Legacy / archived code | `_archive/` |

---

## 🚀 Quick Commands

```bash
# View backend logs
docker logs radio-api

# Run backend tests
cd apps/api && pytest

# Check nginx config
nginx -t

# Restart all services
cd infrastructure/docker && docker-compose restart
```

---

## ⚠️ Rules for Contributors

1. **No secrets in the repo.** Use `.env.example` as a template and keep real `.env` files local.
2. **No fix/debug scripts in the root.** Temporary ops scripts go in `scripts/ops/` (or run locally and discard).
3. **No log or audit output files.** Never commit `*_results.txt`, `*_audit.*`, or similar dumps.
4. **No binaries.** Tools like `wp-cli.phar` are downloaded at deploy time, not committed.
5. **All app code lives under `apps/`.** Nothing in root except docs and config files.

---

**Last Updated:** 2026-05-18
**Structure Version:** 3.0 (Clean Monorepo)
