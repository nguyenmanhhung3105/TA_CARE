/* Real-provider local checks; restores original form values after persistence. */
const {chromium} = require('playwright');
const fs = require('node:fs'), assert = require('node:assert/strict');
const ids = JSON.parse(fs.readFileSync(process.env.TACARE_UI_IDENTITY_FILE || 'runtime/tacare/nearby_test_identities.json', 'utf8'));
const hub = 'http://tacare.localhost:8069';
(async () => {
  const browser = await chromium.launch({channel: 'chrome', headless: true});
  let page, original;
  const errors = [];
  async function restore() {
    await page.goto(original.edit_url); await page.waitForLoadState('networkidle');
    const form = page.locator('[data-work-form]');
    await form.locator('.gm-address-editor, .gm-picker-advanced').evaluateAll(nodes => nodes.forEach(n => n.open = true));
    await form.locator('[name=geo_lat]').fill(String(original.point[0]));
    await form.locator('[name=geo_lon]').fill(String(original.point[1]));
    await form.locator('[data-geo-address-manual]').fill(original.location);
    await form.locator('[name=flex_region_id]').selectOption(original.region);
    await form.locator('[name=geo_share]').setChecked(original.shared);
    await form.locator('[name=intent][value=publish]').click();
    await page.waitForURL(url => /\/tuhoso\/work\/\d+$/.test(url.pathname));
    original = null;
  }
  try {
    const context = await browser.newContext({viewport: {width: 1440, height: 1100}, reducedMotion: 'reduce'});
    page = await context.newPage(); page.on('pageerror', e => errors.push(e.message));
    await page.goto(hub + '/web/login'); await page.waitForLoadState('networkidle');
    const who = ids.find(i => i.role === 'provider'), login = page.locator('.tc-login-form');
    await login.locator('[name=login]').fill(who.login); await login.locator('[name=password]').fill(who.password);
    await login.getByRole('button', {name: 'Đăng nhập', exact: true}).click();
    await page.waitForURL(u => !u.pathname.startsWith('/care/sso/') && !u.pathname.startsWith('/web/login') && !u.searchParams.has('login'));
    await page.waitForLoadState('networkidle'); await page.goto(hub + '/#nearby-connections');
    await page.locator('#nearby-connections').scrollIntoViewIfNeeded();
    await page.waitForFunction(() => document.querySelector('.gm-results .gm-result'));
    await page.waitForFunction(() => document.querySelector('[data-nearby-canvas]').dataset.mapPalette === 'soft');
    assert.equal(await page.evaluate(() => window.careMapServices.address({street: 'Đường QA', country: 'Vietnam', countrycode: 'VN'})), 'Đường QA, Việt Nam');
    const api = await context.request.get(hub + '/tacare/nearby/data?view=receive&radius=10');
    const data = await api.json(); assert(data.markers.length);
    await page.locator('.gm-results .gm-result').first().getByRole('button', {name: 'Xem đường đi', exact: true}).click();
    await page.waitForFunction(() => document.querySelector('[data-geo-route-status]').textContent.startsWith('Tuyến ô tô'), {timeout: 20000});
    assert(await page.evaluate(() => !!document.querySelector('[data-nearby-canvas]').careMap.careGL.getLayer('tacare-route-line')));
    const directions = new URL(await page.locator('[data-geo-directions]').getAttribute('href'));
    assert.equal(directions.hostname, 'www.google.com'); assert.equal(directions.searchParams.get('api'), '1');
    assert.equal(directions.searchParams.get('destination'), data.markers[0].point.join(','));
    assert.equal(directions.searchParams.get('origin'), data.source.point.join(','));
    await page.locator('#nearby-connections').screenshot({path: 'runtime/nearby-map-review/route-soft-palette-1440.png'});
    await page.setViewportSize({width: 375, height: 1000});
    assert(!await page.evaluate(() => document.documentElement.scrollWidth > innerWidth + 1));
    await page.locator('#nearby-connections').screenshot({path: 'runtime/nearby-map-review/route-soft-palette-375.png'});

    await page.goto(data.source.edit_url); await page.waitForLoadState('networkidle');
    const form = page.locator('[data-work-form]');
    await form.locator('.gm-address-editor, .gm-picker-advanced').evaluateAll(nodes => nodes.forEach(n => n.open = true));
    original = {...data.source, location: await form.locator('[name=flex_location]').inputValue(),
      region: await form.locator('[name=flex_region_id]').inputValue()};
    fs.writeFileSync('runtime/tacare/nearby_navigation_restore.json', JSON.stringify(original), {mode: 0o600});
    const point = original.point[0] > 18 ? [21.0273, 105.8524] : [10.7769, 106.7009];
    await form.locator('.gm-picker-details').evaluate(n => n.open = true);
    await form.locator('[name=geo_lat]').fill(String(point[0]));
    await form.locator('[name=geo_lon]').fill(String(point[1]));
    await form.locator('[name=geo_lon]').dispatchEvent('change');
    await page.waitForFunction(() => document.querySelector('[data-geo-status]').textContent.startsWith('Đã lấy địa chỉ'), {timeout: 20000});
    const full = await form.locator('[name=flex_location]').inputValue();
    assert(full.includes('Việt Nam')); assert(full.includes(',')); assert(full.length > 40);
    assert.equal(await form.locator('[name=geo_address]').inputValue(), full);
    const mapUrl = new URL(await form.locator('[data-geo-url]').inputValue());
    assert.equal(mapUrl.searchParams.get('query'), point.join(','));
    const extended = (full + ', Cổng phụ khu làm việc, lối vào bên trái, ' + 'ghi chú điểm hẹn để kiểm thử lưu đủ địa chỉ '.repeat(6)).trim();
    assert(extended.length > 250 && extended.length < 1000);
    await form.locator('[data-geo-address-manual]').fill(extended);
    await page.locator('#work-place').screenshot({path: 'runtime/nearby-map-review/full-address-picker-375.png'});
    await form.locator('[name=intent][value=publish]').click();
    await page.waitForURL(url => /\/tuhoso\/work\/\d+$/.test(url.pathname));
    const persisted = await context.request.get(hub + '/tacare/nearby/data?view=receive&source_id=' + original.id);
    assert.equal((await persisted.json()).source.address, extended, 'Full address persisted without truncation');
    await page.goto(original.edit_url); await page.waitForLoadState('networkidle');
    assert.equal(await form.locator('[name=flex_location]').inputValue(), extended);
    assert.equal(await form.locator('[name=geo_address]').inputValue(), extended);
    await form.locator('.gm-address-editor, .gm-picker-advanced').evaluateAll(nodes => nodes.forEach(n => n.open = true));

    // An older or failed geocoder response must never replace a typed address.
    await page.route('https://photon.komoot.io/**', async route => {
      await new Promise(resolve => setTimeout(resolve, 1800));
      await route.fulfill({json: {features: [{properties: {street: 'Địa chỉ chậm không được ghi đè', city: 'Hà Nội', country: 'Việt Nam', countrycode: 'VN'}}]}}).catch(() => {});
    });
    await form.locator('[name=geo_lat]').fill(String(point[0] + .001));
    const pendingReverse = page.waitForRequest(r => r.url().startsWith('https://photon.komoot.io/'));
    await form.locator('[name=geo_lat]').dispatchEvent('change');
    await pendingReverse;
    await form.locator('[data-geo-address-manual]').fill('Nội dung người dùng giữ lại');
    await page.waitForTimeout(2500);
    assert.equal(await form.locator('[name=flex_location]').inputValue(), 'Nội dung người dùng giữ lại');
    await restore();
    assert.deepEqual(errors, []);
    console.log('PASS real Photon full address → main location field → database/reopened form >250 chars; Google point URL; soft map palette; real OSRM road geometry/distance/time; approximate-only directions URL; 375/1440; stale geocoder cannot overwrite edits; original location restored');
  } finally {
    if (original) await restore().catch(() => {});
    await browser.close();
  }
})().catch(e => {console.error(e.stack); process.exit(1);});
