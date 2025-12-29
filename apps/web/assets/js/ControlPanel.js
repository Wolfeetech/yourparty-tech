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
                                // Check if we have a genre element, if not create/append
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
            artistEl.textContent = song.artist;
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
            }
        });
    }
}

// Init when ready
document.addEventListener('DOMContentLoaded', () => {
    window.controlPanel = new ControlPanel();
});
