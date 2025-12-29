/**
 * ControlPanel.js
 * 
 * Real-time "Mission Control" dashboard logic.
 * Handles polling for Vibe/Mood updates, Queue management, and Steering.
 */

class ControlPanel {
    constructor() {
        this.apiBase = 'https://api.yourparty.tech';
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
            tagBtn.addEventListener('click', async () => {
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
                if (modal) modal.showModal();
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
            // 1. Fetch Moods & Steering (Backend)
            const [moodsRes, steerRes] = await Promise.all([
                fetch(`${this.apiBase}/moods`),
                fetch(`${this.apiBase}/control/steer`)
            ]);

            this.fetchQueue(); // Poll Queue separately (non-blocking)

            this.updateMoods(await moodsRes.json());
            this.updateSteering(await steerRes.json());

            // 2. Fetch Now Playing (AzuraCast Public JSON)
            // Using static JSON for performance/reliability
            const npRes = await fetch('https://radio.yourparty.tech/api/nowplaying_static/radio.yourparty.json');
            const npData = await npRes.json();
            this.updateNowPlaying(npData);

        } catch (e) {
            console.error("❌ Control Pulse Failed:", e);
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
            artistEl.style.display = 'inline';
        }

        // Update Visualizer State?
        // (Visualizer usually handles itself via audio context, but we can sync state if needed)
    }

    async submitTag(mood) {
        if (!this.currentSongId) {
            alert("No song playing to tag!");
            return;
        }

        const statusEl = document.getElementById('tag-status');
        if (statusEl) statusEl.textContent = `Tagging as ${mood}...`;

        try {
            const res = await fetch(`${this.apiBase}/mood-tag`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    song_id: this.currentSongId,
                    mood: mood,
                    station_id: 1
                })
            });

            const result = await res.json();

            if (result.success || result.status === 'ok') { // Robust check
                if (statusEl) statusEl.textContent = "✅ Tag Saved!";
                setTimeout(() => {
                    document.getElementById('vibe-tag-modal').close();
                    if (statusEl) statusEl.textContent = "";
                }, 1000);
            } else {
                if (statusEl) statusEl.textContent = "❌ Save Failed";
            }
        } catch (e) {
            console.error("Tag error:", e);
            if (statusEl) statusEl.textContent = "❌ Connection Error";
        }
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

                await fetch(`${this.apiBase}/control/steer`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
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
            const res = await fetch(`${this.apiBase}/control/queue/${id}`, { method: 'DELETE' });
            if (res.ok) {
                this.fetchQueue(); // Refresh immediately
                // Also refresh Pulse to update other clients
                fetch(`${this.apiBase}/control/queue`);
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
            const res = await fetch(`${this.apiBase}/control/library/search?q=${encodeURIComponent(query)}`);
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
            const res = await fetch(`${this.apiBase}/control/queue`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
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
}

// Init when ready
document.addEventListener('DOMContentLoaded', () => {
    window.controlPanel = new ControlPanel();
});
