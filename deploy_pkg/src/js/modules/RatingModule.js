/**
 * YourParty Rating Module
 */
export default class RatingModule {
    constructor(config) {
        this.config = config;
        this.currentSongId = null;
        this.currentRating = 0;
        this.isSubmitting = false;

        this.SELECTORS = {
            container: '.rating-container',
            stars: '.rating-stars',
            star: '.rating-star',
            average: '.rating-average',
            total: '.rating-total',
            feedback: '.rating-feedback'
        };

        this.init();
    }

    init() {
        // Event Delegation
        document.body.addEventListener('click', (e) => {
            const star = e.target.closest(this.SELECTORS.star);
            if (!star) return;

            e.preventDefault();
            const container = star.closest(this.SELECTORS.container);
            if (!container) return;

            const stars = Array.from(container.querySelectorAll(this.SELECTORS.star));
            const index = stars.indexOf(star);

            if (index !== -1) {
                this.handleRate(index + 1);
            }
        });

        // Hover Effects
        document.body.addEventListener('mouseover', (e) => {
            const star = e.target.closest(this.SELECTORS.star);
            if (star) {
                const container = star.closest(this.SELECTORS.container);
                if (container) {
                    const stars = Array.from(container.querySelectorAll(this.SELECTORS.star));
                    const index = stars.indexOf(star);
                    this.highlightGlobal(index + 1, true);
                }
            }
        });

        document.body.addEventListener('mouseout', (e) => {
            if (e.target.closest(this.SELECTORS.star)) {
                this.highlightGlobal(this.currentRating, false);
            }
        });

        console.log('[RatingModule] Initialized (ES6)');
    }

    setInitialRating(songId, average, total, userRating = 0) {
        this.currentSongId = songId;
        this.currentRating = userRating;
        this.highlightGlobal(userRating, false);
        this.updateDisplay(average, total);
    }

    highlightGlobal(count, isHover) {
        document.querySelectorAll(this.SELECTORS.container).forEach(container => {
            const stars = container.querySelectorAll(this.SELECTORS.star);
            stars.forEach((star, index) => {
                if (index < count) {
                    star.classList.add(isHover ? 'hover' : 'active');
                } else {
                    star.classList.remove('hover', 'active');
                }
            });
        });
    }

    updateDisplay(average, total) {
        const avgEls = document.querySelectorAll(this.SELECTORS.average);
        const totalEls = document.querySelectorAll(this.SELECTORS.total);

        if (average != null) {
            avgEls.forEach(el => el.textContent = Number(average).toFixed(1));
        }
        if (total != null) {
            const t = total === 1 ? '1 vote' : `${total} votes`;
            totalEls.forEach(el => el.textContent = `(${t})`);
        }
    }

    async handleRate(rating) {
        if (this.isSubmitting || !this.currentSongId) return;
        this.isSubmitting = true;

        const containers = document.querySelectorAll(this.SELECTORS.container);
        containers.forEach(c => c.classList.add('loading'));

        try {
            const baseUrl = this.config.restBase || '/api';
            const response = await fetch(`${baseUrl}/rate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    song_id: this.currentSongId,
                    rating: rating,
                    // optional metadata
                    title: document.getElementById('track-title')?.textContent,
                    artist: document.getElementById('track-artist')?.textContent
                })
            });

            if (!response.ok) throw new Error('Rating failed');

            const data = await response.json();

            this.currentRating = rating;
            this.highlightGlobal(rating, false);
            this.updateDisplay(data.ratings?.average, data.ratings?.total);

            // Visual success
            containers.forEach(c => {
                this.showFeedback(c, 'Thanks!', 'success');
                this.animateStars(c, rating);
            });

        } catch (e) {
            console.error(e);
            containers.forEach(c => this.showFeedback(c, 'Error', 'error'));
        } finally {
            this.isSubmitting = false;
            containers.forEach(c => c.classList.remove('loading'));
        }
    }

    showFeedback(container, msg, type) {
        // Reuse or create feedback element logic
        // Simplified for brevity
        const el = document.createElement('div');
        el.className = `rating-msg ${type}`;
        el.textContent = msg;
        el.style.position = 'absolute';
        el.style.top = '-20px'; // Pop up
        el.style.right = '0';
        el.style.color = type === 'success' ? '#10b981' : '#ef4444';
        el.style.fontWeight = 'bold';
        el.style.fontSize = '0.8rem';

        container.style.position = 'relative';
        container.appendChild(el);
        setTimeout(() => el.remove(), 2000);
    }

    animateStars(container, count) {
        const stars = container.querySelectorAll(this.SELECTORS.star);
        stars.forEach((s, i) => {
            if (i < count) {
                s.style.transform = 'scale(1.2)';
                setTimeout(() => s.style.transform = 'scale(1)', 200);
            }
        });
    }
}
