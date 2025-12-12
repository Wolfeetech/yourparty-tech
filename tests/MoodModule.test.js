import MoodModule from '../src/js/modules/MoodModule.js';

const mockConfig = {
    restBase: 'https://api.test',
    nonce: 'test-nonce'
};

global.fetch = jest.fn();

describe('MoodModule', () => {
    let moodModule;

    beforeEach(() => {
        document.body.innerHTML = `
            <button id="mood-tag-button">Tag Mood</button>
            <div id="mood-dialog"></div>
        `;
        fetch.mockClear();
        localStorage.clear();
    });

    test('should initialize correctly', () => {
        moodModule = new MoodModule(mockConfig);
        expect(moodModule).toBeDefined();
    });

    test('should return true if on cooldown', () => {
        const songId = '123';
        // Mock existing cooldown
        const cooldowns = { [songId]: Date.now() }; // Just voted
        localStorage.setItem('yp_mood_cooldowns', JSON.stringify(cooldowns));

        moodModule = new MoodModule(mockConfig);

        expect(moodModule.isOnCooldown(songId)).toBe(true);
    });

    test('should return false if cooldown expired', () => {
        const songId = '123';
        const expiredTime = Date.now() - (10 * 60 * 1000); // 10 mins ago
        const cooldowns = { [songId]: expiredTime };
        localStorage.setItem('yp_mood_cooldowns', JSON.stringify(cooldowns));

        moodModule = new MoodModule(mockConfig);

        expect(moodModule.isOnCooldown(songId)).toBe(false);
    });

    test('should return false if never voted', () => {
        moodModule = new MoodModule(mockConfig);
        expect(moodModule.isOnCooldown('999')).toBe(false);
    });
});
