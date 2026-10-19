/** Route and section selection shared by all three sites. */
function initCareNavigation() {
  const root = document.querySelector('.tc-live');
  if (!root) return;
  const current = new URL(location.href);
  const languages = (root.dataset.urlLanguages || '').split(',');
  const pathOf = url => {
    const first = url.pathname.split('/')[1];
    return languages.includes(first) ? url.pathname.slice(first.length + 1) || '/' : url.pathname;
  };
  const currentPath = pathOf(current);
  const groups = [...root.querySelectorAll('header nav, .tc-editor-sidebar nav')];
  const relatedRoute = (url) => {
    const path = currentPath;
    url = {pathname:pathOf(url)};
    if (url.pathname === '/kvl/jobs') return /^\/kvl\/job\/\d+$/.test(path);
    if (url.pathname === '/kvl/flexible/new') return path === '/kvl/job/new';
    if (url.pathname === '/kvl/flexible/mine') return path === '/kvl/manage' ||
      /^\/kvl\/flexible\/\d+(\/edit)?$/.test(path) || /^\/kvl\/job\/\d+\/(edit|preview|history)$/.test(path);
    if (url.pathname === '/tuhoso/profiles') return path === '/tuhoso/me' ||
      /^\/tuhoso\/(profile|work)\/\d+(\/edit)?$/.test(path) || path === '/tuhoso/work/new';
    if (url.pathname === '/tacare/connections') return /^\/tacare\/connection\/\d+/.test(path);
    if (url.pathname === '/tacare/matching') return /^\/tacare\/job\/\d+$/.test(path);
    return false;
  };
  const updateRoutes = () => {
    groups.forEach((group) => {
      const links = [...group.querySelectorAll('a[href]')];
      let selected = null, best = -1;
      links.forEach((link) => {
        const url = new URL(link.href, location.href);
        if (url.origin !== current.origin || url.hash) return;
        const linkPath = pathOf(url);
        const match = link.classList.contains('is-current') || relatedRoute(url) || linkPath === currentPath ||
          (linkPath !== '/' && currentPath.startsWith(linkPath + '/'));
        if (!match) return;
        if ([...url.searchParams].some(([key,value]) => current.searchParams.get(key) !== value &&
          !(key === 'scope' && !current.searchParams.has(key) && value === (root.dataset.accountRole === 'admin' ? 'all' : 'mine')))) return;
        const score = linkPath.length + [...url.searchParams].length * 100;
        if (score > best) { selected = link; best = score; }
      });
      links.forEach(link => { if (link === selected) link.setAttribute('aria-current','page'); else link.removeAttribute('aria-current'); });
    });
    root.querySelectorAll('header [data-nav-link]:not(nav a)').forEach(link => {
      const url = new URL(link.href,location.href);
      if (url.origin === current.origin && pathOf(url) === currentPath) link.setAttribute('aria-current','page');
      else link.removeAttribute('aria-current');
    });
  };
  updateRoutes();
  groups.forEach(group => {
    const links = [...group.querySelectorAll('a[href]')].filter(a => {
      const u = new URL(a.href,location.href);
      return u.origin === current.origin && pathOf(u) === currentPath && u.hash && document.getElementById(u.hash.slice(1));
    });
    if (!links.length) return;
    let queued = false;
    const update = () => {
      queued = false;
      const active = [...links].reverse().find(a => document.getElementById(new URL(a.href).hash.slice(1)).getBoundingClientRect().top <= Math.max(150,innerHeight*.25));
      if (active) group.querySelectorAll('a').forEach(a => {
        if (a === active) a.setAttribute('aria-current','location'); else a.removeAttribute('aria-current');
      });
      else updateRoutes();
    };
    addEventListener('scroll',() => { if (!queued) { queued = true; requestAnimationFrame(update); } },{passive:true});
    addEventListener('hashchange',update);
    update();
  });
  root.querySelectorAll('.fw-tabs a.is-active').forEach(a => a.setAttribute('aria-current','page'));
}
if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded',initCareNavigation,{once:true});
else initCareNavigation();
