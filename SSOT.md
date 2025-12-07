# Single Source of Truth (SSOT) - YourParty.tech

## Project Overview
**Goal**: Create a professional, authentic web presence for **YourParty Tech** (Small Business, 2 Owners).
**Philosophy**: "Authentic Quality" - We don't pretend to be an XXL corporation or influencers. We are two ambitious professionals delivering excellent event tech. What we do, we do perfectly.
**Core Rule**: Always finish tasks completely. Verify functionality before moving on. No half-baked solutions.
**Headline Note**: *User dislikes "System Sound Precision". Needs replacement.*

## Current State
- **Workspace**: Reset/Re-initialized.
- **Repository**: **MISSING** (User to provide URL).
- **Environment**: Windows `StudioPC` (Local), Proxmox VE (Remote Host).
- **Server Theme Path**: `/var/www/yourparty.tech/wp-content/themes/yourparty-tech`

## Insight & Audit (Browser)
- **Status**: Site loads. REST API funktioniert (`/status`).
- **Critical**: WebSocket errors (`wss://api.yourparty.tech/ws/...`) - **AKTIV DEBUGGEN**
  - ✅ Nginx Proxy korrekt konfiguriert `/ws/` → Container
  - ✅ SSL-Zertifikat mit SANs (api.yourparty.tech) erstellt
  - ✅ Backend läuft **im Container** (war auf PVE Host)
  - ✅ Uvicorn mit `--proxy-headers --forwarded-allow-ips *`
  - ✅ CORS korrekt (ALLOWED_ORIGINS)
  - ❌ WebSocket Handshake schlägt fehl - **Ursache unklar**
- **Legal**: ✅ Impressum & Datenschutz deployed (Best Practice).
- **Structure**: ✅ Local files -> `infrastructure/`.
- **UI/UX**: "Kindergarten" Animationen leicht angepasst. Vollständige Überarbeitung ausstehend.
- **New Feature**: **Overscroll Player** (Scroll down -> Fullscreen).

## Tech Stack
- **Frontend**: HTML5, Vanilla CSS (Premium/Dark Mode), JavaScript (Interactive elements).
- **Backend/Platform**: WordPress (inferred), AzuraCast (Radio), Nginx/Caddy (likely).
- **Infrastructure**: Proxmox VE (PVE).

## Roadmap
See [ROADMAP.md](ROADMAP.md) for detailed task list and priorities.

## DevOps & Infrastructure
- **PVE Access**: Goal is to allow `ssh pve` usage.
- **Keys**: To be located/configured.

## Design Guidelines
- **Visuals**: Dark mode, vibrant accents, glassmorphism, micro-animations.
- **UX**: Wow-factor on load, responsive, dynamic.
