# YourParty.tech - Curator Admin Guide

> **Last Updated:** December 29, 2025  
> **Tested Version:** 3.4.0 (Decoupled & Visualized)  
> **Dashboard URL:** https://yourparty.tech/control/

---

## 🎯 Quick Start

The Control Panel allows curators to manage the radio experience in real-time with instant visual feedback.

### Access Requirements
- WordPress admin login (automatically detected)
- No additional authentication needed if logged in

---

## 📻 Core Features

### 1. Browse & Add Tracks (Ranked)

| Step | Action |
|------|--------|
| 1 | Click the **🔍 OPEN LIBRARY** button in the Radio Queue header |
| 2 | **NEW:** By default, it shows the **"🔥 HIGHEST RATED VIBES"** |
| 3 | Use the search bar to find specific tracks |
| 4 | Click **+ ADD** on any track to queue it |

> [!TIP]
> Top Rated tracks show their Star Rating (e.g., `★ 4.8`) right in the list.

---

### 2. Manage the Queue (Metadata Enhanced)

| Action | How |
|--------|-----|
| View Queue | Scroll to "RADIO QUEUE" section |
| **NEW:** See Vibe | Look for badges like `[ ENERGETIC ]` or `[ CHILL ]` next to titles |
| **NEW:** See Rating | High-rated tracks show a gold star `★ 5.0` badge |
| Delete Track | Click the **✕** button on any queued item |

> [!NOTE]
> The queue refresh is nearly instant. Metadata (Mood/Rating) is fetched live.

---

### 3. Tag Current Track (Mood Tagging)

| Step | Action |
|------|--------|
| 1 | Click **🏷️ TAG** in the footer |
| 2 | Select a mood: ENERGY, CHILL, EUPHORIC, DARK, GROOVY, or HYPNOTIC |
| 3 | Modal closes automatically after 1.5 seconds |
| 4 | **NEW:** The tag will immediately appear in the **Now Playing** footer area |

---

### 4. Vibe Steering (Manual Mode)

| Step | Action |
|------|--------|
| 1 | Click **AUTO PILOT** to toggle off |
| 2 | Select a target mood: ENERGETIC, CHILL, HYPNOTIC, DARK |
| 3 | The scheduler will prioritize harmonically compatible tracks matching that mood |

---

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| **Features Missing?** | **Force Reload** (Ctrl+Shift+R) to clear browser cache. We updated the scripts. |
| "Searching..." hangs | Check connection. Only admins can search. |
| Queue not updating | Click "OPEN LIBRARY" and close it to force a refresh. |
| "NO DATA YET" | Only appears for unrated/untagged tracks. Start tagging! |

---

## 📊 Dashboard Sections

1.  **SYSTEM STATUS** - API connection, listeners, mode
2.  **COMMUNITY VIBE** - Aggregate mood data
3.  **RADIO QUEUE** - **Enhanced** with Mood/Rating badges
4.  **LIBRARY INTEL** - **Enhanced** with Live Metadata
5.  **VIBE STEERING** - Manual mood control
6.  **NOW PLAYING** - Current track with metadata

---

## ⚠️ Known Limitations

1.  **Real-time Sync** - 5-second delay for internal sync (Decoupled Architecture).
2.  **Cold Start** - First load of playlists might take 5s while cache warms up. After that, it's instant.

---

## 🧪 Verification Checklist

- [ ] "OPEN LIBRARY" shows "HIGHEST RATED VIBES"
- [ ] Queue items show `[ MOOD ]` and `★ Rating`
- [ ] Validated Page Load Speed (< 1s)

---

*This guide was auto-generated and verified through browser testing.*
