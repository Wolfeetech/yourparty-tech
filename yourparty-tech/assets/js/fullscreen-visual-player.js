/**
 * Fullscreen Visual Player - Controls & UI
 */
const FullscreenVisualPlayer = (function () {
    'use strict';

    let overlay, canvas, modeSelector, trackInfo;
    let isActive = false;

    function init() {
        createOverlay();
        bindEvents();
    }

    function createOverlay() {
        // Create fullscreen overlay
        overlay = document.createElement('div');
        overlay.id = 'fullscreen-visual-overlay';
        overlay.className = 'fullscreen-visual-overlay';
        overlay.innerHTML = `
            <canvas id="fullscreen-visual-canvas"></canvas>
            
            <!-- Close Button -->
            <button class="visual-close-btn" id="visual-close-btn" title="Exit (ESC)">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M18 6L6 18M6 6l12 12"></path>
                </svg>
            </button>

            <!-- Mode Selector -->
            <div class="visual-mode-selector" id="visual-mode-selector">
                <div class="mode-selector-header">
                    <h4>Visual Modes</h4>
                    <button class="mode-selector-toggle" id="mode-selector-toggle">☰</button>
                </div>
                <div class="mode-selector-list" id="mode-selector-list"></div>
            </div>

            <!-- Track Info Overlay -->
            <div class="visual-track-info" id="visual-track-info">
                <img id="visual-cover" src="" alt="Cover">
                <div class="visual-track-meta">
                    <h2 id="visual-title">Waiting for signal...</h2>
                    <p id="visual-artist">YourParty Radio</p>
                </div>
            </div>

            <!-- Controls -->
            <div class="visual-controls" id="visual-controls">
                <button class="visual-control-btn" id="visual-play-btn">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M8 5v14l11-7z"/>
                    </svg>
                </button>
                <button class="visual-control-btn" id="visual-mode-prev">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M15 18l-6-6 6-6"/>
                    </svg>
                </button>
                <span class="visual-mode-name" id="visual-mode-name">Spectrum</span>
                <button class="visual-control-btn" id="visual-mode-next">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M9 18l6-6-6-6"/>
                    </svg>
                </button>
            </div>
        `;

        document.body.appendChild(overlay);
        canvas = document.getElementById('fullscreen-visual-canvas');
        modeSelector = document.getElementById('mode-selector-list');
        trackInfo = document.getElementById('visual-track-info');
    }

    function bindEvents() {
        // Close button
        document.getElementById('visual-close-btn')?.addEventListener('click', close);

        // ESC key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && isActive) close();
        });

        // Mode navigation
        document.getElementById('visual-mode-prev')?.addEventListener('click', () => {
            if (typeof VisualEngine !== 'undefined') {
                const modes = VisualEngine.getModes();
                const current = VisualEngine.getCurrentMode();
                const idx = modes.findIndex(m => m.id === current.id);
                const prevIdx = (idx - 1 + modes.length) % modes.length;
                VisualEngine.setMode(prevIdx);
                updateModeUI();
            }
        });

        document.getElementById('visual-mode-next')?.addEventListener('click', () => {
            if (typeof VisualEngine !== 'undefined') {
                VisualEngine.nextMode();
                updateModeUI();
            }
        });

        // Play/Pause
        document.getElementById('visual-play-btn')?.addEventListener('click', () => {
            if (typeof StreamController !== 'undefined') {
                StreamController.togglePlay();
            }
        });

        // Mode selector toggle
        document.getElementById('mode-selector-toggle')?.addEventListener('click', () => {
            modeSelector.classList.toggle('active');
        });

        // Populate mode list
        if (typeof VisualEngine !== 'undefined') {
            populateModeList();
        }
    }

    function populateModeList() {
        const modes = VisualEngine.getModes();
        modeSelector.innerHTML = '';

        modes.forEach((mode, idx) => {
            const btn = document.createElement('button');
            btn.className = 'mode-btn';
            btn.dataset.mode = idx;
            btn.innerHTML = `
                <span class="mode-icon">${mode.type === 'light' ? '💡' : '🎵'}</span>
                <span class="mode-label">${mode.name}</span>
            `;
            btn.addEventListener('click', () => {
                VisualEngine.setMode(idx);
                updateModeUI();
                modeSelector.classList.remove('active');
            });
            modeSelector.appendChild(btn);
        });
    }

    function updateModeUI() {
        const current = VisualEngine.getCurrentMode();
        const modeName = document.getElementById('visual-mode-name');
        if (modeName) modeName.textContent = current.name;

        // Update mode list active state
        document.querySelectorAll('.mode-btn').forEach((btn, i) => {
            btn.classList.toggle('active', i === VisualEngine.getModes().findIndex(m => m.id === current.id));
        });
    }

    function open() {
        if (isActive) return;

        overlay.classList.add('active');
        document.body.style.overflow = 'hidden';
        isActive = true;

        // Initialize VisualEngine with fullscreen canvas
        if (typeof VisualEngine !== 'undefined') {
            VisualEngine.init(canvas);
            updateModeUI();
        }

        // Update track info
        updateTrackInfo();
    }

    function close() {
        overlay.classList.remove('active');
        document.body.style.overflow = '';
        isActive = false;
    }

    function updateTrackInfo() {
        // Sync with current track (called by YourPartyApp on metadata update)
        const title = document.getElementById('track-title')?.textContent;
        const artist = document.getElementById('track-artist')?.textContent;
        const cover = document.getElementById('cover-art')?.src;

        const visualTitle = document.getElementById('visual-title');
        const visualArtist = document.getElementById('visual-artist');
        const visualCover = document.getElementById('visual-cover');

        if (visualTitle) visualTitle.textContent = title || 'Loading...';
        if (visualArtist) visualArtist.textContent = artist || 'YourParty Radio';
        if (visualCover) visualCover.src = cover || '';
    }

    return { init, open, close, updateTrackInfo };
})();

// Auto-init on load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => FullscreenVisualPlayer.init());
} else {
    FullscreenVisualPlayer.init();
}

window.FullscreenVisualPlayer = FullscreenVisualPlayer;
