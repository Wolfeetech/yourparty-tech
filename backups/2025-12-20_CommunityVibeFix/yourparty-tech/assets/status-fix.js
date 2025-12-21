// CRITICAL FIX: Initialize currentSongId globally and update on status fetch
window.currentSongId = null;
window.currentTrackInfo = { title: '', artist: '', id: null };

// Simple status fetcher
async function fetchAndUpdateStatus() {
    try {
        const response = await fetch('/wp-json/yourparty/v1/status');
        if (!response.ok) return;

        const data = await response.json();
        const song = data?.now_playing?.song;

        if (song) {
            window.currentSongId = song.id || null;
            window.currentTrackInfo = {
                id: song.id || null,
                title: song.title || 'Unknown Title',
                artist: song.artist || 'Unknown Artist'
            };

            // Update DOM
            const titleEl = document.getElementById('track-title');
            const artistEl = document.getElementById('track-artist');
            const coverEl = document.getElementById('player-cover');

            if (titleEl) titleEl.textContent = window.currentTrackInfo.title;
            if (artistEl) artistEl.textContent = window.currentTrackInfo.artist;
            if (coverEl && song.art) coverEl.src = song.art;

            console.log('✅ Current Song ID:', window.currentSongId);
        }
    } catch (error) {
        console.error('Status fetch error:', error);
    }
}

// Fetch immediately and every 10 seconds
if (document.getElementById('track-title')) {
    fetchAndUpdateStatus();
    setInterval(fetchAndUpdateStatus, 10000);
}
