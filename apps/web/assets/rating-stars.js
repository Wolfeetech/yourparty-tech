// RATING STARS - VISUAL FEEDBACK & UX
(function () {
    const stars = document.querySelectorAll('.rating-star');
    const feedbackEl = document.querySelector('.rating-feedback') || createFeedbackElement();
    let selectedRating = 0;

    function createFeedbackElement() {
        const el = document.createElement('div');
        el.className = 'rating-feedback';
        const ratingsContainer = document.querySelector('.radio-card__ratings');
        if (ratingsContainer) {
            ratingsContainer.appendChild(el);
        }
        return el;
    }

    // Hover effect - highlight stars up to hovered star
    stars.forEach((star, index) => {
        star.addEventListener('mouseenter', () => {
            highlightStars(index + 1);
        });

        star.addEventListener('mouseleave', () => {
            highlightStars(selectedRating);
        });

        star.addEventListener('click', async () => {
            const value = parseInt(star.dataset.value);

            // Visual feedback immediately
            star.classList.add('selected');
            setTimeout(() => star.classList.remove('selected'), 300);

            selectedRating = value;
            highlightStars(value);

            if (feedbackEl) {
                feedbackEl.textContent = 'Sende Bewertung...';
                feedbackEl.className = 'rating-feedback';
            }

            // Check if we have a song ID
            if (!window.currentSongId) {
                if (feedbackEl) {
                    feedbackEl.textContent = '⚠️ Kein Track aktiv';
                    feedbackEl.className = 'rating-feedback error';
                }
                setTimeout(() => {
                    if (feedbackEl) feedbackEl.textContent = '';
                }, 3000);
                return;
            }

            // Send to API
            try {
                const response = await fetch('/wp-json/yourparty/v1/rate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        song_id: window.currentSongId,
                        rating: value,
                        vote: value >= 4 ? 'like' : value <= 2 ? 'dislike' : 'neutral'
                    })
                });

                if (!response.ok) throw new Error('API Error');

                const result = await response.json();

                if (feedbackEl) {
                    feedbackEl.textContent = `✓ Bewertung gespeichert (${value}/5)`;
                    feedbackEl.className = 'rating-feedback success';
                }

                // Show average if available
                if (result.ratings && result.ratings.average) {
                    setTimeout(() => {
                        if (feedbackEl) {
                            feedbackEl.textContent = `Ø ${result.ratings.average.toFixed(1)}/5 (${result.ratings.total || 1} Bewertungen)`;
                        }
                    }, 2000);
                }

            } catch (error) {
                console.error('Rating error:', error);
                if (feedbackEl) {
                    feedbackEl.textContent = '❌ Fehler beim Speichern';
                    feedbackEl.className = 'rating-feedback error';
                }
            }

            // Clear feedback after 5s
            setTimeout(() => {
                if (feedbackEl && !feedbackEl.textContent.includes('Ø')) {
                    feedbackEl.textContent = '';
                }
            }, 5000);
        });
    });

    function highlightStars(count) {
        stars.forEach((star, index) => {
            if (index < count) {
                star.classList.add('active');
                star.setAttribute('aria-checked', 'true');
            } else {
                star.classList.remove('active');
                star.setAttribute('aria-checked', 'false');
            }
        });
    }
})();
