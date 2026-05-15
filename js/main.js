/* ============================================================
   AGENTY — main.js
   ============================================================ */

(function () {
  'use strict';

  // ── Nav scroll ────────────────────────────────────────────
  const nav = document.getElementById('nav');
  if (nav) {
    const onScroll = () => nav.classList.toggle('scrolled', window.scrollY > 20);
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  // ── Mobile menu ───────────────────────────────────────────
  const mobileBtn = document.getElementById('mobile-btn');
  const mobileMenu = document.getElementById('mobile-menu');
  if (mobileBtn && mobileMenu) {
    mobileBtn.addEventListener('click', () => {
      const isOpen = mobileMenu.classList.toggle('open');
      mobileBtn.classList.toggle('open', isOpen);
      mobileBtn.setAttribute('aria-expanded', String(isOpen));
      document.body.style.overflow = isOpen ? 'hidden' : '';
    });
    mobileMenu.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => {
        mobileMenu.classList.remove('open');
        mobileBtn.classList.remove('open');
        mobileBtn.setAttribute('aria-expanded', 'false');
        document.body.style.overflow = '';
      });
    });
    document.addEventListener('click', (e) => {
      if (!nav.contains(e.target) && mobileMenu.classList.contains('open')) {
        mobileMenu.classList.remove('open');
        mobileBtn.classList.remove('open');
        mobileBtn.setAttribute('aria-expanded', 'false');
        document.body.style.overflow = '';
      }
    });
  }

  // ── Scroll animations ─────────────────────────────────────
  const animatedEls = document.querySelectorAll('[data-animate]');
  if (animatedEls.length > 0 && 'IntersectionObserver' in window) {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            entry.target.classList.add('visible');
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.1, rootMargin: '0px 0px -32px 0px' }
    );
    animatedEls.forEach(el => observer.observe(el));
  } else {
    animatedEls.forEach(el => el.classList.add('visible'));
  }

  // ── FAQ accordion ─────────────────────────────────────────
  document.querySelectorAll('.faq-item__btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const item = btn.closest('.faq-item');
      const isOpen = item.classList.contains('open');
      const list = item.closest('.faq-list');
      if (list) {
        list.querySelectorAll('.faq-item.open').forEach(openItem => {
          if (openItem !== item) {
            openItem.classList.remove('open');
            openItem.querySelector('.faq-item__btn').setAttribute('aria-expanded', 'false');
          }
        });
      }
      item.classList.toggle('open', !isOpen);
      btn.setAttribute('aria-expanded', String(!isOpen));
    });
  });

  // ── Smooth scroll ─────────────────────────────────────────
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', (e) => {
      const target = document.querySelector(anchor.getAttribute('href'));
      if (!target) return;
      e.preventDefault();
      const navH = nav ? nav.offsetHeight : 0;
      const top = target.getBoundingClientRect().top + window.scrollY - navH - 16;
      window.scrollTo({ top, behavior: 'smooth' });
    });
  });

  // ── TextRotate ────────────────────────────────────────────
  //
  // Replicates the TextRotate React component in vanilla JS.
  // Characters animate in from below (translateY 120% → 0) with stagger,
  // and exit upward (translateY 0 → -130%) before the next text enters.
  //
  const rotateEl = document.getElementById('rotate-text');
  const rotateSr = document.getElementById('rotate-sr');

  if (rotateEl && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {

    const TEXTS = [
      'fatura mais.',
      'atende melhor.',
      'cresce mais.',
      'trabalha menos.',
    ];

    const ENTER_STAGGER  = 0.034;  // seconds between characters on enter
    const EXIT_STAGGER   = 0.022;  // seconds between characters on exit
    const ENTER_DURATION = 0.62;   // seconds for each char transition (enter)
    const EXIT_DURATION  = 0.38;   // seconds for each char transition (exit)
    const HOLD_MS        = 2600;   // milliseconds text stays visible

    let current = 0;
    let running = false;

    function buildChars(text) {
      rotateEl.innerHTML = '';
      return [...text].map(char => {
        const span = document.createElement('span');
        span.className = 'char';
        span.textContent = char === ' ' ? ' ' : char;
        // Start below the clip area immediately (before appending)
        span.style.cssText = 'display:inline-block;transform:translateY(120%);opacity:0;';
        rotateEl.appendChild(span);
        return span;
      });
    }

    function enterChars(spans) {
      // Force a reflow so the browser registers the initial transform
      // before the transition starts — otherwise it would skip the animation.
      rotateEl.getBoundingClientRect();

      spans.forEach((span, i) => {
        const delay = i * ENTER_STAGGER;
        span.style.transition =
          `transform ${ENTER_DURATION}s cubic-bezier(0.34, 1.4, 0.64, 1) ${delay}s,` +
          `opacity 0.4s ease ${delay}s`;
        span.style.transform = 'translateY(0)';
        span.style.opacity   = '1';
      });
    }

    function exitChars(spans) {
      return new Promise(resolve => {
        spans.forEach((span, i) => {
          const delay = i * EXIT_STAGGER;
          span.style.transition =
            `transform ${EXIT_DURATION}s cubic-bezier(0.55, 0, 1, 0.45) ${delay}s,` +
            `opacity 0.25s ease ${delay}s`;
          span.style.transform = 'translateY(-130%)';
          span.style.opacity   = '0';
        });

        // Resolve after the last character finishes exiting
        const totalMs = (spans.length * EXIT_STAGGER + EXIT_DURATION) * 1000;
        setTimeout(resolve, totalMs);
      });
    }

    async function rotate() {
      if (running) return;
      running = true;

      const currentSpans = [...rotateEl.querySelectorAll('.char')];
      await exitChars(currentSpans);

      current = (current + 1) % TEXTS.length;
      rotateSr.textContent = TEXTS[current];

      const newSpans = buildChars(TEXTS[current]);
      enterChars(newSpans);

      // Wait for the enter animation to settle before releasing the lock
      const enterTotal = (newSpans.length * ENTER_STAGGER + ENTER_DURATION) * 1000;
      setTimeout(() => { running = false; }, enterTotal);
    }

    // Initialise: build first text and animate in
    const initSpans = buildChars(TEXTS[0]);
    rotateSr.textContent = TEXTS[0];
    // Small delay so the page has rendered before the first animation
    setTimeout(() => {
      enterChars(initSpans);
      setInterval(rotate, HOLD_MS);
    }, 300);
  }

  // ── Stat counter animation ────────────────────────────────
  function animateCounter(el, target, duration) {
    const start = performance.now();
    const isFloat = String(target).includes('.');
    const update = (now) => {
      const progress = Math.min((now - start) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      const val = eased * target;
      el.textContent = isFloat ? val.toFixed(1) : Math.floor(val).toLocaleString('pt-BR');
      if (progress < 1) requestAnimationFrame(update);
      else el.textContent = isFloat ? target.toFixed(1) : target.toLocaleString('pt-BR');
    };
    requestAnimationFrame(update);
  }

  const statNums = document.querySelectorAll('.stat__num');
  if (statNums.length > 0 && 'IntersectionObserver' in window) {
    const statObserver = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        const el = entry.target;
        const raw = el.textContent.trim();
        const match = raw.match(/([+\-−]?)(\d+(?:\.\d+)?)(.*)/);
        if (match) {
          const prefix = match[1];
          const num    = parseFloat(match[2]);
          const suffix = match[3];
          el.innerHTML = '';
          const pre   = document.createTextNode(prefix);
          const count = document.createElement('span');
          const suf   = document.createTextNode(suffix);
          count.textContent = '0';
          el.appendChild(pre);
          el.appendChild(count);
          el.appendChild(suf);
          setTimeout(() => animateCounter(count, num, 1200), 200);
        }
        statObserver.unobserve(el);
      });
    }, { threshold: 0.5 });
    statNums.forEach(el => statObserver.observe(el));
  }

})();
