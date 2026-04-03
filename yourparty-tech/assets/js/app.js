/**
 * YourParty Tech - Main Application
 * Orchestrates all modules
 */

const YourPartyApp = (function () {
    'use strict';

    // Configuration from WordPress
    let config = {};

    // Polling interval
    const STATUS_POLL_INTERVAL = 10000; // 10 seconds
    let pollTimer = null;

    /**
     * Initialize application
     */
    function init() {
        // Get config from WordPress
        config = window.YourPartyConfig || {};

        // Initialize modules
        initModules();
        initToastSystem();

        // Start status polling
        fetchStatus();
        startPolling();

        // Listen for stream events
        bindStreamEvents();
        bindUIEvents();

        // Initial fetch
        fetchHistory();

        console.log('[YourPartyApp] Ready');
    }

    /**
     * Initialize all modules
     */
    function initModules() {
        // Stream Controller
        if (typeof StreamController !== 'undefined') {
            StreamController.init({
                streamUrl: config.streamUrl
            });
        }

        // Rating Module
        if (typeof RatingModule !== 'undefined') {
            RatingModule.init();
        }

        // Mood Module
        if (typeof MoodModule !== 'undefined') {
            MoodModule.init();
        }

        // Realtime Module (WebSockets)
        if (typeof RealtimeModule !== 'undefined') {
            RealtimeModule.init();
        }
    }

    /**
     * Fetch current status from API
     */
    async function fetchStatus() {
        const endpoint = config.restBase ? `${config.restBase}/status` : '/status';

        try {
            const response = await fetch(endpoint);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);

            const data = await response.json();
            updateUI(data);

        } catch (error) {
            console.error('[YourPartyApp] Status fetch error:', error);
        }
    }

    /**
     * Update UI with status data
     */
    /**
     * Update UI with status data
     */
    function updateUI(data) {
        const song = data.now_playing?.song;
        if (!song) return;

        // Update track info
        updateTrackInfo(song);

        // Update ratings
        updateRating(song);

        // Update moods
        updateMood(song);

        // Update listeners
        updateListeners(data.listeners?.total || 0);

        // Update Next Track
        updateNextTrack(data.playing_next?.song);

        // Notify modules
        notifyModules(song);
    }

    /**
     * Update Next Track display
     */
    function updateNextTrack(song) {
        const el = document.getElementById('next-track-marquee');
        if (!el) return;

        if (song) {
            el.textContent = `Coming up: ${song.artist} - ${song.title}`;
            el.parentElement.style.opacity = '1';
        } else {
            el.textContent = '';
            el.parentElement.style.opacity = '0';
        }
    }

    /**
     * Update track display
     */
    function updateTrackInfo(song) {
        const titleEl = document.getElementById('track-title');
        const artistEl = document.getElementById('track-artist');
        const artEl = document.getElementById('cover-art');

        // Text Updates with "Flash" effect
        if (titleEl) {
            const newTitle = song.title || 'Unknown Title';
            if (titleEl.textContent !== newTitle) {
                titleEl.style.opacity = '0';
                setTimeout(() => {
                    titleEl.textContent = newTitle;
                    titleEl.style.opacity = '1';
                }, 200);
            }
        }
        if (artistEl) {
            const newArtist = song.artist || 'Unknown Artist';
            if (artistEl.textContent !== newArtist) {
                artistEl.style.opacity = '0';
                setTimeout(() => {
                    artistEl.textContent = newArtist;
                    artistEl.style.opacity = '1';
                }, 200);
            }
        }

        // Cover Art Transition
        if (artEl) {
            let newSrc = song.art || _generateFallbackGradient(song.title);

            // PROXY FIX: Avoid HTTP/2 Errors with local proxy
            if (newSrc && (newSrc.includes('radio.yourparty.tech') || newSrc.includes('/api/station'))) {
                newSrc = '/wp-content/themes/yourparty-tech/image-proxy.php?url=' + encodeURIComponent(newSrc);
            }

            // Check if changed (using attribute to avoid resolved URL mismatch)
            if (artEl.getAttribute('data-src') !== newSrc) {
                artEl.setAttribute('data-src', newSrc);

                artEl.style.transition = 'opacity 0.5s ease';
                artEl.style.opacity = '0';

                const img = new Image();
                img.onload = () => {
                    artEl.src = newSrc;
                    artEl.style.opacity = '1';
                };
                img.onerror = () => {
                    console.warn('[App] Image Load Failed, using fallback');
                    artEl.src = _generateFallbackGradient(song.title);
                    artEl.style.opacity = '1';
                };
                img.src = newSrc;
            }
        }

        // Update Media Session
        if (typeof StreamController !== 'undefined') {
            StreamController.updateMetadata(song);
        }
    }

    // Helper: Generate a deterministic gradient for songs with no cover
    function _generateFallbackGradient(str) {
        if (!str) return 'https://placehold.co/600x600/050505/333333?text=NO+ART';
        let hash = 0;
        for (let i = 0; i < str.length; i++) {
            hash = str.charCodeAt(i) + ((hash << 5) - hash);
        }
        const c1 = (hash & 0x00FFFFFF).toString(16).toUpperCase();
        const c2 = ((hash * 2) & 0x00FFFFFF).toString(16).toUpperCase();
        return `https://ui-avatars.com/api/?name=${encodeURIComponent(str)}&background=${c1}&color=${c2}&size=600&font-size=0.33`;
    }

    /**
     * Update rating display
     */
    function updateRating(song) {
        const rating = song.rating || {};
        const average = rating.average || 0;
        const total = rating.total || 0;

        if (typeof RatingModule !== 'undefined') {
            RatingModule.setInitialRating(song.id, average, total);
        }

        // Fallback: direct DOM update
        const avgEl = document.getElementById('rating-average');
        const totalEl = document.getElementById('rating-total');

        if (avgEl) avgEl.textContent = average > 0 ? average.toFixed(1) : '--';
        if (totalEl) {
            totalEl.textContent = total > 0
                ? `(${total} ${total === 1 ? 'Bewertung' : 'Bewertungen'})`
                : '';
        }
    }

    /**
     * Update mood display
     */
    function updateMood(song) {
        const topMood = song.top_mood;
        const moods = song.moods || {};

        if (typeof MoodModule !== 'undefined') {
            MoodModule.setMoodData(song.id, topMood, moods);
        }
    }

    /**
     * Update listener count
     */
    function updateListeners(count) {
        const el = document.getElementById('listener-count');
        if (el) el.textContent = count;
    }

    /**
     * Notify modules of song change
     */
    function notifyModules(song) {
        // Set global song ID for modules
        window.currentSongId = song.id;

        // Dispatch event
        window.dispatchEvent(new CustomEvent('songChange', {
            detail: { song }
        }));
    }

    /**
     * Start status polling
     */
    function startPolling() {
        stopPolling();
        pollTimer = setInterval(fetchStatus, STATUS_POLL_INTERVAL);
    }



    /**
     * Stop status polling
     */
    function stopPolling() {
        if (pollTimer) {
            clearInterval(pollTimer);
            pollTimer = null;
        }
    }

    /**
     * Bind UI events
     */
    function bindUIEvents() {
        const refreshBtn = document.getElementById('refresh-history');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', (e) => {
                e.preventDefault();
                const btn = e.currentTarget;
                btn.style.opacity = '0.5';
                fetchHistory().finally(() => btn.style.opacity = '1');
            });
        }

        // Visualizer Mode Buttons (Fullscreen)
        document.querySelectorAll('.vis-mode-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const mode = btn.dataset.mode;
                if (typeof VisualizerController !== 'undefined') {
                    VisualizerController.setMode(mode);
                    // Active state
                    document.querySelectorAll('.vis-mode-btn').forEach(b => {
                        b.style.background = 'rgba(255,255,255,0.1)';
                        b.style.color = 'rgba(255,255,255,0.6)';
                    });
                    btn.style.background = 'var(--primary)';
                    btn.style.color = '#fff';
                }
            });
        });
    }

    /**
     * Bind stream events
     */
    function bindStreamEvents() {
        window.addEventListener('stream:play', () => {
            fetchStatus(); // Get latest on play
        });
    }

    /**
     * Fetch and render history
     */
    async function fetchHistory() {
        const endpoint = config.restBase ? `${config.restBase}/history` : '/history';

        try {
            const response = await fetch(endpoint);
            const data = await response.json();
            // WP API might wrap in {history: [...]}
            const list = Array.isArray(data) ? data : (data.history || []);
            renderHistory(list);
        } catch (error) {
            console.error('[YourPartyApp] History fetch error:', error);
        }
    }

    /**
     * Render history list (UL Style)
     */
    function renderHistory(items) {
        const container = document.getElementById('history-list');
        if (!container) return;

        if (items.length === 0) {
            container.innerHTML = '<li class="history-item">Keine History verfügbar</li>';
            return;
        }

        container.innerHTML = items.map(item => {
            const song = item.song || item;
            const playedAt = new Date(item.played_at * 1000);
            const timeStr = playedAt.toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' });

            // Stats
            const rating = song.rating?.average || 0;
            const mood = song.top_mood || '';

            return `
            <li class="history-item" style="display: flex; gap: 1rem; align-items: center; padding: 0.75rem 0; border-bottom: 1px solid var(--color-glass-border);">
                <div style="position:relative;">
                    <img src="${song.art || _generateFallbackGradient(song.title)}" alt="" style="width: 48px; height: 48px; border-radius: 4px; object-fit: cover; background: #222;" onerror="this.src='${_generateFallbackGradient(song.title)}'">
                    ${rating > 0 ? `<div style="position:absolute; bottom:-4px; right:-4px; background:#10b981; color:#fff; font-size:10px; padding:1px 4px; border-radius:4px; font-weight:bold;">★${rating.toFixed(1)}</div>` : ''}
                </div>
                <div style="flex: 1; min-width: 0;">
                    <div style="color: var(--color-text); font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; display:flex; gap:6px; align-items:center;">
                        ${song.title}
                        ${mood ? `<span style="font-size:9px; background:rgba(255,255,255,0.1); padding:2px 4px; border-radius:2px; color:#aaa;">${mood.toUpperCase()}</span>` : ''}
                    </div>
                    <div style="color: var(--color-text-muted); font-size: 0.85rem;">${song.artist}</div>
                </div>
                <div style="color: var(--color-text-muted); font-size: 0.75rem;">${timeStr}</div>
            </li>
            `;
        }).join('');
    }

    /**
     * Toast Notification System
     */
    function initToastSystem() {
        // Create container if not exists
        if (!document.getElementById('yp-toast-container')) {
            const container = document.createElement('div');
            container.id = 'yp-toast-container';
            Object.assign(container.style, {
                position: 'fixed',
                bottom: '20px',
                right: '20px',
                display: 'flex',
                flexDirection: 'column',
                gap: '10px',
                zIndex: '99999',
                pointerEvents: 'none'
            });
            document.body.appendChild(container);
        }

        // Expose global
        window.showToast = showToast;
    }

    function showToast(message, type = 'info') {
        const container = document.getElementById('yp-toast-container');
        if (!container) return;

        const toast = document.createElement('div');

        // Styles
        const colors = {
            info: '#fff',
            success: '#10b981', // emerald-500
            error: '#ef4444',   // red-500
            warning: '#f59e0b'  // amber-500
        };
        const color = colors[type] || colors.info;

        Object.assign(toast.style, {
            background: 'rgba(10, 10, 10, 0.9)',
            color: color,
            padding: '12px 24px',
            borderRadius: '4px',
            border: `1px solid ${color}`,
            fontFamily: 'var(--font-display, monospace)',
            fontSize: '14px',
            boxShadow: '0 4px 6px rgba(0,0,0,0.3)',
            backdropFilter: 'blur(8px)',
            opacity: '0',
            transform: 'translateY(20px)',
            transition: 'all 0.3s cubic-bezier(0.16, 1, 0.3, 1)',
            pointerEvents: 'auto'
        });

        toast.textContent = message;

        // Icon
        const icon = document.createElement('span');
        icon.style.marginRight = '8px';
        icon.textContent = type === 'success' ? '✓' : (type === 'error' ? '✕' : 'ℹ');
        toast.prepend(icon);

        container.appendChild(toast);

        // Animate in
        requestAnimationFrame(() => {
            toast.style.opacity = '1';
            toast.style.transform = 'translateY(0)';
        });

        // Remove
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateY(10px)';
            setTimeout(() => toast.remove(), 300);
        }, 4000);
    }

    // Public API
    return {
        init,
        fetchStatus,
        fetchHistory,
        getConfig: () => config,
        getStreamController: () => (typeof StreamController !== 'undefined' ? StreamController : null),
        showToast
    };
})();

