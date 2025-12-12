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

        // Dynamic URL based on config or host
        const slug = this.config.stationSlug || 'logrmp'; // Fallback
        const host = window.location.host;
        const wsUrl = `wss://${host}/ws/${slug}`;

        if (this.reconnectAttempts === 0) {
            console.log('[Realtime] Connecting to ' + wsUrl);
        }

        try {
            this.socket = new WebSocket(wsUrl);
        } catch (e) {
            this.scheduleReconnect();
            return;
        }

        this.socket.onopen = () => {
            console.log('[Realtime] Connected');
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
            console.log('[Realtime] stopped retrying (Fallback to polling).');
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
    }
}
