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

  // ── Hero rotating text ────────────────────────────────────
  const rotateEl = document.querySelector('.hero__rotate-text');
  if (rotateEl) {
    const rotateTexts = ['Vender mais', 'Fidelizar mais', 'Encantar mais', 'Economizar mais', 'Crescer mais'];
    let rotIdx = 0;
    setInterval(() => {
      // Slide out upward
      rotateEl.style.opacity = '0';
      rotateEl.style.transform = 'translateY(-24px)';
      setTimeout(() => {
        // Instantly reset to below (no transition)
        rotateEl.style.transition = 'none';
        rotateEl.style.opacity = '0';
        rotateEl.style.transform = 'translateY(24px)';
        rotIdx = (rotIdx + 1) % rotateTexts.length;
        rotateEl.textContent = rotateTexts[rotIdx];
        // Double rAF: first frame applies the "from" state, second frame triggers transition
        requestAnimationFrame(() => {
          requestAnimationFrame(() => {
            rotateEl.style.transition = '';
            rotateEl.style.opacity = '1';
            rotateEl.style.transform = 'translateY(0)';
          });
        });
      }, 380);
    }, 2800);
  }

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

  // ── Lucas photos fan animation ────────────────────────────────
  const lucasPhotos = document.getElementById('lucas-photos');
  if (lucasPhotos && 'IntersectionObserver' in window) {
    const photoObserver = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          setTimeout(() => entry.target.classList.add('animated'), 200);
          photoObserver.unobserve(entry.target);
        }
      });
    }, { threshold: 0.3 });
    photoObserver.observe(lucasPhotos);
  }

  // ── Cal.com modal ─────────────────────────────────────────────
  const calModal    = document.getElementById('cal-modal');
  const calClose    = document.getElementById('cal-modal-close');
  const calBackdrop = document.getElementById('cal-modal-backdrop');

  function openCalModal() {
    if (!calModal) return;
    calModal.classList.add('open');
    calModal.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
  }
  function closeCalModal() {
    if (!calModal) return;
    calModal.classList.remove('open');
    calModal.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
  }

  if (calModal) {
    document.querySelectorAll('[data-cal-link]').forEach(el => {
      el.addEventListener('click', e => { e.preventDefault(); openCalModal(); });
    });
    if (calClose)    calClose.addEventListener('click', closeCalModal);
    if (calBackdrop) calBackdrop.addEventListener('click', closeCalModal);
    document.addEventListener('keydown', e => {
      if (e.key === 'Escape') closeCalModal();
    });
  }

  // ── Universal auto-reveal ─────────────────────────────────
  (function () {
    if (!('IntersectionObserver' in window)) return;

    const sel = [
      'h2', 'h3', 'h4', '.pg-label', '.pg-subhead',
      '.feat-card', '.dore-card', '.dore-col', '.process-col',
      '.faq-item', '.product-row', '.cta-box', '.prod-price__card',
      '.sh-sub__text', '.sh-sub .btn', '.sh-sub__stats',
    ].join(',');

    const skip = el =>
      !!el.closest('nav, footer, .sh') ||
      el.hasAttribute('data-reveal') ||
      el.hasAttribute('data-animate') ||
      !!el.closest('[data-reveal], [data-animate]');

    const els = [...document.querySelectorAll(sel)].filter(el => !skip(el));

    els.forEach(el => el.classList.add('ar'));

    // Stagger siblings within the same parent (cards in grids, etc.)
    els.forEach(el => {
      const group = [...(el.parentElement?.children || [])].filter(c => c.classList.contains('ar'));
      const i = group.indexOf(el);
      if (i > 0) el.style.transitionDelay = Math.min(i * 0.1, 0.35) + 's';
    });

    const io = new IntersectionObserver(entries => {
      entries.forEach(({ target, isIntersecting }) => {
        if (!isIntersecting) return;
        target.classList.add('in');
        io.unobserve(target);
      });
    }, { threshold: 0.08, rootMargin: '0px 0px -40px 0px' });

    els.forEach(el => io.observe(el));
  })();

  // ── Slot-machine animation — sh-sub stat numbers ──────────
  const shSub = document.querySelector('.sh-sub');
  if (shSub) {
    const statNums = shSub.querySelectorAll('.prod-hero__stat-num');
    let fired = false;

    function slotAnimate(el) {
      const final  = el.textContent.trim();
      const digits = '0123456789';
      let frame    = 0;
      const total  = 20;

      (function tick() {
        frame++;
        const progress = frame / total;
        el.textContent = final.split('').map((ch, i) => {
          if (!/\d/.test(ch)) return ch;
          if (progress >= 0.45 + (i / final.length) * 0.45) return ch;
          return digits[Math.floor(Math.random() * 10)];
        }).join('');
        if (frame < total) setTimeout(tick, 35 + frame * 7);
        else el.textContent = final;
      })();
    }

    new IntersectionObserver(entries => {
      if (entries[0].isIntersecting && !fired) {
        fired = true;
        statNums.forEach((el, i) => setTimeout(() => slotAnimate(el), i * 140));
      }
    }, { threshold: 0.4 }).observe(shSub);
  }

})();
