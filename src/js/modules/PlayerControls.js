/**
 * Player Controls & UI
 */

export default class PlayerControls {
    constructor() {
        this.dom = {
            title: document.getElementById('track-title'),
            artist: document.getElementById('track-artist'),
            cover: document.getElementById('cover-art'),
            marquee: document.getElementById('next-track-marquee'),
            playBtn: document.getElementById('play-toggle'),
            bg: document.querySelector('.hero-fullscreen'), // For dynamic BG if needed
            listenerCount: document.getElementById('listener-count')
        };

        this.audio = document.getElementById('radio-audio');
        this.isPlaying = false;

        this.bindEvents();
    }

    bindEvents() {
        if (this.dom.playBtn) {
            this.dom.playBtn.addEventListener('click', () => this.togglePlay());
        }
    }

    togglePlay() {
        // Delegate to StreamController via global app instance (or event)
        if (window.YourPartyAppInstance && window.YourPartyAppInstance.modules.stream) {
            window.YourPartyAppInstance.modules.stream.togglePlay();
        } else {
            console.warn('Stream module not ready');
        }
    }

    setPlayState(playing) {
        this.isPlaying = playing;
        const btn = this.dom.playBtn;
        if (!btn) return;

        const iconPlay = btn.querySelector('.icon-play');
        const iconPause = btn.querySelector('.icon-pause');

        if (playing) {
            if (iconPlay) iconPlay.style.display = 'none';
            if (iconPause) iconPause.style.display = 'block';
            btn.classList.add('playing');
        } else {
            if (iconPlay) iconPlay.style.display = 'block';
            if (iconPause) iconPause.style.display = 'none';
            btn.classList.remove('playing');
        }
    }

    update(data) {
        if (!data || !data.now_playing || !data.now_playing.song) return;

        const song = data.now_playing.song;
        const next = data.playing_next?.song;

        this.updateTrackInfo(song);
        this.updateNextTrack(next);
    }

    updateTrackInfo(song) {
        // Safe Update
        if (this.dom.title) {
            this.dom.title.textContent = song.title;
            this.dom.title.classList.remove('skeleton');
        }
        if (this.dom.artist) {
            this.dom.artist.textContent = song.artist;
            this.dom.artist.classList.remove('skeleton');
        }

        // Cover Art with generic fallback
        if (this.dom.cover) {
            const newSrc = song.art || this.generateFallback(song.title);
            if (this.dom.cover.src !== newSrc) {
                this.dom.cover.src = newSrc;
            }
        }
    }

    updateNextTrack(song) {
        if (!this.dom.marquee) return;

        if (song) {
            const text = song.text || `${song.artist} - ${song.title}`;
            this.dom.marquee.textContent = `NEXT: ${text}`;
            this.dom.marquee.parentNode.style.opacity = '1';
        } else {
            this.dom.marquee.textContent = 'Queue Empty';
            this.dom.marquee.parentNode.style.opacity = '0.5';
        }
    }

    generateFallback(str) {
        if (!str) return 'https://placehold.co/600x600/10b981/ffffff?text=YP';
        // Simple consistent hash for color? 
        // For now just return placeholder or use the complex one from original app.js if needed
        return `https://ui-avatars.com/api/?name=${encodeURIComponent(str)}&background=random&size=600`;
    }
}
