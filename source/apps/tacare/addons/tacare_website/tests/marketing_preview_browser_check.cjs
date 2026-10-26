/* Local QA only. Identities are read from an ignored private file, never seeded. */
const {chromium} = require('playwright');
const fs = require('node:fs');
const assert = require('node:assert/strict');
const identityPath = process.env.TACARE_UI_IDENTITY_FILE || 'runtime/tacare/marketing_preview_identities.json';
const identities = JSON.parse(fs.readFileSync(identityPath, 'utf8'));
const kho = 'http://khovieclam.localhost:8069', hub = 'http://tacare.localhost:8069';

(async () => {
  const browser = await chromium.launch({channel: 'chrome', headless: true});
  const shots = 'runtime/marketing-preview-review';
  fs.mkdirSync(shots, {recursive: true});
  let context, page;
  const errors = [];
  async function fresh() {
    if (context) await context.close();
    context = await browser.newContext({viewport: {width: 1440, height: 1100}});
    page = await context.newPage();
    page.on('pageerror', e => errors.push(e.message));
  }
  async function go(url) {
    const response = await page.goto(url);
    assert(response.status() < 400, 'Page unavailable: ' + new URL(url).pathname);
    await page.waitForLoadState('networkidle');
    await page.evaluate(() => document.fonts.ready);
  }
  async function signIn(role) {
    const identity = identities.find(i => i.role === role);
    assert(identity, 'Missing existing QA identity');
    const form = page.locator('.tc-login-form');
    await form.locator('[name=login]').fill(identity.login);
    await form.locator('[name=password]').fill(identity.password);
    await form.getByRole('button', {name: 'Đăng nhập', exact: true}).click();
    await page.waitForURL(url => !url.pathname.startsWith('/care/sso/') && !url.searchParams.has('login'));
    await page.waitForLoadState('networkidle');
  }
  try {
    await fresh();
    await go(kho + '/');
    const preview = page.locator('#matching-preview');
    assert.equal(await preview.locator('.km-card').count(), 2);
    assert.equal(await preview.locator('[data-profile-id],[data-capability-id],a[href*="/tacare/pair/"],a[href*="/profile/"]').count(), 0);
    assert.equal(await preview.locator('.lp-comparison,form').count(), 0);
    assert((await preview.innerText()).includes('Thông tin hồ sơ chỉ hiện cho tài khoản có quyền.'));
    for (const width of [320, 375, 768, 1024, 1440, 1920]) {
      await page.setViewportSize({width, height: 1100});
      assert.equal(await preview.locator('.km-grid').evaluate(n => getComputedStyle(n).gridTemplateColumns.split(' ').length), width >= 1024 ? 2 : 1);
      assert(!await page.evaluate(() => document.documentElement.scrollWidth > innerWidth + 1), 'Horizontal overflow at ' + width);
    }
    await page.setViewportSize({width: 1440, height: 1100});
    for (const img of await preview.locator('img').all()) {
      await img.scrollIntoViewIfNeeded();
      await img.evaluate(n => n.decode());
      assert(await img.evaluate(n => n.naturalWidth > 0));
    }
    await preview.screenshot({path: shots + '/guest-1440.png'});
    await page.setViewportSize({width: 375, height: 1100});
    await preview.screenshot({path: shots + '/guest-375.png'});
    await page.setViewportSize({width: 1440, height: 1100});
    await preview.getByRole('link', {name: 'Đăng nhập để xem matching của bạn', exact: true}).first().click();
    await page.waitForLoadState('networkidle');
    assert.equal(new URL(page.url()).hostname, 'tacare.localhost');
    assert.equal(await page.locator('#tc-login-dialog[open]').count(), 1);
    assert.equal(await page.locator('.lp-pair,.lp-comparison').count(), 0);
    assert.equal(await page.locator('.tc-login-form [name=redirect]').inputValue(), '/tacare/matching');
    await signIn('business');
    assert.match(new URL(page.url()).pathname, /\/tacare\/matching$/);
    assert(await page.locator('.lp-pair').count(), 'Own suggestions must be available after sign-in');
    const detailUrl = await page.locator('.lp-pair').first().getByRole('link', {name: 'Đối chiếu hai phía', exact: true}).getAttribute('href');
    await go(hub + detailUrl);
    assert(await page.locator('.lp-comparison tbody tr').count());
    await go(kho + '/');
    assert.equal(await page.locator('#matching-preview .km-card').count(), 2);
    assert.equal(await page.locator('#matching-preview').getByRole('link', {name: 'Xem matching của tôi', exact: true}).count(), 2);
    await fresh();
    await go(hub + '/web/login');
    await signIn('other_business');
    const denied = await context.request.get(hub + detailUrl);
    assert([403, 404].includes(denied.status()), 'Other organization cannot view the shown pair');
    await fresh();
    await go(hub + detailUrl);
    assert.equal(await page.locator('#tc-login-dialog[open]').count(), 1);
    assert.equal(await page.locator('.lp-pair,.lp-comparison').count(), 0);
    assert.deepEqual(errors, []);
    console.log('PASS Kho marketing: two anonymous current previews, images and responsive grid; CTA requires native login, opens own real matches; foreign account and guest cannot read pair details; no records created');
  } finally {
    await browser.close();
  }
})().catch(e => {console.error(e.stack); process.exit(1);});
