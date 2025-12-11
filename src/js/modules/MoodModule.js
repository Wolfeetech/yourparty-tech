/**
 * YourParty Mood Tagging Module
 * Handles Mood/Genre voting, dialogs, and offline queueing.
 */

export const MOODS = {
    'energetic': { label: 'Energetic', emoji: '⚡', color: '#f59e0b' },
    'chill': { label: 'Chill', emoji: '🌴', color: '#10b981' },
    'euphoric': { label: 'Euphoric', emoji: '🤩', color: '#fbbf24' },
    'dark': { label: 'Dark', emoji: '🌑', color: '#6b7280' },
    'groovy': { label: 'Groovy', emoji: '💃', color: '#ec4899' },
    'melodic': { label: 'Melodic', emoji: '🎹', color: '#8b5cf6' },
    'melancholic': { label: 'Melancholic', emoji: '😢', color: '#6366f1' },
    'aggressive': { label: 'Aggressive', emoji: '😤', color: '#ef4444' },
    'hypnotic': { label: 'Hypnotic', emoji: '🌀', color: '#a78bfa' },
    'trippy': { label: 'Trippy', emoji: '🍄', color: '#c084fc' },
    'warm': { label: 'Warm', emoji: '☀️', color: '#fb923c' },
    'uplifting': { label: 'Uplifting', emoji: '🚀', color: '#3b82f6' },
    'atmospheric': { label: 'Atmospheric', emoji: '🌫️', color: '#3b82f6' },
    'raw': { label: 'Raw', emoji: '🏗️', color: '#78716c' }
};

export const GENRES = {
    'tech-house': 'Tech House',
    'deep-house': 'Deep House',
    'progressive-house': 'Progressive House',
    'afro-house': 'Afro House',
    'bass-house': 'Bass House',
    'dnb': 'Drum & Bass',
    'trance': 'Trance',
    'psytrance': 'Psytrance',
    'disco': 'Disco',
    'funk': 'Funk',
    'hiphop': 'HipHop',
    'trap': 'Trap',
    'dubstep': 'Dubstep',
    'garage': 'UK Garage',
    'breakbeat': 'Breakbeat',
    'ambient': 'Ambient',
    'downtempo': 'Downtempo',
    'melodic-techno': 'Melodic Techno',
    'techno': 'Techno',
    'minimal': 'Minimal',
    'indie': 'Indie',
    'pop': 'Pop',
    'rock': 'Rock',
    'schlager': 'Schlager'
};

class MoodModule {
    constructor(appConfig) {
        this.config = appConfig;
        this.currentSongId = null;
        this.currentMoods = {};

        // Offline Queue
        this.voteQueue = JSON.parse(localStorage.getItem('yp_vote_queue') || '[]');

        // Cooldowns
        this.cooldowns = JSON.parse(localStorage.getItem('yp_vote_cooldowns') || '{}');

        this.init();
    }

    init() {
        console.log('[MoodModule] Init (ES6)');
        this.bindGlobalEvents();
        this.createDialog();
        this.processQueue(); // Try to flush queue on init

        // Listen for online status
        window.addEventListener('online', () => this.processQueue());
    }

    bindGlobalEvents() {
        document.addEventListener('click', (e) => {
            // Tag Button
            if (e.target.closest('#mood-tag-button')) {
                e.preventDefault();
                this.openDialog();
            }

            // Vibe/Steering Buttons
            const vibeBtn = e.target.closest('.vibe-btn');
            if (vibeBtn) {
                e.preventDefault();
                this.handleSteering(vibeBtn);
            }
        });
    }

