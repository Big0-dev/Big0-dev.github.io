/**
 * Text Scramble Effect
 * Creates a cyberpunk-style text scramble animation with glitches
 */
class TextScramble {
  constructor(el) {
    this.el = el;
    this.chars = '!<>-_\\/[]{}—=+*^?#@$%&アイウエオカキク01';
    this.update = this.update.bind(this);
  }

  setText(newText) {
    const oldText = this.el.innerText;
    const length = Math.max(oldText.length, newText.length);
    const promise = new Promise((resolve) => this.resolve = resolve);
    this.queue = [];

    for (let i = 0; i < length; i++) {
      const from = oldText[i] || '';
      const to = newText[i] || '';
      const start = Math.floor(Math.random() * 30);
      const end = start + Math.floor(Math.random() * 50);
      this.queue.push({ from, to, start, end, char: this.randomChar() });
    }

    cancelAnimationFrame(this.frameRequest);
    this.frame = 0;
    this.update();
    return promise;
  }

  update() {
    let output = '';
    let complete = 0;

    for (let i = 0, n = this.queue.length; i < n; i++) {
      let { from, to, start, end, char } = this.queue[i];

      if (this.frame >= end) {
        complete++;
        // Even completed chars occasionally glitch
        if (Math.random() < 0.03) {
          output += `<span class="scramble-char glitch">${this.randomChar()}</span>`;
        } else {
          output += to;
        }
      } else if (this.frame >= start) {
        // High frequency character changes for more glitchy effect
        if (Math.random() < 0.5) {
          char = this.randomChar();
          this.queue[i].char = char;
        }
        // Random glitch intensity
        const glitchClass = Math.random() < 0.2 ? 'scramble-char glitch-intense' : 'scramble-char';
        output += `<span class="${glitchClass}">${char}</span>`;
      } else {
        // Pre-start chars also occasionally glitch
        if (Math.random() < 0.05) {
          output += `<span class="scramble-char glitch">${this.randomChar()}</span>`;
        } else {
          output += from;
        }
      }
    }

    this.el.innerHTML = output;

    if (complete === this.queue.length) {
      // Small delay then resolve to let final glitches settle
      setTimeout(() => this.resolve(), 100);
    } else {
      this.frameRequest = requestAnimationFrame(this.update);
      this.frame++;
    }
  }

  randomChar() {
    return this.chars[Math.floor(Math.random() * this.chars.length)];
  }
}

// Initialize text scramble on hero section
document.addEventListener('DOMContentLoaded', function() {
  const el = document.querySelector('.hero-scramble-text');
  if (!el) return;

  const phrases = [
    'Next Level Innovation',
    'AI-Powered Solutions',
    'Digital Transformation',
    'Intelligent Automation',
    'Data-Driven Growth'
  ];

  const fx = new TextScramble(el);
  let counter = 0;

  const next = () => {
    fx.setText(phrases[counter]).then(() => {
      setTimeout(next, 3000);
    });
    counter = (counter + 1) % phrases.length;
  };

  // Start the animation
  next();
});
