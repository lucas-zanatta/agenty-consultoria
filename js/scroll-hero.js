(function () {
  const media = document.getElementById('sh-media');
  if (!media) return;

  const bg      = document.getElementById('sh-bg');
  const overlay = document.getElementById('sh-overlay');
  const wordL   = document.getElementById('sh-word-l');
  const wordR   = document.getElementById('sh-word-r');
  const hint    = document.getElementById('sh-hint');
  const badge   = document.getElementById('sh-badge');
  const reveal  = document.getElementById('sh-reveal');

  let progress = 0;
  let expanded = false;
  let touchY   = 0;

  const mobile = () => window.innerWidth < 768;

  function apply(p) {
    const w  = 300 + p * (window.innerWidth  - 300);
    const h  = 400 + p * (window.innerHeight - 400);
    const tx = p * (mobile() ? 100 : 160);

    media.style.width        = w + 'px';
    media.style.height       = h + 'px';
    media.style.borderRadius = (1 - p) * 16 + 'px';
    bg.style.opacity         = 1 - p;
    overlay.style.opacity    = Math.max(0, 0.5 - p * 0.3);
    wordL.style.transform    = 'translateX(-' + tx + 'px)';
    wordR.style.transform    = 'translateX('  + tx + 'px)';
    hint.style.opacity       = Math.max(0, 1 - p * 4);
    badge.style.opacity      = Math.max(0, 1 - p * 3);
  }

  function unlock() {
    expanded = true;
    document.body.style.overflow = '';
    reveal.classList.add('visible');
  }

  function lock() {
    expanded = false;
    document.body.style.overflow = 'hidden';
    reveal.classList.remove('visible');
    window.scrollTo(0, 0);
  }

  function onWheel(e) {
    if (expanded && e.deltaY < 0 && window.scrollY <= 5) {
      e.preventDefault();
      progress = 0;
      apply(0);
      lock();
      return;
    }
    if (expanded) return;
    e.preventDefault();
    progress = Math.min(1, Math.max(0, progress + e.deltaY * 0.001));
    apply(progress);
    if (progress >= 1) unlock();
  }

  function onTouchStart(e) {
    touchY = e.touches[0].clientY;
  }

  function onTouchMove(e) {
    if (!touchY) return;
    const delta = touchY - e.touches[0].clientY;

    if (expanded && delta < -20 && window.scrollY <= 5) {
      e.preventDefault();
      progress = 0;
      apply(0);
      lock();
      return;
    }
    if (expanded) return;

    e.preventDefault();
    const factor = delta < 0 ? 0.008 : 0.005;
    progress = Math.min(1, Math.max(0, progress + delta * factor));
    apply(progress);
    if (progress >= 1) unlock();
    touchY = e.touches[0].clientY;
  }

  function onTouchEnd() {
    touchY = 0;
  }

  // Initialise
  lock();
  apply(0);

  window.addEventListener('wheel',      onWheel,      { passive: false });
  window.addEventListener('touchstart', onTouchStart, { passive: true  });
  window.addEventListener('touchmove',  onTouchMove,  { passive: false });
  window.addEventListener('touchend',   onTouchEnd);
})();
