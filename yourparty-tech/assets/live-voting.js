// LIVE VOTING WIDGET - Real-time Community Vibe Display
(function () {
    'use strict';

    // ========== CONFIGURATION ==========
    const CONFIG = {
        wsUrl: 'wss://yourparty.tech/ws/votes', // WebSocket endpoint
        apiUrl: '/wp-json/yourparty/v1',
        pollInterval: 5000, // Fallback if WS fails
        // Default vibes - can be overridden by API
        defaultVibes: [
            { id: 'energy', label: 'Energy', icon: '⚡', color: '#f59e0b' },
            { id: 'chill', label: 'Chill', icon: '🌊', color: '#3b82f6' },
            { id: 'dark', label: 'Dark', icon: '🌑', color: '#6366f1' },
            { id: 'euphoric', label: 'Euphoric', icon: '✨', color: '#ec4899' }
        ],
        // Genre-specific vibe presets
        vibePresets: {
            techno: [
                { id: 'dark', label: 'Dark', icon: '🌑', color: '#6366f1' },
                { id: 'hypnotic', label: 'Hypnotic', icon: '🌀', color: '#8b5cf6' },
                { id: 'driving', label: 'Driving', icon: '🔥', color: '#ef4444' },
                { id: 'acid', label: 'Acid', icon: '⚗️', color: '#22c55e' }
            ],
            house: [
                { id: 'groovy', label: 'Groovy', icon: '🕺', color: '#f59e0b' },
                { id: 'soulful', label: 'Soulful', icon: '💜', color: '#a855f7' },
                { id: 'deep', label: 'Deep', icon: '🌊', color: '#3b82f6' },
                { id: 'funky', label: 'Funky', icon: '🎸', color: '#ec4899' }
            ],
            trance: [
                { id: 'euphoric', label: 'Euphoric', icon: '✨', color: '#ec4899' },
                { id: 'uplifting', label: 'Uplifting', icon: '🚀', color: '#f59e0b' },
                { id: 'progressive', label: 'Progressive', icon: '🌀', color: '#8b5cf6' },
                { id: 'psy', label: 'Psy', icon: '👁️', color: '#22c55e' }
            ]
        }
    };

    // Active vibes (can change based on genre/mode)
    let activeVibes = CONFIG.defaultVibes;

    // ========== STATE ==========
    let state = {
        votes: { energy: 0, chill: 0, dark: 0, euphoric: 0 },
        total: 0,
        dominant: null,
        trackMoods: {}, // Mood counts for current track
        currentGenre: null,
        userVoted: false,
        ws: null,
        widgetEl: null
    };

    // ========== CREATE WIDGET ==========
    function createWidget() {
        const widget = document.createElement('div');
        widget.id = 'live-voting-widget';
        widget.className = 'live-voting';

        widget.innerHTML = `
      <div class="live-voting__header">
        <span class="live-voting__title">🎵 COMMUNITY VIBE</span>
        <span class="live-voting__live-badge">● LIVE</span>
      </div>
      
      <!-- TRACK MOOD TAGS - Shows this track's vibes -->
      <div class="live-voting__track-vibes">
        <div class="live-voting__track-header">THIS TRACK'S VIBES</div>
        <div class="live-voting__track-tags">
          ${activeVibes.map(v => `
            <div class="live-voting__tag" data-vibe="${v.id}" style="--vibe-color: ${v.color}">
              <span class="live-voting__tag-icon">${v.icon}</span>
              <span class="live-voting__tag-count">0</span>
            </div>
          `).join('')}
        </div>
      </div>
      
      <div class="live-voting__bars">
        ${activeVibes.map(v => `
          <div class="live-voting__bar-row" data-vibe="${v.id}">
            <span class="live-voting__bar-icon">${v.icon}</span>
            <span class="live-voting__bar-label">${v.label}</span>
            <div class="live-voting__bar-track">
              <div class="live-voting__bar-fill" style="--vibe-color: ${v.color}"></div>
            </div>
            <span class="live-voting__bar-percent">0%</span>
          </div>
        `).join('')}
      </div>
      
      <div class="live-voting__stats">
        <span class="live-voting__total">0 votes</span>
        <span class="live-voting__dominant"></span>
      </div>
      
      <div class="live-voting__buttons">
        ${activeVibes.map(v => `
          <button class="live-voting__btn" data-vibe="${v.id}" style="--vibe-color: ${v.color}">
            <span>${v.icon}</span>
            <span>${v.label}</span>
          </button>
        `).join('')}
      </div>
      
      <div class="live-voting__feedback"></div>
    `;

        return widget;
    }

    // ========== UPDATE UI ==========
    function updateUI() {
        if (!state.widgetEl) return;

        const total = state.total || 1; // Avoid division by zero

        activeVibes.forEach(v => {
            const count = state.votes[v.id] || 0;
            const percent = Math.round((count / total) * 100);

            const row = state.widgetEl.querySelector(`[data-vibe="${v.id}"].live-voting__bar-row`);
            if (row) {
                row.querySelector('.live-voting__bar-fill').style.width = `${percent}%`;
                row.querySelector('.live-voting__bar-percent').textContent = `${percent}%`;
            }
        });

        // Update stats
        const totalEl = state.widgetEl.querySelector('.live-voting__total');
        if (totalEl) {
            totalEl.textContent = `${state.total} vote${state.total !== 1 ? 's' : ''}`;
        }

        // Update dominant
        const dominantEl = state.widgetEl.querySelector('.live-voting__dominant');
        if (dominantEl && state.dominant) {
            const vibeConfig = activeVibes.find(v => v.id === state.dominant);
            if (vibeConfig) {
                dominantEl.textContent = `🏆 ${vibeConfig.icon} ${vibeConfig.label}`;
            }
        }
    }

    // ========== VOTE SUBMISSION ==========
    async function submitVote(vibeId) {
        if (state.userVoted) {
            showFeedback('Already voted!', 'info');
            return;
        }

        const songId = window.currentSongId || 'unknown';

        try {
            const response = await fetch(`${CONFIG.apiUrl}/vote-mood`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    song_id: songId,
                    mood_current: vibeId
                })
            });

            if (!response.ok) throw new Error(`HTTP ${response.status}`);

            const data = await response.json();

            // Update local state
            state.userVoted = true;
            state.votes[vibeId] = (state.votes[vibeId] || 0) + 1;
            state.total++;

            // Recalculate dominant
            state.dominant = Object.entries(state.votes)
                .sort((a, b) => b[1] - a[1])[0]?.[0];

            updateUI();
            showFeedback('✓ Vote counted!', 'success');

            // Disable buttons
            state.widgetEl.querySelectorAll('.live-voting__btn').forEach(btn => {
                btn.disabled = true;
                if (btn.dataset.vibe === vibeId) {
                    btn.classList.add('selected');
                }
            });

        } catch (e) {
            console.error('[LiveVoting] Vote error:', e);
            showFeedback('Network error', 'error');
        }
    }

    function showFeedback(message, type) {
        const feedbackEl = state.widgetEl?.querySelector('.live-voting__feedback');
        if (feedbackEl) {
            feedbackEl.textContent = message;
            feedbackEl.className = `live-voting__feedback live-voting__feedback--${type}`;
            setTimeout(() => { feedbackEl.textContent = ''; }, 3000);
        }
    }

    // ========== WEBSOCKET CONNECTION ==========
    function connectWebSocket() {
        try {
            state.ws = new WebSocket(CONFIG.wsUrl);

            state.ws.onopen = () => {
                console.log('[LiveVoting] WebSocket connected');
                state.widgetEl?.querySelector('.live-voting__live-badge')?.classList.add('connected');
            };

            state.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    if (data.type === 'vote_update') {
                        state.votes = data.votes || state.votes;
                        state.total = data.total || Object.values(state.votes).reduce((a, b) => a + b, 0);
                        state.dominant = data.dominant;
                        updateUI();
                    }
                } catch (e) {
                    console.warn('[LiveVoting] WS message parse error:', e);
                }
            };

            state.ws.onclose = () => {
                console.log('[LiveVoting] WebSocket closed, falling back to polling');
                state.widgetEl?.querySelector('.live-voting__live-badge')?.classList.remove('connected');
                setTimeout(startPolling, 1000);
            };

            state.ws.onerror = (e) => {
                console.warn('[LiveVoting] WebSocket error:', e);
            };

        } catch (e) {
            console.warn('[LiveVoting] WebSocket not supported, using polling');
            startPolling();
        }
    }

    // ========== POLLING FALLBACK ==========
    function startPolling() {
        async function poll() {
            try {
                const response = await fetch(`${CONFIG.apiUrl}/mood-stats`);
                if (response.ok) {
                    const data = await response.json();
                    state.votes = data.votes || state.votes;
                    state.total = data.total || 0;
                    state.dominant = data.dominant;
                    updateUI();
                }
            } catch (e) {
                console.warn('[LiveVoting] Poll error:', e);
            }
        }

        poll();
        setInterval(poll, CONFIG.pollInterval);
    }

    // ========== EVENT HANDLERS ==========
    function setupEventListeners() {
        state.widgetEl.querySelectorAll('.live-voting__btn').forEach(btn => {
            btn.addEventListener('click', () => {
                submitVote(btn.dataset.vibe);
            });
        });
    }

    // ========== INITIALIZE ==========
    function init() {
        // Find container or create one
        let container = document.getElementById('live-voting-container');
        if (!container) {
            // Insert after player if no container exists
            const player = document.querySelector('.hero-player') || document.querySelector('.player-section');
            if (player) {
                container = document.createElement('div');
                container.id = 'live-voting-container';
                player.parentNode.insertBefore(container, player.nextSibling);
            } else {
                console.warn('[LiveVoting] No container found');
                return;
            }
        }

        state.widgetEl = createWidget();
        container.appendChild(state.widgetEl);

        setupEventListeners();
        connectWebSocket();

        console.log('[LiveVoting] Widget initialized');
    }

    // Start when DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Expose for external use
    window.LiveVoting = {
        updateVotes: (votes) => { state.votes = votes; updateUI(); },
        getState: () => state
    };

})();
