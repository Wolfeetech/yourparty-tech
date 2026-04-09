/**
 * Status Manager
 * Handles API Polling and Status State
 */

export default class StatusManager {
    constructor(config) {
        this.config = config;
        this.pollInterval = 5000;
        this.timer = null;
        this.subscribers = [];
        this.lastState = null;
    }

    start() {
        this.fetchStatus();
        this.timer = setInterval(() => this.fetchStatus(), this.pollInterval);
    }

    stop() {
        if (this.timer) clearInterval(this.timer);
    }

    subscribe(callback) {
        this.subscribers.push(callback);
    }

    notify(data) {
        this.subscribers.forEach(cb => cb(data));
    }

    async fetchStatus() {
        const endpoint = this.config.restBase ? `${this.config.restBase}/status` : '/status';
        try {
            const response = await fetch(endpoint);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);

            const data = await response.json();
            this.lastState = data;
            this.notify(data);
        } catch (err) {
            console.warn('[StatusManager] Fetch Error:', err);
        }
    }
}
