/**
 * Matrix Rain Effect
 */
(function() {
  const canvas = document.getElementById('matrix-canvas');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');

  let width, height;
  const fontSize = 18;

  function resize() {
    const rect = canvas.parentElement.getBoundingClientRect();
    width = rect.width;
    height = rect.height;
    canvas.width = width;
    canvas.height = height;
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    initDrops();
  }

  // Matrix characters (katakana + numbers + symbols)
  const chars = 'アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン0123456789';
  const trailLength = 20;

  const primaryColor = '#7f3e98';

  let drops = [];

  function initDrops() {
    drops = [];
    const columnCount = Math.floor(width / fontSize);

    for (let i = 0; i < columnCount; i++) {
      drops.push({
        x: i * fontSize,
        y: Math.random() * -height * 2,
        speed: 0.5 + Math.random() * 1,
        chars: generateChars()
      });
    }
  }

  function generateChars() {
    const arr = [];
    for (let i = 0; i < trailLength; i++) {
      arr.push(chars[Math.floor(Math.random() * chars.length)]);
    }
    return arr;
  }

  function animate() {
    ctx.clearRect(0, 0, width, height);
    ctx.font = `${fontSize}px monospace`;

    for (const drop of drops) {
      // Draw trail
      for (let i = 0; i < trailLength; i++) {
        const charY = drop.y - i * fontSize;

        if (charY < -fontSize || charY > height + fontSize) continue;

        // Head character is bright, trail fades
        let alpha;
        if (i === 0) {
          alpha = 0.9; // Bright head
          ctx.fillStyle = '#ffffff';
        } else {
          alpha = (1 - i / trailLength) * 0.5;
          ctx.fillStyle = primaryColor;
        }

        ctx.globalAlpha = alpha;
        ctx.fillText(drop.chars[i], drop.x, charY);
      }

      // Update position
      drop.y += drop.speed;

      // Randomly change characters in trail - all chars flicker
      for (let i = 0; i < trailLength; i++) {
        if (Math.random() < 0.15) {
          drop.chars[i] = chars[Math.floor(Math.random() * chars.length)];
        }
      }

      // Reset when fully off screen
      if (drop.y - trailLength * fontSize > height) {
        drop.y = Math.random() * -height;
        drop.speed = 0.5 + Math.random() * 1;
        drop.chars = generateChars();
      }
    }

    ctx.globalAlpha = 1;
    requestAnimationFrame(animate);
  }

  resize();
  window.addEventListener('resize', resize);
  animate();
})();
