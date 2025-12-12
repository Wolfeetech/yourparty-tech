// Mock LocalStorage
const localStorageMock = (function () {
    let store = {};
    return {
        getItem: jest.fn(key => store[key] || null),
        setItem: jest.fn((key, value) => { store[key] = value.toString(); }),
        removeItem: jest.fn(key => { delete store[key]; }),
        clear: jest.fn(() => { store = {}; })
    };
})();
Object.defineProperty(window, 'localStorage', { value: localStorageMock });

// Mock Fetch
global.fetch = jest.fn(() =>
    Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ status: 'success' }),
        text: () => Promise.resolve('ok')
    })
);

// Mock Window Config
window.YourPartyConfig = {
    restBase: 'http://localhost/wp-json/yourparty/v1',
    nonce: 'test-nonce'
};

// Mock Console to keep output clean (optional, keeping errors)
global.console = {
    ...console,
    // log: jest.fn(),
    warn: jest.fn(),
};
