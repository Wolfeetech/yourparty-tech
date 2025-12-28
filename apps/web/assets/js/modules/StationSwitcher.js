/**
 * YourParty Station Switcher Module
 * Orchestrates switching between radio stations with seamless audio transition
 */

export default class StationSwitcher {
    constructor(config = {}) {
        this.config = config;
        this.streamController = config.streamController;
        this.realtimeModule = config.realtimeModule;

        // Station definitions
        this.stations = [
            {
                id: 1,
                name: 'YourParty Radio',
                shortName: 'Radio',
                stream: config.streamUrls?.[1] || 'https://radio.yourparty.tech/radio.mp3',
                slug: 'radio.yourparty',
                icon: '📻'
            },
            {
                id: 2,
                name: 'Mixtapes',
                shortName: 'Mixtapes',
                stream: config.streamUrls?.[2] || 'https://radio.yourparty.tech/radio2.mp3',
                slug: 'radio2.yourparty',
                icon: '💿'
            }
        ];

        // State
        this.currentStation = this.loadSavedStation();
        this.isTransitioning = false;

        // API config
        this.apiBase = config.apiBase || '/api';

        this.init();
    }

    init() {
        this.bindUI();
        this.updateUI();
        console.log(`[StationSwitcher] Initialized on Station ${this.currentStation}`);
    }

    /**
     * Load saved station from localStorage or default to 1
     */
    loadSavedStation() {
        try {
            const saved = localStorage.getItem('yourparty_station');
            if (saved) {
                const id = parseInt(saved, 10);
                if (this.stations.find(s => s.id === id)) {
                    return id;
                }
            }
        } catch (e) { /* localStorage unavailable */ }
        return 1;
    }

    /**
     * Save station preference
     */
    saveStation(stationId) {
        try {
            localStorage.setItem('yourparty_station', stationId.toString());
        } catch (e) { /* localStorage unavailable */ }
    }

    /**
     * Get current station config
     */
    getCurrentStation() {
        return this.stations.find(s => s.id === this.currentStation) || this.stations[0];
    }

    /**
     * Get station by ID
     */
    getStation(id) {
        return this.stations.find(s => s.id === id);
    }

    /**
     * Switch to a different station
     */
    async switchTo(stationId) {
        if (stationId === this.currentStation || this.isTransitioning) {
            return;
        }

        const newStation = this.getStation(stationId);
        if (!newStation) {
            console.error(`[StationSwitcher] Unknown station: ${stationId}`);
            return;
        }

        console.log(`[StationSwitcher] Switching to ${newStation.name}`);
        this.isTransitioning = true;

        try {
            // 1. Update stream URL
            if (this.streamController?.setStreamUrl) {
                await this.streamController.setStreamUrl(newStation.stream);
            }

            // 2. Reconnect WebSocket to new room
            if (this.realtimeModule?.switchStation) {
                this.realtimeModule.switchStation(newStation.slug);
            }

            // 3. Fetch new station status
            await this.fetchStationStatus(stationId);

            // 4. Update state
            this.currentStation = stationId;
            this.saveStation(stationId);

            // 5. Update UI
            this.updateUI();

            // 6. Dispatch event for other modules
            window.dispatchEvent(new CustomEvent('stationChange', {
                detail: { station: newStation }
            }));

            console.log(`[StationSwitcher] Switched to ${newStation.name}`);

        } catch (error) {
            console.error('[StationSwitcher] Switch failed:', error);
        } finally {
            this.isTransitioning = false;
        }
    }

    /**
     * Fetch status for a specific station
     */
    async fetchStationStatus(stationId) {
        try {
            const response = await fetch(`${this.apiBase}/status?station_id=${stationId}`);
            if (response.ok) {
                const data = await response.json();
                // Dispatch status update event
                if (data.now_playing?.song) {
                    window.dispatchEvent(new CustomEvent('songChange', {
                        detail: { song: data.now_playing.song }
                    }));
                }
                return data;
            }
        } catch (error) {
            console.warn('[StationSwitcher] Status fetch failed:', error);
        }
        return null;
    }

    /**
     * Bind UI event handlers
     */
    bindUI() {
        // Station switcher buttons
        document.querySelectorAll('[data-station]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const stationId = parseInt(btn.dataset.station, 10);
                this.switchTo(stationId);
            });
        });
    }

    /**
     * Update UI to reflect current station
     */
    updateUI() {
        const current = this.getCurrentStation();

        // Update button states
        document.querySelectorAll('[data-station]').forEach(btn => {
            const id = parseInt(btn.dataset.station, 10);
            btn.classList.toggle('active', id === this.currentStation);
            btn.setAttribute('aria-pressed', id === this.currentStation ? 'true' : 'false');
        });

        // Update station name display
        const nameEl = document.querySelector('.station-name');
        if (nameEl) {
            nameEl.textContent = current.shortName;
        }

        // Update document title
        document.title = `${current.shortName} | YourParty`;
    }
}
