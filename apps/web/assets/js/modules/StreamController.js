/**
 * YourParty Stream Controller
 * Handles audio playback with "Dual Deck" crossfading for seamless transitions
 */

export default class StreamController {
    constructor(config = {}) {
        this.config = config;

        // Dual Deck System
        this.deckA = null;
        this.deckB = null;
        this.activeDeck = 'A'; // 'A' or 'B'

        // Audio Context Graph
        this.audioContext = null;
        this.masterGain = null;
        this.analyser = null;
        this.gainA = null;
        this.gainB = null;
        this.sourceA = null;
        this.sourceB = null;

        this.isPlaying = false;
        this.currentUrl = config.streamUrl || '';

        // Constants
        this.CROSSFADE_DURATION = 2.5; // seconds

        this.SELECTORS = {
            audioA: '#radio-audio-a',
            audioB: '#radio-audio-b',
            playBtn: '#play-toggle, .radio-card__play, #mini-play-toggle'
        };

        this.init();
    }

    init() {
        // Initialize Decks
        this.deckA = this._createDeck('radio-audio-a');
        this.deckB = this._createDeck('radio-audio-b');

        // Check if legacy element exists and adopt it
        const legacy = document.getElementById('radio-audio');
        if (legacy) {
            legacy.id = 'radio-audio-legacy'; // Rename to avoid conflict
            legacy.pause();
            legacy.src = '';
        }

        // Enable CORS
        this.deckA.crossOrigin = "anonymous";
        this.deckB.crossOrigin = "anonymous";

        // Bind Events
        this.bindDeckEvents(this.deckA);
        this.bindDeckEvents(this.deckB);

        // UI Setup
        const miniPlayer = document.getElementById('mini-player');
        if (miniPlayer) miniPlayer.style.display = 'flex';

        // Initial URL setup
        if (this.currentUrl) {
            this.deckA.src = this.currentUrl;
        }

        console.log('[StreamController] "Dual Deck" Engine Initialized');
    }

    _createDeck(id) {
        let el = document.getElementById(id);
        if (!el) {
            el = document.createElement('audio');
            el.id = id;
            el.style.display = 'none';
            el.preload = 'none';
            document.body.appendChild(el);
        }
        return el;
    }

    initAudioContext() {
        if (this.audioContext) return;

        try {
            const AudioContext = window.AudioContext || window.webkitAudioContext;
            this.audioContext = new AudioContext();

            // Create Nodes
            this.masterGain = this.audioContext.createGain();
            this.gainA = this.audioContext.createGain();
            this.gainB = this.audioContext.createGain();
            this.analyser = this.audioContext.createAnalyser();

            // Config Analyser
            this.analyser.fftSize = 256;
            this.analyser.smoothingTimeConstant = 0.8;

            // Connect Graph
            // Source -> Gain -> Master -> Analyser -> Destination
            this.masterGain.connect(this.analyser);
            this.analyser.connect(this.audioContext.destination);

            this.gainA.connect(this.masterGain);
            this.gainB.connect(this.masterGain);

            // Connect Decks (delayed to avoid "autostart" issues)
            this._connectDeck(this.deckA, this.gainA, 'sourceA');
            this._connectDeck(this.deckB, this.gainB, 'sourceB');

            // Initial Gains
            this.gainA.gain.value = 1.0;
            this.gainB.gain.value = 0.0;

            console.log('[StreamController] Audio Graph Connected');
        } catch (e) {
            console.error('[StreamController] AudioContext init failed:', e);
        }
    }

    _connectDeck(audioEl, gainNode, sourceProp) {
        try {
            if (this[sourceProp]) return; // Already connected
            const source = this.audioContext.createMediaElementSource(audioEl);
            source.connect(gainNode);
            this[sourceProp] = source;
        } catch (e) {
            console.warn(`[StreamController] Failed to connect ${sourceProp}:`, e);
            // Handling for "MediaElementAudioSourceNode" already connected error
        }
    }

