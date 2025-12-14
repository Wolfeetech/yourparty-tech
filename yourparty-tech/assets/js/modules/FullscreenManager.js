/**
 * Fullscreen Visual Player Manager
 */
import VisualEngine from './VisualEngine.js';
import StreamController from './StreamController.js';

export default class FullscreenManager {
    constructor() {
        this.isActive = false;
        this.dom = {};

        // Dependencies are injected or global? 
        // For Fullscreen Visuals we often need a separate instance of VisualEngine or re-use one.
        // Let's assume we use the app's VisualEngine instance
    }

    init(visualEngineInstance, streamInstance) {
        this.visualEngine = visualEngineInstance;
        this.stream = streamInstance;

        this.createOverlay();
        this.bindEvents();
    }

    createOverlay() {
        if (document.getElementById('fullscreen-visual-overlay')) return;

        const overlay = document.createElement('div');
        overlay.id = 'fullscreen-visual-overlay';
        overlay.className = 'fullscreen-visual-overlay';
        overlay.innerHTML = `
            <canvas id="fullscreen-visual-canvas"></canvas>
            <button class="visual-close-btn" id="visual-close-btn">×</button>
            <div class="visual-controls">
                <button id="visual-mode-prev">←</button>
                <span id="visual-mode-name">Mode</span>
                <button id="visual-mode-next">→</button>
            </div>
         `;
        document.body.appendChild(overlay);

        this.dom.overlay = overlay;
        this.dom.canvas = document.getElementById('fullscreen-visual-canvas');
        this.dom.modeName = document.getElementById('visual-mode-name');
    }

    bindEvents() {
        document.getElementById('visual-close-btn')?.addEventListener('click', () => this.close());
        document.getElementById('visual-mode-next')?.addEventListener('click', () => {
            this.visualEngine.nextMode();
            this.updateUI();
        });

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') this.close();
        });

        // Trigger from somewhere? e.g. "Expand" button in player
        // We need to listen to a global event or expose an open method
    }

    open() {
        this.isActive = true;
        this.dom.overlay.classList.add('active');
        document.body.style.overflow = 'hidden';

        // Re-init visual engine on this new canvas? 
        // Or just resize? The VisualEngine class in this refactor assumes one canvas at a time potentially.
        // Let's re-init it with the fullscreen canvas.
        if (this.visualEngine) {
            this.visualEngine.init(this.dom.canvas, this.stream.analyser);
            this.updateUI();
        }
    }

    close() {
        this.isActive = false;
        this.dom.overlay.classList.remove('active');
        document.body.style.overflow = '';

        // Restore Inline Visualizer?
        // This logic is complex. Ideally VisualEngine handles multiple canvases or we switch back.
        // For now, let's just hide overlay.
    }

    updateUI() {
        if (this.visualEngine && this.dom.modeName) {
            this.dom.modeName.textContent = this.visualEngine.getCurrentMode().name;
        }
    }
}
