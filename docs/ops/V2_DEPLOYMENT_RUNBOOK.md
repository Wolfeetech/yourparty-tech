# V2 Migration - Deployment Runbook
## YourParty.tech "Zero Dead Air" Strategy

This document outlines the **safe, parallel deployment** strategy ensuring no listener downtime.

---

## Pre-Flight Checklist

- [ ] AzuraCast has a "Fallback/Maintenance" playlist with 60+ minutes of music
- [ ] V1 containers are running and healthy
- [ ] MongoDB backup completed (`./scripts/backup_before_v2.sh`)
- [ ] `.env` file populated from `.env.v2.example`

---

## Port Mapping (V1 vs V2 Parallel Operation)

| Service | V1 Port | V2 Port | Notes |
|---------|---------|---------|-------|
| FastAPI Backend | 8000 | **8001** | V2 on different port |
| WordPress | 8080 | 8080 | Shared (theme hot-reload) |
| Directus | - | **8055** | New service |
| Meilisearch | - | **7700** | New service |
| Redis | - | **6379** | New service |
| PostgreSQL | - | **5432** | Internal only |

---

## Deployment Steps

### Phase 1: Start V2 Stack (Parallel)

```bash
cd infrastructure/docker

# Copy and edit env
cp .env.v2.example .env
nano .env  # Fill in credentials

# Start V2 services (V1 keeps running!)
docker-compose -f docker-compose.v2.yml up -d directus postgres redis meilisearch beets
```

**V1 still serves all traffic. V2 services warm up in background.**

### Phase 2: Run Migration (Non-Destructive)

```bash
# Dry run first
python scripts/migrate_v1_to_v2.py --dry-run

# If counts look good, execute
python scripts/migrate_v1_to_v2.py
```

**MongoDB is READ-ONLY during migration. No data loss possible.**

### Phase 3: Start V2 Backend (Different Port)

```bash
# Start backend on port 8001
docker-compose -f docker-compose.v2.yml up -d backend
```

**Test V2 at localhost:8001. V1 still at localhost:8000.**

### Phase 4: Verify V2

```bash
python scripts/verify_v2_system.py

# Manual tests:
# - Vote on localhost:8001/vote-mood
# - Check Directus at localhost:8055
# - Search via localhost:7700
```

### Phase 5: Switch Traffic (The "Flip")

Once V2 is verified:

```bash
# Update nginx to route to V2 backend (port 8001)
# OR update WordPress API proxy to hit 8001

# Then stop V1 backend
docker stop yourparty-api-v1
```

**Radio stream NEVER stops - AzuraCast is untouched throughout.**

---

## Rollback Plan

If V2 fails verification:

```bash
# Stop V2 services
docker-compose -f docker-compose.v2.yml down

# V1 is still running - no action needed
```

---

## AzuraCast Fallback Playlist

Ensure AzuraCast has a **Fallback Playlist** configured:

1. Log into AzuraCast admin
2. Go to Station → Playlists
3. Create/verify playlist named "Fallback" or "Maintenance"
4. Enable as fallback: Playlist Settings → "Play if no other tracks available"
5. Add 60+ minutes of ambient/safe tracks

This ensures the stream NEVER goes silent, even if the middleware dies.

---

**Author:** Antigravity System Architect  
**Date:** 2025-12-30
