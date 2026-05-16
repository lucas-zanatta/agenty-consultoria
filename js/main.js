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
  const mobileBtn  = document.getElementById('mobile-btn');
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
    document.addEventListener('click', e => {
      if (nav && !nav.contains(e.target) && mobileMenu.classList.contains('open')) {
        mobileMenu.classList.remove('open');
        mobileBtn.classList.remove('open');
        mobileBtn.setAttribute('aria-expanded', 'false');
        document.body.style.overflow = '';
      }
    });
  }

  // ── Smooth scroll for anchor links ────────────────────────
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', e => {
      const target = document.querySelector(anchor.getAttribute('href'));
      if (!target) return;
      e.preventDefault();
      const navH = nav ? nav.offsetHeight : 0;
      const top  = target.getBoundingClientRect().top + window.scrollY - navH - 20;
      window.scrollTo({ top, behavior: 'smooth' });
    });
  });

  // ── Hero word-by-word animation ───────────────────────────
  const heroWords = document.querySelectorAll('.hero__word');
  if (heroWords.length > 0 && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    heroWords.forEach((word, i) => {
      setTimeout(() => word.classList.add('in'), i * 90 + 200);
    });
  } else {
    heroWords.forEach(w => w.classList.add('in'));
  }

  // ── Scroll-driven parallax ────────────────────────────────
  //
  // Elements with [data-parallax="speed"] move at speed * scrollDelta.
  // The hero image wrapper uses this for the sticky depth effect.
  //
  const parallaxEls = document.querySelectorAll('[data-parallax]');
  let   scrollY = 0;
  let   ticking = false;

  function applyParallax() {
    parallaxEls.forEach(el => {
      const speed = parseFloat(el.dataset.parallax) || 0.2;
      const rect  = el.getBoundingClientRect();
      if (rect.bottom < -100 || rect.top > window.innerHeight + 100) return;
      const inner  = el.querySelector('.hero__visual-inner');
      if (inner) {
        // Scale grows as user scrolls (image expands); cap at 1.38x
        const scale  = Math.min(1 + scrollY * 0.00022, 1.38);
        const offset = -(scrollY * speed);
        el.style.transform    = `scale(${scale})`;
        inner.style.transform = `translateY(${offset}px)`;
      } else {
        el.style.transform = `translateY(${-(scrollY * speed)}px)`;
      }
    });
    ticking = false;
  }

  if (parallaxEls.length > 0) {
    window.addEventListener('scroll', () => {
      scrollY = window.scrollY;
      if (!ticking) {
        requestAnimationFrame(applyParallax);
        ticking = true;
      }
    }, { passive: true });
  }

  // ── Scroll reveal ─────────────────────────────────────────
  const revealEls = document.querySelectorAll('[data-reveal]');
  if (revealEls.length > 0 && 'IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('in');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.08, rootMargin: '0px 0px -48px 0px' });
    revealEls.forEach(el => observer.observe(el));
  } else {
    revealEls.forEach(el => el.classList.add('in'));
  }

  // ── Old [data-animate] compat (subpages) ─────────────────
  const animatedEls = document.querySelectorAll('[data-animate]');
  if (animatedEls.length > 0 && 'IntersectionObserver' in window) {
    const observer2 = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          observer2.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1, rootMargin: '0px 0px -32px 0px' });
    animatedEls.forEach(el => observer2.observe(el));
  } else {
    animatedEls.forEach(el => el.classList.add('visible'));
  }

  // ── FAQ accordion ─────────────────────────────────────────
  document.querySelectorAll('.faq-item__btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const item   = btn.closest('.faq-item');
      const isOpen = item.classList.contains('open');
      const list   = item.closest('.faq-list, .faq-accordion');
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

  // ── Product row hover: pointer cursor on desktop ──────────
  // CSS handles the visual; this just makes sure links inside rows work
  document.querySelectorAll('.product-row').forEach(row => {
    row.addEventListener('click', () => {
      const link = row.querySelector('a');
      if (link) link.click();
    });
  });

  // ── Marquee pause on hover (CSS handles it; belt-and-suspenders) ──
  const marqueeTrack = document.querySelector('.marquee__track');
  if (marqueeTrack) {
    const marquee = marqueeTrack.closest('.marquee');
    if (marquee) {
      marquee.addEventListener('mouseenter', () => {
        marqueeTrack.style.animationPlayState = 'paused';
      });
      marquee.addEventListener('mouseleave', () => {
        marqueeTrack.style.animationPlayState = 'running';
      });
    }
  }

  // ── Stat counter animation (subpages) ────────────────────
  function animateCounter(el, target, duration) {
    const start   = performance.now();
    const isFloat = String(target).includes('.');
    const update  = now => {
      const p     = Math.min((now - start) / duration, 1);
      const eased = 1 - Math.pow(1 - p, 3);
      const val   = eased * target;
      el.textContent = isFloat ? val.toFixed(1) : Math.floor(val).toLocaleString('pt-BR');
      if (p < 1) requestAnimationFrame(update);
      else el.textContent = isFloat ? target.toFixed(1) : target.toLocaleString('pt-BR');
    };
    requestAnimationFrame(update);
  }

  const statNums = document.querySelectorAll('.stat__num, .why__stat-num');
  if (statNums.length > 0 && 'IntersectionObserver' in window) {
    const statObserver = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        const el  = entry.target;
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

  // ── Section progress indicator ────────────────────────────
  //
  // Highlights nav links as user scrolls through numbered sections.
  //
  const sections = document.querySelectorAll('[id]');
  const navLinks = document.querySelectorAll('.nav__link');
  if (sections.length > 0 && navLinks.length > 0 && 'IntersectionObserver' in window) {
    const sectionObserver = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const id = entry.target.id;
          navLinks.forEach(link => {
            link.classList.toggle('active', link.getAttribute('href') === `#${id}`);
          });
        }
      });
    }, { threshold: 0.4 });
    sections.forEach(s => sectionObserver.observe(s));
  }

})();
