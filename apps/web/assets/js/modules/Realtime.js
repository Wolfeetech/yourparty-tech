/**
 * Realtime Module (WebSockets)
 */
export default class RealtimeModule {
    constructor(config) {
        this.config = config;
        this.socket = null;
        this.reconnectAttempts = 0;
        this.subscribers = [];

        // Delay connection
        setTimeout(() => this.connect(), 500);
    }

    connect() {
        if (this.socket && (this.socket.readyState === WebSocket.CONNECTING || this.socket.readyState === WebSocket.OPEN)) return;

        // Dynamic URL based on config
        const slug = this.config.stationSlug || 'radio.yourparty';

        // Fix: Use the configured public base (AzuraCast) instead of local WP host
        let wsHost = window.location.host;

        // Smart fallback logic
        if (wsHost === 'yourparty.tech' || wsHost === 'www.yourparty.tech') {
            wsHost = 'radio.yourparty.tech';
        }

        if (this.config.publicBase) {
            try {
                const url = new URL(this.config.publicBase);
                if (url.host) wsHost = url.host;
            } catch (e) { }
        }

        const wsUrl = `wss://${wsHost}/ws/${slug}`;

        if (this.reconnectAttempts === 0) {
            // console.log('[Realtime] Connecting to ' + wsUrl);
        }

        try {
            this.socket = new WebSocket(wsUrl);
        } catch (e) {
            this.scheduleReconnect();
            return;
        }

        this.socket.onopen = () => {
            // console.log('[Realtime] Connected');
            this.reconnectAttempts = 0;
            // Send subscription/hello if needed
            this.socket.send(JSON.stringify({ "subs": { [slug]: {} } }));
        };

        this.socket.onmessage = (event) => {
            try {
                const msg = JSON.parse(event.data);
                this.handleMessage(msg);
            } catch (e) { } // Silent parse error
        };

        this.socket.onclose = () => {
            this.scheduleReconnect();
        };

        this.socket.onerror = (err) => {
            // Silence initial error to avoid noisy console if offline
            if (this.reconnectAttempts > 5) return;
            console.warn('[Realtime] WS Error');
        };
    }

    scheduleReconnect() {
        if (this.reconnectAttempts > 10) {
            // console.log('[Realtime] stopped retrying (Fallback to polling).');
            return;
        }

        const delay = Math.min(2000 * Math.pow(1.5, this.reconnectAttempts), 30000);
        this.reconnectAttempts++;
        setTimeout(() => this.connect(), delay);
    }

    handleMessage(msg) {
        // Dispatch to app or subscribers
        // For now, simple dispatch to window like original, or we could add subscriber system
        if (msg.type === 'song') {
            const songData = msg.song || msg.data;
            // Creating legacy event for compatibility
            window.dispatchEvent(new CustomEvent('songChange', {
                detail: { song: songData }
            }));
        }

        if (msg.type === 'steer') {
            console.log('[Realtime] Steer Update:', msg.data);
            window.dispatchEvent(new CustomEvent('steerChange', {
                detail: msg.data
            }));
        }

        if (msg.type === 'pulse') {
            // "Pulse" signal means "Go fetch fresh data for X"
            console.log('[Realtime] Pulse:', msg.target);
            window.dispatchEvent(new CustomEvent('pulse', {
                detail: msg.target
            }));
        }
    }

    /**
     * Switch to a different station's WebSocket room
     */
    switchStation(newSlug) {
        console.log(`[Realtime] Switching to station: ${newSlug}`);
        this.config.stationSlug = newSlug;

        // Close existing connection
        if (this.socket) {
            this.socket.close();
        }

        // Reset reconnect counter and connect to new room
        this.reconnectAttempts = 0;
        setTimeout(() => this.connect(), 100);
    }
}