    bindDeckEvents(audioEl) {
        audioEl.addEventListener('playing', () => {
            if (this._getActiveDeck() === audioEl) {
                this.isPlaying = true;
                this.dispatchEvent('stream:playing');
            }
        });
        audioEl.addEventListener('pause', () => {
            // Only dispatch pause if WE initiated it on active deck
            // Ignore pauses from crossfading/background decks
        });
        audioEl.addEventListener('error', (e) => {
            if (this._getActiveDeck() === audioEl) {
                this.dispatchEvent('stream:error', { error: e });
            }
        });
    }

    /* Controls */

    async togglePlay() {
        this.initAudioContext();

        // Resume context if suspended (browser policy)
        if (this.audioContext?.state === 'suspended') {
            await this.audioContext.resume();
        }

        const active = this._getActiveDeck();

        if (this.isPlaying || !active.paused) {
            this.pause();
        } else {
            await this.play();
        }
    }

    async play() {
        this.initAudioContext();
        await this.audioContext?.resume();

        try {
            const active = this._getActiveDeck();
            await active.play();
            this.isPlaying = true;
            this.dispatchEvent('stream:playing');
        } catch (e) {
            console.error('[StreamController] Play failed:', e);
            this.dispatchEvent('stream:error', { error: e });
        }
    }

    pause() {
        const active = this._getActiveDeck();
        active.pause();
        this.isPlaying = false;
        this.dispatchEvent('stream:paused');
    }

    /**
     * Crossfade to a new URL
     */
    async crossfadeTo(newUrl) {
        if (newUrl === this.currentUrl) return;
        this.currentUrl = newUrl;

        console.log(`[StreamController] Crossfading to ${newUrl}`);
        this.initAudioContext();
        await this.audioContext?.resume();

        // Identify decks
        const currentDeck = this.activeDeck === 'A' ? this.deckA : this.deckB;
        const nextDeck = this.activeDeck === 'A' ? this.deckB : this.deckA;
        const currentGain = this.activeDeck === 'A' ? this.gainA : this.gainB;
        const nextGain = this.activeDeck === 'A' ? this.gainB : this.gainA;

        // Prepare Next Deck
        nextDeck.src = newUrl;
        nextDeck.load(); // Ensure buffering starts

        // Start Next Deck (Muted via Gain)
        // Ensure gain is 0 before playing
        nextGain.gain.cancelScheduledValues(this.audioContext.currentTime);
        nextGain.gain.setValueAtTime(0, this.audioContext.currentTime);

        try {
            await nextDeck.play();
        } catch (e) {
            console.error("Autoplay prevented on crossfade deck", e);
            // If autoplay fails, we can't crossfade properly. Hard cut fallback.
            currentDeck.pause();
            setTimeout(() => nextDeck.play(), 100);
        }

        // Perform Crossfade
        const now = this.audioContext.currentTime;
        const fadeTime = this.CROSSFADE_DURATION;

        // Current -> Fade Out
        currentGain.gain.cancelScheduledValues(now);
        currentGain.gain.setValueAtTime(currentGain.gain.value, now);
        currentGain.gain.linearRampToValueAtTime(0, now + fadeTime);

        // Next -> Fade In
        nextGain.gain.cancelScheduledValues(now);
        nextGain.gain.setValueAtTime(0, now);
        nextGain.gain.linearRampToValueAtTime(1, now + fadeTime);

        // Update State
        this.activeDeck = this.activeDeck === 'A' ? 'B' : 'A';
        this.isPlaying = true; // Ensure state is playing

        // Cleanup Old Deck after fade
        setTimeout(() => {
            currentDeck.pause();
            currentDeck.src = ''; // Release resource
            // Ensure gain is strictly 0
            currentGain.gain.setValueAtTime(0, this.audioContext.currentTime);
        }, (fadeTime + 0.5) * 1000);
    }

    // Legacy Adapter for compatibility
    async setStreamUrl(url) {
        await this.crossfadeTo(url);
    }

    _getActiveDeck() {
        return this.activeDeck === 'A' ? this.deckA : this.deckB;
    }

    dispatchEvent(name, detail = {}) {
        window.dispatchEvent(new CustomEvent(name, { detail }));
    }
}
