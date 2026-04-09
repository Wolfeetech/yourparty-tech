# Uptime Kuma Initial Setup Guide

## Access
**URL:** http://192.168.178.110:3001

## First Login
1. Open the URL above in your browser
2. Create an admin account (first user becomes admin)
3. Setup 2FA if desired

## Monitors to Add

### Critical (Priority 1)
| Name | Type | URL/Host | Interval |
|------|------|----------|----------|
| Website | HTTP(s) | `https://yourparty.tech` | 60s |
| Radio Stream | HTTP(s) | `https://radio.yourparty.tech/radio.mp3` | 60s |
| API Health | HTTP(s) - JSON Query | `https://api.yourparty.tech/health` | 30s |
| AzuraCast | HTTP(s) | `https://radio.yourparty.tech/api/nowplaying/1` | 60s |

### Infrastructure (Priority 2)
| Name | Type | URL/Host | Port | Interval |
|------|------|----------|------|----------|
| MongoDB | TCP Port | `192.168.178.222` | 27017 | 120s |
| MariaDB | TCP Port | `192.168.178.208` | 3306 | 120s |
| NPM Proxy | HTTP(s) | `https://npm.yourparty.tech` | - | 120s |

### Optional
| Name | Type | URL/Host | Interval |
|------|------|----------|----------|
| WebSocket | WebSocket | `wss://radio.yourparty.tech/ws/radio.yourparty` | 60s |
| Proxmox | HTTP(s) | `https://192.168.178.25:8006` | 300s |

## Notification Setup (Telegram)
1. Create Telegram Bot via @BotFather
2. Get Chat ID from @userinfobot
3. In Uptime Kuma: Settings → Notifications → Add Telegram
4. Token: `your_bot_token`
5. Chat ID: `your_chat_id`

## Status Page
1. Go to Status Pages → Create
2. Add monitors to the page
3. Get public URL to share
