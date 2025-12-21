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
            { id: 'energy', label: 'Energy', icon: '\u26A1', color: '#f59e0b' },
            { id: 'chill', label: 'Chill', icon: '\uD83C\uDF0A', color: '#3b82f6' },
            { id: 'dark', label: 'Dark', icon: '\uD83C\uDF11', color: '#6366f1' },
            { id: 'euphoric', label: 'Euphoric', icon: '\u2728', color: '#ec4899' }
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
            ],
            disco: [
                { id: 'funky', label: 'Funky', icon: '🕺', color: '#f59e0b' },
                { id: 'groovy', label: 'Groovy', icon: '🪩', color: '#ec4899' },
                { id: 'soulful', label: 'Soulful', icon: '💜', color: '#a855f7' },
                { id: 'classic', label: 'Classic', icon: '🎤', color: '#eab308' }
            ]
        }
    };

    // Active vibes (can change based on genre/mode)
    let activeVibes = CONFIG.defaultVibes;

    // ========== DYNAMIC VIBES ==========
    function handleSongUpdate(song) {
        if (!song) return;
        window.currentSongId = song.id;

        const genre = (song.genre || '').toLowerCase();
        if (state.currentGenre !== genre) {
            state.currentGenre = genre;
            updateVibes(genre);
        }
    }

    function updateVibes(genre) {
        let newVibes = CONFIG.defaultVibes;

        // Find matching preset (e.g. "tech house" matches "house")
        const presetKey = Object.keys(CONFIG.vibePresets).find(k => genre.includes(k));
        if (presetKey) {
            newVibes = CONFIG.vibePresets[presetKey];
            console.log(`[LiveVoting] Switched to ${presetKey} vibes`);
        } else {
            console.log(`[LiveVoting] Using default vibes for genre: ${genre}`);
        }

        // Update global active vibes
        activeVibes = newVibes;

        // Re-render UI components
        reRenderButtons();
    }

    function reRenderButtons() {
        if (!state.widgetEl) return;

        // 1. Update Track Tags Section
        const tagContainer = state.widgetEl.querySelector('.live-voting__track-tags');
        if (tagContainer) {
            tagContainer.innerHTML = activeVibes.map(v => `
                <div class="live-voting__tag" data-vibe="${v.id}" style="--vibe-color: ${v.color}">
                  <span class="live-voting__tag-icon">${v.icon}</span>
                  <span class="live-voting__tag-count">0</span>
                </div>
            `).join('');
        }

        // 2. Update Progress Bars
        const barContainer = state.widgetEl.querySelector('.live-voting__bars');
        if (barContainer) {
            barContainer.innerHTML = activeVibes.map(v => `
              <div class="live-voting__bar-row" data-vibe="${v.id}">
                <span class="live-voting__bar-icon">${v.icon}</span>
                <span class="live-voting__bar-label">${v.label}</span>
                <div class="live-voting__bar-track">
                  <div class="live-voting__bar-fill" style="--vibe-color: ${v.color}"></div>
                </div>
                <span class="live-voting__bar-percent">0%</span>
              </div>
            `).join('');
        }

        // 3. Update Buttons
        const btnContainer = state.widgetEl.querySelector('.live-voting__buttons');
        if (btnContainer) {
            btnContainer.innerHTML = activeVibes.map(v => `
              <button class="live-voting__btn" data-vibe="${v.id}" style="--vibe-color: ${v.color}">
                <span>${v.icon}</span>
                <span>${v.label}</span>
              </button>
            `).join('');

            // Re-attach listeners to NEW buttons
            setupEventListeners();
        }

        // Reset local votes display since context changed
        updateUI();
    }

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
        <span class="live-voting__title">&#127911; COMMUNITY VIBE</span>
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
      
      <!-- USER STATS (Gamification) -->
      <div class="live-voting__user-stats" style="margin-top: 10px; font-size: 0.8em; color: #aaa; text-align: center; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 5px;">
        <span class="stats-points">💎 ...</span>
        <span class="stats-streak" style="margin-left: 10px;">🔥 ...</span>
      </div>
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

    // ========== USER IDENTITY ==========
    function getUserId() {
        let id = localStorage.getItem('yourparty_user_id');
        if (!id) {
            id = 'user_' + Math.random().toString(36).substr(2, 9) + Date.now().toString(36);
            localStorage.setItem('yourparty_user_id', id);
        }
        return id;
    }

    // ========== GAME STATS ==========
    async function updateUserStats() {
        const userId = getUserId();
        try {
            const response = await fetch(`${CONFIG.apiUrl}/user-stats/${userId}`);
            if (response.ok) {
                const data = await response.json();
                if (data && state.widgetEl) {
                    const ptsEl = state.widgetEl.querySelector('.stats-points');
                    const strEl = state.widgetEl.querySelector('.stats-streak');
                    if (ptsEl) ptsEl.textContent = `💎 ${data.total_points || 0} pts`;
                    if (strEl) strEl.textContent = `🔥 ${data.current_streak || 0} day streak`;
                }
            }
        } catch (e) {
            console.warn('[LiveVoting] Stats fetch error', e);
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
                    mood_current: vibeId,
                    user_id: getUserId()
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
            updateUserStats(); // Refresh points after voting
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
                    } else if (data.type === 'song') {
                        handleSongUpdate(data.song);
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

                    // Handle Genre from API if available
                    if (data.genre && data.song_id) {
                        handleSongUpdate({ id: data.song_id, genre: data.genre });
                    }

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
            // Intelligent Placement: Replace the static "Vibe Deck" if it exists
            const existingDeck = document.querySelector('.vibe-deck');
            if (existingDeck) {
                container = document.createElement('div');
                container.id = 'live-voting-container';
                // Insert distinct styling class to match layout
                container.style.marginTop = '20px';
                container.style.width = '100%';
                container.style.maxWidth = '600px';

                existingDeck.parentNode.replaceChild(container, existingDeck);
                console.log('[LiveVoting] Replaced static Vibe Deck');
            } else {
                // Fallback: Insert after hero player ID
                const player = document.getElementById('hero-player') || document.querySelector('.hero-fullscreen');
                if (player) {
                    container = document.createElement('div');
                    container.id = 'live-voting-container';
                    // Insert INSIDE the container if possible? No, user wanted it below.
                    // But #hero-player is a Section.
                    // Let's try to find .glass-player-wrapper and put it after
                    const wrapper = player.querySelector('.glass-player-wrapper');
                    if (wrapper) {
                        wrapper.parentNode.insertBefore(container, wrapper.nextSibling);
                    } else {
                        player.appendChild(container); // Fallback
                    }
                } else {
                    console.warn('[LiveVoting] No suitable container found');
                    return;
                }
            }
        }

        state.widgetEl = createWidget();
        container.appendChild(state.widgetEl);

        setupEventListeners();
        connectWebSocket();
        updateUserStats(); // Initial fetch

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
