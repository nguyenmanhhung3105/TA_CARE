/* Uses only generated CI accounts inside the networkless application container. */
const {chromium} = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const fixture = JSON.parse(fs.readFileSync('/var/lib/odoo/tacare_ci-fixture.json'));
const base = site => `http://${site}.localhost:8069`;
const sites = ['khovieclam', 'tuhoso', 'tacare'];
const delay = ms => new Promise(resolve => setTimeout(resolve, ms));

(async () => {
  const browser = await chromium.launch({headless: true, args: ['--no-sandbox', '--disable-dev-shm-usage']});
  let page;
  let stage = 'startup';
  try {
    const guest = await browser.newContext();
    page = await guest.newPage();
    for (let attempt = 0; attempt < 90; attempt++) {
      try {
        const response = await guest.request.get(base('khovieclam') + '/', {timeout: 3000});
        if (response.status() === 200) break;
      } catch {}
      if (attempt === 89) throw new Error('CI HTTP startup failed');
      await delay(1000);
    }
    stage = 'homepages';
    const markers = {khovieclam: 'tc-jobs', tuhoso: 'tc-profiles', tacare: 'tc-hub'};
    for (const site of sites) {
      for (const width of [1440, 375]) {
        await page.setViewportSize({width, height: 1000});
        const response = await page.goto(base(site), {waitUntil: 'networkidle'});
        assert.equal(response.status(), 200);
        assert.equal(await page.locator('.' + markers[site]).count(), 1);
        assert.equal(await page.locator('h1').count(), 1);
        assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth + 1), false);
        assert.equal((await page.locator('body').innerText()).includes('A CSS error occurred'), false);
        await page.screenshot({path: `/reports/${site}-${width}.png`, fullPage: true});
      }
    }
    stage = 'public-card-navigation';
    const detail = `/kvl/job/${fixture.job_id}`;
    for (const prefix of ['', '/en']) {
      for (const selector of ['.sx-work-photo', '.sx-work-body h3 a', '.sx-work-bottom .sx-text-link']) {
        await page.goto(base('khovieclam') + prefix + '/kvl/jobs', {waitUntil: 'networkidle'});
        const card = page.locator('.sx-work-card').filter({has: page.locator(`a[href$="${detail}"]`)}).first();
        assert.equal(await card.count(), 1);
        await card.locator(selector).click();
        await page.waitForURL(url => url.pathname.endsWith(detail));
        assert.equal(await page.locator('#tc-login-dialog[open]').count(), 0);
        assert.equal(await page.locator('a[href$="/edit"],a[href$="/remove"]').count(), 0);
      }
    }
    await page.getByRole('link', {name: 'Tạo hồ sơ từ công việc này', exact: true}).click();
    await page.waitForFunction(() => document.querySelector('#tc-login-dialog')?.open);
    await page.goto(base('khovieclam'), {waitUntil: 'networkidle'});
    await page.locator('.sx-main-nav a[href$="/kvl/jobs"]').click();
    await page.waitForURL(url => url.pathname.endsWith('/kvl/jobs'));
    assert.equal(await page.locator('#tc-login-dialog[open]').count(), 0);
    await page.locator('.sx-header-actions a[href$="/kvl/flexible/new"]').click();
    await page.waitForFunction(() => document.querySelector('#tc-login-dialog')?.open);
    await guest.close();

    async function status(context, site) {
      const response = await context.request.get(base(site) + '/care/sso/status');
      assert.equal(response.status(), 200);
      return response.json();
    }
    async function login(context, kind) {
      const account = fixture.accounts[kind];
      const response = await context.request.get(base('khovieclam') + '/?login=1');
      const html = await response.text();
      const token = html.match(/name="csrf_token"[^>]*value="([^"]+)"/)?.[1];
      assert(token, 'Native CSRF token missing');
      await context.request.post(base('khovieclam') + '/web/login', {form: {
        csrf_token: token, login: account.login, password: account.credential, redirect: '/',
      }});
      assert.equal((await status(context, 'khovieclam')).uid, account.id);
    }
    stage = 'native-login-sso-and-ownership';
    for (const kind of ['person', 'business', 'admin']) {
      const context = await browser.newContext();
      await login(context, kind);
      for (const site of sites) {
        const allowed = kind !== 'business' || site !== 'tuhoso';
        assert.equal((await status(context, site)).uid, allowed ? fixture.accounts[kind].id : false);
      }
      if (kind === 'person') {
        page = await context.newPage();
        const own = await page.goto(base('tuhoso') + `/tuhoso/profile/${fixture.private_profile_id}`);
        assert.equal(own.status(), 200);
        const create = await page.goto(base('tuhoso') + '/tuhoso/profiles/new');
        assert.equal(create.status(), 200);
        await page.locator('input[name=profile_title]').fill('CI Browser Created Profile');
        await page.locator('form[action="/tuhoso/profiles/create"] button[type=submit]').click();
        await page.waitForURL(url => url.pathname === '/tuhoso/work/new' && url.searchParams.has('profile_id'));
      }
      await context.request.get(base('tacare') + '/web/session/logout?redirect=/');
      for (const site of sites) assert.equal((await status(context, site)).uid, false);
      await context.close();
    }
    const other = await browser.newContext();
    await login(other, 'other');
    const denied = await other.request.get(base('tuhoso') + `/tuhoso/profile/${fixture.private_profile_id}`);
    assert([403, 404].includes(denied.status()));
    await other.close();
    fs.writeFileSync('/reports/browser.txt', 'PASS homepages/responsive, public card clicks, private-action login, native role SSO/global logout, owner form and foreign-profile denial\n');
    console.log('PASS CI browser: public navigation, native auth/SSO, owner form and private record isolation');
  } catch {
    if (page && !page.isClosed()) await page.screenshot({path: '/reports/browser-failure.png', fullPage: true}).catch(() => {});
    // Never expose native request/cookie/credential diagnostics in an uploaded artifact.
    fs.writeFileSync('/reports/browser.txt', `FAIL browser stage: ${stage}\n`);
    throw new Error(`CI browser failed at ${stage}; see synthetic screenshots and private runtime diagnostics`);
  } finally {
    await browser.close();
  }
})().catch(error => { console.error(error.message); process.exitCode = 1; });
