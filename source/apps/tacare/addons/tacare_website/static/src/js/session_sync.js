/** Refresh open tabs when a server-side SSO group signs in/out or changes user. */
function initCareSessionSync() {
  const root = document.querySelector('.tc-live');
  if (!root) return;
  const initial = Number(root.dataset.sessionUser || 0);
  let busy = false;
  const check = async () => {
    if (busy || document.hidden) return;
    busy = true;
    try {
      const response = await fetch('/care/sso/status', {credentials:'same-origin',cache:'no-store',
        headers:{Accept:'application/json'}});
      if (!response.ok) return;
      const result = await response.json();
      if (result.syncing) return;
      if (Number(result.uid || 0) !== initial) {
        // Hide stale personal content before reloading. Failed connectivity never
        // changes authentication; each server request still checks revocation.
        root.style.visibility = 'hidden';
        // Always navigate with GET, including a failed /web/login POST page.
        location.replace(location.href);
      }
    } catch { /* Recheck on focus/next interval when connectivity returns. */ }
    finally { busy = false; }
  };
  let timer;
  const start = () => { clearInterval(timer); timer = setInterval(check,3000); check(); };
  addEventListener('focus',check);
  document.addEventListener('visibilitychange',check);
  addEventListener('pageshow',start);
  addEventListener('pagehide',()=>clearInterval(timer));
  start();
}
if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded',initCareSessionSync,{once:true});
else initCareSessionSync();
