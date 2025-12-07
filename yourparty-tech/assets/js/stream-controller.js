/**
 * YourParty Stream Controller
 * Handles audio playback with live sync
 * v3.5.1 Fixed Global Scope
 */

window.StreamController = (function () {
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
        playBtn: '#play-toggle, .radio-card__play, .immersive-play-btn, #immersive-play-btn',
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
            // Create hidden audio element if missing
            audioElement = document.createElement('audio');
            audioElement.id = 'radio-audio';
            audioElement.style.display = 'none';
            document.body.appendChild(audioElement);
            // Re-select
            audioElement = document.querySelector(SELECTORS.audio);
        }

        // Enable CORS for Visualizer (Crucial!)
        audioElement.crossOrigin = "anonymous";
        audioElement.preload = "none"; // Save bandwidth until play

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
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                togglePlay();
            });
        });

        // Mini player
        const miniBtn = document.querySelector(SELECTORS.miniPlayBtn);
        if (miniBtn) {
            miniBtn.addEventListener('click', (e) => {
                e.preventDefault();
                togglePlay();
            });
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
    async function togglePlay() {
        if (!audioElement) return;
        try {
            if (audioElement.paused) {
                await play();
            } else {
                pause();
            }
        } catch (error) {
            console.error('[StreamController] Playback error:', error);
        }
    }

    /**
     * Start playback with live sync
     */
    async function play() {
        reloadStream();
        initAudioContext(); // Must happen on user interaction!
        try {
            await audioElement.play();
            isPlaying = true;
            dispatchEvent('stream:play');
        } catch (e) {
            console.error("Autoplay/Play failed", e);
        }
    }

    /**
     * Pause playback
     */
    function pause() {
        audioElement.pause();
        isPlaying = false;
        dispatchEvent('stream:pause');
    }

    /**
     * Reload stream source for live sync
     */
    function reloadStream() {
        if (!streamUrl) return;

        const sourceEl = audioElement.querySelector('source');
        const cleanUrl = streamUrl.split('?')[0];
        const newUrl = `${cleanUrl}?_=${Date.now()}`;

        if (sourceEl) {
            sourceEl.src = newUrl;
        } else {
            audioElement.src = newUrl;
        }
        audioElement.load();
    }

    /**
     * Initialize Web Audio API for visualizer
     */
    function initAudioContext() {
        if (audioContext && audioContext.state === 'running') return;

        try {
            if (!audioContext) {
                audioContext = new (window.AudioContext || window.webkitAudioContext)();
                analyser = audioContext.createAnalyser();
                analyser.fftSize = 4096; // Premium High-Res

                const source = audioContext.createMediaElementSource(audioElement);
                source.connect(analyser);
                analyser.connect(audioContext.destination);

                dispatchEvent('stream:audioContextReady', { analyser });
            }

            if (audioContext.state === 'suspended') {
                audioContext.resume();
            }
        } catch (error) {
            console.warn('[StreamController] AudioContext init error (likely no user gesture):', error);
        }
    }

    /**
     * Setup Media Session API
     */
    function setupMediaSession() {
        if (!('mediaSession' in navigator)) return;
        navigator.mediaSession.setActionHandler('play', play);
        navigator.mediaSession.setActionHandler('pause', pause);
    }

    function updateMetadata(track) {
        if (!('mediaSession' in navigator)) return;
        navigator.mediaSession.metadata = new MediaMetadata({
            title: track.title || 'Unknown Track',
            artist: track.artist || 'YourParty Radio',
            album: track.album || 'YourParty Radio',
            artwork: track.art ? [{ src: track.art, sizes: '512x512', type: 'image/jpeg' }] : []
        });
    }

    // Event handlers
    function onPlay() { updatePlayButtons(true); dispatchEvent('stream:playing'); }
    function onPause() { updatePlayButtons(false); dispatchEvent('stream:paused'); }
    function onError(e) {
        console.error('[StreamController] Stream error:', e);
        dispatchEvent('stream:error', { error: e });
        updatePlayButtons(false);
    }
    function onBuffering() { dispatchEvent('stream:buffering'); }
    function onPlaying() { dispatchEvent('stream:playing'); }

    function updatePlayButtons(playing) {
        // Simple text toggle for now, or icon class toggle
        // Assuming icons are controlled via CSS classes or inner content
        document.querySelectorAll(SELECTORS.playBtn).forEach(btn => {
            btn.classList.toggle('playing', playing);
            // Optionally change icon text/html if needed by theme
        });
    }

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
