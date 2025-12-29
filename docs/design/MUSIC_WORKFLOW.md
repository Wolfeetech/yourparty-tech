# The "Perfect" Music Workflow (Single Source of Truth)

This document defines the architecture for a centralized, automated music system where MongoDB is the Single Source of Truth (SSOT), effectively feeding both the interactive home player (Music Assistant) and the radio station (AzuraCast).

## Core Philosophy
1.  **One Database**: Metadata, ratings, and moods live in MongoDB.
2.  **One Storage**: Files live on the NAS (`\\192.168.178.25\music`).
3.  **Automated Sync**: Changes in DB automatically propagate to file tags (portability) and radio playlists (AzuraCast).

## Architecture

```mermaid
graph TD
    User[User / DJ] -->|Adds Music| NAS[NAS Storage (\\music)]
    User -->|Rates/Tags| Mass[Music Assistant]
    
    subgraph "Central Intelligence (Apps/API)"
        Scanner[Library Service]
        Mongo[(MongoDB)]
        TagWriter[Tag Writer]
        PlayGen[Playlist Generator]
    end
    
    NAS -->|Scan| Scanner
    Scanner -->|Metadata| Mongo
    Mass -->|Votes| Mongo
    
    Mongo -->|Sync| TagWriter
    TagWriter -->|ID3 Tags| NAS
    
    Mongo -->|Queries| PlayGen
    PlayGen -->|API Update| Azura[AzuraCast Radio]
    
    NAS -->|Mount| Azura
    NAS -->|SMB| Mass
```

## Workflow Steps

### 1. Ingestion (The "New Music" Flow)
*   **Action**: You drop a file into `\\NAS\music\Inbox`.
*   **Automation**:
    1.  `library_service.py` detects the new file.
    2.  Calculates **Acoustic Fingerprint** to prevent duplicates.
    3.  Moves file to `\\NAS\music\Artist\Album\Title.mp3`.
    4.  Creates entry in **MongoDB**.
    5.  Triggers `azuracast_client.sync_media()` so the Radio knows it exists.

### 2. Curation (The "Vibe" Flow)
*   **Action**: You are listening in Music Assistant OR **watching the Livestream (yourparty.tech)** and click "Like" or "Chill Vibe".
*   **Automation**:
    1.  Vote is sent to **MongoDB** (via API/Webhook).
    2.  `music_manager.py` (Script) wakes up and writes the rating/mood into the **File ID3 Tags** (`TXXX:Mood`, `POPM:Rating`).
    3.  **Result**: If you copy this file to a USB stick for your car, the rating is *inside the file*.

### 3. Radio Programming (The "Playlist" Flow)
*   **Trigger**: A Scheduled Task (e.g., every hour) or a specific "Update Radio" button.
*   **Automation**:
    1.  **Starlight Playlist** (Euphoric): System queries MongoDB for `mood=euphoric` & `rating>4`.
    2.  **Slow Burn Playlist** (Chill): System queries MongoDB for `mood=chill`.
    3.  System calculates the list of **AzuraCast Media IDs** for these songs.
    4.  System calls AzuraCast API to **Replace Playlist Content** with the new dynamic list.
    5.  **Result**: The Radio Station automatically reflects your latest votes and mood tags without manual playlist editing.

## Implementation Checklist

### Phase 1: Foundation (Done/In-Progress)
- [x] **NAS Mount**: Server can see files (`Z:` / `/mnt/data`).
- [x] **MongoDB**: Database is running.
- [x] **Tag Sync**: `music_manager.py` writes Mongo data to ID3 tags.

### Phase 2: The "Link" (Next Steps)
- [ ] **AzuraCast ID Sync**: We need to store the `azuracast_media_id` in MongoDB so we can command the radio precisely.
- [ ] **Playlist Sync Script**: Create `sync_playlists.py` to map Mongo Queries -> AzuraCast Playlists.

### Phase 3: Music Assistant Integration (Blocked on Token)
- [ ] **Mass Provider**: Connect SMB Share to Mass.
- [ ] **Mass Metadata**: Ensure Mass reads the ID3 tags we just wrote.
