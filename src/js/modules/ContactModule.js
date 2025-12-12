/**
 * YourParty Contact Module
 * Handles contact form submission with security checks (Nonce/Honeypot)
 */
export default class ContactModule {
    constructor(config) {
        this.config = config;
        this.form = document.getElementById('contact-form');
        this.submitBtn = this.form?.querySelector('button[type="submit"]');
        this.feedback = document.getElementById('form-feedback');

        this.isSubmitting = false;

        this.init();
    }

    init() {
        if (!this.form) return;

        this.form.addEventListener('submit', (e) => this.handleSubmit(e));

        // Real-time validation (optional, can add later)
        this.form.querySelectorAll('input, textarea').forEach(input => {
            input.addEventListener('input', () => {
                input.classList.remove('error');
            });
        });

        console.log('[ContactModule] Initialized');
    }

    async handleSubmit(e) {
        e.preventDefault();
        if (this.isSubmitting) return;

        // 1. Honeypot Check
        const honey = this.form.querySelector('input[name="website_url"]'); // Hidden field
        if (honey && honey.value) {
            console.warn('[Contact] Bot detected (honeypot).');
            return; // Silent fail
        }

        // 2. Client-side Validation
        if (!this.validate()) return;

        this.isSubmitting = true;
        this.setLoading(true);

        try {
            const formData = new FormData(this.form);
            // Add Nonce from config
            if (this.config.nonce) {
                formData.append('_wpnonce', this.config.nonce);
            }

            // Send to WP REST API or Admin-Post
            // Using a custom endpoint for cleaner JSON handling
            const endpoint = `${this.config.restBase}/contact`;

            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    // 'Content-Type': 'multipart/form-data', // Do NOT set this manually with FormData
                    'X-WP-Nonce': this.config.nonce
                },
                body: formData
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message || 'Submission failed');
            }

            this.showFeedback('Message sent successfully!', 'success');
            this.form.reset();

        } catch (error) {
            console.error('[Contact] Error:', error);
            this.showFeedback(error.message || 'Failed to send message.', 'error');
        } finally {
            this.isSubmitting = false;
            this.setLoading(false);
        }
    }

    validate() {
        let isValid = true;

        // Simple required checks
        const required = this.form.querySelectorAll('[required]');
        required.forEach(field => {
            if (!field.value.trim()) {
                field.classList.add('error');
                isValid = false;
            }
        });

        // Email check
        const email = this.form.querySelector('input[type="email"]');
        if (email && email.value) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(email.value)) {
                email.classList.add('error');
                isValid = false;
            }
        }

        if (!isValid) {
            this.showFeedback('Please fill in all required fields correctly.', 'error');
        }

        return isValid;
    }

    setLoading(loading) {
        if (this.submitBtn) {
            this.submitBtn.disabled = loading;
        }
        this.form.classList.toggle('submitting', loading);
    }

    showFeedback(msg, type) {
        if (!this.feedback) {
            this.feedback = document.createElement('div');
            this.feedback.id = 'form-feedback';
            this.submitBtn.parentNode.insertBefore(this.feedback, this.submitBtn.nextSibling);
        }

        this.feedback.textContent = msg;
        this.feedback.className = `form-feedback ${type}`;
        this.feedback.style.display = 'block';

        if (type === 'success') {
            setTimeout(() => {
                this.feedback.style.display = 'none';
            }, 5000);
        }
    }
}
