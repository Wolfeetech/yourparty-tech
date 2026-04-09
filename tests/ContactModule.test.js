import ContactModule from '../src/js/modules/ContactModule';

describe('ContactModule', () => {
    let module;
    let form;
    let config;

    beforeEach(() => {
        // Setup DOM
        document.body.innerHTML = `
            <form id="contact-form">
                <input type="text" name="name" required value="Test User">
                <input type="email" name="email" required value="test@example.com">
                <textarea name="message" required>Hello World</textarea>
                <input type="text" name="website_url" style="display:none" value="">
                <button type="submit">Send</button>
            </form>
            <div id="form-feedback"></div>
        `;

        form = document.getElementById('contact-form');
        config = { restBase: '/api', nonce: '12345' };

        // Reset Mocks
        fetch.mockClear();

        module = new ContactModule(config);
    });

    test('should initialize and attach submit handler', () => {
        expect(module.form).toBeDefined();
    });

    test('should fail validation if required field is empty', () => {
        form.querySelector('[name="name"]').value = '';
        const valid = module.validate();
        expect(valid).toBe(false);
        expect(form.querySelector('[name="name"]').classList.contains('error')).toBe(true);
    });

    test('should fail silent if honeypot is filled', async () => {
        form.querySelector('[name="website_url"]').value = 'im-a-bot';

        await module.handleSubmit({ preventDefault: jest.fn() });

        expect(fetch).not.toHaveBeenCalled();
    });

    test('should submit valid form data via fetch', async () => {
        await module.handleSubmit({ preventDefault: jest.fn() });

        expect(fetch).toHaveBeenCalledTimes(1);
        expect(fetch).toHaveBeenCalledWith('/api/contact', expect.objectContaining({
            method: 'POST',
            headers: expect.objectContaining({
                'X-WP-Nonce': '12345'
            })
        }));
    });
});
