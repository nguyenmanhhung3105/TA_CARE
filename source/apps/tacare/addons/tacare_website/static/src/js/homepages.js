/** Homepages deliberately use different information and interaction patterns. */
function initCareHomepages() {
  const home = document.querySelector('[data-care-home]');
  if (!home) return;
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  let paused = reduced.matches;

  const togglePanels = (buttons, panels, attribute, panelAttribute) => {
    buttons.forEach((button) => button.addEventListener('click', () => {
      const selected = button.getAttribute(attribute);
      buttons.forEach((item) => item.setAttribute('aria-pressed', String(item === button)));
      panels.forEach((panel) => { panel.hidden = panel.getAttribute(panelAttribute) !== selected; });
    }));
  };
  togglePanels([...home.querySelectorAll('[data-sector-tab]')],
    [...home.querySelectorAll('[data-sector-panel]')], 'data-sector-tab', 'data-sector-panel');
  togglePanels([...home.querySelectorAll('[data-profile-example]')],
    [...home.querySelectorAll('[data-profile-panel]')], 'data-profile-example', 'data-profile-panel');

  const checklist = home.querySelector('[data-preparation-checklist]');
  checklist?.addEventListener('change', () => {
    const inputs = [...checklist.querySelectorAll('input[type="checkbox"]')];
    home.querySelector('[data-checklist-count]').textContent =
      `${inputs.filter((input) => input.checked).length} / ${inputs.length} điều đã sẵn sàng`;
  });

  const motionToggle = home.querySelector('[data-motion-toggle]');
  const updateMotion = () => {
    home.classList.toggle('care-motion-paused', paused || reduced.matches);
    if (motionToggle) {
      motionToggle.disabled = reduced.matches;
      motionToggle.setAttribute('aria-pressed', String(paused || reduced.matches));
      motionToggle.textContent = reduced.matches ? 'Đã giảm chuyển động' :
        paused ? 'Tiếp tục chuyển động' : 'Tạm dừng chuyển động';
    }
  };
  motionToggle?.addEventListener('click', () => { paused = !paused; updateMotion(); });
  reduced.addEventListener('change', () => { paused = reduced.matches; updateMotion(); });
  updateMotion();
  document.addEventListener('visibilitychange', () => {
    home.classList.toggle('care-page-hidden', document.hidden);
  });

  if ('IntersectionObserver' in window) {
    if (!reduced.matches) {
      home.classList.add('care-motion-ready');
      const reveal = new IntersectionObserver((entries) => entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          reveal.unobserve(entry.target);
        }
      }), { threshold: 0.06, rootMargin: '0px 0px -12px 0px' });
      home.querySelectorAll('[data-reveal]').forEach((element) => reveal.observe(element));
    }
    const stage = home.querySelector('.h-stage');
    if (stage) new IntersectionObserver(([entry]) => {
      stage.classList.toggle('is-offscreen', !entry.isIntersecting);
    }).observe(stage);
    const ratios = new Map();
    const chapters = [...home.querySelectorAll('[data-story-step]')];
    chapters.forEach((chapter) => ratios.set(chapter, 0));
    const story = new IntersectionObserver((entries) => {
      if (window.innerWidth <= 600) return;
      entries.forEach((entry) => ratios.set(entry.target, entry.intersectionRatio));
      const selected = [...ratios].sort((a, b) => b[1] - a[1])[0];
      if (!selected || selected[1] === 0) return;
      const index = selected[0].dataset.storyStep;
      home.querySelectorAll('[data-story-visual]').forEach((figure) => {
        figure.classList.toggle('is-active', figure.dataset.storyVisual === index);
      });
      home.querySelectorAll('[data-story-dot]').forEach((dot) => {
        dot.classList.toggle('is-active', dot.dataset.storyDot === index);
      });
    }, { threshold: [0, 0.1, 0.25, 0.5, 0.75, 1], rootMargin: '-15% 0px -15% 0px' });
    chapters.forEach((chapter) => story.observe(chapter));
  }

  const gallery = home.querySelector('[data-story-gallery]');
  if (gallery) {
    const controls = [...home.querySelectorAll('[data-story-scroll]')];
    const updateControls = () => controls.forEach((button) => {
      button.disabled = Number(button.dataset.storyScroll) < 0 ? gallery.scrollLeft < 2 :
        gallery.scrollLeft + gallery.clientWidth >= gallery.scrollWidth - 2;
    });
    controls.forEach((button) => button.addEventListener('click', () => {
      const card = gallery.querySelector('article');
      gallery.scrollBy({left: Number(button.dataset.storyScroll) * (card.getBoundingClientRect().width +
        Number.parseFloat(getComputedStyle(gallery).columnGap)), behavior: reduced.matches ? 'auto' : 'smooth'});
    }));
    gallery.addEventListener('scroll', updateControls, { passive: true });
    window.addEventListener('resize', updateControls, { passive: true });
    updateControls();
  }

  const path = home.querySelector('[data-draw-path]');
  if (path) {
    const length = path.getTotalLength();
    const map = path.closest('.h-map');
    let queued = false;
    path.style.strokeDasharray = String(length);
    const draw = () => {
      queued = false;
      if (paused || reduced.matches || document.hidden) { path.style.strokeDashoffset = '0'; return; }
      const box = map.getBoundingClientRect();
      const progress = Math.max(0, Math.min(1, (window.innerHeight - box.top) / (box.height + window.innerHeight * 0.2)));
      path.style.strokeDashoffset = String(length * (1 - progress));
    };
    window.addEventListener('scroll', () => {
      if (!queued) { queued = true; requestAnimationFrame(draw); }
    }, { passive: true });
    motionToggle?.addEventListener('click', draw);
    reduced.addEventListener('change', draw);
    draw();
  }
}
if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initCareHomepages, { once: true });
else initCareHomepages();
