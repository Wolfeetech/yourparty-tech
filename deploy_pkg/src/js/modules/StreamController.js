/**
 * YourParty Stream Controller
 * Handles audio playback with live sync
 */

export default class StreamController {
    constructor(config = {}) {
        this.config = config;
        this.audioElement = null;
        this.audioContext = null;
        this.analyser = null;
        this.isPlaying = false;
        this.streamUrl = config.streamUrl || '';

        // Playback State
        this.isLocked = false;
        this.playQueue = Promise.resolve();

        this.SELECTORS = {
            audio: '#radio-audio',
            playBtn: '#play-toggle, .radio-card__play',
            miniPlayBtn: '#mini-play-toggle',
            visualizer: '#inline-visualizer'
        };

        this.init();
    }

    init() {
        this.audioElement = document.querySelector(this.SELECTORS.audio);

        if (!this.audioElement) {
            // Create hidden audio element for Dashboard
            this.audioElement = document.createElement('audio');
            this.audioElement.id = 'radio-audio';
            this.audioElement.style.display = 'none';
            document.body.appendChild(this.audioElement);
        }

        // Enable CORS for Visualizer
        this.audioElement.crossOrigin = "anonymous";

        this.bindEvents();
        this.setupMediaSession();

        // Reveal Player UI
        const miniPlayer = document.getElementById('mini-player');
        if (miniPlayer) {
            miniPlayer.style.display = 'flex';
        }

        console.log('[StreamController] Initialized (ES6)');
    }

    bindEvents() {
        // Main play button - Delegation or direct?
        // Relying on PlayerControls for UI triggers might be better, but let's keep direct binding for now to ensure compatibility
        // Actually, PlayerControls calls this.togglePlay() via global or module instance.
        // Let's expose a method.

        // Audio events
        this.audioElement.addEventListener('play', () => this.onPlay());
        this.audioElement.addEventListener('pause', () => this.onPause());
        this.audioElement.addEventListener('error', (e) => this.onError(e));
        this.audioElement.addEventListener('playing', () => this.onPlaying());
    }

    togglePlay() {
        if (!this.audioElement || this.isLocked) return;

        this.isLocked = true;
        setTimeout(() => this.isLocked = false, 300);

        if (this.audioElement.paused) {
            this.queueAction('play');
        } else {
            this.queueAction('pause');
        }
    }

    queueAction(action) {
        this.playQueue = this.playQueue.then(async () => {
            try {
                if (action === 'play') {
                    await this.performPlay();
                } else {
                    this.performPause();
                }
            } catch (err) {
                console.error(`[StreamController] Action ${action} failed:`, err);
            }
        });
    }

    async performPlay() {
        this.initAudioContext();
        try {
            await this.audioElement.play();
            this.isPlaying = true;
            this.dispatchEvent('stream:play');
        } catch (error) {
            console.warn('[StreamController] Play failed:', error);
            this.isPlaying = false;
            if (error.name !== 'AbortError') {
                this.dispatchEvent('stream:error', { error });
            }
        }
    }

    performPause() {
        this.audioElement.pause();
        this.isPlaying = false;
        this.dispatchEvent('stream:pause');
    }

    initAudioContext() {
        if (this.audioContext) return;
        try {
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            this.analyser = this.audioContext.createAnalyser();
            this.analyser.fftSize = 256;
            const source = this.audioContext.createMediaElementSource(this.audioElement);
            source.connect(this.analyser);
            this.analyser.connect(this.audioContext.destination);
            this.dispatchEvent('stream:audioContextReady', { analyser: this.analyser });
        } catch (error) {
            console.warn('[StreamController] AudioContext error:', error);
        }
    }

    setupMediaSession() {
        if (!('mediaSession' in navigator)) return;
        navigator.mediaSession.setActionHandler('play', () => this.queueAction('play'));
        navigator.mediaSession.setActionHandler('pause', () => this.queueAction('pause'));
    }

    updateMetadata(track) {
        if (!('mediaSession' in navigator)) return;
        navigator.mediaSession.metadata = new MediaMetadata({
            title: track.title || 'Unknown Track',
            artist: track.artist || 'Unknown Artist',
            album: track.album || 'YourParty Radio',
            artwork: track.art ? [{ src: track.art, sizes: '512x512', type: 'image/jpeg' }] : []
        });
    }

    onPlay() { this.dispatchEvent('stream:playing'); }
    onPause() { this.dispatchEvent('stream:paused'); }
    onPlaying() { this.dispatchEvent('stream:playing'); }
    onError(e) { this.dispatchEvent('stream:error', { error: e }); }

    dispatchEvent(name, detail = {}) {
        window.dispatchEvent(new CustomEvent(name, { detail }));
    }
}
