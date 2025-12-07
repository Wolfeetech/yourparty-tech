/**
 * YourParty Visual Engine - Professional Grade
 * Audio-Reactive Visualizers + Light-to-Sound Shows + Video Player Ready
 */
const VisualEngine = (function () {
    'use strict';

    let canvas, ctx, analyser, dataArray;
    let animationId;
    let currentMode = 0;
    const DPI = window.devicePixelRatio || 1;

    // Particle systems state
    let particles = [];
    let rings = [];
    let strobePhase = 0;
    let colorWashHue = 0;

    const MODES = [
        { id: 'pro_spectrum', name: 'Pro Spectrum', type: 'audio' },
        { id: 'precision_wave', name: 'Precision Waveform', type: 'audio' },
        { id: 'particle_field', name: 'Particle Field', type: 'audio' },
        { id: 'frequency_rings', name: 'Frequency Rings', type: 'audio' },
        { id: 'energy_matrix', name: 'Energy Matrix', type: 'audio' },
        { id: 'strobe_lights', name: 'Strobe Lights', type: 'light' },
        { id: 'color_wash', name: 'Color Wash', type: 'light' },
        { id: 'kaleidoscope', name: 'Kaleidoscope', type: 'audio' }
    ];

    function init(canvasElement) {
        canvas = canvasElement || document.getElementById('audio-visualizer');
        if (!canvas) {
            console.warn('[VisualEngine] Canvas not found');
            return false;
        }

        ctx = canvas.getContext('2d', { alpha: false, desynchronized: true });

        // Get AudioContext from StreamController
        if (typeof StreamController !== 'undefined') {
            analyser = StreamController.getAnalyser();
            if (analyser) {
                const bufferLength = analyser.frequencyBinCount;
                dataArray = new Uint8Array(bufferLength);
                resize();
                startRendering();
                return true;
            }
        }
        return false;
    }

    function resize() {
        if (!canvas) return;
        const rect = canvas.parentElement?.getBoundingClientRect() || { width: 800, height: 400 };

        // High-DPI Scaling
        canvas.width = rect.width * DPI;
        canvas.height = rect.height * DPI;
        canvas.style.width = `${rect.width}px`;
        canvas.style.height = `${rect.height}px`;

        if (ctx) ctx.scale(DPI, DPI);
    }

    function startRendering() {
        if (animationId) cancelAnimationFrame(animationId);

        function render(timestamp) {
            if (!analyser || !dataArray) return;

            analyser.getByteFrequencyData(dataArray);

            const w = canvas.width / DPI;
            const h = canvas.height / DPI;

            // Call current mode renderer
            const mode = MODES[currentMode];
            switch (mode.id) {
                case 'pro_spectrum': drawProSpectrum(ctx, dataArray, w, h); break;
                case 'precision_wave': drawPrecisionWave(ctx, dataArray, w, h); break;
                case 'particle_field': drawParticleField(ctx, dataArray, w, h, timestamp); break;
                case 'frequency_rings': drawFrequencyRings(ctx, dataArray, w, h, timestamp); break;
                case 'energy_matrix': drawEnergyMatrix(ctx, dataArray, w, h, timestamp); break;
                case 'strobe_lights': drawStrobeLights(ctx, dataArray, w, h, timestamp); break;
                case 'color_wash': drawColorWash(ctx, dataArray, w, h, timestamp); break;
                case 'kaleidoscope': drawKaleidoscope(ctx, dataArray, w, h, timestamp); break;
            }

            animationId = requestAnimationFrame(render);
        }

        animationId = requestAnimationFrame(render);
    }

    // ==================== MODE 1: PRO SPECTRUM ====================
    function drawProSpectrum(c, data, w, h) {
        c.fillStyle = 'rgba(10, 10, 10, 0.3)';
        c.fillRect(0, 0, w, h);

        const bars = 64;
        const barWidth = w / bars;
        const maxHeight = h * 0.85;

        const gradient = c.createLinearGradient(0, h, 0, 0);
        gradient.addColorStop(0, '#2E8B57');
        gradient.addColorStop(0.5, '#3b82f6');
        gradient.addColorStop(1, '#ec4899');

        for (let i = 0; i < bars; i++) {
            const idx = Math.floor((i / bars) * data.length);
            const value = data[idx] / 255;
            const barHeight = value * maxHeight;

            const x = i * barWidth;
            const y = h - barHeight;

            c.fillStyle = gradient;
            c.fillRect(x, y, barWidth - 3, barHeight);

            // Peak indicator
            if (value > 0.8) {
                c.fillStyle = '#fff';
                c.fillRect(x, y - 3, barWidth - 3, 3);
            }
        }
    }

    // ==================== MODE 2: PRECISION WAVEFORM ====================
    function drawPrecisionWave(c, data, w, h) {
        c.fillStyle = 'rgba(10, 10, 10, 0.2)';
        c.fillRect(0, 0, w, h);

        c.lineWidth = 3;
        c.lineCap = 'round';
        c.shadowBlur = 20;
        c.shadowColor = '#2E8B57';

        const grad = c.createLinearGradient(0, 0, w, 0);
        grad.addColorStop(0, '#00f0ff');
        grad.addColorStop(0.5, '#2E8B57');
        grad.addColorStop(1, '#ec4899');
        c.strokeStyle = grad;

        c.beginPath();
        const sliceWidth = w / data.length;
        for (let i = 0; i < data.length; i++) {
            const v = data[i] / 255;
            const y = h / 2 + (v - 0.5) * h * 0.7;
            i === 0 ? c.moveTo(0, y) : c.lineTo(i * sliceWidth, y);
        }
        c.stroke();
        c.shadowBlur = 0;
    }

    // ==================== MODE 3: PARTICLE FIELD ====================
    function drawParticleField(c, data, w, h, t) {
        c.fillStyle = 'rgba(10, 10, 10, 0.1)';
        c.fillRect(0, 0, w, h);

        if (particles.length === 0) {
            for (let i = 0; i < 150; i++) {
                particles.push({
                    x: Math.random() * w,
                    y: Math.random() * h,
                    vx: (Math.random() - 0.5) * 2,
                    vy: (Math.random() - 0.5) * 2,
                    size: 1 + Math.random() * 3,
                    freq: Math.floor(Math.random() * data.length)
                });
            }
        }

        particles.forEach(p => {
            const intensity = data[p.freq] / 255;

            p.x += p.vx * (1 + intensity * 2);
            p.y += p.vy * (1 + intensity * 2);

            if (p.x < 0) p.x = w;
            if (p.x > w) p.x = 0;
            if (p.y < 0) p.y = h;
            if (p.y > h) p.y = 0;

            c.beginPath();
            c.arc(p.x, p.y, p.size * (1 + intensity), 0, Math.PI * 2);
            c.fillStyle = `rgba(46, 139, 87, ${intensity * 0.8})`;
            c.fill();
        });
    }

    // ==================== MODE 4: FREQUENCY RINGS ====================
    function drawFrequencyRings(c, data, w, h, t) {
        c.fillStyle = 'rgba(10, 10, 10, 0.15)';
        c.fillRect(0, 0, w, h);

        const centerX = w / 2;
        const centerY = h / 2;
        const maxRadius = Math.min(w, h) / 2.5;
        const ringsCount = 8;

        for (let i = 0; i < ringsCount; i++) {
            const idx = Math.floor((i / ringsCount) * data.length);
            const value = data[idx] / 255;
            const radius = (i + 1) * (maxRadius / ringsCount) * (1 + value * 0.3);

            c.beginPath();
            c.arc(centerX, centerY, radius, 0, Math.PI * 2);
            c.strokeStyle = `hsla(${(i * 40 + t * 0.05) % 360}, 70%, 60%, ${value})`;
            c.lineWidth = 4;
            c.stroke();
        }
    }

    // ==================== MODE 5: ENERGY MATRIX ====================
    function drawEnergyMatrix(c, data, w, h, t) {
        c.fillStyle = 'rgba(10, 10, 10, 0.2)';
        c.fillRect(0, 0, w, h);

        const cols = 20;
        const rows = 12;
        const cellW = w / cols;
        const cellH = h / rows;

        for (let i = 0; i < cols; i++) {
            for (let j = 0; j < rows; j++) {
                const idx = Math.floor(((i + j) / (cols + rows)) * data.length);
                const value = data[idx] / 255;

                if (value > 0.3) {
                    const x = i * cellW;
                    const y = j * cellH;
                    c.fillStyle = `rgba(46, 139, 87, ${value})`;
                    c.fillRect(x + 2, y + 2, cellW - 4, cellH - 4);
                }
            }
        }
    }

    // ==================== MODE 6: STROBE LIGHTS (Light-to-Sound) ====================
    function drawStrobeLights(c, data, w, h, t) {
        const bass = data.slice(0, 10).reduce((a, b) => a + b) / 10;
        const mid = data.slice(10, 50).reduce((a, b) => a + b) / 40;
        const high = data.slice(50, 100).reduce((a, b) => a + b) / 50;

        // Beat detection
        if (bass > 180) {
            strobePhase = (strobePhase + 1) % 2;
        }

        const brightness = strobePhase ? 255 : 20;
        c.fillStyle = `rgb(${brightness}, ${brightness}, ${brightness})`;
        c.fillRect(0, 0, w, h);

        // Color accents on beat
        if (mid > 150) {
            c.fillStyle = `rgba(236, 72, 153, ${(mid - 150) / 100})`;
            c.fillRect(0, h / 3, w, h / 3);
        }
        if (high > 120) {
            c.fillStyle = `rgba(59, 130, 246, ${(high - 120) / 100})`;
            c.fillRect(w / 4, 0, w / 2, h);
        }
    }

    // ==================== MODE 7: COLOR WASH (Light-to-Sound) ====================
    function drawColorWash(c, data, w, h, t) {
        const avg = data.reduce((a, b) => a + b) / data.length;
        colorWashHue = (colorWashHue + avg / 500) % 360;

        const gradient = c.createRadialGradient(w / 2, h / 2, 0, w / 2, h / 2, Math.max(w, h));
        gradient.addColorStop(0, `hsla(${colorWashHue}, 80%, 60%, 1)`);
        gradient.addColorStop(0.5, `hsla(${(colorWashHue + 60) % 360}, 70%, 50%, 0.8)`);
        gradient.addColorStop(1, `hsla(${(colorWashHue + 120) % 360}, 60%, 40%, 0.6)`);

        c.fillStyle = gradient;
        c.fillRect(0, 0, w, h);
    }

    // ==================== MODE 8: KALEIDOSCOPE ====================
    function drawKaleidoscope(c, data, w, h, t) {
        c.fillStyle = 'rgba(10, 10, 10, 0.1)';
        c.fillRect(0, 0, w, h);

        c.save();
        c.translate(w / 2, h / 2);

        const segments = 8;
        for (let i = 0; i < segments; i++) {
            c.save();
            c.rotate((Math.PI * 2 / segments) * i);

            for (let j = 0; j < 20; j++) {
                const idx = Math.floor((j / 20) * data.length);
                const value = data[idx] / 255;
                const radius = j * 15;

                c.beginPath();
                c.arc(radius, 0, value * 10, 0, Math.PI * 2);
                c.fillStyle = `hsla(${(j * 18 + t * 0.1) % 360}, 70%, 60%, ${value})`;
                c.fill();
            }

            c.restore();
        }

        c.restore();
    }

    function setMode(index) {
        if (index >= 0 && index < MODES.length) {
            currentMode = index;
            // Reset mode-specific state
            particles = [];
            rings = [];
            strobePhase = 0;
            return MODES[index];
        }
        return null;
    }

    function nextMode() {
        currentMode = (currentMode + 1) % MODES.length;
        particles = [];
        return MODES[currentMode];
    }

    function getModes() {
        return MODES;
    }

    function getCurrentMode() {
        return MODES[currentMode];
    }

    window.addEventListener('resize', resize);

    return {
        init,
        resize,
        setMode,
        nextMode,
        getModes,
        getCurrentMode,
        getAnalyser: () => analyser
    };
})();

// Global export
window.VisualEngine = VisualEngine;
