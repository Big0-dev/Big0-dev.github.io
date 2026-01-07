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
