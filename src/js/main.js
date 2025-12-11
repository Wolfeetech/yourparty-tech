/**
 * YourParty Tech - Frontend Entry Point
 */
import MoodModule from './modules/MoodModule.js';
// We will import other modules as we create them
// import StatusManager from './modules/StatusManager.js';
import PlayerControls from './modules/PlayerControls.js';
import RealtimeModule from './modules/Realtime.js';
import Visualizer from './modules/Visualizer.js';
import StreamController from './modules/StreamController.js';

console.log('[Main] Initializing YourParty Frontend...');

class YourPartyApp {
    constructor() {
        // Window Global Config (PHP injection)
        this.config = window.YourPartyConfig || { restBase: '/wp-json/yourparty/v1' };

        this.state = {
            currentSong: null,
            isConnected: false
        };

        this.modules = {
            mood: new MoodModule(this.config),
            status: new StatusManager(this.config),
            player: new PlayerControls(),
            realtime: new RealtimeModule(this.config),
            visualizer: new Visualizer(),
            stream: new StreamController(this.config)
        };

        this.init();
    }

    init() {
        // Connect Status Manager to other modules
        this.modules.status.subscribe((data) => {
            this.handleStatusUpdate(data);
        });

        this.modules.status.start();

        // Global Error Handler
        window.onclick = () => {
            // Unlock Audio Context if needed
        };

        console.log('[Main] App Ready');

        // Expose for debugging
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

            // Fix Station Loading Bug by verifying we have real data
            if (song.title === 'Unknown Title' && !data.is_live) {
                // Keep loading state? No, render what we have.
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
