/** Accessible photo carousel and progressive disclosure for flexible-work forms. */
function initFlexibleWork() {
  document.querySelectorAll('[data-work-carousel]').forEach((root) => {
    const slides = [...root.querySelectorAll('[data-work-slide]')];
    const dots = [...root.querySelectorAll('[data-work-dot]')];
    const pause = root.querySelector('[data-work-pause]');
    const reduced = matchMedia('(prefers-reduced-motion: reduce)');
    let index = 0;
    let stopped = reduced.matches || root.dataset.workAutoplay === '0';
    let timer;
    let hovering = false;
    let manualPlayback = false;
    const updateTimer = () => {
      clearInterval(timer);
      pause.textContent = reduced.matches ? 'Đã giảm chuyển động' : stopped ? 'Tiếp tục' : 'Tạm dừng';
      pause.disabled = reduced.matches;
      pause.setAttribute('aria-pressed', String(stopped || reduced.matches));
      if (!stopped && !reduced.matches && !document.hidden &&
          (manualPlayback || !hovering && !root.contains(document.activeElement))) {
        timer = setInterval(() => show(index + 1, false), 6500);
      }
    };
    const show = (next, announce = true) => {
      index = (next + slides.length) % slides.length;
      slides.forEach((slide, i) => {
        const active = i === index;
        slide.classList.toggle('is-active', active);
        slide.setAttribute('aria-hidden', String(!active));
        slide.inert = !active;
      });
      dots.forEach((dot, i) => dot.setAttribute('aria-pressed', String(i === index)));
      if (announce) root.querySelector('.fw-carousel-status').textContent = `Ảnh công việc ${index + 1} trên ${slides.length}`;
    };
    root.querySelector('[data-work-prev]').addEventListener('click', () => { show(index - 1); updateTimer(); });
    root.querySelector('[data-work-next]').addEventListener('click', () => { show(index + 1); updateTimer(); });
    dots.forEach((dot, i) => dot.addEventListener('click', () => { show(i); updateTimer(); }));
    // An explicit resume must work while its button still has focus. Merely
    // focusing that button must not reverse the subsequent pause click.
    pause.addEventListener('click', () => { stopped = !stopped; manualPlayback = !stopped; updateTimer(); });
    root.addEventListener('mouseenter', () => { hovering = true; manualPlayback = false; updateTimer(); });
    root.addEventListener('mouseleave', () => { hovering = false; updateTimer(); });
    root.addEventListener('focusin', (event) => {
      if (event.target !== pause) { stopped = true; manualPlayback = false; }
      updateTimer();
    });
    root.addEventListener('focusout', () => setTimeout(() => {
      if (!root.contains(document.activeElement)) manualPlayback = false;
      updateTimer();
    }, 0));
    root.addEventListener('keydown', (event) => {
      if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') {
        event.preventDefault(); show(index + (event.key === 'ArrowRight' ? 1 : -1));
      }
    });
    document.addEventListener('visibilitychange', updateTimer);
    reduced.addEventListener('change', () => {
      if (reduced.matches) { stopped = true; manualPlayback = false; }
      updateTimer();
    });
    show(0, false); updateTimer();
  });
  document.querySelectorAll('[data-work-form]').forEach((form) => {
    const update = () => {
      const remote = form.elements.flex_mode.value === 'remote';
      form.querySelectorAll('[data-work-location]').forEach((node) => { node.hidden = remote; });
      form.querySelector('[data-work-recurring]').hidden = form.elements.flex_schedule.value !== 'recurring';
      const trip = form.querySelector('[data-work-trip]');
      trip.hidden = form.elements.flex_pay_unit.value !== 'trip';
      if (!trip.hidden) trip.open = true;
    };
    form.addEventListener('change', update);
    update();
    const error = document.getElementById('work-form-error');
    if (error) error.focus();
  });
}
if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initFlexibleWork, {once: true});
else initFlexibleWork();
