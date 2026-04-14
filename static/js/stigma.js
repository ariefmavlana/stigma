/**
 * STIgma — Frontend JS
 * ──────────────────────
 * Minimal, progressive-enhancement JS.
 * No frameworks. No dependencies.
 */

/* ── Scroll progress bar ──────────────────────────────────────────────────── */
(function () {
  const bar = document.createElement('div');
  bar.id = 'scroll-progress';
  document.body.prepend(bar);

  const updateProgress = () => {
    const scrollTop = window.scrollY;
    const docHeight = document.documentElement.scrollHeight - window.innerHeight;
    const pct = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;
    bar.style.width = pct + '%';
  };

  // Only show on post detail pages
  if (document.querySelector('.prose-stigma')) {
    window.addEventListener('scroll', updateProgress, { passive: true });
  }
})();

/* ── Lazy-load images ─────────────────────────────────────────────────────── */
(function () {
  if ('loading' in HTMLImageElement.prototype) return; // native support
  const images = document.querySelectorAll('img[loading="lazy"]');
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const img = entry.target;
        img.src = img.dataset.src || img.src;
        observer.unobserve(img);
      }
    });
  });
  images.forEach(img => observer.observe(img));
})();

/* ── Smooth anchor scroll ─────────────────────────────────────────────────── */
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', (e) => {
    const target = document.querySelector(anchor.getAttribute('href'));
    if (target) {
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  });
});

/* ── Copy code blocks ─────────────────────────────────────────────────────── */
document.querySelectorAll('.codehilite pre, .prose-stigma pre').forEach(pre => {
  const btn = document.createElement('button');
  btn.textContent = 'Copy';
  btn.style.cssText = `
    position: absolute; top: 0.5rem; right: 0.5rem;
    font-family: 'IBM Plex Mono', monospace; font-size: 0.65rem;
    text-transform: uppercase; letter-spacing: 0.1em;
    background: #2e2e2e; color: #a0a0a0;
    border: none; padding: 0.25rem 0.5rem; cursor: pointer;
  `;
  pre.style.position = 'relative';
  pre.parentNode.style.position = 'relative';
  pre.parentNode.appendChild(btn);

  btn.addEventListener('click', () => {
    navigator.clipboard.writeText(pre.textContent).then(() => {
      btn.textContent = 'Copied!';
      btn.style.color = '#f4f4f4';
      setTimeout(() => {
        btn.textContent = 'Copy';
        btn.style.color = '#a0a0a0';
      }, 1500);
    });
  });
});

/* ── Message auto-dismiss ─────────────────────────────────────────────────── */
setTimeout(() => {
  document.querySelectorAll('[data-auto-dismiss]').forEach(el => {
    el.style.transition = 'opacity 0.4s';
    el.style.opacity = '0';
    setTimeout(() => el.remove(), 400);
  });
}, 5000);
