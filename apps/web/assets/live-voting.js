// LIVE VOTING WIDGET - MTV-Style Track Voting
(function () {
    'use strict';

    // ========== CONFIGURATION ==========
    const CONFIG = {
        apiUrl: '/wp-json/yourparty/v1',
        backendUrl: '/wp-json/yourparty/v1', // WordPress proxy to FastAPI
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
            <style>
                .live-voting__track-cards {
                    display: grid;
                    grid-template-columns: repeat(3, 1fr);
                    gap: 15px;
                    margin: 15px 0;
                }
                .track-card {
                    background: rgba(255,255,255,0.05);
                    border-radius: 12px;
                    padding: 10px;
                    cursor: pointer;
                    transition: all 0.2s;
                    text-align: center;
                    border: 2px solid transparent;
                }
                .track-card:hover {
                    background: rgba(255,255,255,0.1);
                    transform: translateY(-2px);
                }
                .track-card--voted {
                    border-color: #00ff88;
                    box-shadow: 0 0 15px rgba(0, 255, 136, 0.2);
                }
                .track-card__cover {
                    position: relative;
                    width: 100%;
                    aspect-ratio: 1;
                    overflow: hidden;
                    border-radius: 8px;
                    margin-bottom: 8px;
                    background: #000;
                }
                .track-card__cover img {
                    width: 100%;
                    height: 100%;
                    object-fit: cover;
                }
                .track-card__title {
                    font-weight: bold;
                    font-size: 0.9rem;
                    white-space: nowrap;
                    overflow: hidden;
                    text-overflow: ellipsis;
                    color: #fff;
                }
                .track-card__artist {
                    font-size: 0.8rem;
                    color: #aaa;
                    white-space: nowrap;
                    overflow: hidden;
                    text-overflow: ellipsis;
                }
                .vote-count {
                    display: block;
                    font-size: 1.2rem;
                    font-weight: bold;
                    color: #00ff88;
                    margin-top: 5px;
                }
                .vote-label {
                    font-size: 0.7rem;
                    text-transform: uppercase;
                    opacity: 0.7;
                }
                @media (max-width: 600px) {
                    .live-voting__track-cards {
                        grid-template-columns: 1fr; /* Stack on mobile */
                    }
                    .track-card {
                        display: flex; /* Row layout on mobile list */
                        align-items: center;
                        text-align: left;
                        gap: 15px;
                    }
                    .track-card__cover {
                        width: 60px;
                        margin-bottom: 0;
                    }
                }
            </style>
            <div class="live-voting__header">
                <h3 class="live-voting__title">VOTE FOR NEXT TRACK</h3>
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
                        <img src="${coverArt}" alt="${track.title}" loading="lazy" onerror="handleImageError(this)" />
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

            // Check for backend error
            if (data.error) {
                console.warn('[LiveVoting] Backend returned error:', data.error);
                renderError('Voting temporarily unavailable');
                return;
            }

            state.candidates = data.candidates || [];
            state.votes = data.votes || {};

            console.log('[LiveVoting] Candidates loaded:', state.candidates);

            if (state.candidates.length === 0) {
                renderNoCandidates();
            } else {
                renderTrackCards();
            }
        } catch (error) {
            console.error('[LiveVoting] Failed to fetch candidates:', error);
            renderError('Could not load voting options');
        }
    }

    function renderError(message) {
        const cardsContainer = document.getElementById('track-cards');
        if (!cardsContainer) return;

        cardsContainer.innerHTML = `
            <div class="voting-error">
                <span class="voting-error__icon">⚠️</span>
                <span class="voting-error__message">${message}</span>
                <button class="voting-error__retry" onclick="window.dispatchEvent(new Event('retryVoting'))">Retry</button>
            </div>
        `;
    }

    function renderNoCandidates() {
        const cardsContainer = document.getElementById('track-cards');
        if (!cardsContainer) return;

        cardsContainer.innerHTML = '<div class="no-candidates">No candidates available right now. Check back soon!</div>';
    }

    // Allow retry from error state
    window.addEventListener('retryVoting', () => {
        renderTrackVotingUI();
        fetchCandidates();
    });

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
    function generateGradient(str) {
        let hash = 0;
        for (let i = 0; i < str.length; i++) {
            hash = str.charCodeAt(i) + ((hash << 5) - hash);
        }
        const c1 = `hsl(${hash % 360}, 70%, 50%)`;
        const c2 = `hsl(${(hash + 40) % 360}, 70%, 30%)`;
        return `linear-gradient(135deg, ${c1}, ${c2})`;
    }

    window.handleImageError = function (img) {
        const card = img.closest('.track-card');
        const title = card.querySelector('.track-card__title').innerText;
        const gradient = generateGradient(title);

        const wrapper = img.parentElement;
        wrapper.innerHTML = `<div style="width:100%; height:100%; background: ${gradient}; display:flex; align-items:center; justify-content:center; font-size:2rem; color:white; font-weight:bold;">${title.charAt(0)}</div>`;
    }

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
