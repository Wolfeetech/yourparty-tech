/**
 * Community Steering Module
 * Handles "Vote Next Vibe" interactions.
 */

document.addEventListener('DOMContentLoaded', () => {
    const buttons = document.querySelectorAll('.vibe-btn');
    const feedback = document.getElementById('vibe-feedback');

    buttons.forEach(btn => {
        btn.addEventListener('click', async () => {
            const vote = btn.dataset.vote;
            if (!vote) return;

            // Optimistic UI
            buttons.forEach(b => b.classList.remove('selected'));
            btn.classList.add('selected');

            try {
                // Use Python API
                const response = await fetch('https://api.yourparty.tech/vote-next', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ vote: vote })
                });

                if (response.ok) {
                    const data = await response.json();
                    feedback.innerHTML = `VOTE REGISTERED: ${vote.toUpperCase()}!<br>`;

                    if (data.prediction) {
                        feedback.innerHTML += `<small>Coming up: <strong>${data.prediction.title}</strong></small>`;
                    }

                    feedback.className = 'vibe-feedback success';

                    // Simple rate limit visual
                    buttons.forEach(b => b.disabled = true);
                    setTimeout(() => {
                        buttons.forEach(b => b.disabled = false);
                        feedback.textContent = '';
                    }, 5000);
                } else {
                    throw new Error('Vote failed');
                }
            } catch (e) {
                feedback.textContent = 'ERROR SUBMITTING VOTE';
                feedback.className = 'vibe-feedback error';
            }
        });
    });
});
