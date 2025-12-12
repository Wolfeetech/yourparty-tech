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
        this.currentTrack = null;

        // State
        this.selectedMoodCurrent = null;
        this.selectedMoodNext = null;
        this.activeTab = 'current';

        // Offline Queue
        this.voteQueue = JSON.parse(localStorage.getItem('yp_vote_queue') || '[]');

        // Cooldowns
        this.cooldowns = JSON.parse(localStorage.getItem('yp_mood_cooldowns') || '{}');
        this.VOTE_COOLDOWN_MS = 5 * 60 * 1000; // 5 Minutes

        this.init();
    }

    init() {
        console.log('[MoodModule] Init (ES6 - Dual Voting)');
        this.bindGlobalEvents();
        this.createDialog();
        this.processQueue(); // Try to flush queue on init

        // Explicit Check & Bind for Debugging
        // Global Event Delegation for Dynamic Elements
        document.body.addEventListener('click', (e) => {
            const btn = e.target.closest('#mood-tag-button');
            if (btn) {
                console.log('[MoodModule] Delegated Click Triggered');
                e.preventDefault();
                e.stopPropagation();
                this.openDialog();
            }
        });

        // Debug Log
        if (document.getElementById('mood-tag-button')) {
            console.log('[MoodModule] Tag Button Visible on Init');
        }

        // Listen for online status
        window.addEventListener('online', () => this.processQueue());

        // Backward Compatibility
        window.openMoodDialog = () => this.openDialog();
    }

    bindGlobalEvents() {
        document.addEventListener('click', (e) => {
            // Tag Button
            if (e.target.closest('#mood-tag-button')) {
                e.preventDefault();
                this.openDialog();
            }

            // Vibe/Steering Buttons (Quick Vote)
            const vibeBtn = e.target.closest('.vibe-btn');
            if (vibeBtn) {
                e.preventDefault();
                this.handleSteering(vibeBtn);
            }
        });
    }

    async handleSteering(btn) {
        // Quick vote for "Next" mood
        const vote = btn.dataset.vote;
        if (!vote) return;

        // Visual Feedback
        const allBtns = document.querySelectorAll('.vibe-btn');
        allBtns.forEach(b => b.classList.remove('selected'));
        btn.classList.add('selected');

        const payload = {
            song_id: this.currentSongId || 'global',
            mood_next: vote,
            source: 'steering_deck',
            timestamp: Date.now()
        };

        if (!navigator.onLine) {
            this.queueVote(payload);
            this.showGlobalFeedback(`Vibe "${vote}" queued (offline).`, 'warning');
            return;
        }

        try {
            await this.sendVote(payload);
            this.showGlobalFeedback(`VOTE: ${vote.toUpperCase()} recorded!`, 'success');
        } catch (e) {
            console.error(e);
            this.queueVote(payload);
            this.showGlobalFeedback('Network error. Vote queued.', 'warning');
        }
    }

    showGlobalFeedback(msg, type) {
        // Fallback feedback if no specific element exists
        const fb = document.getElementById('vibe-feedback');
        if (fb) {
            fb.textContent = msg;
            fb.className = `vibe-feedback ${type}`;
            setTimeout(() => fb.textContent = '', 4000);
        } else {
            console.log(`[Feedback] ${msg}`);
        }
    }

    createDialog() {
        if (document.getElementById('mood-dialog')) return;

        const moodButtonsHTML = Object.entries(MOODS).map(([key, m]) => `
            <button class="mood-btn" data-value="${key}" 
                    aria-label="${m.label}" role="radio" aria-checked="false">
                <span class="emoji">${m.emoji}</span>
                <span class="label">${m.label}</span>
            </button>
        `).join('');

        const dialog = document.createElement('div');
        dialog.id = 'mood-dialog';
        dialog.className = 'mood-dialog glass-panel';
        dialog.style.display = 'none';

        // Accessibility
        dialog.setAttribute('role', 'dialog');
        dialog.setAttribute('aria-modal', 'true');
        dialog.setAttribute('aria-labelledby', 'mood-dialog-title');

        dialog.innerHTML = `
            <div class="mood-dialog-backdrop" id="mood-backdrop"></div>
            <div class="mood-dialog-content">
                <button class="close-btn" id="mood-close" aria-label="Close">&times;</button>
                <h3 id="mood-dialog-title">Tag Vibe & Genre</h3>
                <p class="track-info" id="mood-track-info">Loading...</p>
                
                <!-- TABS -->
                <div class="mood-tabs" role="tablist">
                    <button class="mood-tab active" data-tab="current" role="tab" aria-selected="true">🎵 Current Song</button>
                    <button class="mood-tab" data-tab="next" role="tab" aria-selected="false">⏭️ Next Vibe</button>
                </div>

                <!-- PANEL: CURRENT -->
                <div class="mood-panel active" id="panel-current" role="tabpanel">
                    <p class="hint">How does this song make you feel?</p>
                    <div class="mood-grid" data-target="current">
                        ${moodButtonsHTML}
                    </div>
                </div>

                <!-- PANEL: NEXT -->
                <div class="mood-panel" id="panel-next" role="tabpanel" style="display:none;">
                    <p class="hint">What vibe do you want next?</p>
                    <div class="mood-grid" data-target="next">
                        ${moodButtonsHTML}
                    </div>
                </div>

                <div class="status-msg" id="mood-status" role="status" aria-live="polite"></div>

                <div class="dialog-actions">
                     <button id="mood-submit-btn" class="submit-btn" disabled>Submit Vote</button>
                </div>
            </div>
        `;

        document.body.appendChild(dialog);

        // Bind Events
        const close = () => this.closeDialog();
        dialog.querySelector('#mood-close').onclick = close;
        dialog.querySelector('#mood-backdrop').onclick = close;

        // Tabs
        dialog.querySelectorAll('.mood-tab').forEach(tab => {
            tab.onclick = () => this.switchTab(tab.dataset.tab);
        });

        // Mood Selection
        dialog.querySelectorAll('.mood-btn').forEach(btn => {
            btn.onclick = (e) => this.handleSelection(e);
        });

        // Submit
        dialog.querySelector('#mood-submit-btn').onclick = () => this.handleSubmit();
    }

    switchTab(tabName) {
        this.activeTab = tabName;
        const dialog = document.getElementById('mood-dialog');

        // Update Tabs
        dialog.querySelectorAll('.mood-tab').forEach(t => {
            const isActive = t.dataset.tab === tabName;
            t.classList.toggle('active', isActive);
            t.setAttribute('aria-selected', isActive);
        });

        // Update Panels
        const panelCurrent = dialog.querySelector('#panel-current');
        const panelNext = dialog.querySelector('#panel-next');

        if (tabName === 'current') {
            panelCurrent.style.display = 'block';
            panelNext.style.display = 'none';
        } else {
            panelCurrent.style.display = 'none';
            panelNext.style.display = 'block';
        }
    }

    handleSelection(e) {
        const btn = e.currentTarget;
        const value = btn.dataset.value;
        const target = btn.closest('.mood-grid').dataset.target; // 'current' or 'next'

        // Deselect others in same grid
        const grid = btn.closest('.mood-grid');
        grid.querySelectorAll('.mood-btn').forEach(b => {
            b.classList.remove('selected');
            b.setAttribute('aria-checked', 'false');
        });

        // Select clicked
        btn.classList.add('selected');
        btn.setAttribute('aria-checked', 'true');

        if (target === 'current') {
            this.selectedMoodCurrent = value;
        } else {
            this.selectedMoodNext = value;
        }

        this.updateSubmitButton();
    }

    updateSubmitButton() {
        const btn = document.getElementById('mood-submit-btn');
        if (btn) {
            btn.disabled = (!this.selectedMoodCurrent && !this.selectedMoodNext);
        }
    }

    openDialog() {
        const dialog = document.getElementById('mood-dialog');
        const trackInfo = document.getElementById('mood-track-info');

        // Check Cooldown
        if (this.currentSongId && this.isOnCooldown(this.currentSongId)) {
            alert("You've already voted on this track recently. Please wait.");
            return;
        }

        // Get info
        const title = this.currentTrack?.title || document.getElementById('track-title')?.textContent || 'Unknown';
        const artist = this.currentTrack?.artist || document.getElementById('track-artist')?.textContent || 'Unknown';

        trackInfo.textContent = `${artist} - ${title}`;

        // Reset State
        this.selectedMoodCurrent = null;
        this.selectedMoodNext = null;
        this.activeTab = 'current';
        this.switchTab('current');
        this.updateSubmitButton();

        // Clear previous selections
        dialog.querySelectorAll('.mood-btn').forEach(b => {
            b.classList.remove('selected');
            b.setAttribute('aria-checked', 'false');
        });

        dialog.classList.add('active');
        dialog.style.display = 'flex';
    }

    closeDialog() {
        const dialog = document.getElementById('mood-dialog');
        dialog.classList.remove('active');
        setTimeout(() => {
            dialog.style.display = 'none';
            this.showStatus('');
        }, 200);
    }

    async handleSubmit() {
        if (!this.currentSongId) {
            this.showStatus('Error: No active song identified.', 'error');
            return;
        }

        const payload = {
            song_id: this.currentSongId,
            mood_current: this.selectedMoodCurrent,
            mood_next: this.selectedMoodNext,
            timestamp: Date.now()
        };

        const btn = document.getElementById('mood-submit-btn');
        btn.disabled = true;
        btn.textContent = 'Sending...';

        if (!navigator.onLine) {
            this.queueVote(payload);
            this.showStatus('Saved offline. Will sync later.', 'success');
            setTimeout(() => this.closeDialog(), 1500);
            return;
        }

        try {
            await this.sendVote(payload);
            this.showStatus('Vote recorded! Thanks.', 'success');

            // Set cooldown
            this.setCooldown(this.currentSongId);

            setTimeout(() => {
                this.closeDialog();
                btn.textContent = 'Submit Vote';
            }, 1000);

        } catch (err) {
            console.error(err);
            this.queueVote(payload);
            this.showStatus('Network error. Queued.', 'warning');
            setTimeout(() => this.closeDialog(), 1500);
        }
    }

    async sendVote(payload) {
        const baseUrl = this.config.restBase || '/wp-json/yourparty/v1'; // Default to WP proxy
        // Note: New endpoint is /vote-mood
        const endpoint = `${baseUrl}/vote-mood`;

        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const txt = await response.text();
            throw new Error(`API Error: ${response.status} ${txt}`);
        }
    }

    queueVote(payload) {
        this.voteQueue.push(payload);
        localStorage.setItem('yp_vote_queue', JSON.stringify(this.voteQueue));
    }

    async processQueue() {
        if (this.voteQueue.length === 0 || !navigator.onLine) return;

        console.log(`[MoodModule] Processing ${this.voteQueue.length} queued votes...`);
        const queue = [...this.voteQueue];
        this.voteQueue = [];
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

    isOnCooldown(songId) {
        const lastVote = this.cooldowns[songId];
        if (!lastVote) return false;
        return (Date.now() - lastVote) < this.VOTE_COOLDOWN_MS;
    }

    setCooldown(songId) {
        this.cooldowns[songId] = Date.now();
        localStorage.setItem('yp_mood_cooldowns', JSON.stringify(this.cooldowns));
    }

    showStatus(msg, type = '') {
        const el = document.getElementById('mood-status');
        if (el) {
            el.textContent = msg;
            el.className = 'status-msg ' + type;
        }
    }

    setCurrentSong(songId, moods) {
        this.currentSongId = songId;
        // Optionally store more metadata if passed
    }
}

export default MoodModule;
