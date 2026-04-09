/**
 * YourParty Shoutout Module
 * Allows users to send shoutouts/messages to the studio.
 */
export default class ShoutoutModule {
    constructor(config) {
        this.config = config;
        this.dialog = document.getElementById('shoutout-dialog');
        this.form = document.getElementById('shoutout-form');
        this.openBtn = document.getElementById('open-shoutout-btn');
        this.closeBtn = document.getElementById('close-shoutout-btn');
        this.feedback = document.getElementById('shoutout-feedback');

        this.init();
    }

    init() {
        if (!this.dialog || !this.form) return;

        // Open/Close handlers
        if (this.openBtn) {
            this.openBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.open();
            });
        }

        if (this.closeBtn) {
            this.closeBtn.addEventListener('click', () => this.close());
        }

        // Close on outside click
        this.dialog.addEventListener('click', (e) => {
            if (e.target === this.dialog) this.close();
        });

        // Form Submission
        this.form.addEventListener('submit', (e) => this.handleSubmit(e));
    }

    open() {
        this.dialog.classList.add('active');
        this.dialog.setAttribute('aria-hidden', 'false');
        // Auto focus textarea
        const textarea = this.form.querySelector('textarea');
        if (textarea) setTimeout(() => textarea.focus(), 100);
    }

    close() {
        this.dialog.classList.remove('active');
        this.dialog.setAttribute('aria-hidden', 'true');
        this.resetFeedback();
    }

    resetFeedback() {
        if (this.feedback) {
            this.feedback.style.display = 'none';
            this.feedback.className = 'shoutout-feedback';
        }
    }

    async handleSubmit(e) {
        e.preventDefault();

        const msgInput = this.form.querySelector('textarea[name="message"]');
        const senderInput = this.form.querySelector('input[name="sender"]');

        const message = msgInput?.value.trim();
        const sender = senderInput?.value.trim() || 'Anonymous';

        if (!message) return;

        // Visual loading state
        const submitBtn = this.form.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.disabled = true;
        submitBtn.textContent = 'Sending...';

        try {
            const response = await fetch(`${this.config.apiBase}/shoutout`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: message,
                    sender: sender
                })
            });

            if (!response.ok) throw new Error('Failed to send');

            // Success
            this.showFeedback('Shoutout sent! 🎉', 'success');
            this.form.reset();
            setTimeout(() => this.close(), 2000);

        } catch (error) {
            console.error('Shoutout error:', error);
            this.showFeedback('Error sending shoutout. Try again.', 'error');
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
        }
    }

    showFeedback(msg, type) {
        if (!this.feedback) return;
        this.feedback.textContent = msg;
        this.feedback.className = `shoutout-feedback ${type}`;
        this.feedback.style.display = 'block';
    }
}
