/**
 * Visualizer Module
 */
export default class Visualizer {
    constructor() {
        this.analyser = null;
        this.animationId = null;
        this.canvas = document.getElementById('inline-visualizer') || document.getElementById('monitor-visualizer');
        this.ctx = this.canvas ? this.canvas.getContext('2d', { alpha: false }) : null;

        this.modeIndex = 0;
        this.modes = ['modern_wave', 'rta_spectrum', 'rgb_waveform', 'oscilloscope', 'matrix'];

        if (this.canvas) {
            this.init();
        }
    }

    init() {
        // Mode switch
        this.canvas.addEventListener('click', () => {
            this.modeIndex = (this.modeIndex + 1) % this.modes.length;
            // Show toast if available?
            console.log(`Visualizer Mode: ${this.modes[this.modeIndex]}`);
        });
        this.canvas.style.cursor = 'pointer';

        window.addEventListener('resize', () => this.resize());
        this.resize();

        // Listen for AudioContext event from StreamController
        window.addEventListener('stream:audioContextReady', (e) => {
            this.analyser = e.detail.analyser;
            if (this.analyser) {
                this.analyser.fftSize = 4096;
                this.analyser.smoothingTimeConstant = 0.85;
            }
            this.startRendering();
        });

        this.drawIdle();
    }

    resize() {
        if (!this.canvas) return;
        const dpr = window.devicePixelRatio || 1;
        const rect = this.canvas.getBoundingClientRect();
        this.canvas.width = rect.width * dpr;
        this.canvas.height = rect.height * dpr;
    }

    startRendering() {
        if (this.animationId) cancelAnimationFrame(this.animationId);
        this.render();
    }

    drawIdle() {
        if (!this.ctx || !this.canvas) return;
        this.ctx.fillStyle = '#111';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
    }

    render() {
        this.animationId = requestAnimationFrame(() => this.render());
        if (!this.analyser || !this.ctx) return;

        const w = this.canvas.width;
        const h = this.canvas.height;
        const fftSize = this.analyser.frequencyBinCount;
        const freqData = new Uint8Array(fftSize);
        this.analyser.getByteFrequencyData(freqData);

        // Clear
        this.ctx.fillStyle = 'rgba(5, 5, 5, 1)';
        this.ctx.fillRect(0, 0, w, h);

        const mode = this.modes[this.modeIndex];

        // Basic implementations
        if (mode === 'modern_wave') this.drawModernWave(freqData, w, h);
        else this.drawRTASpectrum(freqData, w, h);
    }

    drawRTASpectrum(data, w, h) {
        const bars = 64;
        const barW = w / bars;
        for (let i = 0; i < bars; i++) {
            const index = Math.floor(i * (data.length / bars));
            const val = data[index];
            const barH = (val / 255) * h;
            this.ctx.fillStyle = `hsl(${i * 4}, 100%, 50%)`;
            this.ctx.fillRect(i * barW, h - barH, barW - 1, barH);
        }
    }

    drawModernWave(data, w, h) {
        this.ctx.lineWidth = 2;
        this.ctx.strokeStyle = '#00ff88';
        this.ctx.beginPath();
        const slice = Math.floor(data.length / w);
        for (let x = 0; x < w; x++) {
            const i = x * slice;
            const val = data[i];
            const y = h - ((val / 255) * h);
            if (x === 0) this.ctx.moveTo(x, y);
            else this.ctx.lineTo(x, y);
        }
        this.ctx.stroke();
    }
}
