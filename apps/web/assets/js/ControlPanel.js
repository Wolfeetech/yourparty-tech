/**
 * ControlPanel.js
 * 
 * Real-time "Mission Control" dashboard logic.
 * Handles polling for Vibe/Mood updates, Queue management, and Steering.
 */

class ControlPanel {
    constructor() {
        this.apiBase = 'https://api.yourparty.tech';
        this.wpApiBase = '/wp-json/yourparty/v1';  // WordPress REST API
        this.nonce = (window.YourPartyConfig && window.YourPartyConfig.nonce) || '';
        this.pollInterval = 5000; // 5s
        this.pollTimer = null;

        // DOM Elements
        this.els = {
            dominantName: document.getElementById('dominant-mood-name'),
            dominantIcon: document.getElementById('dominant-mood-icon'),
            moodBars: document.getElementById('mood-bars'),
            totalVotes: document.querySelector('.vibe-stats .stat:nth-child(1) .stat-value'),
            listeners: document.querySelector('.vibe-stats .stat:nth-child(2) .stat-value'),
            queueList: document.querySelector('.queue-list'),
            steeringMode: document.getElementById('steer_mode_input')
        };

        this.init();
    }

    init() {
        console.log("🚀 CONTROL PANEL: Systems Online");
        this.startPolling();
        this.bindSteering();
        this.bindRealtime();
    }

    bindRealtime() {
        console.log("🔌 Binding Realtime Events...");

        // Listen for Steering Updates
        window.addEventListener('steerChange', (e) => {
            this.updateSteering(e.detail);
        });

        // Listen for 'Pulse' (Data Refresh Signals)
        window.addEventListener('pulse', (e) => {
            if (e.detail === 'moods') {
                this.fetchPulse(); // Refresh Moods immediately
            }
        });

        // Bind Tag Button
        const tagBtn = document.getElementById('mood-tag-button');
        if (tagBtn) {
            tagBtn.addEventListener('click', async (e) => {
                // Stop other scripts (mood-dialog.js, app.js) from handling this event
                e.stopImmediatePropagation();
                const modal = document.getElementById('vibe-tag-modal');
                if (modal) {
                    // Update Modal Title
                    const trackTitle = document.getElementById('track-title')?.textContent;
                    const modalTitle = document.getElementById('modal-track-title');
                    if (modalTitle) modalTitle.textContent = trackTitle || 'Unknown Track';

                    // Reset Status
                    const status = document.getElementById('tag-status');
                    if (status) status.textContent = 'Loading Genre...';

                    modal.showModal();

                    // Fetch Smart Genre
                    if (this.currentSongId) {
                        try {
                            const res = await fetch(`${this.apiBase}/track-metadata?song_id=${this.currentSongId}`);
                            const data = await res.json();
                            if (data.success && data.genre) {
                                // Display Genre
                                let genreEl = document.getElementById('modal-track-genre');
                                if (!genreEl) {
                                    genreEl = document.createElement('div');
                                    genreEl.id = 'modal-track-genre';
                                    genreEl.style.cssText = "color: var(--emerald); font-size: 12px; margin-top: 5px; text-transform: uppercase; letter-spacing: 1px;";
                                    modalTitle.parentNode.appendChild(genreEl);
                                }
                                genreEl.textContent = `[ ${data.genre} ]`;
                                if (status) status.textContent = '';
                            } else {
                                if (status) status.textContent = '';
                            }
                        } catch (e) { console.error(e); if (status) status.textContent = ''; }
                    }
                }
            });
        }

        // Bind Library Button
        const browseBtn = document.getElementById('open-library-btn');
        if (browseBtn) {
            browseBtn.addEventListener('click', () => {
                const modal = document.getElementById('library-modal');
                if (modal) {
                    modal.showModal();
                    this.fetchTopRated(); // Show content immediately
                }
            });
        }

        // Bind Library Search Input
        const searchInput = document.getElementById('lib-search-input');
        if (searchInput) {
            let timeout;
            searchInput.addEventListener('input', (e) => {
                const val = e.target.value.trim();
                clearTimeout(timeout);
                if (val.length > 2) {
                    timeout = setTimeout(() => this.searchLibrary(val), 500);
                }
            });
        }
    }

