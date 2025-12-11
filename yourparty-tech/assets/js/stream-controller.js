/**
 * YourParty Stream Controller
 * Handles audio playback with live sync
 */

const StreamController = (function () {
    'use strict';

    // State
    let audioElement = null;
    let audioContext = null;
    let analyser = null;
    let isPlaying = false;
    let streamUrl = '';

    // Selectors
    const SELECTORS = {
        audio: '#radio-audio',
        playBtn: '#play-toggle, .radio-card__play',
        miniPlayBtn: '#mini-play-toggle',
        visualizer: '#inline-visualizer'
    };

    /**
     * Initialize stream controller
     */
    function init(config = {}) {
        streamUrl = config.streamUrl || '';
        audioElement = document.querySelector(SELECTORS.audio);

        if (!audioElement) {
            // Create hidden audio element for Dashboard
            audioElement = document.createElement('audio');
            audioElement.id = 'radio-audio';
            audioElement.style.display = 'none';
            document.body.appendChild(audioElement);
            // Re-select
            audioElement = document.querySelector(SELECTORS.audio);
        }

        // Enable CORS for Visualizer
        audioElement.crossOrigin = "anonymous";

        bindEvents();
        setupMediaSession();

        // Reveal Player UI
        const miniPlayer = document.getElementById('mini-player');
        if (miniPlayer) {
            miniPlayer.style.display = 'flex';
        }

        console.log('[StreamController] Initialized');
    }

    /**
     * Bind UI events
     */
    function bindEvents() {
        // Main play button
        document.querySelectorAll(SELECTORS.playBtn).forEach(btn => {
            btn.addEventListener('click', togglePlay);
        });

        // Mini player
        const miniBtn = document.querySelector(SELECTORS.miniPlayBtn);
        if (miniBtn) {
            miniBtn.addEventListener('click', togglePlay);
        }

        // Audio events
        audioElement.addEventListener('play', onPlay);
        audioElement.addEventListener('pause', onPause);
        audioElement.addEventListener('error', onError);
        audioElement.addEventListener('waiting', onBuffering);
        audioElement.addEventListener('playing', onPlaying);
    }

    /**
     * Toggle play/pause
     */
    // Playback State Management
    let isLocked = false; // Prevents rapid re-triggering (debounce)
    let playQueue = Promise.resolve(); // Promise queue for sequential execution

    /**
     * Toggle play/pause (Debounced)
     */
    function togglePlay() {
        if (!audioElement || isLocked) return;

        isLocked = true;
        setTimeout(() => isLocked = false, 300); // Simple 300ms debounce

        if (audioElement.paused) {
            queueAction('play');
        } else {
            queueAction('pause');
        }
    }

    /**
     * Queue a playback action to ensure sequential execution
     */
    function queueAction(action) {
        console.log(`[StreamController] Queueing action: ${action}`);

        playQueue = playQueue.then(async () => {
            try {
                if (action === 'play') {
                    await performPlay();
                } else {
                    performPause(); // Pause is synchronous/instant usually
                }
            } catch (err) {
                console.error(`[StreamController] Action ${action} failed:`, err);
            }
        });
    }

    /**
     * Perform Play Logic
     */
    async function performPlay() {
        console.log('[StreamController] Performing Play...');

        // Optimistic UI
        updatePlayButtons(true);

        // Ensure AudioContext
        initAudioContext();

        try {
            await audioElement.play();
            console.log('[StreamController] Playback started');
            isPlaying = true;
            dispatchEvent('stream:play');
        } catch (error) {
            console.warn('[StreamController] Play failed:', error);
            isPlaying = false;
            updatePlayButtons(false); // Revert UI

            if (error.name !== 'AbortError') {
                dispatchEvent('stream:error', { error });
            }
        }
    }

    /**
     * Perform Pause Logic
     */
    function performPause() {
        console.log('[StreamController] Performing Pause...');
        audioElement.pause();
        isPlaying = false;
        updatePlayButtons(false);
        dispatchEvent('stream:pause');
    }

    // Public API Methods (mapped to queue)
    function play() { queueAction('play'); }
    function pause() { queueAction('pause'); }

    /**
     * Reload stream source for live sync
     */
    function reloadStream() {
        if (!streamUrl) return;

        const cleanUrl = streamUrl.split('?')[0];
        // Timestamp prevents caching
        const newUrl = `${cleanUrl}?_=${Date.now()}`;

        if (audioElement.querySelector('source')) {
            audioElement.querySelector('source').src = newUrl;
        } else {
            audioElement.src = newUrl;
        }
        audioElement.load();
    }

    /**
     * Initialize Web Audio API for visualizer
     */
    function initAudioContext() {
        if (audioContext) return;

        try {
            audioContext = new (window.AudioContext || window.webkitAudioContext)();
            analyser = audioContext.createAnalyser();
            analyser.fftSize = 256;

            const source = audioContext.createMediaElementSource(audioElement);
            source.connect(analyser);
            analyser.connect(audioContext.destination);

            dispatchEvent('stream:audioContextReady', { analyser });
        } catch (error) {
            console.warn('[StreamController] AudioContext error:', error);
        }
    }

    /**
     * Setup Media Session API for system controls
     */
    function setupMediaSession() {
        if (!('mediaSession' in navigator)) return;

        navigator.mediaSession.setActionHandler('play', play);
        navigator.mediaSession.setActionHandler('pause', pause);
    }

    /**
     * Update Media Session metadata
     */
    function updateMetadata(track) {
        if (!('mediaSession' in navigator)) return;

        navigator.mediaSession.metadata = new MediaMetadata({
            title: track.title || 'Unknown Track',
            artist: track.artist || 'Unknown Artist',
            album: track.album || 'YourParty Radio',
            artwork: track.art ? [
                { src: track.art, sizes: '512x512', type: 'image/jpeg' }
            ] : []
        });
    }

    // Event handlers
    function onPlay() {
        updatePlayButtons(true);
        dispatchEvent('stream:playing');
    }

    function onPause() {
        updatePlayButtons(false);
        dispatchEvent('stream:paused');
    }

    function onError(e) {
        console.error('[StreamController] Stream error:', e);
        dispatchEvent('stream:error', { error: e });
    }

    function onBuffering() {
        dispatchEvent('stream:buffering');
    }

    function onPlaying() {
        dispatchEvent('stream:playing');
    }

    /**
     * Update all play buttons
     */
    function updatePlayButtons(playing) {
        const label = playing ? 'Pausieren' : 'Abspielen';

        document.querySelectorAll(`${SELECTORS.playBtn}, ${SELECTORS.miniPlayBtn}`).forEach(btn => {
            if (!btn) return;

            // Logic for buttons with dedicated icon spans (Front Page)
            const playIcon = btn.querySelector('.icon-play');
            const pauseIcon = btn.querySelector('.icon-pause');

            if (playIcon && pauseIcon) {
                playIcon.style.display = playing ? 'none' : 'inline';
                pauseIcon.style.display = playing ? 'inline' : 'none';
            } else {
                // Fallback for simple buttons (Mini Player often just has text or one icon)
                const icon = playing ? '❚❚' : '▶';
                const iconEl = btn.querySelector('span') || btn;
                // Only replace text if it looks like an icon (short) to avoid wiping text buttons
                if (iconEl.textContent.length < 3) {
                    iconEl.textContent = icon;
                }
            }

            btn.setAttribute('aria-label', label);
            btn.classList.toggle('playing', playing);
        });
    }

    /**
     * Dispatch custom event
     */
    function dispatchEvent(name, detail = {}) {
        window.dispatchEvent(new CustomEvent(name, { detail }));
    }

    // Public API
    return {
        init,
        play,
        pause,
        togglePlay,
        updateMetadata,
        getAnalyser: () => analyser,
        isPlaying: () => isPlaying
    };
})();

// Export and Global Attachment
window.StreamController = StreamController;

if (typeof module !== 'undefined' && module.exports) {
    module.exports = StreamController;
}