// Export
if (typeof module !== 'undefined' && module.exports) {
    module.exports = YourPartyApp;
}




// VisualizerController is now loaded from visualizer-premium.js
// This prevents conflicts and ensures the premium visualizer is used.

/**
 * Realtime Module (WebSockets)
 */
const RealtimeModule = (function () {
    let socket;
    let reconnectAttempts = 0;

    function init() {
        connect();
    }

    function connect() {
        if (socket && (socket.readyState === WebSocket.CONNECTING || socket.readyState === WebSocket.OPEN)) return;

        const clientId = Math.random().toString(36).substring(7);
        const host = 'api.yourparty.tech';
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const url = `${protocol}//${host}/ws/${clientId}`;

        console.log('[Realtime] Connecting to ' + url);

        try {
            socket = new WebSocket(url);
        } catch (e) {
            console.warn('[Realtime] Init Error', e);
            scheduleReconnect();
            return;
        }

        socket.onopen = () => {
            console.log('[Realtime] Connected');
            reconnectAttempts = 0;
        };

        socket.onmessage = (event) => {
            try {
                const msg = JSON.parse(event.data);
                handleMessage(msg);
            } catch (e) { console.warn('[Realtime] Parse error', e); }
        };

        socket.onclose = () => {
            scheduleReconnect();
        };

        socket.onerror = (err) => {
            // console.warn('WS Error');
        };
    }

    function scheduleReconnect() {
        const delay = Math.min(2000 * Math.pow(1.5, reconnectAttempts), 30000);
        reconnectAttempts++;
        setTimeout(connect, delay);
    }

    function handleMessage(msg) {
        if (msg.type === 'vote_update') {
            updateVoteUI(msg.stats, msg.total);
        } else if (msg.type === 'steering_update') {
            updateSteeringUI(msg.votes);
        }
    }

    function updateVoteUI(stats, total) {
        if (!total) total = 1;
        document.querySelectorAll('.vibe-btn').forEach(btn => {
            const voteType = btn.dataset.vote;
            if (!voteType) return;
            const count = stats[voteType] || 0;
            const percent = Math.round((count / total) * 100);

            let badge = btn.querySelector('.vote-badge');
            if (!badge) {
                badge = document.createElement('span');
                badge.className = 'vote-badge';
                btn.appendChild(badge);
            }
            if (count > 0) {
                badge.textContent = `${percent}%`;
                badge.style.opacity = '1';
                btn.style.setProperty('--vote-percent', `${percent}%`);
                btn.classList.add('has-votes');
            } else {
                badge.style.opacity = '0';
                btn.style.removeProperty('--vote-percent');
                btn.classList.remove('has-votes');
            }
        });
    }

    function updateSteeringUI(votes) {
        if (!votes) return;
        const total = Object.values(votes).reduce((a, b) => a + b, 0) || 1;

        document.querySelectorAll('.vibe-btn').forEach(btn => {
            const voteType = btn.dataset.vote;
            if (!voteType) return;
            const count = votes[voteType] || 0;
            const percent = Math.round((count / total) * 100);

            let badge = btn.querySelector('.vote-count-badge');
            if (!badge) {
                badge = document.createElement('span');
                badge.className = 'vote-count-badge';
                badge.style.cssText = 'position:absolute; bottom: -8px; left: 50%; transform: translateX(-50%); background: #2E8B57; color: white; border-radius: 10px; padding: 2px 6px; font-size: 10px; opacity:0; transition:opacity 0.3s; font-weight: bold; box-shadow: 0 2px 4px rgba(0,0,0,0.5); white-space: nowrap;';
                btn.appendChild(badge);
            }
            if (count > 0) {
                badge.textContent = `${percent}% (${count})`;
                badge.style.opacity = '1';
                btn.style.borderColor = '#2E8B57';
            } else {
                badge.style.opacity = '0';
                btn.style.borderColor = '';
            }
        });
    }

    return { init };
})();