    async handleSteering(btn) {
        const vote = btn.dataset.vote;
        if (!vote) return;

        // Visual Feedback
        const allBtns = document.querySelectorAll('.vibe-btn');
        allBtns.forEach(b => b.classList.remove('selected'));
        btn.classList.add('selected');

        try {
            const baseUrl = this.config.restBase || '/api';
            // Use prediction endpoint
            const response = await fetch(`${baseUrl}/vote-next`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ vote: vote, timestamp: Date.now() })
            });

            const feedbackVal = document.getElementById('vibe-feedback');

            if (response.ok) {
                const data = await response.json();
                if (feedbackVal) {
                    feedbackVal.innerHTML = `VOTE: ${vote.toUpperCase()}!`;
                    if (data.prediction) {
                        feedbackVal.innerHTML += ` <small>(Next: ${data.prediction.title})</small>`;
                    }
                    feedbackVal.className = 'vibe-feedback success';
                    setTimeout(() => feedbackVal.textContent = '', 4000);
                }
            } else {
                throw new Error('Vote failed');
            }
        } catch (e) {
            console.error(e);
            this.showStatus('Steering failed.', 'error');
        }
    }

    createDialog() {
        if (document.getElementById('mood-dialog')) return;

        const moodGrid = Object.entries(MOODS).map(([key, m]) => `
            <button class="mood-btn" data-mood="${key}">
                <span class="emoji">${m.emoji}</span>
                <span class="label">${m.label}</span>
            </button>
        `).join('');

        const genreGrid = Object.entries(GENRES).map(([key, label]) => `
            <button class="mood-btn" data-genre="${key}">
                <span class="label">${label}</span>
            </button>
        `).join('');

        const dialog = document.createElement('div');
        dialog.id = 'mood-dialog';
        dialog.className = 'mood-dialog glass-panel';
        dialog.style.display = 'none';

        dialog.innerHTML = `
            <div class="mood-dialog-backdrop" id="mood-backdrop"></div>
            <div class="mood-dialog-content">
                <button class="close-btn" id="mood-close">&times;</button>
                <h3>Tag Vibe & Genre</h3>
                <p class="track-info" id="mood-track-info">Loading...</p>
                
                <div class="tag-section">
                    <h4>Vibe / Energy</h4>
                    <div class="mood-grid">${moodGrid}</div>
                </div>

                <div class="tag-section">
                    <h4>Genre</h4>
                    <div class="genre-grid">${genreGrid}</div>
                </div>

                <div class="status-msg" id="mood-status"></div>
            </div>
        `;

        document.body.appendChild(dialog);

        // Bind events
        const close = () => this.closeDialog();
        dialog.querySelector('#mood-close').onclick = close;
        dialog.querySelector('#mood-backdrop').onclick = close;

        dialog.querySelectorAll('.mood-btn').forEach(btn => {
            btn.onclick = (e) => this.handleSelection(e);
        });
    }

    openDialog() {
        const dialog = document.getElementById('mood-dialog');
        const trackInfo = document.getElementById('mood-track-info');

        // Get info from DOM as fallback or current state
        const title = document.getElementById('track-title')?.textContent || 'Unknown';
        const artist = document.getElementById('track-artist')?.textContent || 'Unknown';

        if (title.toUpperCase().includes("WAITING") || title.toUpperCase().includes("OFFLINE")) {
            alert("Please wait for a track to play.");
            return;
        }

        trackInfo.textContent = `${artist} - ${title}`;
        dialog.classList.add('active');
        dialog.style.display = 'flex';
    }

    closeDialog() {
        const dialog = document.getElementById('mood-dialog');
        dialog.classList.remove('active');
        setTimeout(() => {
            dialog.style.display = 'none';
            const status = document.getElementById('mood-status');
            if (status) status.textContent = '';
        }, 200);
    }

    handleSelection(e) {
        const btn = e.currentTarget;
        const mood = btn.dataset.mood;
        const genre = btn.dataset.genre;

        if (mood) this.submitVote(mood, 'mood', btn);
        if (genre) this.submitVote(genre, 'genre', btn);
    }

    async submitVote(val, type, btnElement) {
        if (!this.currentSongId || this.currentSongId === '0') {
            this.showStatus('No active song!', 'error');
            return;
        }

        // Check Cooldown
        const now = Date.now();
        const lastVote = this.cooldowns[this.currentSongId];
        if (lastVote && (now - lastVote < 300000)) { // 5 mins
            this.showStatus('Cooldown active (5m).', 'warning');
            return;
        }

        // Visual Feedback
        btnElement.style.transform = 'scale(0.95)';
        setTimeout(() => btnElement.style.transform = 'scale(1)', 100);

        const payload = {
            song_id: this.currentSongId,
            tag: val,
            type: type,
            timestamp: now
        };

        if (!navigator.onLine) {
            this.queueVote(payload);
            this.showStatus('Saved offline. Will sync later.', 'success');
            return;
        }

        try {
            await this.sendVote(payload);
            this.showStatus(`${type === 'mood' ? 'Mood' : 'Genre'} saved!`, 'success');

            // Set cooldown
            this.cooldowns[this.currentSongId] = now;
            localStorage.setItem('yp_vote_cooldowns', JSON.stringify(this.cooldowns));

        } catch (err) {
            console.error(err);
            // Fallback to queue if API fails
            this.queueVote(payload);
            this.showStatus('Network error. Queued.', 'warning');
        }
    }

    async sendVote(payload) {
        const baseUrl = this.config.restBase || '/api';
        const response = await fetch(`${baseUrl}/mood-tag`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (!response.ok) throw new Error('API Error');
    }

    queueVote(payload) {
        this.voteQueue.push(payload);
        localStorage.setItem('yp_vote_queue', JSON.stringify(this.voteQueue));
    }

    async processQueue() {
        if (this.voteQueue.length === 0 || !navigator.onLine) return;

        console.log(`[MoodModule] Processing ${this.voteQueue.length} queued votes...`);

        const queue = [...this.voteQueue]; // Copy
        this.voteQueue = []; // Clear local
        localStorage.setItem('yp_vote_queue', '[]');

        for (const payload of queue) {
            try {
                await this.sendVote(payload);
                console.log('Synced vote:', payload);
            } catch (err) {
                console.error('Sync failed, requeueing:', payload);
                this.voteQueue.push(payload); // Put back
            }
        }
        localStorage.setItem('yp_vote_queue', JSON.stringify(this.voteQueue));
    }

    showStatus(msg, type) {
        const el = document.getElementById('mood-status');
        if (el) {
            el.textContent = msg;
            el.className = 'status-msg ' + type;
            setTimeout(() => el.textContent = '', 3000);
        }
    }

    setCurrentSong(songId, moods) {
        this.currentSongId = songId;
        this.currentMoods = moods || {};
        this.updateDisplay();
    }

    updateDisplay() {
        // Here we could update badges on the player if we want to show current consensus
    }
}

export default MoodModule;
