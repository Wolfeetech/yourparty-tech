/**
 * YourParty Tech - Main Application
 * Orchestrates all modules
 */
console.log('[DEBUG] app.js IS LOADING (Top of file)');

const YourPartyApp = (function () {
    'use strict';

    // Configuration from WordPress
    let config = {};

    // Polling interval
    const STATUS_POLL_INTERVAL = 5000; // 5 seconds
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

        // VISUAL DEBUG: Confirm App Started
        showToast('System Init: Connecting...', 'info');

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
        console.log(`[DEBUG] Fetching status from: ${endpoint}`);

        try {
            const response = await fetch(endpoint);
            console.log(`[DEBUG] Fetch response status: ${response.status}`);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);

            const data = await response.json();
            console.log('[DEBUG] Status Data received:', data);

            // VISUAL DEBUG: confirm data arrived
            if (data.now_playing?.song) {
                // showToast('Data Sync: OK', 'success'); 
            }

            updateUI(data);

        } catch (error) {
            console.error('[YourPartyApp] Status fetch error:', error);
        }
    }

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

        // Update Steering/Vibe Status
        updateSteeringStatus(data.steering);

        // Notify modules
        notifyModules(song);
    }

    /**
     * Update Steering Status Display
     */
    function updateSteeringStatus(steering) {
        const el = document.getElementById('vibe-status');
        if (!el) return;

        if (!steering) {
            el.textContent = 'AUTO PILOT';
            el.style.color = 'var(--neon-green)';
            return;
        }

        const mode = steering.mode || 'auto';
        const target = steering.target || 'neutral';

        if (mode === 'manual') {
            el.innerHTML = `<span style="color:#ef4444">⚠ MANUAL OVERRIDE: ${target.toUpperCase()}</span>`;
        } else if (target && target !== 'neutral') {
            el.innerHTML = `<span>VIBE SHIFTING TO: <span style="color:#f59e0b">${target.toUpperCase()}</span></span>`;
        } else {
            el.innerHTML = '<span style="color:var(--neon-green)">🤖 AUTO PILOT ACTIVE</span>';
        }
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
        // Support BOTH old and new IDs
        const titleEl = document.getElementById('track-title') || document.getElementById('immersive-title');
        const artistEl = document.getElementById('track-artist') || document.getElementById('immersive-artist');
        const artEl = document.getElementById('cover-art') || document.getElementById('immersive-cover-img');

        // Text Updates with "Flash" effect (remove/add class if I had CSS, but just text for now)
        if (titleEl) {
            if (titleEl.textContent !== song.title) {
                titleEl.style.opacity = '0';
                setTimeout(() => {
                    titleEl.textContent = song.title || 'Unknown Title';
                    titleEl.style.opacity = '1';
                }, 200);
            }
        }
        if (artistEl) {
            if (artistEl.textContent !== song.artist) {
                artistEl.style.opacity = '0';
                setTimeout(() => {
                    artistEl.textContent = song.artist || 'Unknown Artist';
                    artistEl.style.opacity = '1';
                }, 200);
            }
        }

        // Cover Art Transition
        if (artEl) {
            const newSrc = song.art || _generateFallbackGradient(song.title);
            if (artEl.src !== newSrc) {
                artEl.style.transition = 'opacity 0.5s ease';
                artEl.style.opacity = '0';

                const img = new Image();
                img.onload = () => {
                    artEl.src = newSrc;
                    artEl.style.opacity = '1';
                };
                img.onerror = () => {
                    artEl.src = _generateFallbackGradient(song.title);
                    artEl.style.opacity = '1';
                }
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
    }

    /**
     * Bind stream events
     */
    function bindStreamEvents() {
        window.addEventListener('stream:play', () => {
            fetchStatus(); // Get latest on play
        });
        window.addEventListener('stream:playing', () => updatePlayState(true));
        window.addEventListener('stream:paused', () => updatePlayState(false));
    }

    function updatePlayState(isPlaying) {
        // Support BOTH IDs
        const btn = document.getElementById('play-toggle') || document.getElementById('immersive-play-btn');
        if (!btn) return;

        const iconPlay = btn.querySelector('.icon-play') || btn.querySelector('span:first-child');
        const iconPause = btn.querySelector('.icon-pause') || btn.querySelector('span:last-child');

        if (isPlaying) {
            btn.classList.add('playing');
            if (iconPlay) iconPlay.style.display = 'none';
            if (iconPause) iconPause.style.display = 'inline';
        } else {
            btn.classList.remove('playing');
            if (iconPlay) iconPlay.style.display = 'inline';
            if (iconPause) iconPause.style.display = 'none';
        }
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

/**
 * Visualizer Module
 * High-Fidelity Audio Analysis
 */
const VisualizerController = (function () {
    let analyser;
    let animationId;
    let canvas, ctx;
    let modeIndex = 0;
    // Modes: Modern Wave (Spline), RTA (Bars), RGB Scroll, Oscilloscope, Matrix
    const modes = ['modern_wave', 'rta_spectrum', 'rgb_waveform', 'oscilloscope', 'matrix'];

    // Buffers
    let canvasImmersive, ctxImmersive;

    function init() {
        // Support both Frontend (inline) and Control (monitor) canvases
        canvas = document.getElementById('inline-visualizer') || document.getElementById('monitor-visualizer');
        canvasImmersive = document.getElementById('immersive-canvas');

        if (canvas) {
            ctx = canvas.getContext('2d', { alpha: false }); // Optimize

            // Interaction: Restore Click to Change Mode
            canvas.addEventListener('click', () => {
                modeIndex = (modeIndex + 1) % modes.length;
                showToast(`Visualizer: ${modes[modeIndex].replace('_', ' ').toUpperCase()}`);
            });
            canvas.style.cursor = 'pointer';
        }

        if (canvasImmersive) {
            ctxImmersive = canvasImmersive.getContext('2d');
        }

        window.addEventListener('resize', resize);
        resize();

        window.addEventListener('stream:audioContextReady', (e) => {
            analyser = e.detail.analyser;
            if (analyser) {
                // High precision for modern look
                analyser.fftSize = 4096;
                analyser.smoothingTimeConstant = 0.85;
            }
            startRendering();
        });

        drawIdle();
    }

    function resize() {
        const dpr = window.devicePixelRatio || 1;

        if (canvas) {
            const rect = canvas.getBoundingClientRect();
            canvas.width = rect.width * dpr;
            canvas.height = rect.height * dpr;
        }

        if (canvasImmersive) {
            canvasImmersive.width = window.innerWidth * dpr;
            canvasImmersive.height = window.innerHeight * dpr;
        }
    }

    function showToast(msg) {
        if (window.showToast) window.showToast(msg);
    }

    function startRendering() {
        if (animationId) cancelAnimationFrame(animationId);
        render();
    }

    function drawIdle() {
        if (!ctx || !canvas) return;
        ctx.fillStyle = '#111';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // Don't draw text, just black
    }

    // Render Loop
    function render() {
        animationId = requestAnimationFrame(render);
        if (!analyser || !ctx) return;

        const w = canvas.width;
        const h = canvas.height;

        // Data Fetch
        const fftSize = analyser.frequencyBinCount;
        const freqData = new Uint8Array(fftSize);
        analyser.getByteFrequencyData(freqData);

        // Clear
        ctx.fillStyle = 'rgba(5, 5, 5, 1)';
        ctx.fillRect(0, 0, w, h);

        const mode = modes[modeIndex];

        if (mode === 'modern_wave') drawModernWave(ctx, freqData, w, h);
        else if (mode === 'rta_spectrum') drawRTASpectrum(ctx, freqData, w, h);
        else if (mode === 'rgb_waveform') drawModernWave(ctx, freqData, w, h); // Fallback to Wave
        else if (mode === 'oscilloscope') drawModernWave(ctx, freqData, w, h); // Fallback
        else if (mode === 'matrix') drawRTASpectrum(ctx, freqData, w, h); // Fallback
    }

    // Simple Spectrum RTA
    function drawRTASpectrum(c, data, w, h) {
        const bars = 64;
        const barW = w / bars;

        for (let i = 0; i < bars; i++) {
            // scale logarithmic
            const index = Math.floor(i * (data.length / bars));
            const val = data[index];
            const barH = (val / 255) * h;

            c.fillStyle = `hsl(${i * 4}, 100%, 50%)`;
            c.fillRect(i * barW, h - barH, barW - 1, barH);
        }
    }

    function drawModernWave(c, data, w, h) {
        c.lineWidth = 2;
        c.strokeStyle = '#00ff88';
        c.beginPath();
        const slice = Math.floor(data.length / w);
        for (let x = 0; x < w; x++) {
            const i = x * slice;
            const val = data[i];
            const y = h - ((val / 255) * h);
            if (x === 0) c.moveTo(x, y);
            else c.lineTo(x, y);
        }
        c.stroke();
    }

    function setImmersive(active) {
        resize(); // Force check
    }

    // Public API
    return { init, setImmersive };
})();

/**
 * Realtime Module (WebSockets)
 */
const RealtimeModule = (function () {
    let socket;
    let reconnectAttempts = 0;

    function init() {
        // Delay connection slightly to allow config to load
        setTimeout(connect, 500);
    }

    function connect() {
        if (socket && (socket.readyState === WebSocket.CONNECTING || socket.readyState === WebSocket.OPEN)) return;

        // Dynamic Host from Config
        let host = 'yourparty.tech'; // Default to main domain
        const config = YourPartyApp.getConfig();

        let wsUrl = 'wss://yourparty.tech/ws/logrmp';
        // If config has specific logic, use it, but for now strict proxy via yourparty.tech
        // Note: We haven't configured WS proxy yet, so this might fail until that step is active.
        // Fallsback to direct API if needed, but let's try to stick to proxy.

        console.log('[Realtime] Connecting to ' + wsUrl);

        try {
            socket = new WebSocket(wsUrl);
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
        } else if (msg.type === 'song') {
            const songData = msg.song || msg.data;
            window.dispatchEvent(new CustomEvent('songChange', {
                detail: { song: songData }
            }));
        }
    }

    function updateSteeringUI(votes) {
        // Placeholder
    }

    function updateVoteUI(stats, total) {
        // Placeholder
    }

    return { init };
})();

/**
 * Fullscreen Manager
 */
const FullscreenManager = (function () {
    let overlay, enterBtn, exitBtn, playBtn;

    function init() {
        // Updated IDs for the new Immersive Layout
        overlay = document.querySelector('.hero-fullscreen') || document.getElementById('immersive-overlay');

        enterBtn = document.getElementById('fullscreen-toggle');
        const visualizerToggle = document.getElementById('visualizer-toggle');
        exitBtn = document.getElementById('exit-fullscreen');

        playBtn = document.getElementById('play-toggle') || document.getElementById('immersive-play-btn');

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
    }

    function enterFullscreen() {
        if (!overlay) return;
        overlay.classList.add('active');
        document.body.style.overflow = 'hidden';
        VisualizerController.setImmersive(true);
    }

    function exitFullscreen() {
        if (!overlay) return;
        overlay.classList.remove('active');
        document.body.style.overflow = '';
        VisualizerController.setImmersive(false);
    }

    function updateUI(song) {
        if (!song) return;
        // Logic handled by main app mostly
    }

    function updatePlayState(isPlaying) {
        // Logic handled by main app
    }

    return { init };
})();

// Initialize Everything
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        console.log('[DEBUG] DOMContentLoaded - Initializing YourPartyApp');
        YourPartyApp.init();
        VisualizerController.init();
        FullscreenManager.init();
    });
} else {
    console.log('[DEBUG] ReadyState Complete - Initializing YourPartyApp');
    YourPartyApp.init();
    VisualizerController.init();
    FullscreenManager.init();
}
