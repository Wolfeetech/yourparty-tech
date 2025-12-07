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
    let textCanvas;
    let scrollCanvas, scrollCtx;
    let matrixCanvas, matrixCtx;
    let canvasImmersive, ctxImmersive;

    function init() {
        canvas = document.getElementById('inline-visualizer');
        canvasImmersive = document.getElementById('immersive-canvas');

        if (canvas) {
            ctx = canvas.getContext('2d', { alpha: false }); // Optimize

            ctx = canvas.getContext('2d', { alpha: false }); // Optimize

            // Interaction: Removed per user request ("ist mist")
            // External buttons control mode now.
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
            // Set render size
            canvas.width = rect.width * dpr;
            canvas.height = rect.height * dpr;

            // Re-init buffers
            scrollCanvas = null;
            matrixCanvas = null;
        }

        if (canvasImmersive) {
            canvasImmersive.width = window.innerWidth * dpr;
            canvasImmersive.height = window.innerHeight * dpr;
        }
    }

    function showToast(msg) {
        if (!ctx) return;
        const w = canvas.width;
        // Simple overlay
        // We render it in the loop to persist for a few frames if needed, 
        // but for now, we just rely on the 'render' loop to draw the label.
    }

    function startRendering() {
        if (animationId) cancelAnimationFrame(animationId);
        render();
    }

    function drawIdle() {
        if (!ctx || !canvas) return;
        ctx.fillStyle = '#0a0a0a';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        ctx.fillStyle = '#4b5563';
        ctx.font = '500 16px Inter, sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText('WAITING FOR AUDIO...', canvas.width / 2, canvas.height / 2);
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
        const timeData = new Uint8Array(fftSize);
        analyser.getByteFrequencyData(freqData);
        analyser.getByteTimeDomainData(timeData);

        // Clear with slight trail for CRT feel
        ctx.fillStyle = 'rgba(5, 5, 5, 1)';
        ctx.fillRect(0, 0, w, h);

        // Draw Grid (Technical Look)
        drawGrid(ctx, w, h);

        const mode = modes[modeIndex];
        ctx.save();

        switch (mode) {
            case 'modern_wave':
                // Renamed internally to "Precision Scope"
                drawPrecisionScope(ctx, timeData, w, h);
                break;
            case 'rta_spectrum':
                drawProSpectrum(ctx, freqData, w, h);
                break;
            case 'rgb_waveform': // GFX Mode
                drawMatrixRain(ctx, freqData, w, h);
                break;
            case 'oscilloscope': // Keep classic but refine
            case 'matrix': // Fallback or duplicate
                drawPrecisionScope(ctx, timeData, w, h);
                break;
        }
        ctx.restore();

        // Label
        ctx.fillStyle = '#00ff41'; // Matrix/Terminal Green
        ctx.font = '10px "JetBrains Mono", monospace';
        ctx.textAlign = 'right';
        ctx.textBaseline = 'top';
        ctx.fillText(`MODE: ${mode.toUpperCase()} // 48KHZ // ACTIVE`, w - 10, 10);
    }

    function drawGrid(c, w, h) {
        c.strokeStyle = 'rgba(255, 255, 255, 0.03)'; // Fainter, more premium grid
        c.lineWidth = 1;

        // Horizontal lines
        c.beginPath();
        for (let y = 0; y < h; y += h / 4) {
            c.moveTo(0, y); c.lineTo(w, y);
        }
        // Vertical lines
        for (let x = 0; x < w; x += w / 8) {
            c.moveTo(x, 0); c.lineTo(x, h);
        }
        c.stroke();
    }

    // 1. Precision Scope (Replaces Modern Wave)
    // A single, hyper-fast, glowing line representing the actual audio waveform.
    function drawPrecisionScope(c, data, w, h) {
        c.lineWidth = 2;
        c.strokeStyle = '#00f0ff'; // Cyan
        c.shadowBlur = 10;
        c.shadowColor = '#00f0ff';

        c.beginPath();
        const sliceWidth = w / data.length;
        let x = 0;

        for (let i = 0; i < data.length; i++) {
            const v = data[i] / 128.0; // 0..2 mostly
            const y = (v * h / 2); // Center is h/2

            if (i === 0) c.moveTo(x, y);
            else c.lineTo(x, y);

            x += sliceWidth;
        }
        c.stroke();
        c.shadowBlur = 0;

        // Center line
        c.strokeStyle = 'rgba(0, 240, 255, 0.1)';
        c.lineWidth = 1;
        c.beginPath();
        c.moveTo(0, h / 2);
        c.lineTo(w, h / 2);
        c.stroke();
    }

    // 2. Pro Spectrum (Replaces RTA)
    // 64-band RTA with "LED Segment" look
    function drawProSpectrum(c, data, w, h) {
        const bands = 64;
        // Logarithmic sampling? For now, linear is cleaner code-wise, maybe step it
        const step = Math.floor(data.length * 0.7 / bands); // Drop high freq noise
        const barW = (w / bands) - 2;

        for (let i = 0; i < bands; i++) {
            let sum = 0;
            // Average bin
            for (let j = 0; j < step; j++) sum += data[i * step + j];
            let val = sum / step;

            // Draw LED segments
            const segments = 10;
            const level = (val / 255) * segments;

            const x = i * (barW + 2) + 1;

            for (let s = 0; s < segments; s++) {
                // Color scaling
                let color = '#3b82f6'; // Blue base
                if (s > 6) color = '#eab308'; // Yellow warn
                if (s > 8) color = '#ef4444'; // Red peak

                c.fillStyle = (s < level) ? color : 'rgba(50,50,50,0.5)';
                const segH = (h / segments) - 2;
                const y = h - (s * (segH + 2)) - segH;

                c.fillRect(x, y, barW, segH);
            }
        }
    }

    // 3. Matrix Rain (Replaces RBG/GFX)
    let drops = [];
    function drawMatrixRain(c, data, w, h) {
        const fontSize = 12;
        const columns = Math.ceil(w / fontSize);

        if (drops.length !== columns) {
            drops = new Array(columns).fill(0);
        }

        c.fillStyle = 'rgba(0, 0, 0, 0.05)'; // Fast fade for trails
        c.fillRect(0, 0, w, h);

        c.fillStyle = '#0F0'; // Green
        c.font = fontSize + 'px monospace';

        const beat = data[4]; // Sub-bass bin

        for (let i = 0; i < drops.length; i++) {
            const char = String.fromCharCode(0x30A0 + Math.random() * 96);

            // Audio Reactivity: Brightness or Speed
            // We use simple: if beat hits, randomly spawn new drops high up
            if (beat > 200 && Math.random() > 0.95) drops[i] = 0;

            const x = i * fontSize;
            const y = drops[i] * fontSize;

            c.fillText(char, x, y);

            if (y > h && Math.random() > 0.975) {
                drops[i] = 0;
            }
            drops[i]++;
        }
    }

    // Legacy Oscilloscope (for fallback)
    function drawOscillo(c, d, w, h) { drawPrecisionScope(c, d, w, h); }
    function drawMatrix(c, d, w, h) { drawMatrixRain(c, d, w, h); }
    function drawModernWave(c, d, w, h) { drawPrecisionScope(c, d, w, h); }
    function drawRGBScroll(c, d, w, h) { drawMatrixRain(c, d, w, h); }

    function setImmersive(active) {
        resize(); // Force check
    }

    // --- RENDERERS ---

    function drawModernWave(c, data, w, h) {
        // Premium "Liquid" Waveform
        c.lineWidth = 4;
        c.lineCap = 'round';
        c.shadowBlur = 20;
        c.shadowColor = '#a855f7'; // Purple glow

        // Vibrant Gradient
        const gradient = c.createLinearGradient(0, 0, w, 0);
        gradient.addColorStop(0, '#00f0ff');   // Cyan
        gradient.addColorStop(0.5, '#2E8B57'); // Emerald
        gradient.addColorStop(1, '#800080');   // Purple
        c.strokeStyle = gradient;

        // Fill Gradient
        const fillGrad = c.createLinearGradient(0, 0, 0, h);
        fillGrad.addColorStop(0, 'rgba(236, 72, 153, 0.2)');
        fillGrad.addColorStop(1, 'rgba(59, 130, 246, 0.0)');

        c.beginPath();

        // Downsample to fewer points for smoothness
        const points = [];
        const slice = Math.floor(data.length / 40); // 40 points

        for (let i = 0; i < 44; i++) { // Slight overscan
            let sum = 0;
            const start = i * slice;
            if (start + slice < data.length) {
                for (let j = 0; j < slice; j++) sum += data[start + j];
                const val = sum / slice;
                // Scale & Dampen
                const y = h - ((val / 255) * h * 0.7) - (h * 0.1);
                points.push({ x: (i / 40) * w, y: y });
            }
        }

        if (points.length < 2) return;

        // Draw Smooth Curve
        c.moveTo(points[0].x, points[0].y);

        for (let i = 0; i < points.length - 1; i++) {
            const p0 = points[i];
            const p1 = points[i + 1];
            const midX = (p0.x + p1.x) / 2;
            const midY = (p0.y + p1.y) / 2;
            c.quadraticCurveTo(p0.x, p0.y, midX, midY);
        }

        // Connect to bottom for fill
        c.lineTo(w, h);
        c.lineTo(0, h);
        c.closePath();

        // Fill
        c.fillStyle = fillGrad;
        c.fill();

        // Stroke (redraw curve part only for sharp line)
        c.beginPath();
        c.moveTo(points[0].x, points[0].y);
        for (let i = 0; i < points.length - 1; i++) {
            const p0 = points[i];
            const p1 = points[i + 1];
            const midX = (p0.x + p1.x) / 2;
            const midY = (p0.y + p1.y) / 2;
            c.quadraticCurveTo(p0.x, p0.y, midX, midY);
        }
        c.stroke();
        c.shadowBlur = 0;

        // Add "Beat" Circle in background if bass is high
        const bass = data[5];
        if (bass > 180) {
            c.beginPath();
            c.arc(w / 2, h / 2, (bass / 255) * 100, 0, Math.PI * 2);
            c.fillStyle = `rgba(255,255,255, ${(bass - 180) / 300})`;
            c.fill();
        }
    }

    // Matrix Rain State
    let matrixDrops = [];

    function drawMatrix(c, data, w, h) {
        // Init drops
        const cols = Math.floor(w / 10);
        if (matrixDrops.length !== cols) {
            matrixDrops = new Array(cols).fill(0).map(() => Math.random() * h);
        }

        // Fade background (Trail effect)
        c.fillStyle = 'rgba(0, 0, 0, 0.1)';
        c.fillRect(0, 0, w, h);

        c.fillStyle = '#0f0'; // Hacker Green
        c.font = '10px monospace';

        for (let i = 0; i < cols; i++) {
            // Audio reactivity: Speed depends on frequency
            const freqIndex = Math.floor((i / cols) * data.length * 0.5); // Use lower half
            const val = data[freqIndex];
            const speed = 1 + (val / 20); // Faster with volume

            // Char choice: Hex
            const valid = "0123456789ABCDEF";
            const char = valid.charAt(Math.floor(Math.random() * valid.length));

            // Color based on intensity
            const intensity = val / 255;
            c.fillStyle = `rgba(0, ${255}, ${100}, ${intensity})`;

            if (val > 100) {
                c.fillText(char, i * 10, matrixDrops[i]);
            }

            // Move drop
            matrixDrops[i] += speed;

            // Reset
            if (matrixDrops[i] > h && Math.random() > 0.975) {
                matrixDrops[i] = 0;
            }
        }
    }

    function setMode(nameOrIndex) {
        if (typeof nameOrIndex === 'number') {
            modeIndex = nameOrIndex % modes.length;
        } else if (typeof nameOrIndex === 'string') {
            const idx = modes.indexOf(nameOrIndex);
            if (idx >= 0) modeIndex = idx;
        }
        // Force redraw or toast logic if needed
        const modeName = modes[modeIndex].replace('_', ' ').toUpperCase();
        if (window.showToast) window.showToast(`VISUALIZER: ${modeName}`);
    }

    // Public API
    return { init, setImmersive, setMode, getModes: () => modes, getAnalyser: () => analyser };
})();

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
