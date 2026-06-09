/**
 * 科幻动态线条背景（Canvas）
 */
(function initSciFiBackground() {
    const canvas = document.getElementById('sci-fi-canvas');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    let width = 0;
    let height = 0;
    let animationId = null;
    let tick = 0;

    const nodes = [];
    const pulses = [];
    const NODE_COUNT = 48;
    const MAX_LINK_DIST = 160;

    function readCssVar(name, fallback) {
        const value = getComputedStyle(document.documentElement).getPropertyValue(name).trim();
        return value || fallback;
    }

    function resize() {
        width = window.innerWidth;
        height = window.innerHeight;
        canvas.width = width;
        canvas.height = height;
        initNodes();
    }

    function initNodes() {
        nodes.length = 0;
        for (let i = 0; i < NODE_COUNT; i += 1) {
            nodes.push({
                x: Math.random() * width,
                y: Math.random() * height,
                vx: (Math.random() - 0.5) * 0.35,
                vy: (Math.random() - 0.5) * 0.35,
                r: 1.2 + Math.random() * 1.8,
            });
        }
    }

    function maybeSpawnPulse(x1, y1, x2, y2) {
        if (Math.random() > 0.004) return;
        pulses.push({
            x1, y1, x2, y2,
            t: 0,
            speed: 0.012 + Math.random() * 0.02,
        });
    }

    function drawGrid() {
        const gridColor = readCssVar('--line-grid', 'rgba(96, 165, 250, 0.12)');
        const step = 56;
        const offset = (tick * 0.4) % step;

        ctx.strokeStyle = gridColor;
        ctx.lineWidth = 1;

        for (let x = -step; x < width + step; x += step) {
            ctx.beginPath();
            ctx.moveTo(x + offset, 0);
            ctx.lineTo(x + offset, height);
            ctx.stroke();
        }

        for (let y = -step; y < height + step; y += step) {
            ctx.beginPath();
            ctx.moveTo(0, y + offset * 0.6);
            ctx.lineTo(width, y + offset * 0.6);
            ctx.stroke();
        }
    }

    function drawLinks() {
        const lineColor = readCssVar('--line-color', 'rgba(20, 184, 166, 0.22)');

        for (let i = 0; i < nodes.length; i += 1) {
            for (let j = i + 1; j < nodes.length; j += 1) {
                const a = nodes[i];
                const b = nodes[j];
                const dx = a.x - b.x;
                const dy = a.y - b.y;
                const dist = Math.hypot(dx, dy);
                if (dist > MAX_LINK_DIST) continue;

                const alpha = (1 - dist / MAX_LINK_DIST) * 0.55;
                ctx.globalAlpha = alpha;
                ctx.strokeStyle = lineColor;
                ctx.lineWidth = 1;
                ctx.beginPath();
                ctx.moveTo(a.x, a.y);
                ctx.lineTo(b.x, b.y);
                ctx.stroke();
                ctx.globalAlpha = 1;

                maybeSpawnPulse(a.x, a.y, b.x, b.y);
            }
        }
    }

    function drawNodes() {
        const glow = readCssVar('--line-glow', 'rgba(6, 182, 212, 0.55)');
        const primary = readCssVar('--primary-color', '#14B8A6');

        nodes.forEach((node) => {
            node.x += node.vx;
            node.y += node.vy;

            if (node.x < 0 || node.x > width) node.vx *= -1;
            if (node.y < 0 || node.y > height) node.vy *= -1;

            const gradient = ctx.createRadialGradient(node.x, node.y, 0, node.x, node.y, node.r * 4);
            gradient.addColorStop(0, glow);
            gradient.addColorStop(1, 'rgba(6, 182, 212, 0)');

            ctx.fillStyle = gradient;
            ctx.beginPath();
            ctx.arc(node.x, node.y, node.r * 4, 0, Math.PI * 2);
            ctx.fill();

            ctx.fillStyle = primary;
            ctx.beginPath();
            ctx.arc(node.x, node.y, node.r, 0, Math.PI * 2);
            ctx.fill();
        });
    }

    function drawPulses() {
        const glow = readCssVar('--line-glow', 'rgba(6, 182, 212, 0.55)');

        for (let i = pulses.length - 1; i >= 0; i -= 1) {
            const pulse = pulses[i];
            pulse.t += pulse.speed;
            if (pulse.t >= 1) {
                pulses.splice(i, 1);
                continue;
            }

            const x = pulse.x1 + (pulse.x2 - pulse.x1) * pulse.t;
            const y = pulse.y1 + (pulse.y2 - pulse.y1) * pulse.t;

            ctx.strokeStyle = glow;
            ctx.lineWidth = 2;
            ctx.shadowColor = glow;
            ctx.shadowBlur = 12;
            ctx.beginPath();
            ctx.arc(x, y, 2.5, 0, Math.PI * 2);
            ctx.stroke();
            ctx.shadowBlur = 0;
        }
    }

    function drawScanLine() {
        const y = ((tick * 1.2) % (height + 120)) - 60;
        const gradient = ctx.createLinearGradient(0, y - 30, 0, y + 30);
        gradient.addColorStop(0, 'rgba(6, 182, 212, 0)');
        gradient.addColorStop(0.5, 'rgba(20, 184, 166, 0.08)');
        gradient.addColorStop(1, 'rgba(6, 182, 212, 0)');
        ctx.fillStyle = gradient;
        ctx.fillRect(0, y - 30, width, 60);
    }

    function frame() {
        tick += 1;
        ctx.clearRect(0, 0, width, height);
        drawGrid();
        drawLinks();
        drawNodes();
        drawPulses();
        drawScanLine();
        animationId = requestAnimationFrame(frame);
    }

    resize();
    frame();

    window.addEventListener('resize', () => {
        resize();
    });

    document.addEventListener('visibilitychange', () => {
        if (document.hidden) {
            cancelAnimationFrame(animationId);
        } else {
            frame();
        }
    });
})();
