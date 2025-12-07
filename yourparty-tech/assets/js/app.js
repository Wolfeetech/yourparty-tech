/**
 * YourParty Tech - Main Application
 * Orchestrates all modules
 * v3.4.2 Debug Mode
 */

(function (window, document) {
    'use strict';

    // GLOBAL ERROR HANDLER (DEBUG)
    window.addEventListener('error', function (e) {
        const msg = e.message || e.toString();
        const box = document.getElementById('debug-error-bar') || document.createElement('div');
        box.id = 'debug-error-bar';
        box.style.cssText = "position:fixed;bottom:0;left:0;width:100%;background:#ef4444;color:white;z-index:9999999;padding:10px;font-family:monospace;font-size:12px;text-align:center;";
        box.innerText = "JS CRASH: " + msg;
        if (!box.parentNode) document.body.appendChild(box);
        console.error("GLOBAL ERROR CAPTURED:", e);
    });

    // 1. MAIN APP MODULE
    window.YourPartyApp = (function () {
        let config = {};
        const STATUS_POLL_INTERVAL = 10000;
        let pollTimer = null;

        function init() {
            console.log('[YourPartyApp] Initializing...');
            config = window.YourPartyConfig || {
                restBase: 'https://yourparty.tech/wp-json/yourparty/v1', // Fallback
                streamUrl: 'https://radio.yourparty.tech/radio/8000/radio.mp3' // Fallback
            };

            try {
                initModules();
                initToastSystem();
                fetchStatus(); // Async, don't await
                startPolling();
                bindStreamEvents();
                bindUIEvents();
                fetchHistory(); // Async
            } catch (e) {
                console.error('[YourPartyApp] Init Crash:', e);
                throw e; // Rethrow to trigger visible error bar
            }
        }

        function initModules() {
            if (typeof window.StreamController !== 'undefined') {
                window.StreamController.init({ streamUrl: config.streamUrl });
            }
        }

        async function fetchStatus() {
            const endpoint = config.restBase ? `${config.restBase}/status` : '/status';
            try {
                const response = await fetch(endpoint);
                if (!response.ok) {
                    console.warn(`[YourPartyApp] Status fetch failed: ${response.status}`);
                    return;
                }
                const data = await response.json();
                updateUI(data);
            } catch (error) {
                console.error('[YourPartyApp] Status fetch error:', error);
                // Don't throw, just log
            }
        }

        function updateUI(data) {
            const song = data.now_playing?.song;
            if (!song) return;

            window.yourPartyCurrentSong = song;

            updateTrackInfo(song);
            updateRating(song);
            updateMood(song);

            const listeners = data.listeners?.total || 0;
            const el = document.getElementById('listener-count');
            if (el) el.textContent = listeners;

            updateNextTrack(data.playing_next?.song);
            notifyModules(song);
        }

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

        function updateTrackInfo(song) {
            const titleEl = document.getElementById('track-title');
            const artistEl = document.getElementById('track-artist');
            const artEl = document.getElementById('cover-art');

            if (titleEl && titleEl.textContent !== song.title) {
                titleEl.textContent = song.title || 'Unknown Title';
            }
            if (artistEl && artistEl.textContent !== song.artist) {
                artistEl.textContent = song.artist || 'Unknown Artist';
            }

            if (artEl) {
                const newSrc = song.art || _generateFallbackGradient(song.title);
                if (artEl.src !== newSrc) {
                    artEl.style.transition = 'opacity 0.5s ease';
                    artEl.src = newSrc;
                }
            }

            if (typeof window.StreamController !== 'undefined') {
                window.StreamController.updateMetadata(song);
            }
        }

        function _generateFallbackGradient(str) {
            if (!str) return 'https://placehold.co/600x600/050505/333333?text=NO+ART';
            let hash = 0;
            for (let i = 0; i < str.length; i++) hash = str.charCodeAt(i) + ((hash << 5) - hash);
            const c1 = (hash & 0x00FFFFFF).toString(16).toUpperCase();
            const c2 = ((hash * 2) & 0x00FFFFFF).toString(16).toUpperCase();
            return `https://ui-avatars.com/api/?name=${encodeURIComponent(str)}&background=${c1}&color=${c2}&size=600&font-size=0.33`;
        }

        function updateRating(song) {
            const rating = song.rating || {};
            const average = rating.average || 0;
            const total = rating.total || 0;

            if (typeof window.RatingModule !== 'undefined') {
                window.RatingModule.setInitialRating(song.id, average, total);
            }

            const avgEl = document.getElementById('rating-average');
            const totalEl = document.getElementById('rating-total');
            if (avgEl) avgEl.textContent = average > 0 ? average.toFixed(1) : '--';
            if (totalEl) totalEl.textContent = total > 0 ? `(${total})` : '';
            // Force visible update
            if (avgEl) avgEl.style.display = 'inline-block';
        }

        function updateMood(song) {
            const topMood = song.top_mood;
            const moods = song.moods || {};
            const topGenre = song.top_genre || '';
            const genres = song.genres || {};

            if (typeof window.MoodModule !== 'undefined') {
                window.MoodModule.setMoodData(song.id, topMood, moods, topGenre, genres);
            }
        }

        function notifyModules(song) {
            window.currentSongId = song.id;
            window.dispatchEvent(new CustomEvent('songChange', { detail: { song } }));
        }

        function startPolling() {
            stopPolling();
            pollTimer = setInterval(fetchStatus, STATUS_POLL_INTERVAL);
        }

        function stopPolling() {
            if (pollTimer) { clearInterval(pollTimer); pollTimer = null; }
        }

        function bindUIEvents() {
            const refreshBtn = document.getElementById('refresh-history');
            if (refreshBtn) {
                refreshBtn.addEventListener('click', (e) => {
                    e.preventDefault();
                    fetchHistory();
                });
            }
        }

        function bindStreamEvents() {
            window.addEventListener('stream:play', () => fetchStatus());
        }

        async function fetchHistory() {
            const endpoint = config.restBase ? `${config.restBase}/history` : '/history';
            try {
                const response = await fetch(endpoint);
                const data = await response.json();
                const list = Array.isArray(data) ? data : (data.history || []);
                renderHistory(list);
            } catch (error) {
                // console.error('[YourPartyApp] History fetch error:', error);
            }
        }

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
                const rating = song.rating?.average || 0;
                const mood = song.top_mood || '';
                return `<li class="history-item" style="display: flex; gap: 10px; align-items: center; padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.1);">
                    <img src="${song.art || _generateFallbackGradient(song.title)}" style="width: 48px; height: 48px; border-radius: 4px;">
                    <div style="flex:1;">
                        <div style="color:#fff; font-weight:500;">${song.title} ${mood ? `<small>(${mood})</small>` : ''}</div>
                        <div style="color:#888; font-size:12px;">${song.artist}</div>
                    </div>
                    <div style="color:#666; font-size:10px;">${timeStr}</div>
                </li>`;
            }).join('');
        }

        function initToastSystem() {
            if (!document.getElementById('yp-toast-container')) {
                const container = document.createElement('div');
                container.id = 'yp-toast-container';
                Object.assign(container.style, {
                    position: 'fixed', bottom: '20px', right: '20px', display: 'flex', flexDirection: 'column', gap: '10px', zIndex: '99999', pointerEvents: 'none'
                });
                document.body.appendChild(container);
            }
            window.showToast = showToast;
        }

        function showToast(message, type = 'info') {
            const container = document.getElementById('yp-toast-container');
            if (!container) return;
            const toast = document.createElement('div');
            Object.assign(toast.style, {
                background: 'rgba(10, 10, 10, 0.9)', color: '#fff', padding: '12px 24px', borderRadius: '4px', border: '1px solid #555', pointerEvents: 'auto', transition: 'all 0.3s', opacity: '0', transform: 'translateY(10px)'
            });
            toast.textContent = message;
            container.appendChild(toast);
            requestAnimationFrame(() => { toast.style.opacity = '1'; toast.style.transform = 'translateY(0)'; });
            setTimeout(() => { toast.style.opacity = '0'; setTimeout(() => toast.remove(), 300); }, 3000);
        }

        return {
            init,
            fetchStatus,
            fetchHistory,
            getConfig: () => config,
            getStreamController: () => (typeof window.StreamController !== 'undefined' ? window.StreamController : null),
            showToast
        };
    })();

    // 2. INLINE VISUALIZER ADAPTER
    window.InlineVisualizerAdapter = (function () {
        function init() {
            const canvas = document.getElementById('inline-visualizer');
            if (!canvas) {
                console.warn("No inline visualizer canvas found.");
                return;
            }
            if (typeof window.VisualEngine === 'undefined') {
                console.error("VisualEngine is missing!");
                // Try to alert user visually?
                return;
            }

            if (window.VisualEngine.init(canvas)) {
                window.VisualEngine.setMode(1); // Precision Wave
            }

            document.querySelectorAll('.vis-btn').forEach(btn => {
                if (btn.id === 'visualizer-toggle') return;
                btn.addEventListener('click', (e) => {
                    e.preventDefault();
                    document.querySelectorAll('.vis-btn').forEach(b => b.classList.remove('active'));
                    btn.classList.add('active');
                    const mode = btn.dataset.mode;
                    if (mode === 'waveform') window.VisualEngine.setMode(1);
                    if (mode === 'spectrum') window.VisualEngine.setMode(0);
                    if (mode === 'rgb_waveform') window.VisualEngine.setMode(4);
                });
            });
        }
        return { init };
    })();

    // 3. REALTIME MODULE
    window.RealtimeModule = (function () {
        let socket;
        function init() { try { connect(); } catch (e) { console.error("Realtime Init Error", e); } }
        function connect() {
            const host = 'api.yourparty.tech';
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            socket = new WebSocket(`${protocol}//${host}/ws/client`);
            socket.onmessage = (e) => {
                try {
                    const msg = JSON.parse(e.data);
                    if (msg.type === 'vote_update') updateVoteUI(msg.stats, msg.total);
                } catch (err) { }
            };
            socket.onclose = () => setTimeout(connect, 5000);
            socket.onerror = (e) => console.warn("WebSocket Error", e);
        }
        function updateVoteUI(stats, total) {
            if (!total) total = 1;
            document.querySelectorAll('.vibe-btn').forEach(btn => {
                const type = btn.dataset.vote;
                const count = stats[type] || 0;
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
                } else {
                    badge.style.opacity = '0';
                }
            });
        }
        return { init };
    })();


    // 4. BOOTSTRAPPER
    function initAll() {
        console.log('[App] Bootstrapping v3.4.2...');
        try {
            if (window.YourPartyApp) window.YourPartyApp.init();
            if (window.InlineVisualizerAdapter) window.InlineVisualizerAdapter.init();
            if (window.RatingModule) window.RatingModule.init();
            if (window.MoodModule) window.MoodModule.init();
            if (window.FullscreenVisualPlayer) window.FullscreenVisualPlayer.init();
            if (window.RealtimeModule) window.RealtimeModule.init();

            // Mood Button Binding
            const moodBtn = document.getElementById('mood-tag-button');
            if (moodBtn) {
                moodBtn.addEventListener('click', (e) => {
                    e.preventDefault();
                    if (window.yourPartyCurrentSong && window.MoodModule) {
                        window.MoodModule.openDialog(window.yourPartyCurrentSong);
                    } else {
                        window.showToast("Bitte warten... Songdaten laden", "warning");
                        if (window.YourPartyApp) window.YourPartyApp.fetchStatus(); // Try force update
                    }
                });
            }
        } catch (e) {
            console.error("FATAL BOOTSTRAP ERROR", e);
            throw e; // Show bar
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initAll);
    } else {
        initAll();
    }

})(window, document);
