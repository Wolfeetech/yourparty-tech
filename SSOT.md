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
- **Local Theme Path**: `c:\Users\StudioPC\yourparty-tech\yourparty-tech\yourparty-tech` (Nested)
- **Archive**: `_archive_frontend` (Unused React App).

## Insight & Audit (Browser)
- **Status**: ✅ **ALLE FEATURES AKTIV!**
- **WebSocket**: ✅ `[Realtime] Connected`
- **Vote-Next**: ✅ Funktioniert (Steering-Votes werden gezählt)
- **Rating-System**: ✅ 5-Sterne-Rating in MongoDB gespeichert
- **Mood-Tagging**: ✅ Moods werden gespeichert + `top_mood` berechnet
- **MongoDB**: ✅ Verbindung wiederhergestellt (Container 202)
- **ID3-Sync**: ✅ Code vorhanden, wird bei Rating/Mood getriggert
- **Legal Pages**: ✅ Impressum & Datenschutz deployed
- **UI/UX**: Premium CSS deployed (Gradienten, subtile Animationen)
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

## Design Guidelines (CI)
- **Primary Color**: `#8b5cf6` (Violet) - used for primary actions and highlights.
- **Accent Color**: `#ec4899` (Pink) - used for gradients and secondary highlights.
- **Background**: `#0f0f13` (Dark) with subtle radial gradients.
- **Typography**: 'Inter', sans-serif.
- **Glassmorphism**: heavily used for cards (`rgba(30, 30, 35, 0.6)` + `blur(12px)`).

## Communication Style & Philosophy
- **Authentic Quality**: We are ambitious professionals (2-man team). No corporate "bullshit".
- **Tone**: Friendly, professional, service-oriented. Use direct **"DU"** (You).
- **Style**: Use marketing hooks ("Mach dein Event legendär", "Kein Stress"). Active voice.
- **Focus**: Stage Management, FOH/Light Operating, 4K Drone Shots.
- **Radio Stream**: Is a *feature* (technical reference/inspiration), NOT the main product.
- **Headline Example**: "Mach dein Event legendär."
