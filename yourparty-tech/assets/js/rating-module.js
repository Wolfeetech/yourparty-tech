/**
 * YourParty Rating Module
 * Best Practice ES6 Module for star ratings
 */

const RatingModule = (function () {
    'use strict';

    // Configuration
    const CONFIG = {
        apiEndpoint: (window.YourPartyConfig && window.YourPartyConfig.restBase)
            ? window.YourPartyConfig.restBase + '/rate'
            : 'https://api.yourparty.tech/rate',
        selectors: {
            container: '.rating-container',
            stars: '.rating-stars',
            star: '.rating-star',
            average: '.rating-average',
            total: '.rating-total',
            feedback: '.rating-feedback'
        },
        classes: {
            active: 'active',
            hover: 'hover',
            loading: 'loading',
            success: 'success',
            error: 'error'
        },
        animation: {
            duration: 300,
            delay: 50
        }
    };

    // State
    let currentSongId = null;
    let currentRating = 0;
    let isSubmitting = false;

    /**
     * Initialize rating system
     */
    function init() {
        // Query ALL containers (inline + fullscreen)
        const containers = document.querySelectorAll(CONFIG.selectors.container);
        if (containers.length === 0) return;

        containers.forEach(container => bindEvents(container));

        // Listen for song changes (Best Practice)
        window.addEventListener('songChange', (e) => {
            if (e.detail && e.detail.song) {
                setNewSong(e.detail.song.id);
            }
        });

        // Use global ID if already set
        if (window.currentSongId) {
            setNewSong(window.currentSongId);
        }

        console.log('[RatingModule] Initialized ' + containers.length + ' instances');
    }

    function setNewSong(id) {
        if (currentSongId !== id) {
            currentSongId = id;
            currentRating = 0;
            resetStars();
        }
    }

    // Removed observeSongChanges() hack

    /**
     * Bind event listeners for a specific container
     */
    function bindEvents(container) {
        const stars = container.querySelectorAll(CONFIG.selectors.star);

        stars.forEach((star, index) => {
            // Click to rate
            star.addEventListener('click', (e) => {
                e.preventDefault();
                handleRate(index + 1);
            });

            // Hover preview - Update ALL containers to sync hover state
            star.addEventListener('mouseenter', () => highlightGlobal(index + 1, true));
            star.addEventListener('mouseleave', () => highlightGlobal(currentRating, false));

            // Keyboard support
            star.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    handleRate(index + 1);
                }
            });
        });
    }

    /**
     * Highlight stars across ALL containers
     */
    function highlightGlobal(count, isHover) {
        document.querySelectorAll(CONFIG.selectors.container).forEach(container => {
            highlightStars(container, count, isHover);
        });
    }

    /**
     * Highlight stars in one container
     */
    function highlightStars(container, count, isHover) {
        const stars = container.querySelectorAll(CONFIG.selectors.star);

        stars.forEach((star, index) => {
            if (index < count) {
                star.classList.add(isHover ? CONFIG.classes.hover : CONFIG.classes.active);
            } else {
                star.classList.remove(CONFIG.classes.hover, CONFIG.classes.active);
            }
        });
    }

    /**
     * Handle rating submission
     */
    async function handleRate(rating) {
        if (isSubmitting || !currentSongId) return;

        isSubmitting = true;

        // Show loading on all containers
        const containers = document.querySelectorAll(CONFIG.selectors.container);
        containers.forEach(c => c.classList.add(CONFIG.classes.loading));

        try {
            const response = await fetch(CONFIG.apiEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    song_id: currentSongId,
                    rating: rating,
                    vote: null,
                    // Send metadata to ensure DB sync
                    title: document.getElementById('track-title')?.innerText || '',
                    artist: document.getElementById('track-artist')?.innerText || ''
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const data = await response.json();

            // Update State
            currentRating = rating;

            // Sync UI everywhere
            highlightGlobal(rating, false);
            updateDisplay(data.ratings?.average, data.ratings?.total);

            // Show Feedback & Animate on all instances
            containers.forEach(container => {
                showFeedback(container, 'Danke!', 'success');
                animateStars(container, rating);
            });

            // Dispatch event for other modules
            window.dispatchEvent(new CustomEvent('rating:saved', { detail: { rating } }));

        } catch (error) {
            console.error('[RatingModule] Error:', error);
            containers.forEach(c => showFeedback(c, 'Fehler', 'error'));
        } finally {
            isSubmitting = false;
            containers.forEach(c => c.classList.remove(CONFIG.classes.loading));
        }
    }

    /**
     * Update rating display text globally
     */
    function updateDisplay(average, total) {
        const avgEls = document.querySelectorAll(CONFIG.selectors.average);
        const totalEls = document.querySelectorAll(CONFIG.selectors.total);

        if (average !== undefined) {
            avgEls.forEach(el => {
                el.textContent = average.toFixed(1);
                el.setAttribute('aria-label', `Durchschnitt: ${average.toFixed(1)} Sterne`);
            });
        }

        if (total !== undefined) {
            const text = total === 1 ? '1 Bewertung' : `${total} Bewertungen`;
            totalEls.forEach(el => el.textContent = `(${text})`);
        }
    }

    /**
     * Show feedback message inside a container
     */
    function showFeedback(container, message, type) {
        let feedback = container.querySelector(CONFIG.selectors.feedback);

        if (!feedback) {
            feedback = document.createElement('div');
            feedback.className = 'rating-feedback';
            container.appendChild(feedback);
        }

        feedback.textContent = message;
        feedback.className = `rating-feedback ${type}`;

        // Ensure visible
        feedback.style.opacity = '1';

        // Auto-hide
        setTimeout(() => {
            feedback.style.opacity = '0';
        }, 3000);
    }

    /**
     * Animate stars
     */
    function animateStars(container, rating) {
        const stars = container.querySelectorAll(CONFIG.selectors.star);

        stars.forEach((star, index) => {
            if (index < rating) {
                setTimeout(() => {
                    star.classList.add('just-rated');
                    setTimeout(() => star.classList.remove('just-rated'), CONFIG.animation.duration);
                }, index * CONFIG.animation.delay);
            }
        });
    }

    function observeSongChanges() {
        if (typeof window !== 'undefined') {
            const desc = Object.getOwnPropertyDescriptor(window, 'currentSongId');
            if (!desc || desc.configurable) {
                Object.defineProperty(window, 'currentSongId', {
                    get: () => currentSongId,
                    set: (value) => {
                        if (value !== currentSongId) {
                            currentSongId = value;
                            currentRating = 0;
                            resetStars();
                        }
                    },
                    configurable: true
                });
            }
        }
    }

    function resetStars() {
        document.querySelectorAll(CONFIG.selectors.container).forEach(container => {
            const stars = container.querySelectorAll(CONFIG.selectors.star);
            stars.forEach(star => {
                star.classList.remove(CONFIG.classes.active, CONFIG.classes.hover);
            });
        });
        updateDisplay(null, null);
    }

    function setInitialRating(songId, average, total, userRating = 0) {
        currentSongId = songId;
        currentRating = userRating;
        highlightGlobal(userRating, false);
        updateDisplay(average, total);
    }

    // Public API
    const instance = {
        init,
        setInitialRating,
        updateDisplay, // Made public for WS
        setCurrentSong: (id) => { currentSongId = id; }
    };
    window.RatingModule = instance;
    return instance;
})();

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = RatingModule;
}
