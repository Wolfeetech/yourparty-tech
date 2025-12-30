/**
 * YourParty.tech V2 - WebSocket Client Module
 * 
 * Provides persistent WebSocket connection with:
 * - Automatic reconnection with exponential backoff
 * - Event-based message handling
 * - Vote submission via WebSocket
 * - Bandcamp/affiliate link rendering
 */

const YPWebSocket = (function () {
    'use strict';

    // Configuration
    // Dynamic API Base for V2 Testing (Port 8001)
    const API_BASE = (window.location.port === '8001')
        ? 'http://localhost:8001' // V2 Backend Direct
        : ''; // Relative (V1 via Nginx)

    const CONFIG = {
        wsUrl: window.location.protocol === 'https:'
            ? `wss://${window.location.host}/ws/`
            : `ws://${window.location.host}/ws/`,
        reconnectBaseDelay: 1000,
        reconnectMaxDelay: 30000,
        reconnectMultiplier: 1.5,
        heartbeatInterval: 30000,
        stationId: '1'
    };

    // State
    let socket = null;
    let reconnectAttempts = 0;
    let heartbeatTimer = null;
    let listeners = new Map();

    // ========================================
    // CONNECTION MANAGEMENT
    // ========================================

    function connect(stationId) {
        if (stationId) CONFIG.stationId = stationId;

        if (socket && socket.readyState === WebSocket.OPEN) {
            console.log('[WS] Already connected');
            return;
        }

        const url = CONFIG.wsUrl + CONFIG.stationId;
        console.log('[WS] Connecting to:', url);

        try {
            socket = new WebSocket(url);

            socket.onopen = handleOpen;
            socket.onclose = handleClose;
            socket.onerror = handleError;
            socket.onmessage = handleMessage;
        } catch (e) {
            console.error('[WS] Connection failed:', e);
            scheduleReconnect();
        }
    }

    function disconnect() {
        if (heartbeatTimer) {
            clearInterval(heartbeatTimer);
            heartbeatTimer = null;
        }
        if (socket) {
            socket.close();
            socket = null;
        }
    }

    function handleOpen() {
        console.log('[WS] Connected');
        reconnectAttempts = 0;

        // Start heartbeat
        heartbeatTimer = setInterval(() => {
            if (socket && socket.readyState === WebSocket.OPEN) {
                socket.send('ping');
            }
        }, CONFIG.heartbeatInterval);

        emit('connected', {});
    }

    function handleClose(event) {
        console.log('[WS] Disconnected:', event.code, event.reason);

        if (heartbeatTimer) {
            clearInterval(heartbeatTimer);
            heartbeatTimer = null;
        }

        emit('disconnected', { code: event.code, reason: event.reason });

        // Auto-reconnect unless intentional close
        if (event.code !== 1000) {
            scheduleReconnect();
        }
    }

    function handleError(error) {
        console.error('[WS] Error:', error);
        emit('error', error);
    }

    function handleMessage(event) {
        try {
            const data = JSON.parse(event.data);

            // Route by message type
            switch (data.type) {
                case 'song':
                    handleSongUpdate(data.data || data.song);
                    break;
                case 'vote_update':
                    emit('vote_update', data.data);
                    break;
                case 'queue_update':
                    emit('queue_update', data.data);
                    break;
                default:
                    console.log('[WS] Unknown message type:', data.type);
            }

            emit('message', data);
        } catch (e) {
            console.error('[WS] Message parse error:', e);
        }
    }

    function scheduleReconnect() {
        const delay = Math.min(
            CONFIG.reconnectBaseDelay * Math.pow(CONFIG.reconnectMultiplier, reconnectAttempts),
            CONFIG.reconnectMaxDelay
        );

        reconnectAttempts++;
        console.log(`[WS] Reconnecting in ${delay}ms (attempt ${reconnectAttempts})`);

        setTimeout(() => connect(), delay);
    }

    // ========================================
    // SONG UPDATE HANDLING
    // ========================================

    function handleSongUpdate(song) {
        if (!song) return;

        // Update global state
        window.currentSongId = song.id;
        window.currentSong = song;

        // Update DOM elements
        updateTrackDisplay(song);
        updateAlbumArt(song.art);
        updateRatingDisplay(song.rating);
        updateMoodDisplay(song.top_mood);
        updateBandcampLink(song);

        emit('song', song);
    }

    function updateTrackDisplay(song) {
        const titleEl = document.getElementById('track-title');
        const artistEl = document.getElementById('track-artist');
        const albumEl = document.getElementById('track-album');

        if (titleEl) titleEl.textContent = song.title || 'Unknown';
        if (artistEl) artistEl.textContent = song.artist || 'Unknown Artist';
        if (albumEl) albumEl.textContent = song.album || '';
    }

    function updateAlbumArt(artUrl) {
        const artEl = document.getElementById('album-art');
        if (artEl && artUrl) {
            artEl.src = artUrl;
            artEl.style.opacity = '1';
        }
    }

    function updateRatingDisplay(rating) {
        const ratingEl = document.getElementById('track-rating');
        if (ratingEl && rating) {
            const avg = rating.average || 0;
            const stars = '★'.repeat(Math.round(avg)) + '☆'.repeat(5 - Math.round(avg));
            ratingEl.textContent = stars;
            ratingEl.setAttribute('data-rating', avg);
        }
    }

    function updateMoodDisplay(mood) {
        const moodEl = document.getElementById('track-mood');
        if (moodEl) {
            moodEl.textContent = mood ? `Mood: ${mood}` : '';
            moodEl.className = mood ? `mood-tag mood-${mood}` : 'mood-tag';
        }
    }

    function updateBandcampLink(song) {
        const container = document.getElementById('affiliate-links');
        if (!container) return;

        container.innerHTML = '';

        // Bandcamp link
        if (song.bandcamp_url) {
            const link = createAffiliateLink(song.bandcamp_url, 'Buy on Bandcamp', 'bandcamp');
            container.appendChild(link);
        }

        // Discogs link
        if (song.discogs_url) {
            const link = createAffiliateLink(song.discogs_url, 'View on Discogs', 'discogs');
            container.appendChild(link);
        }
    }

    function createAffiliateLink(url, text, type) {
        const link = document.createElement('a');
        link.href = url;
        link.target = '_blank';
        link.rel = 'noopener noreferrer';
        link.className = `affiliate-link affiliate-${type}`;
        link.innerHTML = `<span class="affiliate-icon"></span>${text}`;
        return link;
    }

    // ========================================
    // VOTE SUBMISSION
    // ========================================

    function sendVote(voteType, data) {
        if (!socket || socket.readyState !== WebSocket.OPEN) {
            console.warn('[WS] Not connected, falling back to REST');
            return sendVoteREST(voteType, data);
        }

        socket.send(JSON.stringify({
            type: 'vote',
            vote_type: voteType,
            ...data
        }));

        return Promise.resolve({ status: 'sent' });
    }

    async function sendVoteREST(voteType, data) {
        const endpoints = {
            mood_current: '/wp-json/yourparty/v1/vote-mood',
            mood_next: '/api/vote-mood-next',
            track: '/api/vote-track',
            rating: '/api/rate'
        };

        const url = API_BASE + (endpoints[voteType] || endpoints.mood_current);

        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        return response.json();
    }

    // ========================================
    // EVENT SYSTEM
    // ========================================

    function on(event, callback) {
        if (!listeners.has(event)) {
            listeners.set(event, []);
        }
        listeners.get(event).push(callback);
    }

    function off(event, callback) {
        if (listeners.has(event)) {
            const callbacks = listeners.get(event);
            const index = callbacks.indexOf(callback);
            if (index > -1) {
                callbacks.splice(index, 1);
            }
        }
    }

    function emit(event, data) {
        if (listeners.has(event)) {
            listeners.get(event).forEach(callback => {
                try {
                    callback(data);
                } catch (e) {
                    console.error(`[WS] Event handler error (${event}):`, e);
                }
            });
        }
    }

    // ========================================
    // PUBLIC API
    // ========================================

    return {
        connect,
        disconnect,
        on,
        off,
        send: (data) => socket && socket.send(JSON.stringify(data)),
        sendVote,
        isConnected: () => socket && socket.readyState === WebSocket.OPEN,

        // Convenience vote methods
        voteMood: (mood, songId) => sendVote('mood_current', {
            mood_current: mood,
            song_id: songId || window.currentSongId
        }),
        voteMoodNext: (mood) => sendVote('mood_next', { mood_next: mood }),
        voteTrack: (songId) => sendVote('track', { song_id: songId }),
        submitRating: (rating, songId) => sendVote('rating', {
            rating,
            song_id: songId || window.currentSongId
        })
    };
})();

// Auto-connect when DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        YPWebSocket.connect();
    });
} else {
    YPWebSocket.connect();
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = YPWebSocket;
}
