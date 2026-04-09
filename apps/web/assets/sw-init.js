if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        // Register from root to ensure scope is /
        navigator.serviceWorker.register('/sw.js')
            .then(registration => {
                console.log('ServiceWorker registration successful with scope: ', registration.scope);
            }, err => {
                console.log('ServiceWorker registration failed: ', err);
            });
    });
}