/**
 * Fullscreen Manager
 */
const FullscreenManager = (function () {
    let overlay, enterBtn, exitBtn, playBtn;

    function init() {
        overlay = document.getElementById('immersive-overlay');
        enterBtn = document.getElementById('fullscreen-toggle');
        const visualizerToggle = document.getElementById('visualizer-toggle');
        exitBtn = document.getElementById('exit-fullscreen');
        playBtn = document.getElementById('immersive-play-btn');

        if (!overlay) return;

        if (enterBtn) enterBtn.addEventListener('click', enterFullscreen);
        if (visualizerToggle) visualizerToggle.addEventListener('click', enterFullscreen);
        if (exitBtn) exitBtn.addEventListener('click', exitFullscreen);

        if (playBtn) {
            playBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                if (typeof StreamController !== 'undefined') {
                    StreamController.togglePlay();
                } else {
                    const controller = YourPartyApp.getStreamController();
                    if (controller) controller.togglePlay();
                }
            });
        }

        window.addEventListener('songChange', (e) => updateUI(e.detail.song));
        window.addEventListener('stream:playing', () => updatePlayState(true));
        window.addEventListener('stream:paused', () => updatePlayState(false));

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') exitFullscreen();
        });
    }

    function enterFullscreen() {
        overlay.classList.add('active');
        document.body.style.overflow = 'hidden';
        if (document.documentElement.requestFullscreen) {
            // Optional: User might rely on browser UI, so maybe don't force it immediately unless requested
            // document.documentElement.requestFullscreen().catch(err => console.warn(err));
        }
        VisualizerController.setImmersive(true);
    }

    // OVERSCROLL LOGIC
    window.addEventListener('scroll', () => {
        if (overlay.classList.contains('active')) return;

        // Check if we are at the bottom
        const scrollPosition = window.innerHeight + window.scrollY;
        const bodyHeight = document.body.offsetHeight;
        const buffer = 50; // pixels past bottom

        if (scrollPosition >= bodyHeight + buffer) {
            console.log('[Fullscreen] Overscroll trigger');
            enterFullscreen();
        }
    });

    function exitFullscreen() {
        overlay.classList.remove('active');
        document.body.style.overflow = '';
        if (document.exitFullscreen && document.fullscreenElement) {
            document.exitFullscreen().catch(err => console.warn(err));
        }
        VisualizerController.setImmersive(false);
    }

    function updateUI(song) {
        if (!song) return;
        const titleEl = document.getElementById('immersive-title');
        const artistEl = document.getElementById('immersive-artist');
        const img = document.getElementById('immersive-cover-img');
        if (titleEl) titleEl.textContent = song.title || 'Unknown Track';
        if (artistEl) artistEl.textContent = song.artist || 'YourParty Radio';
        if (img) img.src = song.art || '';
    }

    function updatePlayState(isPlaying) {
        const btn = document.getElementById('immersive-play-btn');
        if (!btn) return;
        if (isPlaying) {
            btn.classList.add('playing');
            btn.querySelector('.icon-play').style.display = 'none';
            btn.querySelector('.icon-pause').style.display = 'inline';
        } else {
            btn.classList.remove('playing');
            btn.querySelector('.icon-play').style.display = 'inline';
            btn.querySelector('.icon-pause').style.display = 'none';
        }
    }

    return { init };
})();

// Initialize Everything
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        YourPartyApp.init();
        VisualizerController.init();
        FullscreenManager.init();
    });
} else {
    YourPartyApp.init();
    VisualizerController.init();
    FullscreenManager.init();
}
