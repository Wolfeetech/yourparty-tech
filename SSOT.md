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
- **Status**: Site loads, but has issues.
- **Critical**: WebSocket errors (`wss://api.yourparty.tech`) - **FIX APPLIED**: Added `--proxy-headers` to Uvicorn service. Verifying.
- **Legal**: Impressum & Datenschutz deployed (Best Practice).
- **Structure**: Local files organized into `infrastructure/`.
- **Legal**: Impressum & Datenschutz are empty.
- **UI/UX**: User feedback: "Kindergarten" animations. Buttons broken. `/control` broken.
- **Visualizer**: Needs to be "Premium/Pro".
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