    startPolling() {
        this.fetchPulse();
        this.pollTimer = setInterval(() => this.fetchPulse(), this.pollInterval);
    }

    async fetchPulse() {
        try {
            // 1. Fetch Moods & Steering (via WordPress proxy) - Use allSettled to prevent partial failure blocking
            const results = await Promise.allSettled([
                fetch(`${this.wpApiBase}/control/moods`, { headers: { 'X-WP-Nonce': this.nonce } }),
                fetch(`${this.wpApiBase}/control/steer`, { headers: { 'X-WP-Nonce': this.nonce } })
            ]);

            const moodsRes = results[0].status === 'fulfilled' ? results[0].value : null;
            const steerRes = results[1].status === 'fulfilled' ? results[1].value : null;

            this.fetchQueue(); // Poll Queue separately (non-blocking)

            if (moodsRes && moodsRes.ok) this.updateMoods(await moodsRes.json());
            if (steerRes && steerRes.ok) this.updateSteering(await steerRes.json());
        } catch (e) {
            console.error("❌ Control Pulse Partial Error:", e);
        }

        try {
            // 2. Fetch Now Playing (AzuraCast Public JSON) - Critical for Tagging
            // Using static JSON for performance/reliability
            const npRes = await fetch('https://radio.yourparty.tech/api/nowplaying_static/radio.yourparty.json');
            if (npRes.ok) {
                const npData = await npRes.json();
                this.updateNowPlaying(npData);
            }
        } catch (e) {
            console.error("❌ Now Playing Sync Failed:", e);
        }
    }

    updateNowPlaying(data) {
        if (!data || !data.now_playing || !data.now_playing.song) return;

        const song = data.now_playing.song;
        this.currentSongId = song.id; // Store for tagging

        // Update Footer
        const titleEl = document.getElementById('track-title');
        const artistEl = document.getElementById('track-artist');

        if (titleEl) {
            titleEl.textContent = song.title;
            titleEl.classList.remove('skeleton');
        }
        if (artistEl) {
            let meta = '';
            if (song.initial_key) meta += ` <span class="badge" style="background:#333; padding:2px 6px; border-radius:4px; font-size:0.8em;">🔑 ${song.initial_key}</span>`;
            if (song.bpm) meta += ` <span class="badge" style="background:#333; padding:2px 6px; border-radius:4px; font-size:0.8em; margin-left:4px;">🥁 ${song.bpm}</span>`;

            artistEl.innerHTML = song.artist + meta;
            artistEl.innerHTML = song.artist + meta;
            artistEl.style.display = 'inline';
        }

        // Fetch authoritative metadata (Mood, Rating) from Mongo
        this.fetchTrackMetadata(song.id);

        // Update Visualizer State?
        // (Visualizer usually handles itself via audio context, but we can sync state if needed)
    }

    async submitTag(mood) {
        if (!this.currentSongId) {
            alert("No song playing to tag!");
            return;
        }

        const statusEl = document.getElementById('tag-status');
        const modal = document.getElementById('vibe-tag-modal');
        if (statusEl) statusEl.textContent = `Tagging as ${mood}...`;

        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 15000); // 15 second timeout

