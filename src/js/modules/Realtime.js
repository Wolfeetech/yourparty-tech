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

        // Use dynamic host or default
        const wsUrl = 'wss://yourparty.tech/ws/logrmp';
        console.log('[Realtime] Connecting to ' + wsUrl);

        try {
            this.socket = new WebSocket(wsUrl);
        } catch (e) {
            console.warn('[Realtime] Init Error', e);
            this.scheduleReconnect();
            return;
        }

        this.socket.onopen = () => {
            console.log('[Realtime] Connected');
            this.reconnectAttempts = 0;
        };

        this.socket.onmessage = (event) => {
            try {
                const msg = JSON.parse(event.data);
                this.handleMessage(msg);
            } catch (e) { console.warn('[Realtime] Parse error', e); }
        };

        this.socket.onclose = () => {
            this.scheduleReconnect();
        };

        this.socket.onerror = () => { };
    }

    scheduleReconnect() {
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
