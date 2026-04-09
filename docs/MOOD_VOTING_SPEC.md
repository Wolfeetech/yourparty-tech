# Mood Voting Specification

## Overview

The mood voting system allows listeners to:
1. **Tag current song's mood** - What mood does this track have?
2. **Vote for next song's mood** - What vibe do you want next?

This data influences the automatic DJ to select tracks matching community preferences.

---

## API Endpoints

### POST `/vote-mood`

Submit a mood vote for the current song and/or preference for the next.

**Request:**
```json
{
  "song_id": "abc123",
  "mood_current": "energy",
  "mood_next": "chill",
  "rating": 4,
  "vote": "like",
  "user_id": "anonymous"
}
```

**Valid Moods:**
- `energy`, `chill`, `groove`, `dark`, `euphoric`
- `melancholic`, `hypnotic`, `aggressive`, `trippy`, `warm`

**Response:**
```json
{
  "success": true,
  "song_id": "abc123",
  "mood_current": "energy",
  "mood_next": "chill",
  "mood_counts": { "energy": 5, "chill": 3 },
  "dominant_mood": "energy"
}
```

### GET `/mood-stats`

Get aggregated mood statistics.

**Response:**
```json
{
  "dominant_next_mood": "chill",
  "feature_flags": {
    "FEATURE_MOOD_VOTES": true,
    "FEATURE_MOOD_SYNC": false,
    "FEATURE_MOOD_AUTODJ": true,
    "MOOD_CYCLE_SECONDS": 300
  }
}
```

---

## Feature Flags

| Flag | Default | Description |
|------|---------|-------------|
| `FEATURE_MOOD_VOTES` | `true` | Enable mood voting endpoints |
| `FEATURE_MOOD_SYNC` | `false` | Sync moods to ID3/AzuraCast |
| `FEATURE_MOOD_AUTODJ` | `false` | Enable automatic DJ based on votes |
| `MOOD_CYCLE_SECONDS` | `300` | Auto-DJ cycle interval (5 min) |
| `MOOD_VOTE_COOLDOWN_MINUTES` | `5` | Rate limit per song |

---

## MongoDB Collections

### `mood_next_votes`

Stores user preferences for what mood they want next.

```json
{
  "_id": ObjectId,
  "song_id": "abc123",
  "mood_next": "chill",
  "user_id": "anonymous",
  "timestamp": ISODate
}
```

**Indexes:** `timestamp`, `mood_next`

### `moods` (existing)

Stores mood tags for songs.

```json
{
  "_id": ObjectId,
  "song_id": "abc123",
  "mood": "energy",
  "user_id": "anonymous",
  "timestamp": ISODate
}
```

---

## ID3 Tags (Future)

When `FEATURE_MOOD_SYNC=true`, the dominant mood is written to the ID3 TMOO frame:

```
TMOO: energy
```

See [Mutagen ID3 TMOO spec](https://mutagen-specs.readthedocs.io/en/latest/id3/id3v2.4.0-frames.html#tmoo)

---

## Auto-DJ Logic

When `FEATURE_MOOD_AUTODJ=true`:

1. Every `MOOD_CYCLE_SECONDS` (default 5 min), the scheduler runs
2. Queries votes from last 10 minutes to find dominant `mood_next`
3. Selects a random track with matching mood tag
4. Queues track in AzuraCast via `/api/station/1/request/{media_id}`
5. Falls back to top-rated tracks if no matching mood

**Prometheus Metrics:**

- `mood_queue_triggered_total` - Successful mood-based queue actions
- `mood_fallback_triggered_total` - Fallback to general rotation
