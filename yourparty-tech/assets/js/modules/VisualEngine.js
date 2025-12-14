/**
 * YourParty Visual Engine - Professional Grade
 * Audio-Reactive Visualizers + Light-to-Sound Shows
 */
export default class VisualEngine {
    constructor() {
        this.canvas = null;
        this.ctx = null;
        this.analyser = null;
        this.dataArray = null;
        this.animationId = null;
        this.currentMode = 0;
        this.DPI = window.devicePixelRatio || 1;

        // Particle systems state
        this.particles = [];
        this.strobePhase = 0;
        this.colorWashHue = 0;

        this.MODES = [
            { id: 'pro_spectrum', name: 'Pro Spectrum', type: 'audio' },
            { id: 'precision_wave', name: 'Precision Waveform', type: 'audio' },
            { id: 'particle_field', name: 'Particle Field', type: 'audio' },
            { id: 'frequency_rings', name: 'Frequency Rings', type: 'audio' },
            { id: 'energy_matrix', name: 'Energy Matrix', type: 'audio' },
            { id: 'strobe_lights', name: 'Strobe Lights', type: 'light' },
            { id: 'color_wash', name: 'Color Wash', type: 'light' },
            { id: 'kaleidoscope', name: 'Kaleidoscope', type: 'audio' }
        ];
    }

    init(canvasElement, analyser) {
        this.canvas = canvasElement || document.getElementById('audio-visualizer');
        if (!this.canvas) {
            console.warn('[VisualEngine] Canvas not found');
            return false;
        }

        this.ctx = this.canvas.getContext('2d', { alpha: false, desynchronized: true });
        this.analyser = analyser;

        if (this.analyser) {
            const bufferLength = this.analyser.frequencyBinCount;
            this.dataArray = new Uint8Array(bufferLength);
            this.resize();
            this.startRendering();

            window.addEventListener('resize', () => this.resize());

            // Interaction: Switch Mode on Canvas Click
            this.canvas.addEventListener('click', () => {
                this.nextMode();

                // Show floating Feedback
                // TODO: Maybe implement a better UI toast via main.js later
            });

            return true;
        }
        return false;
    }

    // Allows external injection of analyser (e.g. from StreamController event)
    setAnalyser(analyser) {
        this.analyser = analyser;
        const bufferLength = this.analyser.frequencyBinCount;
        this.dataArray = new Uint8Array(bufferLength);
        if (this.canvas && !this.animationId) {
            this.startRendering();
        }
    }

    resize() {
        if (!this.canvas) return;
        const rect = this.canvas.parentElement?.getBoundingClientRect() || { width: 800, height: 400 };

        this.canvas.width = rect.width * this.DPI;
        this.canvas.height = rect.height * this.DPI;
        // Don't force style width/height if it's fullscreen or responsive via CSS

        if (this.ctx) this.ctx.scale(this.DPI, this.DPI);
    }

    startRendering() {
        if (this.animationId) cancelAnimationFrame(this.animationId);

        const render = (timestamp) => {
            this.animationId = requestAnimationFrame(render);

            if (!this.analyser || !this.dataArray || !this.ctx) return;

            // Differentiate data needed based on mode
            const mode = this.MODES[this.currentMode];

            if (mode.id === 'precision_wave' || mode.id === 'oscilloscope') {
                this.analyser.getByteTimeDomainData(this.dataArray);
            } else {
                this.analyser.getByteFrequencyData(this.dataArray);
            }

            const w = this.canvas.width / this.DPI;
            const h = this.canvas.height / this.DPI;

            // Clear with trail effect for some modes
            if (mode.id === 'particle_field' || mode.id === 'strobe_lights') {
                this.ctx.fillStyle = 'rgba(0, 0, 0, 0.2)'; // Trails
                this.ctx.fillRect(0, 0, w, h);
            } else {
                this.ctx.clearRect(0, 0, w, h);
            }

            switch (mode.id) {
                case 'pro_spectrum': this.drawProSpectrum(w, h); break;
                case 'precision_wave': this.drawPrecisionWave(w, h); break;
                case 'particle_field': this.drawParticleField(w, h, timestamp); break;
                default: this.drawProSpectrum(w, h); break;
            }
        };

        this.animationId = requestAnimationFrame(render);
    }

    drawProSpectrum(w, h) {
        // Fix: Only render useful frequency range (approx first 70% of bins)
        // MP3s often cut off above 16kHz, leaving the right side empty in linear plots.
        const usefulLimit = Math.floor(this.dataArray.length * 0.7);

        const barWidth = (w / usefulLimit) * 2.5; // Wider bars
        let barHeight;
        let x = 0;

        for (let i = 0; i < usefulLimit; i++) {
            barHeight = (this.dataArray[i] / 255) * h;

            // Color based on height (Frequency intensity)
            // Green (Low) -> Blue (Mid) -> Pink (High)
            const hue = i / usefulLimit * 360;
            this.ctx.fillStyle = `hsl(${hue}, 80%, 50%)`;

            // Draw mirrored? No, classic spectrum for "Pro" feel
            this.ctx.fillRect(x, h - barHeight, barWidth, barHeight);

            x += barWidth + 1;
        }
    }

    drawPrecisionWave(w, h) {
        this.ctx.lineWidth = 2;
        this.ctx.strokeStyle = '#00ff88'; // Neon Green
        this.ctx.beginPath();

        const sliceWidth = w / this.dataArray.length;
        let x = 0;

        for (let i = 0; i < this.dataArray.length; i++) {
            const v = this.dataArray[i] / 128.0;
            const y = (v * h) / 2; // Center it

            if (i === 0) this.ctx.moveTo(x, y);
            else this.ctx.lineTo(x, y);

            x += sliceWidth;
        }

        this.ctx.lineTo(w, h / 2);
        this.ctx.stroke();
    }

    drawParticleField(w, h, t) {
        // Initialize particles if needed
        if (this.particles.length < 50) {
            for (let i = 0; i < 50; i++) {
                this.particles.push({
                    x: Math.random() * w,
                    y: Math.random() * h,
                    size: Math.random() * 3,
                    speed: Math.random() * 2 + 0.5
                });
            }
        }

        // Use low frequency for "Kick" reaction
        const kick = this.dataArray[4];
        const isKicking = kick > 200;

        this.ctx.fillStyle = isKicking ? '#ffffff' : '#00ccff';

        this.particles.forEach(p => {
            p.y -= p.speed * (isKicking ? 2 : 1);
            if (p.y < 0) p.y = h;

            const radius = p.size * (isKicking ? 1.5 : 1);
            this.ctx.beginPath();
            this.ctx.arc(p.x, p.y, radius, 0, Math.PI * 2);
            this.ctx.fill();
        });
    }

    setMode(index) {
        if (index >= 0 && index < this.MODES.length) {
            this.currentMode = index;
            console.log(`[Visual] Mode switched to: ${this.MODES[index].name}`);
        }
    }

    nextMode() {
        this.setMode((this.currentMode + 1) % this.MODES.length);
    }

    getModes() { return this.MODES; }
    getCurrentMode() { return this.MODES[this.currentMode]; }
}
