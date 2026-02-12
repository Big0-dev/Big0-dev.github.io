/**
 * Text Scramble Effect
 * Cyberpunk-style text scramble for the hero headline.
 * Adapted for the dark engineering aesthetic.
 */
class TextScramble {
  constructor(el) {
    this.el = el;
    this.chars = '!<>-_\\/[]{}—=+*^?#@$%&01';
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
        if (Math.random() < 0.02) {
          output += '<span class="scramble-char glitch">' + this.randomChar() + '</span>';
        } else {
          output += to;
        }
      } else if (this.frame >= start) {
        if (Math.random() < 0.5) {
          char = this.randomChar();
          this.queue[i].char = char;
        }
        const cls = Math.random() < 0.15 ? 'scramble-char glitch-intense' : 'scramble-char';
        output += '<span class="' + cls + '">' + char + '</span>';
      } else {
        if (Math.random() < 0.04) {
          output += '<span class="scramble-char glitch">' + this.randomChar() + '</span>';
        } else {
          output += from;
        }
      }
    }

    this.el.innerHTML = output;

    if (complete === this.queue.length) {
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

document.addEventListener('DOMContentLoaded', function() {
  const el = document.querySelector('.hero-scramble');
  if (!el) return;

  const phrases = [
    'Without the Overhead',
    'Senior Engineers Only',
    'Ship Every Two Weeks',
    'No Salespeople',
    'Research-Backed AI',
    'Startup-Ready',
    'Code, Not Slide Decks',
    'Engineers You Trust'
  ];

  const fx = new TextScramble(el);
  let counter = 0;

  const next = () => {
    fx.setText(phrases[counter]).then(() => {
      setTimeout(next, 3500);
    });
    counter = (counter + 1) % phrases.length;
  };

  if ('requestIdleCallback' in window) {
    requestIdleCallback(() => next(), { timeout: 800 });
  } else {
    setTimeout(next, 400);
  }
});
