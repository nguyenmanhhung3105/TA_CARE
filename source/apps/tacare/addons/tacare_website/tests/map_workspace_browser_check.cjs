/* Read-only local UI checks: clearer controls without changing the map engine. */
const {chromium} = require('playwright');
const fs = require('node:fs'), assert = require('node:assert/strict');
const identities = JSON.parse(fs.readFileSync(process.env.TACARE_UI_IDENTITY_FILE || 'runtime/tacare/nearby_test_identities.json', 'utf8'));
const hub = 'http://tacare.localhost:8069', shots = 'runtime/map-workspace-review';
fs.mkdirSync(shots, {recursive: true});
(async () => {
  const browser = await chromium.launch({channel: 'chrome', headless: true});
  let context, page;
  const errors = [];
  async function fresh(role) {
    if (context) await context.close();
    context = await browser.newContext({viewport: {width: 1440, height: 1100}});
    page = await context.newPage(); page.on('pageerror', e => errors.push(e.message));
    if (role) {
      const identity = identities.find(i => i.role === role); assert(identity);
      await page.goto(hub + '/web/login'); await page.waitForLoadState('networkidle');
      const form = page.locator('.tc-login-form');
      await form.locator('[name=login]').fill(identity.login); await form.locator('[name=password]').fill(identity.password);
      await form.getByRole('button', {name: 'Đăng nhập', exact: true}).click();
      await page.waitForURL(u => !u.pathname.startsWith('/care/sso/') && !u.pathname.startsWith('/web/login') && !u.searchParams.has('login'));
      await page.waitForLoadState('networkidle');
    }
    await page.goto(hub + '/#nearby-connections'); await page.locator('#nearby-connections').scrollIntoViewIfNeeded();
    await page.waitForFunction(() => document.querySelector('[data-nearby-canvas]').dataset.baseLoaded === '1');
    if (role) await page.waitForFunction(() => document.querySelector('[data-geo-results-status]').textContent.length && !document.querySelector('[data-geo-results-status]').textContent.startsWith('Đang'));
  }
  async function responsive(role) {
    for (const width of [320, 375, 390, 767, 768, 1024, 1440, 1920]) {
      await page.setViewportSize({width, height: 1100});
      assert(!await page.evaluate(() => document.documentElement.scrollWidth > innerWidth + 1), 'Overflow ' + role + ' ' + width);
      assert.equal(await page.locator('#gm-title').innerText(), 'Bản đồ kết nối TA.CARE');
      const title = await page.locator('#gm-title').boundingBox(), frame = await page.locator('.gm-workspace').boundingBox();
      assert(Math.abs((title.x + title.width / 2) - (frame.x + frame.width / 2)) < 1, 'Centered title at ' + width);
      assert.equal(await page.locator('.gm-section-head').getByRole('heading').count(), 1);
      const background = await page.locator('.gm-workspace').evaluate(n => getComputedStyle(n).display);
      assert.equal(background, width <= 767 ? 'flex' : 'grid', 'SCSS must compile and responsive workspace must apply');
      if ([375, 1440].includes(width)) { await settledMap(); await page.locator('#nearby-connections').screenshot({path: shots + '/' + role + '-' + width + '.png'}); }
    }
    await page.setViewportSize({width: 1440, height: 1100});
  }
  async function settledMap() {
    await page.waitForTimeout(700); // Leaflet zoom animation and ResizeObserver must finish before tile readiness.
    await page.waitForFunction(() => {
      const map=document.querySelector('[data-nearby-canvas]')?.careMap;
      return map?.careGL?.areTilesLoaded() && !map._animatingZoom;
    });
    await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
  }
  try {
    await fresh();
    assert.equal(await page.locator('.gm-result--panel').count(), 0);
    assert.equal(await page.locator('.gm-profession-marker').count(), 0);
    await responsive('guest');
    await page.locator('.gm-guest a').click();
    assert.equal(await page.locator('#tc-login-dialog[open]').count(), 1);
    await page.getByRole('button', {name: 'Đóng cửa sổ đăng nhập', exact: true}).click();

    for (const role of ['provider', 'business']) {
      await fresh(role); await responsive(role);
      assert.equal(await page.locator('[data-geo-view=receive]').count(), role === 'business' ? 0 : 1);
      assert.equal(await page.locator('[data-geo-picker]').count(), 0);
      const refresh = page.locator('[data-geo-refresh]');
      const colors = await refresh.evaluate(n => { const s = getComputedStyle(n); return [s.backgroundColor, s.color, s.borderStyle, s.minHeight]; });
      assert.equal(colors[0], 'rgb(37, 37, 37)'); assert.equal(colors[1], 'rgb(255, 255, 255)'); assert.equal(colors[2], 'solid');
      assert(parseFloat(colors[3]) >= 44);
      await page.locator('[data-geo-radius]').focus(); await page.keyboard.press('Tab');
      assert.equal(await page.locator(':focus').getAttribute('data-geo-refresh'), '1');
      assert(parseFloat(await refresh.evaluate(n => getComputedStyle(n).outlineWidth)) >= 2, 'Visible keyboard focus');
      const slow = async route => { await new Promise(r => setTimeout(r, 450)); await route.continue(); };
      await page.route('**/tacare/nearby/data?**', slow);
      await refresh.click();
      assert(await refresh.isDisabled()); assert.equal(await refresh.getAttribute('aria-busy'), 'true');
      await page.waitForFunction(() => !document.querySelector('[data-geo-refresh]').disabled);
      await page.unroute('**/tacare/nearby/data?**', slow);
      await page.locator('[data-geo-radius]').selectOption('50');
      await page.waitForFunction(() => !document.querySelector('[data-geo-refresh]').disabled);
      const card = page.locator('.gm-result--panel').first(); assert(await card.count());
      assert.equal(await page.locator('.gm-result .gm-google-maps').count(), 0, 'No duplicate external map buttons in cards/popups');
      const response = await context.request.get(hub + '/tacare/nearby/data?view=' + (role === 'provider' ? 'receive' : 'hire') + '&source_id=' + await page.locator('[data-geo-source]').inputValue() + '&radius=50');
      const payload = await response.json();
      assert(await page.locator('[data-geo-route]').evaluate(n => n.hidden));
      const link = card.getByRole('link', {name: 'Xem đối chiếu & kết nối', exact: true});
      assert.equal((await context.request.get(hub + await link.getAttribute('href'))).status(), 200);
      assert.equal(await link.evaluate(n => getComputedStyle(n).color), 'rgb(255, 255, 255)');
      for (const button of await card.getByRole('button').all()) {
        assert((await button.boundingBox()).height >= 44, 'Distinct touch target');
        assert.equal(await button.evaluate(n => getComputedStyle(n).borderStyle), 'solid');
      }
      const edit = page.locator('[data-geo-edit]');
      assert.equal(new URL(await edit.getAttribute('href')).hostname, role === 'business' ? 'khovieclam.localhost' : 'tuhoso.localhost');
      await card.getByRole('button', {name: 'Xem đường đi', exact: true}).click();
      await page.waitForFunction(() => document.querySelector('[data-nearby-canvas]').dataset.routeVisible === '1');
      const previewUrl = new URL(await page.locator('[data-geo-directions]').getAttribute('href'));
      assert.equal(previewUrl.searchParams.get('origin'), payload.source.point.join(','), 'The in-page route preview still compares the two selected records');
      assert.equal(previewUrl.searchParams.get('destination'), payload.markers[0].point.join(','));
      const external = page.locator('[data-geo-directions]');
      assert.equal(await external.getAttribute('target'), '_blank'); assert.equal(await external.getAttribute('rel'), 'noopener');
      // Only this selected-route Google Maps button remains; verify real new-tab navigation.
      await context.route('https://www.google.com/maps/**', route => route.fulfill({contentType:'text/html',body:'<title>Directions navigation check</title>'}));
      const popupEvent = page.waitForEvent('popup'); await external.click(); const popup = await popupEvent;
      await popup.waitForLoadState(); assert.equal(popup.url(), previewUrl.href); await popup.close();
      await context.unroute('https://www.google.com/maps/**');
      await page.waitForFunction(() => !document.querySelector('[data-geo-refresh]').disabled);
      assert((await page.locator('[data-geo-route-distance]').innerText()).endsWith(' km'));
      assert((await page.locator('[data-geo-directions]').boundingBox()).height >= 44);
      const geometry = await page.evaluate(() => JSON.stringify(document.querySelector('[data-nearby-canvas]').careMap.careGL.getStyle().sources['tacare-route'].data));
      await page.locator('[data-geo-fit]').click();
      assert.equal(await page.evaluate(() => JSON.stringify(document.querySelector('[data-nearby-canvas]').careMap.careGL.getStyle().sources['tacare-route'].data)), geometry);
      await settledMap();
      await page.locator('#nearby-connections').screenshot({path: shots + '/' + role + '-route-1440.png'});
      await page.setViewportSize({width: 375, height: 1100});
      assert(!await page.evaluate(() => document.documentElement.scrollWidth > innerWidth + 1));
      await settledMap();
      await page.locator('#nearby-connections').screenshot({path: shots + '/' + role + '-route-375.png'});
      await page.locator('[data-geo-route-clear]').click();
      assert(await page.locator('[data-geo-route]').evaluate(n => n.hidden));
    }
    assert.deepEqual(errors, []);
    console.log('PASS centered map title; guest/native provider/business scopes; 8 widths 320–1920; one selected-route Google Maps button, no duplicate card buttons, permitted coordinates and new-tab navigation; button fills/borders/focus/44px targets; loading state; role/radius controls; owner edit links, pair navigation, route/total km/fit/clear; no business-data writes');
  } finally { await browser.close(); }
})().catch(e => {console.error(e.stack); process.exit(1);});
