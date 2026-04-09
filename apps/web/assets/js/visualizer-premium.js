/**
 * Premium Visualizer Controller - Professional Audio Reactive Visuals
 * High-DPI, Smooth Rendering, Best Practices
 */
const VisualizerController = (function () {
    'use strict';

    let canvas, ctx, analyser, dataArray;
    let animationId;
    let modeIndex = 0;
    let isImmersive = false;
    const DPI = window.devicePixelRatio || 1;

    const modes = ['pro_spectrum', 'precision_scope', 'particle_field'];

    function init() {
        canvas = document.getElementById('audio-visualizer');
        if (!canvas) return;

        ctx = canvas.getContext('2d', { alpha: true });

        // Get AudioContext from StreamController
        if (typeof StreamController !== 'undefined') {
            analyser = StreamController.getAnalyser();
            if (analyser) {
                const bufferLength = analyser.frequencyBinCount;
                dataArray = new Uint8Array(bufferLength);
                resize();
                startRendering();
            }
        }
    }

    function resize() {
        if (!canvas) return;
        const rect = canvas.parentElement.getBoundingClientRect();

        // High-DPI Support
        canvas.width = rect.width * DPI;
        canvas.height = rect.height * DPI;
        canvas.style.width = `${rect.width}px`;
        canvas.style.height = `${rect.height}px`;

        ctx.scale(DPI, DPI);
    }

    function startRendering() {
        if (animationId) return;

        function render() {
            if (!analyser || !dataArray) return;

            analyser.getByteFrequencyData(dataArray);

            const visualWidth = canvas.width / DPI;
            const visualHeight = canvas.height / DPI;

            // Clear with fade for trail effect
            ctx.fillStyle = 'rgba(10, 10, 10, 0.2)';
            ctx.fillRect(0, 0, visualWidth, visualHeight);

            // Render current mode
            switch (modes[modeIndex]) {
                case 'pro_spectrum':
                    drawProSpectrum(ctx, dataArray, visualWidth, visualHeight);
                    break;
                case 'precision_scope':
                    drawPrecisionScope(ctx, dataArray, visualWidth, visualHeight);
                    break;
                case 'particle_field':
                    drawParticleField(ctx, dataArray, visualWidth, visualHeight);
                    break;
            }

            animationId = requestAnimationFrame(render);
        }
        render();
    }

    // ===== PRO SPECTRUM =====
    function drawProSpectrum(c, data, w, h) {
        const bars = 64;
        const barWidth = w / bars;
        const maxHeight = h * 0.8;

        // Create vibrant gradient
        const grad = c.createLinearGradient(0, h, 0, 0);
        grad.addColorStop(0, 'rgba(46, 139, 87, 0.3)');
        grad.addColorStop(0.5, 'rgba(59, 130, 246, 0.6)');
        grad.addColorStop(1, 'rgba(236, 72, 153, 0.9)');

        for (let i = 0; i < bars; i++) {
            const index = Math.floor((i / bars) * data.length);
            const value = data[index];
            const barHeight = (value / 255) * maxHeight;

            const x = i * barWidth;
            const y = h - barHeight;

            // Draw bar with gradient
            c.fillStyle = grad;
            c.fillRect(x, y, barWidth - 2, barHeight);

            // Add glow on peak
            if (value > 200) {
                c.shadowBlur = 20;
                c.shadowColor = '#ec4899';
                c.fillRect(x, y, barWidth - 2, 4);
                c.shadowBlur = 0;
            }
        }
    }

    // ===== PRECISION SCOPE =====
    function drawPrecisionScope(c, data, w, h) {
        c.lineWidth = 3;
        c.lineCap = 'round';
        c.lineJoin = 'round';

        // Emerald glow
        c.shadowBlur = 15;
        c.shadowColor = '#2E8B57';

        const grad = c.createLinearGradient(0, 0, w, 0);
        grad.addColorStop(0, '#00f0ff');
        grad.addColorStop(0.33, '#2E8B57');
        grad.addColorStop(0.66, '#8b5cf6');
        grad.addColorStop(1, '#ec4899');
        c.strokeStyle = grad;

        c.beginPath();

        const sliceWidth = w / data.length;
        let x = 0;

        for (let i = 0; i < data.length; i++) {
            const v = data[i] / 255.0;
            const y = (h / 2) + ((v - 0.5) * h * 0.7);

            if (i === 0) {
                c.moveTo(x, y);
            } else {
                c.lineTo(x, y);
            }

            x += sliceWidth;
        }

        c.stroke();
        c.shadowBlur = 0;
    }

    // ===== PARTICLE FIELD =====
    let particles = [];

    function drawParticleField(c, data, w, h) {
        // Initialize particles
        if (particles.length === 0) {
            for (let i = 0; i < 100; i++) {
                particles.push({
                    x: Math.random() * w,
                    y: Math.random() * h,
                    vx: (Math.random() - 0.5) * 2,
                    vy: (Math.random() - 0.5) * 2,
                    radius: 2 + Math.random() * 3,
                    freq: Math.floor(Math.random() * data.length)
                });
            }
        }

        particles.forEach((p, i) => {
            const intensity = data[p.freq] / 255;

            // Update position
            p.x += p.vx * (1 + intensity);
            p.y += p.vy * (1 + intensity);

            // Wrap around
            if (p.x < 0) p.x = w;
            if (p.x > w) p.x = 0;
            if (p.y < 0) p.y = h;
            if (p.y > h) p.y = 0;

            // Draw with glow
            c.beginPath();
            c.arc(p.x, p.y, p.radius * (1 + intensity), 0, Math.PI * 2);
            c.fillStyle = `rgba(46, 139, 87, ${intensity})`;
            c.fill();

            // Connection lines
            particles.slice(i + 1, i + 4).forEach(p2 => {
                const dist = Math.hypot(p2.x - p.x, p2.y - p.y);
                if (dist < 100) {
                    c.beginPath();
                    c.moveTo(p.x, p.y);
                    c.lineTo(p2.x, p2.y);
                    c.strokeStyle = `rgba(59, 130, 246, ${(1 - dist / 100) * 0.3})`;
                    c.lineWidth = 1;
                    c.stroke();
                }
            });
        });
    }

    function setMode(name) {
        const idx = modes.indexOf(name);
        if (idx >= 0) modeIndex = idx;
    }

    function setImmersive(active) {
        isImmersive = active;
    }

    window.addEventListener('resize', resize);

    return { init, setMode, setImmersive, getModes: () => modes, getAnalyser: () => analyser };
})();
