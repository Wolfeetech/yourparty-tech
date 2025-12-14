/**
 * YourParty Tech - Frontend Entry Point
 */
import MoodModule from './modules/MoodModule.js';
import StatusManager from './modules/StatusManager.js';
import PlayerControls from './modules/PlayerControls.js';
import RealtimeModule from './modules/Realtime.js';
import VisualEngine from './modules/VisualEngine.js';
import StreamController from './modules/StreamController.js';
import RatingModule from './modules/RatingModule.js';
import FullscreenManager from './modules/FullscreenManager.js';
import ContactModule from './modules/ContactModule.js';

console.log('[Main] Initializing YourParty Frontend...');

class YourPartyApp {
    constructor() {
        // Window Global Config (PHP injection)
        this.config = window.YourPartyConfig || { restBase: '/wp-json/yourparty/v1' };

        this.state = {
            currentSong: null,
            isConnected: false
        };

        // Initialize Core State Managers
        const status = new StatusManager(this.config);
        const stream = new StreamController(this.config);
        const visualEngine = new VisualEngine(); // Professional Engine

        this.modules = {
            status: status,
            stream: stream,
            player: new PlayerControls(),
            mood: new MoodModule(this.config),
            rating: new RatingModule(this.config),
            realtime: new RealtimeModule(this.config),
            visuals: visualEngine,
            fullscreen: new FullscreenManager(),
            contact: new ContactModule(this.config)
        };

        this.init();
    }

    init() {
        // Stream -> Visuals binding
        window.addEventListener('stream:audioContextReady', (e) => {
            // Initialize main visualizer on the inline canvas
            const inlineCanvas = document.getElementById('inline-visualizer') || document.getElementById('audio-visualizer');
            if (inlineCanvas) {
                this.modules.visuals.init(inlineCanvas, e.detail.analyser);
            } else {
                this.modules.visuals.setAnalyser(e.detail.analyser);
            }
        });

        // Fullscreen integration
        this.modules.fullscreen.init(this.modules.visuals, this.modules.stream);

        // Connect Status Manager to other modules
        this.modules.status.subscribe((data) => {
            this.handleStatusUpdate(data);
        });

        this.modules.status.start();

        console.log('[Main] App Ready');

        // Expose for debugging/legacy
        window.YourPartyAppInstance = this;
    }

    handleStatusUpdate(data) {
        if (!data) return;

        const song = data.now_playing?.song;
        if (song) {
            this.state.currentSong = song;

            // Notify Modules
            this.modules.player.update(data);
            this.modules.mood.setCurrentSong(song.id, song.moods);

            // Legacy Globals
            window.currentSongId = song.id;
            window.currentTrackInfo = song;

            this.modules.rating.setInitialRating(
                song.id,
                data.now_playing.song.rating?.average,
                data.now_playing.song.rating?.total
            );

            // Fix Station Loading Bug by verifying we have real data
            if (song.title === 'Unknown Title' && !data.is_live && !data.now_playing?.song?.id) {
                // Keep default state or show "Offline"
            }
        }
    }

    // Bridge for legacy interactions if needed
    get currentSongId() {
        return this.state.currentSong?.id || '0';
    }
}

// Start
document.addEventListener('DOMContentLoaded', () => {
    window.YourPartyApp = new YourPartyApp();
});
