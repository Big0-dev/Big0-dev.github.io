/**
 * Ultimate Futuristic Hero Animation
 * Combines: Cyber Grid, DNA Helix, Circuit Board, Morphing Blob, Starfield,
 * Hexagon Network, Wave Lines, Glitch Effect, and Geometric Shapes
 */
(function() {
  'use strict';

  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (prefersReducedMotion) return;

  const heroSection = document.querySelector('.page-hero');
  if (!heroSection) return;

  // Create container
  const container = document.createElement('div');
  container.className = 'hero-bg-animation';
  container.innerHTML = `
    <canvas class="hero-canvas-main"></canvas>
  `;
  heroSection.insertBefore(container, heroSection.firstChild);

  const canvas = container.querySelector('.hero-canvas-main');
  const ctx = canvas.getContext('2d');

  let width, height;
  let animationId;
  let isVisible = true;
  let time = 0;

  // Color palette
  const colors = {
    primary: { r: 127, g: 62, b: 152 },
    secondary: { r: 163, g: 102, b: 196 },
    accent: { r: 200, g: 150, b: 255 },
    cyan: { r: 0, g: 255, b: 255 },
    white: { r: 255, g: 255, b: 255 }
  };

  // ========== STARFIELD ==========
  const stars = [];
  const STAR_COUNT = 150;

  function initStars() {
    stars.length = 0;
    for (let i = 0; i < STAR_COUNT; i++) {
      stars.push({
        x: Math.random() * width - width / 2,
        y: Math.random() * height - height / 2,
        z: Math.random() * 1000,
        size: Math.random() * 2 + 0.5
      });
    }
  }

  function drawStarfield() {
    const cx = width / 2;
    const cy = height / 2;

    stars.forEach(star => {
      star.z -= 2;
      if (star.z <= 0) {
        star.x = Math.random() * width - width / 2;
        star.y = Math.random() * height - height / 2;
        star.z = 1000;
      }

      const sx = (star.x / star.z) * 300 + cx;
      const sy = (star.y / star.z) * 300 + cy;
      const size = (1 - star.z / 1000) * star.size * 2;
      const alpha = (1 - star.z / 1000) * 0.8;

      if (sx >= 0 && sx <= width && sy >= 0 && sy <= height) {
        ctx.beginPath();
        ctx.arc(sx, sy, size, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(255, 255, 255, ${alpha})`;
        ctx.fill();

        // Trail
        const tx = ((star.x / (star.z + 50)) * 300 + cx);
        const ty = ((star.y / (star.z + 50)) * 300 + cy);
        ctx.beginPath();
        ctx.moveTo(sx, sy);
        ctx.lineTo(tx, ty);
        ctx.strokeStyle = `rgba(${colors.secondary.r}, ${colors.secondary.g}, ${colors.secondary.b}, ${alpha * 0.3})`;
        ctx.lineWidth = size * 0.5;
        ctx.stroke();
      }
    });
  }

  // ========== CYBER GRID ==========
  function drawCyberGrid() {
    const horizon = height * 0.7;
    const gridLines = 15;
    const perspective = 400;

    ctx.save();
    ctx.globalAlpha = 0.3;

    // Horizontal lines (receding)
    for (let i = 0; i < gridLines; i++) {
      const ratio = i / gridLines;
      const y = horizon + (height - horizon) * Math.pow(ratio, 1.5);
      const alpha = ratio * 0.5;

      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(width, y);
      ctx.strokeStyle = `rgba(${colors.primary.r}, ${colors.primary.g}, ${colors.primary.b}, ${alpha})`;
      ctx.lineWidth = 1;
      ctx.stroke();
    }

    // Vertical lines (perspective)
    const vanishX = width / 2;
    for (let i = -10; i <= 10; i++) {
      const bottomX = vanishX + i * 80;
      const alpha = 0.3 - Math.abs(i) * 0.02;

      ctx.beginPath();
      ctx.moveTo(vanishX, horizon);
      ctx.lineTo(bottomX, height);
      ctx.strokeStyle = `rgba(${colors.primary.r}, ${colors.primary.g}, ${colors.primary.b}, ${alpha})`;
      ctx.lineWidth = 1;
      ctx.stroke();
    }

    // Pulsing glow on horizon
    const pulseAlpha = 0.2 + Math.sin(time * 0.02) * 0.1;
    const gradient = ctx.createLinearGradient(0, horizon - 30, 0, horizon + 30);
    gradient.addColorStop(0, 'transparent');
    gradient.addColorStop(0.5, `rgba(${colors.accent.r}, ${colors.accent.g}, ${colors.accent.b}, ${pulseAlpha})`);
    gradient.addColorStop(1, 'transparent');
    ctx.fillStyle = gradient;
    ctx.fillRect(0, horizon - 30, width, 60);

    ctx.restore();
  }

  // ========== DNA HELIX ==========
  const helixNodes = [];
  const HELIX_SEGMENTS = 20;

  function drawDNAHelix() {
    const centerX = width * 0.85;
    const startY = 50;
    const helixHeight = height - 100;
    const radius = 40;
    const twist = time * 0.02;

    ctx.save();
    ctx.globalAlpha = 0.6;

    for (let i = 0; i < HELIX_SEGMENTS; i++) {
      const progress = i / HELIX_SEGMENTS;
      const y = startY + progress * helixHeight;
      const angle = progress * Math.PI * 4 + twist;

      const x1 = centerX + Math.cos(angle) * radius;
      const x2 = centerX + Math.cos(angle + Math.PI) * radius;

      // Draw connecting bar
      ctx.beginPath();
      ctx.moveTo(x1, y);
      ctx.lineTo(x2, y);
      ctx.strokeStyle = `rgba(${colors.secondary.r}, ${colors.secondary.g}, ${colors.secondary.b}, 0.3)`;
      ctx.lineWidth = 2;
      ctx.stroke();

      // Draw nodes
      const nodeSize = 4 + Math.sin(angle) * 2;
      ctx.beginPath();
      ctx.arc(x1, y, nodeSize, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(${colors.primary.r}, ${colors.primary.g}, ${colors.primary.b}, 0.8)`;
      ctx.fill();

      ctx.beginPath();
      ctx.arc(x2, y, nodeSize, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(${colors.accent.r}, ${colors.accent.g}, ${colors.accent.b}, 0.8)`;
      ctx.fill();
    }

    ctx.restore();
  }

  // ========== CIRCUIT BOARD ==========
  const circuits = [];
  const CIRCUIT_COUNT = 8;

  function initCircuits() {
    circuits.length = 0;
    for (let i = 0; i < CIRCUIT_COUNT; i++) {
      circuits.push(createCircuit());
    }
  }

  function createCircuit() {
    const startX = Math.random() * width * 0.3;
    const startY = Math.random() * height;
    const path = [{ x: startX, y: startY }];
    let x = startX, y = startY;

    for (let j = 0; j < 5 + Math.random() * 5; j++) {
      const dir = Math.random() > 0.5;
      if (dir) {
        x += 30 + Math.random() * 50;
      } else {
        y += (Math.random() > 0.5 ? 1 : -1) * (20 + Math.random() * 30);
      }
      path.push({ x, y });
    }

    return {
      path,
      progress: 0,
      speed: 0.005 + Math.random() * 0.01,
      active: Math.random() > 0.5
    };
  }

  function drawCircuits() {
    ctx.save();
    ctx.globalAlpha = 0.4;

    circuits.forEach(circuit => {
      if (!circuit.active) {
        if (Math.random() < 0.002) circuit.active = true;
        return;
      }

      circuit.progress += circuit.speed;
      if (circuit.progress > 1) {
        circuit.progress = 0;
        circuit.active = Math.random() > 0.3;
        Object.assign(circuit, createCircuit());
      }

      const path = circuit.path;
      const totalLen = path.length - 1;
      const currentSegment = Math.floor(circuit.progress * totalLen);
      const segmentProgress = (circuit.progress * totalLen) % 1;

      // Draw full path dimly
      ctx.beginPath();
      ctx.moveTo(path[0].x, path[0].y);
      for (let i = 1; i < path.length; i++) {
        ctx.lineTo(path[i].x, path[i].y);
      }
      ctx.strokeStyle = `rgba(${colors.primary.r}, ${colors.primary.g}, ${colors.primary.b}, 0.2)`;
      ctx.lineWidth = 2;
      ctx.stroke();

      // Draw active segment
      if (currentSegment < path.length - 1) {
        const from = path[currentSegment];
        const to = path[currentSegment + 1];
        const currentX = from.x + (to.x - from.x) * segmentProgress;
        const currentY = from.y + (to.y - from.y) * segmentProgress;

        // Glowing dot
        ctx.beginPath();
        ctx.arc(currentX, currentY, 4, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(${colors.cyan.r}, ${colors.cyan.g}, ${colors.cyan.b}, 0.9)`;
        ctx.shadowColor = `rgba(${colors.cyan.r}, ${colors.cyan.g}, ${colors.cyan.b}, 1)`;
        ctx.shadowBlur = 10;
        ctx.fill();
        ctx.shadowBlur = 0;

        // Draw nodes at corners
        path.forEach((point, idx) => {
          if (idx <= currentSegment) {
            ctx.beginPath();
            ctx.arc(point.x, point.y, 3, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(${colors.accent.r}, ${colors.accent.g}, ${colors.accent.b}, 0.8)`;
            ctx.fill();
          }
        });
      }
    });

    ctx.restore();
  }

  // ========== HEXAGON NETWORK ==========
  function drawHexagonNetwork() {
    const hexSize = 45;
    const hexHeight = hexSize * Math.sqrt(3);
    const cols = Math.ceil(width / (hexSize * 1.5)) + 1;
    const rows = Math.ceil(height / hexHeight) + 1;

    ctx.save();

    for (let row = 0; row < rows; row++) {
      for (let col = 0; col < cols; col++) {
        const x = col * hexSize * 1.5;
        const y = row * hexHeight + (col % 2 ? hexHeight / 2 : 0);

        // Pulse based on position and time
        const dist = Math.sqrt(Math.pow(x - width/2, 2) + Math.pow(y - height/2, 2));
        const pulse = Math.sin(dist * 0.008 - time * 0.025) * 0.5 + 0.5;
        const alpha = 0.25 + pulse * 0.35;

        drawHexagon(x, y, hexSize * 0.9, alpha);
      }
    }

    ctx.restore();
  }

  function drawHexagon(x, y, size, alpha) {
    ctx.beginPath();
    for (let i = 0; i < 6; i++) {
      const angle = (Math.PI / 3) * i - Math.PI / 6;
      const hx = x + size * Math.cos(angle);
      const hy = y + size * Math.sin(angle);
      if (i === 0) ctx.moveTo(hx, hy);
      else ctx.lineTo(hx, hy);
    }
    ctx.closePath();
    ctx.strokeStyle = `rgba(${colors.primary.r}, ${colors.primary.g}, ${colors.primary.b}, ${alpha})`;
    ctx.lineWidth = 1;
    ctx.stroke();
  }

  // ========== WAVE LINES ==========
  function drawWaveLines() {
    const waveCount = 5;
    ctx.save();

    for (let w = 0; w < waveCount; w++) {
      const baseY = height * 0.3 + w * 30;
      const amplitude = 20 + w * 5;
      const frequency = 0.005 + w * 0.001;
      const speed = 0.02 + w * 0.005;
      const alpha = 0.2 - w * 0.03;

      ctx.beginPath();
      for (let x = 0; x <= width; x += 5) {
        const y = baseY + Math.sin(x * frequency + time * speed) * amplitude
                       + Math.sin(x * frequency * 2 + time * speed * 1.5) * (amplitude * 0.3);
        if (x === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      ctx.strokeStyle = `rgba(${colors.secondary.r}, ${colors.secondary.g}, ${colors.secondary.b}, ${alpha})`;
      ctx.lineWidth = 2;
      ctx.stroke();
    }

    ctx.restore();
  }

  // ========== GEOMETRIC SHAPES ==========
  const shapes = [];
  const SHAPE_COUNT = 5;

  function initShapes() {
    shapes.length = 0;
    for (let i = 0; i < SHAPE_COUNT; i++) {
      shapes.push({
        x: Math.random() * width,
        y: Math.random() * height,
        size: 30 + Math.random() * 40,
        type: Math.floor(Math.random() * 3), // 0: cube, 1: pyramid, 2: octahedron
        rotationX: Math.random() * Math.PI * 2,
        rotationY: Math.random() * Math.PI * 2,
        rotationZ: Math.random() * Math.PI * 2,
        speedX: (Math.random() - 0.5) * 0.02,
        speedY: (Math.random() - 0.5) * 0.02,
        speedZ: (Math.random() - 0.5) * 0.02,
        vx: (Math.random() - 0.5) * 0.5,
        vy: (Math.random() - 0.5) * 0.5
      });
    }
  }

  function drawGeometricShapes() {
    ctx.save();
    ctx.globalAlpha = 0.4;

    shapes.forEach(shape => {
      shape.rotationX += shape.speedX;
      shape.rotationY += shape.speedY;
      shape.rotationZ += shape.speedZ;
      shape.x += shape.vx;
      shape.y += shape.vy;

      // Bounce off edges
      if (shape.x < 0 || shape.x > width) shape.vx *= -1;
      if (shape.y < 0 || shape.y > height) shape.vy *= -1;

      drawWireframeShape(shape);
    });

    ctx.restore();
  }

  function drawWireframeShape(shape) {
    let vertices;
    let edges;

    if (shape.type === 0) {
      // Cube
      const s = shape.size / 2;
      vertices = [
        [-s, -s, -s], [s, -s, -s], [s, s, -s], [-s, s, -s],
        [-s, -s, s], [s, -s, s], [s, s, s], [-s, s, s]
      ];
      edges = [[0,1],[1,2],[2,3],[3,0],[4,5],[5,6],[6,7],[7,4],[0,4],[1,5],[2,6],[3,7]];
    } else if (shape.type === 1) {
      // Pyramid
      const s = shape.size / 2;
      vertices = [
        [0, -s, 0], [-s, s, -s], [s, s, -s], [s, s, s], [-s, s, s]
      ];
      edges = [[0,1],[0,2],[0,3],[0,4],[1,2],[2,3],[3,4],[4,1]];
    } else {
      // Octahedron
      const s = shape.size / 2;
      vertices = [
        [0, -s, 0], [0, s, 0], [-s, 0, 0], [s, 0, 0], [0, 0, -s], [0, 0, s]
      ];
      edges = [[0,2],[0,3],[0,4],[0,5],[1,2],[1,3],[1,4],[1,5],[2,4],[4,3],[3,5],[5,2]];
    }

    // Rotate and project vertices
    const projected = vertices.map(v => {
      let [x, y, z] = v;

      // Rotate X
      let y1 = y * Math.cos(shape.rotationX) - z * Math.sin(shape.rotationX);
      let z1 = y * Math.sin(shape.rotationX) + z * Math.cos(shape.rotationX);
      y = y1; z = z1;

      // Rotate Y
      let x1 = x * Math.cos(shape.rotationY) + z * Math.sin(shape.rotationY);
      z1 = -x * Math.sin(shape.rotationY) + z * Math.cos(shape.rotationY);
      x = x1; z = z1;

      // Rotate Z
      x1 = x * Math.cos(shape.rotationZ) - y * Math.sin(shape.rotationZ);
      y1 = x * Math.sin(shape.rotationZ) + y * Math.cos(shape.rotationZ);
      x = x1; y = y1;

      // Project to 2D
      const scale = 200 / (200 + z);
      return {
        x: shape.x + x * scale,
        y: shape.y + y * scale
      };
    });

    // Draw edges
    edges.forEach(([i, j]) => {
      ctx.beginPath();
      ctx.moveTo(projected[i].x, projected[i].y);
      ctx.lineTo(projected[j].x, projected[j].y);
      ctx.strokeStyle = `rgba(${colors.accent.r}, ${colors.accent.g}, ${colors.accent.b}, 0.6)`;
      ctx.lineWidth = 1.5;
      ctx.stroke();
    });

    // Draw vertices
    projected.forEach(p => {
      ctx.beginPath();
      ctx.arc(p.x, p.y, 2, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(${colors.white.r}, ${colors.white.g}, ${colors.white.b}, 0.8)`;
      ctx.fill();
    });
  }

  // ========== MORPHING BLOB (CSS) ==========
  function updateBlob() {
    const blobTime = time * 0.001;
    const r1 = 30 + Math.sin(blobTime * 2) * 10;
    const r2 = 40 + Math.cos(blobTime * 1.5) * 15;
    const r3 = 35 + Math.sin(blobTime * 2.5) * 12;
    const r4 = 45 + Math.cos(blobTime * 1.8) * 10;

    blob.style.borderRadius = `${r1}% ${100-r1}% ${r2}% ${100-r2}% / ${r3}% ${r4}% ${100-r4}% ${100-r3}%`;
    blob.style.transform = `translate(-50%, -50%) rotate(${time * 0.1}deg)`;
  }

  // ========== GLITCH EFFECT (Disabled - was causing flashes) ==========
  function updateGlitch() {
    // Glitch effect disabled to prevent unwanted flashing
    // Keep the function for potential future use with user toggle
  }

  // ========== MAIN ANIMATION ==========
  function resize() {
    const rect = heroSection.getBoundingClientRect();
    width = canvas.width = rect.width;
    height = canvas.height = rect.height;
    initStars();
  }

  function animate() {
    if (!isVisible) {
      animationId = requestAnimationFrame(animate);
      return;
    }

    time++;
    ctx.clearRect(0, 0, width, height);

    // Layer 1: Background elements
    drawCyberGrid();

    // Layer 2: Mid-ground
    drawStarfield();

    // CSS animations
    updateGlitch();

    animationId = requestAnimationFrame(animate);
  }

  // Visibility observer
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      isVisible = entry.isIntersecting;
    });
  }, { threshold: 0 });

  // Initialize
  resize();
  observer.observe(heroSection);

  if ('requestIdleCallback' in window) {
    requestIdleCallback(() => animate(), { timeout: 100 });
  } else {
    setTimeout(animate, 100);
  }

  let resizeTimeout;
  window.addEventListener('resize', () => {
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(resize, 200);
  });

  window.addEventListener('beforeunload', () => {
    if (animationId) cancelAnimationFrame(animationId);
    observer.disconnect();
  });
})();
