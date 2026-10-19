/** Native Odoo form submission preserves CAPTCHA, session rotation and MFA. */
function initCareAuthentication() {
  const root = document.querySelector('.tc-live');
  const dialog = document.getElementById('tc-login-dialog');
  if (!root || !dialog) return;
  const form = dialog.querySelector('form');
  const languages = (root.dataset.urlLanguages || '').split(',');
  const pathOf = url => {
    const first = url.pathname.split('/')[1];
    return languages.includes(first) ? url.pathname.slice(first.length + 1) || '/' : url.pathname;
  };
  let trigger;
  const safeNext = (value) => {
    try {
      const url = new URL(value || '/', location.origin);
      return url.origin === location.origin && /^\/(kvl\/|tuhoso\/|tacare\/|$)/.test(pathOf(url))
        ? url.pathname + url.search + url.hash : '/';
    } catch { return '/'; }
  };
  const open = (next, opener) => {
    trigger = opener;
    form.elements.redirect.value = safeNext(next);
    if (!dialog.open) dialog.showModal();
    document.documentElement.classList.add('tc-login-is-open');
    dialog.querySelector('[name=login]').focus({preventScroll:true});
  };
  const close = () => {
    dialog.close();
  };
  dialog.addEventListener('close', () => {
    document.documentElement.classList.remove('tc-login-is-open');
    form.elements.password.value = '';
    const url = new URL(location.href);
    ['login','next','reason'].forEach(key => url.searchParams.delete(key));
    history.replaceState(null,'',url.pathname + url.search + url.hash);
    trigger?.focus({preventScroll:true});
  });
  dialog.querySelectorAll('[data-login-close]').forEach(button => button.addEventListener('click', event => {
    event.preventDefault(); close();
  }));
  dialog.addEventListener('click', event => {
    if (event.target !== dialog) return;
    const box = dialog.getBoundingClientRect();
    if (event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom) close();
  });
  root.addEventListener('click', event => {
    if (event.button || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    const link = event.target.closest('a[href]');
    if (!link || dialog.contains(link) || link.target || link.hasAttribute('download')) return;
    const url = new URL(link.href,location.href);
    if (url.origin !== location.origin) return;
    const explicit = link.hasAttribute('data-login-open') || pathOf(url) === '/web/login';
    const requiresLogin = root.dataset.accessGuest === '1' && /^\/(kvl|tuhoso|tacare)(\/|$)/.test(pathOf(url));
    if (explicit || requiresLogin) {
      event.preventDefault();
      open(explicit ? url.searchParams.get('redirect') || '/' : url.pathname + url.search, link);
    }
  });
  dialog.querySelector('[data-login-password]').addEventListener('click', event => {
    const visible = form.elements.password.type === 'password';
    form.elements.password.type = visible ? 'text' : 'password';
    event.currentTarget.textContent = visible ? 'Ẩn' : 'Hiện';
    event.currentTarget.setAttribute('aria-pressed',String(visible));
  });
  // An `open` attribute also leaves the form usable when JavaScript is disabled.
  if (dialog.dataset.autoOpen === '1') {
    if (dialog.open) dialog.removeAttribute('open');
    open(form.elements.redirect.value);
  }
}
if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded',initCareAuthentication,{once:true});
else initCareAuthentication();