            const res = await fetch(`${this.wpApiBase}/mood-tag`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-WP-Nonce': this.nonce
                },
                body: JSON.stringify({
                    song_id: this.currentSongId,
                    mood: mood,
                    station_id: 1
                }),
                signal: controller.signal
            });

            clearTimeout(timeoutId);

            if (res.ok) {
                const result = await res.json();
                if (result.success || result.status === 'ok') {
                    if (statusEl) statusEl.textContent = "✅ Tag Saved!";
                } else {
                    if (statusEl) statusEl.textContent = "✅ Tag Recorded"; // Accept partial success
                }
            } else {
                if (statusEl) statusEl.textContent = `❌ Error ${res.status}`;
            }
        } catch (e) {
            console.error("Tag error:", e);
            if (e.name === 'AbortError') {
                if (statusEl) statusEl.textContent = "⏱️ Timeout - Tag may have saved";
            } else {
                if (statusEl) statusEl.textContent = "❌ Connection Error";
            }
        }

        // Always close modal after a delay regardless of result
        setTimeout(() => {
            if (modal) modal.close();
            if (statusEl) statusEl.textContent = "";
        }, 1500);
    }

    updateMoods(data) {
        if (!data) return;

        // Update Dominant
        if (this.els.dominantName) this.els.dominantName.textContent = data.dominant_mood || '--';

        // Update Bars
        // data.mood_counts = { energetic: 5, chill: 2 ... }
        if (this.els.moodBars && data.mood_counts) {
            const total = Object.values(data.mood_counts).reduce((a, b) => a + b, 0);

            // Clear or Update? Better to Diff. For now, rebuild is safer.
            this.els.moodBars.innerHTML = '';

            // Sort by count
            const sorted = Object.entries(data.mood_counts)
                .sort(([, a], [, b]) => b - a);

            for (const [mood, count] of sorted) {
                const percent = total > 0 ? (count / total) * 100 : 0;

                const item = document.createElement('div');
                item.className = 'mood-bar-item';
                item.innerHTML = `
                    <span class="mood-label">${mood}</span>
                    <div class="bar-container">
                        <div class="bar-fill" style="width:${percent}%; background-color: var(--emerald);"></div>
                    </div>
                    <span class="vote-count">${count}</span>
                `;
                this.els.moodBars.appendChild(item);
            }
        }

        if (this.els.totalVotes) this.els.totalVotes.textContent = data.total_votes || 0;
    }

    updateSteering(data) {
        // Update UI active states based on data.mode and data.target
        const mode = data.mode || 'auto';
        const target = data.target;

        document.querySelectorAll('.steer-btn').forEach(btn => btn.classList.remove('active'));

        if (mode === 'auto') {
            document.querySelector('.steer-btn.auto')?.classList.add('active');
            document.querySelector('.mode-indicator').textContent = 'AUTO';
            document.querySelector('.mode-indicator').classList.remove('manual');
            document.querySelector('.mode-indicator').classList.add('auto');
        } else {
            // Manual
            document.querySelector('.mode-indicator').textContent = 'MANUAL';
            document.querySelector('.mode-indicator').classList.add('manual');
            document.querySelector('.mode-indicator').classList.remove('auto');

            if (target) {
                const targetBtn = document.querySelector(`.steer-btn.mood[value="${target}"]`);
                if (targetBtn) targetBtn.classList.add('active');
            }
        }
    }

    bindSteering() {
        // Hijack forms?
        // The existing PHP uses forms. We can intercept submit.
        const form = document.querySelector('.steering-grid');
        if (!form) return;

        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            // Determine clicked button
            const clickedBtn = e.submitter;
            if (!clickedBtn) return;

            const mode = clickedBtn.classList.contains('auto') ? 'auto' : 'manual';
            const target = clickedBtn.value; // Mood value

            console.log(`📡 Steering change: ${mode} -> ${target}`);

            // Optimistic UI Update
            this.updateSteering({ mode, target });

            try {
                // Determine Mode (Auto vs Mood)
                // The API expects JSON body
                const payload = {
                    mode: mode === 'auto' ? 'auto' : 'mood',
                    target: mode === 'auto' ? null : target
                };

                await fetch(`${this.wpApiBase}/control/steer`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-WP-Nonce': this.nonce
                    },
                    body: JSON.stringify(payload)
                });

                // Fetch fresh pulse to confirm
                setTimeout(() => this.fetchPulse(), 500);

            } catch (err) {
                console.error("Steering failed", err);
                alert("Steering command failed. Check connection.");
                alert("Steering command failed. Check connection.");
            }
        });
    }

    async fetchQueue() {
        if (!this.els.queueList) return;
        try {
            const res = await fetch(`${this.apiBase}/control/queue`);
            const data = await res.json();
            this.updateQueue(data);
        } catch (e) {
            console.error("Queue fetch error:", e);
        }
    }

    updateQueue(items) {
        if (!this.els.queueList) return;

        // Remove 'empty-state' if present and items exist
        if (items && items.length > 0) {
            const empty = this.els.queueList.querySelector('.empty-state');
            if (empty) empty.remove();
        } else {
            // Keep user message if empty
            this.els.queueList.innerHTML = '<div class="empty-state" style="padding:20px; text-align:center; color:#666;">Queue empty or AutoDJ active</div>';
            return;
        }

        this.els.queueList.innerHTML = '';

        items.forEach((item, i) => {
            const song = item.song || {};
            const mood = item.mood_top;
            const key = item.initial_key;
            const bpm = item.bpm;
            const rating = item.rating ? item.rating.average : 0;

            const el = document.createElement('div');
            el.className = 'queue-item';
            el.dataset.id = item.id;

            // Replicate PHP Style Structure + Metadata
            // Structure: queue-pos, queue-track (title+artist), actions

            let metaHtml = '';
            if (key) metaHtml += `<span class="badge key-badge" style="background:#333; color:#aaa; font-size:9px; padding:2px 4px; border-radius:3px; margin-left:5px;">🔑 ${key}</span>`;
            if (bpm) metaHtml += `<span class="badge bpm-badge" style="background:#333; color:#aaa; font-size:9px; padding:2px 4px; border-radius:3px; margin-left:5px;">🥁 ${bpm}</span>`;
            if (mood) metaHtml += `<span class="badge mood-badge" style="background:#222; color:var(--emerald); font-size:9px; padding:2px 4px; border-radius:3px; margin-left:5px; border:1px solid #333;">${mood}</span>`;
            if (rating > 0) metaHtml += `<span class="badge" style="color:#ffd700; font-size:9px; margin-left:5px;">★ ${parseFloat(rating).toFixed(1)}</span>`;

            el.innerHTML = `
                <span class="queue-pos" style="font-family:monospace; color:#666; width:30px; text-align:center;">${i + 1}</span>
                <div class="queue-track" style="flex:1;">
                    <span class="queue-title" style="display:block; font-weight:600; color:#fff;">${song.title || 'Unknown'} ${metaHtml}</span>
                    <span class="queue-artist" style="display:block; font-size:11px; color:var(--emerald); opacity:0.8;">${song.artist || ''}</span>
                </div>
                <div class="queue-actions">
                    <button class="queue-btn move-up" title="Move Up (Coming Soon)" disabled style="opacity:0.3; cursor:not-allowed; border:none; background:none; color:#666;">▲</button>
                    <button class="queue-btn move-down" title="Move Down (Coming Soon)" disabled style="opacity:0.3; cursor:not-allowed; border:none; background:none; color:#666;">▼</button>
                    <button class="queue-btn remove btn-delete" title="Remove Track" style="border:none; background:none; color:#ff4444; font-size:14px; cursor:pointer;">✕</button>
                </div>
            `;

            // Bind Delete
            el.querySelector('.btn-delete').addEventListener('click', (e) => {
                e.preventDefault();
                if (confirm(`Remove "${song.title}" from queue?`)) {
                    // Optimistic UI Removal
                    el.style.opacity = '0.5';
                    this.deleteQueueItem(item.id);
                }
            });

            this.els.queueList.appendChild(el);
        });
    }

    async deleteQueueItem(id) {
        try {
            const res = await fetch(`${this.wpApiBase}/control/queue/${id}`, {
                method: 'DELETE',
                headers: { 'X-WP-Nonce': this.nonce }
            });
            if (res.ok) {
                this.fetchQueue(); // Refresh immediately
            } else {
                alert("Failed to delete item");
            }
        } catch (e) {
            console.error("Delete failed", e);
        }
    }

    async searchLibrary(query) {
        const resultsEl = document.getElementById('lib-search-results');
        if (!resultsEl) return;

        resultsEl.innerHTML = '<div style="text-align:center; padding:20px; color:#888;">Searching...</div>';

        try {
            const res = await fetch(`${this.wpApiBase}/control/library/search?q=${encodeURIComponent(query)}`, {
                headers: { 'X-WP-Nonce': this.nonce }
            });
            const items = await res.json();

            resultsEl.innerHTML = '';

            if (!items || items.length === 0) {
                resultsEl.innerHTML = '<div style="text-align:center; padding:20px; color:#666;">No results found.</div>';
                return;
            }

            items.forEach(item => {
                const song = item.song || {};
                const row = document.createElement('div');
                row.className = 'lib-result-item';
                row.style.cssText = "display:flex; justify-content:space-between; align-items:center; background:rgba(255,255,255,0.05); padding:10px; border-radius:4px; border:1px solid rgba(255,255,255,0.05);";

                row.innerHTML = `
                    <div style="flex:1;">
                        <div style="font-weight:bold; color:#fff; font-size:13px;">${song.title}</div>
                        <div style="font-size:11px; color:#aaa;">${song.artist}</div>
                    </div>
                    <div>
                        <button class="cyber-btn small btn-queue" style="padding:4px 8px; font-size:10px; background:var(--emerald); color:#000; border:none; cursor:pointer;">+ ADD</button>
                    </div>
                `;

                row.querySelector('.btn-queue').addEventListener('click', () => {
                    // request_id is usually what we need, which is item.request_id or item.song.id?
                    // AzuraCast Search Request returns row.request_id usually.
                    // The endpoint expects media_id (song_id or unique_id).
                    // AzuraCast Search API returns: { song: {...}, request_id: "...", request_url: "..." }
                    // We need to use `item.request_song_id` or `item.song.id`?
                    // Let's use `item.request_song_id` or `item.song.id`.
                    // Actually based on `azuracast_client.search_requests`, it returns rows.
                    // Each row usually has `song_id` string or `row.song.id`.
                    // Let's use `item.song.id`.
                    this.queueTrack(item.song.id, song.title);
                });

                resultsEl.appendChild(row);
            });

        } catch (e) {
            console.error("Search error", e);
            resultsEl.innerHTML = '<div style="text-align:center; padding:20px; color:#ff4444;">Search failed.</div>';
        }
    }

    async queueTrack(mediaId, title) {
        if (!confirm(`Add "${title}" to Queue?`)) return;

        try {
            const res = await fetch(`${this.wpApiBase}/control/queue`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-WP-Nonce': this.nonce
                },
                body: JSON.stringify({ media_id: mediaId })
            });
            const data = await res.json();

            if (data.success) {
                alert("Track queued successfully!");
                document.getElementById('library-modal').close();
                this.fetchQueue(); // Refresh queue
            } else {
                alert("Failed to queue track. It might be on cooldown.");
            }
        } catch (e) {
            console.error("Queue error", e);
            alert("Error queuing track.");
        }
    }

    async fetchTopRated() {
        const resultsEl = document.getElementById('lib-search-results');
        if (!resultsEl) return;

        resultsEl.innerHTML = '<div style="text-align:center; padding:20px; color:#888;">Loading Top Rated...</div>';

        try {
            const res = await fetch(`${this.wpApiBase}/control/library/rated`, { headers: { 'X-WP-Nonce': this.nonce } });
            const data = await res.json();

            // API returns { tracks: [], count: N }
            const tracks = data.tracks || [];

            if (tracks.length === 0) {
                resultsEl.innerHTML = '<div style="text-align:center; padding:20px; color:#666;">No rated tracks yet. Start voting!</div>';
                return;
            }

            resultsEl.innerHTML = '<div style="padding:10px; color:var(--emerald); font-size:12px; font-weight:bold; letter-spacing:1px; border-bottom:1px solid #333; margin-bottom:10px;">🔥 HIGHEST RATED VIBES</div>';

            tracks.forEach((track, i) => {
                const row = document.createElement('div');
                row.className = 'lib-result-item';
                row.style.cssText = "display:flex; justify-content:space-between; align-items:center; background:rgba(255,255,255,0.05); padding:10px; border-radius:4px; border:1px solid rgba(255,255,255,0.05); margin-bottom:5px;";

                // Rating Badge
                const rating = parseFloat(track.rating || 0).toFixed(1);

                row.innerHTML = `
                    <div style="flex:1;">
                        <div style="font-weight:bold; color:#fff; font-size:13px;">${track.title || 'Unknown'} <span style="color:#ffd700;">★ ${rating}</span></div>
                        <div style="font-size:11px; color:#aaa;">${track.artist || 'Unknown'}</div>
                    </div>
                    <div>
                        <button class="cyber-btn small btn-queue" style="padding:4px 8px; font-size:10px; background:var(--emerald); color:#000; border:none; cursor:pointer;">+ ADD</button>
                    </div>
                `;

                // Track objects from Mongo usually have `song_id` or `azuracast_id`
                const mid = track.song_id || track.id;
                row.querySelector('.btn-queue').addEventListener('click', () => {
                    this.queueTrack(mid, track.title);
                });

                resultsEl.appendChild(row);
            });

        } catch (e) {
            console.error("Top Rated error", e);
            resultsEl.innerHTML = '<div style="text-align:center; padding:20px; color:#ff4444;">Failed to load top tracks.</div>';
        }
    }

    async fetchTrackMetadata(songId) {
        if (!songId) return;
        try {
            // Get title and artist from current NP state for better matching
            const titleEl = document.getElementById('track-title');
            const artistEl = document.getElementById('track-artist');
            const title = titleEl ? encodeURIComponent(titleEl.textContent.trim()) : '';
            const artistRaw = artistEl ? artistEl.textContent.split('<span')[0].trim() : '';
            const artist = encodeURIComponent(artistRaw);

            // Build URL with all identifiers
            let url = `${this.apiBase}/track-metadata?song_id=${songId}`;
            if (title) url += `&title=${title}`;
            if (artist) url += `&artist=${artist}`;

            const res = await fetch(url);
            const data = await res.json();

            if (data.success) {
                // Update Intel UI
                const artistEl = document.getElementById('track-artist');
                let extras = '';

                if (data.mood) extras += ` <span style="color:var(--emerald); border:1px solid var(--emerald); padding:1px 4px; border-radius:3px; font-size:0.8em; margin-left:5px;">${data.mood}</span>`;

                // We could show rating here too if the endpoint returns it (it doesn't currently, likely needs update)
                // But user specifically asked for "Next song has this mood".

                if (artistEl) artistEl.innerHTML += extras;
            }
        } catch (e) {
            console.error("Meta fetch failed", e);
        }
    }

    // =============================================
    // PLAYLIST MANAGEMENT (NTS-Lite Curator)
    // =============================================

    async fetchPlaylists() {
        try {
            const res = await fetch(`${this.wpApiBase}/curator/playlists`);
            const playlists = await res.json();
            this.renderPlaylists(playlists);
        } catch (e) {
            console.error("Failed to fetch playlists:", e);
        }
    }

    renderPlaylists(playlists) {
        const grid = document.getElementById('playlist-grid');
        if (!grid) return;

        if (!playlists || !Array.isArray(playlists) || playlists.length === 0) {
            console.warn("Playlists data invalid or empty:", playlists);
            grid.innerHTML = '<div style="text-align:center; padding:20px; color:#666;">No playlists yet. Click + NEW to create one.</div>';
            return;
        }

        grid.innerHTML = '';
        playlists.forEach(pl => {
            const card = document.createElement('div');
            card.className = 'playlist-card';
            card.style.cssText = `
                background: rgba(255,255,255,0.03);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 8px;
                padding: 12px;
                margin-bottom: 10px;
                cursor: pointer;
                transition: all 0.2s;
            `;
            card.onmouseover = () => card.style.borderColor = 'var(--emerald)';
            card.onmouseout = () => card.style.borderColor = 'rgba(255,255,255,0.1)';

            const hasSchedule = pl.schedule && pl.schedule.length > 0;
            const scheduleInfo = hasSchedule
                ? `<span style="color:var(--emerald); font-size:10px;">📅 Scheduled</span>`
                : `<span style="color:#666; font-size:10px;">No schedule</span>`;

            card.innerHTML = `
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <div style="font-weight:600; color:#fff;">${pl.name}</div>
                        <div style="font-size:11px; color:#888;">${pl.num_songs || 0} tracks • ${scheduleInfo}</div>
                    </div>
                    <div style="display:flex; gap:5px;">
                        <button class="btn-schedule" data-id="${pl.id}" style="background:#333; border:none; color:#fff; padding:4px 8px; border-radius:4px; cursor:pointer; font-size:10px;">📅</button>
                        <button class="btn-play" data-id="${pl.id}" style="background:var(--emerald); border:none; color:#000; padding:4px 8px; border-radius:4px; cursor:pointer; font-size:10px;">▶</button>
                    </div>
                </div>
            `;

            // Bind schedule button
            card.querySelector('.btn-schedule').addEventListener('click', (e) => {
                e.stopPropagation();
                this.showScheduleDialog(pl);
            });

            // Bind play button (immediate queue)
            card.querySelector('.btn-play').addEventListener('click', (e) => {
                e.stopPropagation();
                this.activatePlaylist(pl.id);
            });

            grid.appendChild(card);
        });
    }

    async fetchSchedule() {
        try {
            const res = await fetch(`${this.wpApiBase}/curator/schedule`);
            const data = await res.json();
            this.renderSchedule(data.schedule || []);
        } catch (e) {
            console.error("Failed to fetch schedule:", e);
        }
    }

    renderSchedule(scheduleItems) {
        const list = document.getElementById('schedule-list');
        if (!list) return;

        if (!scheduleItems || scheduleItems.length === 0) {
            list.innerHTML = '<div style="color:#666;">No scheduled shows. Click 📅 on a playlist to schedule it.</div>';
            return;
        }

        const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
        list.innerHTML = '';

        scheduleItems.forEach(item => {
            const dayNames = (item.days || []).map(d => days[d]).join(', ') || 'Daily';
            const row = document.createElement('div');
            row.style.cssText = 'display:flex; justify-content:space-between; padding:5px 0; border-bottom:1px solid #222;';
            row.innerHTML = `
                <span style="color:#fff;">${item.playlist_name}</span>
                <span style="color:#888;">${item.start_time} - ${item.end_time} (${dayNames})</span>
            `;
            list.appendChild(row);
        });
    }

    async createPlaylist() {
        const name = prompt('Enter playlist name:');
        if (!name) return;

        try {
            const res = await fetch(`${this.wpApiBase}/curator/playlists`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name })
            });
            const result = await res.json();
            if (result.success) {
                this.fetchPlaylists(); // Refresh
                alert(`Playlist "${name}" created!`);
            } else {
                alert('Failed to create playlist');
            }
        } catch (e) {
            console.error('Create playlist error:', e);
            alert('Error creating playlist');
        }
    }

    showScheduleDialog(playlist) {
        const startTime = prompt(`Schedule "${playlist.name}"\n\nStart time (HH:MM):`, '20:00');
        if (!startTime) return;

        const endTime = prompt('End time (HH:MM):', '22:00');
        if (!endTime) return;

        const daysInput = prompt('Days (0=Mon, 6=Sun, comma separated):', '4,5');
        const days = daysInput ? daysInput.split(',').map(d => parseInt(d.trim())).filter(d => !isNaN(d)) : [];

        this.schedulePlaylist(playlist.id, startTime, endTime, days);
    }

    async schedulePlaylist(playlistId, startTime, endTime, days) {
        try {
            const res = await fetch(`${this.wpApiBase}/curator/playlists/${playlistId}/schedule`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ start_time: startTime, end_time: endTime, days })
            });
            const result = await res.json();
            if (result.success) {
                this.fetchSchedule(); // Refresh
                this.fetchPlaylists();
                alert('Schedule added!');
            } else {
                alert('Failed to add schedule');
            }
        } catch (e) {
            console.error('Schedule error:', e);
            alert('Error scheduling playlist');
        }
    }

    async activatePlaylist(playlistId) {
        // This would typically set the playlist as the active source
        // For now, show confirmation
        alert(`Playlist ${playlistId} activated! (Feature in development)`);
    }

    initCuratorFeatures() {
        // Bind create playlist button
        const createBtn = document.getElementById('create-playlist-btn');
        if (createBtn) {
            createBtn.addEventListener('click', () => this.createPlaylist());
        }

        // Initial fetch
        this.fetchPlaylists();
        this.fetchSchedule();
    }
}

// Init when ready
// Init when ready
document.addEventListener('DOMContentLoaded', () => {
    window.controlPanel = new ControlPanel();
    // Legacy support / Curator alias
    window.curator = window.controlPanel;
});

// Init curator features after a short delay
setTimeout(() => {
    if (window.controlPanel.initCuratorFeatures) {
        window.controlPanel.initCuratorFeatures();
    }
}, 500);
});
