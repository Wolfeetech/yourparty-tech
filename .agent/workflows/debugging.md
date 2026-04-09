---
description: How to debug and fix issues with the yourparty.tech system
---

# Debugging Guide

## Step 1: Identify the Problem Layer

```
Frontend (Browser) → WordPress API Proxy → FastAPI Backend → MongoDB/AzuraCast
```

Ask yourself:
- Is it a **display** issue? → Check browser console, `app.js`
- Is it an **API proxy** issue? → Check WordPress `api.php`, PHP logs
- Is it a **backend** issue? → Check FastAPI logs, `api.py`
- Is it a **data** issue? → Check MongoDB, AzuraCast

## Step 2: Check Each Layer

### Frontend (Browser)
// turbo
1. Open https://yourparty.tech/ in browser
2. Open Developer Tools (F12) → Console tab
3. Look for JavaScript errors (red messages)
4. Check Network tab for failed requests (red entries)

### WordPress API Proxy
// turbo
```bash
# Test direct API call
curl -v https://yourparty.tech/wp-json/yourparty/v1/status

# Check PHP error log
ssh pve "pct exec 207 -- tail -50 /var/log/apache2/error.log"
```

### FastAPI Backend
// turbo
```bash
# Test backend directly
curl https://api.yourparty.tech/
curl https://api.yourparty.tech/status

# Check API logs
ssh pve "pct exec 211 -- journalctl -u radio-api -n 100"

# Check if service is running
ssh pve "pct exec 211 -- systemctl status radio-api"
```

### MongoDB
// turbo
```bash
# Connect and check
ssh pve "pct exec 210 -- mongosh yourparty --eval 'db.stats()'"

# Check ratings count
ssh pve "pct exec 210 -- mongosh yourparty --eval 'db.ratings.countDocuments()'"
```

### AzuraCast
// turbo
```bash
# Test now playing
curl https://radio.yourparty.tech/api/nowplaying/1

# Check if stream is live
curl -I https://radio.yourparty.tech/radio.mp3
```

## Common Issues & Fixes

### Issue: "Unknown" in ratings/metadata
**Cause:** Tracks rated without title/artist info
**Fix:**
```bash
# Run enrichment script
ssh pve "pct exec 211 -- python3 /app/enrich_ratings.py"
```

### Issue: Control Panel shows empty data
**Cause:** API endpoint mismatch or MongoDB connection
**Debug:**
```bash
curl https://api.yourparty.tech/ratings
curl https://api.yourparty.tech/moods
```

### Issue: Vote returns 400/404
**Cause:** Wrong endpoint or missing parameters
**Debug:**
```bash
# Test correct endpoint with required params
curl -X POST https://api.yourparty.tech/vote-next-mood \
  -H "Content-Type: application/json" \
  -d '{"song_id": "test123", "mood_next": "energy"}'
```

### Issue: Stream shows offline
**Cause:** AzuraCast down or wrong station ID
**Debug:**
```bash
# Check AzuraCast stations
curl https://radio.yourparty.tech/api/stations
```

## Restart Services

// turbo
```bash
# Restart FastAPI
ssh pve "pct exec 211 -- systemctl restart radio-api"

# Restart WordPress/Apache
ssh pve "pct exec 207 -- systemctl restart apache2"

# Restart AzuraCast
ssh pve "pct exec 208 -- docker restart azuracast"
```
