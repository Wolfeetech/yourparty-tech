if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        const themePath = '/wp-content/themes/yourparty-tech';
        navigator.serviceWorker.register(`${themePath}/sw.js`)
            .then(registration => {
                console.log('ServiceWorker registration successful with scope: ', registration.scope);
            }, err => {
                console.log('ServiceWorker registration failed: ', err);
            });
    });
}
