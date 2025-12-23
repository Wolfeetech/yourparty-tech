// LIVE VOTING WIDGET - MTV-Style Track Voting
(function () {
    'use strict';

    // ========== CONFIGURATION ==========
    const CONFIG = {
        apiUrl: '/wp-json/yourparty/v1',
        backendUrl: 'https://yourparty.tech', // Proxy to FastAPI
        pollInterval: 5000, // Poll for vote updates
        mode: 'track_voting' // 'track_voting' or 'vibe_tagging'
    };

    // ========== STATE ==========
    const state = {
        widgetEl: null,
        candidates: [],
        votes: {},
        userVoted: false,
        votedTrackId: null
    };

    // ========== INITIALIZATION ==========
    function init() {
        const container = document.querySelector('.live-voting-widget');
        if (!container) {
            console.warn('[LiveVoting] Widget container not found');
            return;
        }

        state.widgetEl = container;

        // Render initial UI
        renderTrackVotingUI();

        // Fetch candidates
        fetchCandidates();

        // Start polling for vote updates
        setInterval(fetchVoteUpdates, CONFIG.pollInterval);
    }

    // ========== UI RENDERING ==========
    function renderTrackVotingUI() {
        state.widgetEl.innerHTML = `
            <div class="live-voting__header">
                <h3 class="live-voting__title">🎵 VOTE FOR NEXT TRACK</h3>
                <span class="live-voting__status">LIVE</span>
            </div>
            <div class="live-voting__track-cards" id="track-cards">
                <div class="loading-skeleton">Loading candidates...</div>
            </div>
            <div class="live-voting__footer">
                <small>New candidates every 3 minutes</small>
            </div>
        `;
    }

    function renderTrackCards() {
        const cardsContainer = document.getElementById('track-cards');
        if (!cardsContainer) return;

        if (!state.candidates.length) {
            cardsContainer.innerHTML = '<div class="no-candidates">No candidates available</div>';
            return;
        }

        cardsContainer.innerHTML = state.candidates.map(track => {
            const voteCount = state.votes[track.id] || 0;
            const isVoted = state.votedTrackId === track.id;
            const coverArt = track.cover_art || 'https://placehold.co/300x300/1a1a1a/00ff88?text=♪';

            return `
                <div class="track-card ${isVoted ? 'track-card--voted' : ''}" data-track-id="${track.id}">
                    <div class="track-card__cover">
                        <img src="${coverArt}" alt="${track.title}" loading="lazy" />
                        ${isVoted ? '<div class="track-card__voted-badge">✓ VOTED</div>' : ''}
                    </div>
                    <div class="track-card__info">
                        <div class="track-card__title">${track.title}</div>
                        <div class="track-card__artist">${track.artist}</div>
                    </div>
                    <div class="track-card__votes">
                        <span class="vote-count">${voteCount}</span>
                        <span class="vote-label">votes</span>
                    </div>
                </div>
            `;
        }).join('');

        // Attach click handlers
        cardsContainer.querySelectorAll('.track-card').forEach(card => {
            card.addEventListener('click', handleTrackVote);
        });
    }

    // ========== API CALLS ==========
    async function fetchCandidates() {
        try {
            const response = await fetch(`${CONFIG.backendUrl}/vote-next-candidates`);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);

            const data = await response.json();
            state.candidates = data.candidates || [];
            state.votes = data.votes || {};

            console.log('[LiveVoting] Candidates loaded:', state.candidates);
            renderTrackCards();
        } catch (error) {
            console.error('[LiveVoting] Failed to fetch candidates:', error);
        }
    }

    async function fetchVoteUpdates() {
        if (!state.candidates.length) return;

        try {
            const response = await fetch(`${CONFIG.backendUrl}/vote-next-candidates`);
            if (!response.ok) return;

            const data = await response.json();
            state.votes = data.votes || {};

            // Update vote counts in UI
            updateVoteCounts();
        } catch (error) {
            console.error('[LiveVoting] Failed to fetch vote updates:', error);
        }
    }

    function updateVoteCounts() {
        const cardsContainer = document.getElementById('track-cards');
        if (!cardsContainer) return;

        cardsContainer.querySelectorAll('.track-card').forEach(card => {
            const trackId = card.dataset.trackId;
            const voteCount = state.votes[trackId] || 0;
            const voteCountEl = card.querySelector('.vote-count');
            if (voteCountEl) {
                voteCountEl.textContent = voteCount;
            }
        });
    }

    async function handleTrackVote(event) {
        const card = event.currentTarget;
        const trackId = card.dataset.trackId;

        // Prevent multiple votes
        if (state.userVoted) {
            showToast('You already voted!', 'warning');
            return;
        }

        try {
            const response = await fetch(`${CONFIG.backendUrl}/vote-next-track`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ track_id: trackId })
            });

            if (!response.ok) throw new Error(`HTTP ${response.status}`);

            const result = await response.json();

            // Update local state
            state.userVoted = true;
            state.votedTrackId = trackId;
            state.votes = result.current_votes;

            // Re-render to show voted state
            renderTrackCards();

            showToast('Vote submitted! 🎉', 'success');
        } catch (error) {
            console.error('[LiveVoting] Vote failed:', error);
            showToast('Vote failed. Try again.', 'error');
        }
    }

    // ========== UTILITIES ==========
    function showToast(message, type = 'info') {
        // Use existing toast system if available
        if (window.showToast) {
            window.showToast(type === 'success' ? 'Success' : 'Notice', message);
        } else {
            console.log(`[Toast] ${message}`);
        }
    }

    // ========== STARTUP ==========
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
