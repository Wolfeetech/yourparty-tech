# Status Endpoint Specification

## Overview

The `/status` endpoint provides real-time "Now Playing" information from AzuraCast to the frontend.

---

## Endpoints

### WordPress REST API (Production)
```
GET /wp-json/yourparty/v1/status
```

### Python Backend (Alternative)
```
GET https://yourparty.tech/api/status
```

Both return the same data structure (frontend uses `/api/status` via the `restBase` config).

---

## Response Structure

```json
{
  "now_playing": {
    "song": {
      "id": "abc123",
      "title": "Example Track",
      "artist": "Example Artist",
      "album": "Album Name",
      "art": "https://radio.yourparty.tech/api/station/1/art/abc123.jpg",
      "duration": 240,
      "rating": {
        "average": 4.2,
        "total": 15
      },
      "top_mood": "energy"
    },
    "is_playing": true,
    "live": {
      "is_live": false
    }
  },
  "listeners": {
    "current": 42,
    "total": 1234
  },
  "playing_next": {
    "song": {
      "title": "Next Track",
      "artist": "Next Artist"
    }
  }
}
```

---

## Frontend Integration

The frontend (`app.js`) polls this endpoint every 10 seconds:

```javascript
const fetchStatus = async () => {
  const response = await fetch(buildEndpoint("status"));
  const data = await response.json();
  updateStatus(data);
};

// Called on page load
fetchStatus();
setInterval(fetchStatus, 10000);
```

### DOM Elements Updated
- `#track-title` - Song title
- `#track-artist` - Artist name
- `#cover-art` - Album artwork
- `#listener-count` - Current listeners
- `#track-status` - "On Air" / "Live DJ" / "Offline"

---

## Configuration

### WordPress (`wp-config.php`)
```php
define('YOURPARTY_AZURACAST_URL', 'https://192.168.178.210');
define('YOURPARTY_AZURACAST_API_KEY', 'your-key-here');
```

### Frontend (`functions.php`)
```php
$config = [
    'restBase' => 'https://yourparty.tech/api',  // Python backend
    'wpRestBase' => rest_url('yourparty/v1'),    // WordPress endpoints
    'publicBase' => 'https://radio.yourparty.tech',
    'streamUrl' => 'https://radio.yourparty.tech/listen/radio.yourparty/radio.mp3',
];
```

---

## Troubleshooting

### "Station Loading..." persists
1. **Check browser console** for JavaScript errors
2. **Verify API response**: `curl https://yourparty.tech/api/status`
3. **Clear browser cache** (Ctrl+Shift+R)
4. **Check CORS**: Response must include correct Access-Control headers

### API returns error
1. **Check AzuraCast connection**: Is `192.168.178.210` reachable from WP container?
2. **Verify API key**: Defined in `wp-config.php`?
3. **Check PHP logs**: `/var/log/apache2/error.log`

### CORS Errors
The Python backend (`api.py`) must include `yourparty.tech` in allowed origins:
```python
allow_origins=[
    "https://yourparty.tech",
    "https://www.yourparty.tech",
    ...
]
```

---

## Data Sources

| Source | Path | Returns |
|--------|------|---------|
| Python Backend | `/api/status` | Now playing from internal polling loop |
| WordPress | `/wp-json/yourparty/v1/status` | Proxies AzuraCast `/api/nowplaying/1` |
| AzuraCast Direct | `/api/nowplaying/1` | Raw station data |
