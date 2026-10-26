/* Local Chrome integration; existing identities remain in an ignored 0600 file. */
const {chromium} = require('playwright');
const fs = require('node:fs');
const assert = require('node:assert/strict');
const identities = JSON.parse(fs.readFileSync(process.env.TACARE_UI_IDENTITY_FILE || 'runtime/tacare/nearby_test_identities.json', 'utf8'));
const hub = 'http://tacare.localhost:8069';
const output = 'runtime/nearby-map-review'; fs.mkdirSync(output, {recursive: true});
(async () => {
  const browser = await chromium.launch({channel: 'chrome', headless: true});
  const errors = []; let context, page, restore;
  async function fresh(role) {
    if (context) await context.close();
    context = await browser.newContext({viewport: {width: 1440, height: 1100}, reducedMotion: 'reduce'});
    page = await context.newPage(); page.on('pageerror', e => errors.push(e.message));
    if (role) {
      const who = identities.find(i => i.role === role); assert(who);
      await page.goto(hub + '/web/login');
      await page.waitForLoadState('networkidle');
      const form = page.locator('.tc-login-form');
      await form.locator('[name=login]').fill(who.login);
      await form.locator('[name=password]').fill(who.password);
      await form.getByRole('button', {name: 'Đăng nhập', exact: true}).click();
      await page.waitForURL(url => !url.pathname.startsWith('/care/sso/') && !url.pathname.startsWith('/web/login') && !url.searchParams.has('login'));
      await page.waitForLoadState('networkidle');
      await page.waitForFunction(() => document.querySelector('.tc-live')?.dataset.accessGuest === '0');
    }
    await page.goto(hub + '/#nearby-connections');
    await page.locator('#nearby-connections').scrollIntoViewIfNeeded();
    await page.waitForFunction(() => !!document.querySelector('[data-nearby-canvas] .leaflet-container') || document.querySelector('[data-nearby-canvas]')?.classList.contains('leaflet-container'));
    if (role) await page.waitForFunction(() => document.querySelector('[data-geo-results-status]').textContent.length > 0 && !document.querySelector('[data-geo-results-status]').textContent.includes('Đang đối chiếu'));
  }
  async function payload(view = 'hire', source = 0, radius = 50) {
    const r = await context.request.get(hub + `/tacare/nearby/data?view=${view}&source_id=${source}&radius=${radius}`);
    assert.equal(r.status(), 200); assert.match(r.headers()['cache-control'], /no-store/);
    return r.json();
  }
  async function restoreLocation(value) {
    await page.goto(value.edit_url);
    const form = page.locator('form[data-work-form]');
    await form.locator('.gm-address-editor, .gm-picker-advanced').evaluateAll(nodes => nodes.forEach(n => n.open = true));
    await form.locator('[name=geo_lat]').fill(String(value.point[0]));
    await form.locator('[name=geo_lon]').fill(String(value.point[1]));
    await form.locator('[data-geo-address-manual]').fill(value.form_address ?? value.address ?? '');
    await form.locator('[name=geo_share]').setChecked(value.shared);
    await form.locator('[name=intent][value=publish]').click();
    await page.waitForURL(url => /\/tuhoso\/work\/\d+$/.test(url.pathname));
  }
  try {
    await fresh();
    assert.equal(await page.locator('.gm-profession-marker').count(), 0);
    assert.equal(await page.locator('.gm-results .gm-result').count(), 0);
    const denied = await context.request.get(hub + '/tacare/nearby/data', {maxRedirects: 0});
    assert([302, 303, 403].includes(denied.status()));
    for (const width of [320, 375, 767, 768, 1024, 1440, 1920]) {
      await page.setViewportSize({width, height: 1100});
      assert(!await page.evaluate(() => document.documentElement.scrollWidth > innerWidth + 1), 'Overflow at ' + width);
    }
    await page.setViewportSize({width: 1440, height: 1100});
    await page.locator('#nearby-connections').screenshot({path: output + '/guest-1440.png'});
    await page.locator('.gm-guest a').click();
    assert.equal(await page.locator('#tc-login-dialog[open]').count(), 1);
    await page.getByRole('button', {name: 'Đóng cửa sổ đăng nhập', exact: true}).click();

    await fresh('business');
    let hire = await payload(); assert(hire.markers.length > 0);
    assert.equal(await page.locator('[data-geo-view=receive]').count(), 0);
    assert(await page.locator('.gm-results .gm-result').count() > 0);
    const pairUrl = hire.markers[0].url;
    assert.equal((await context.request.get(hub + pairUrl)).status(), 200);
    await page.locator('.gm-profession-marker').first().focus(); await page.keyboard.press('Enter');
    assert(await page.locator('.gm-popup .gm-result-link').count() > 0);
    await page.keyboard.press('Escape');
    await page.waitForFunction(() => document.querySelector('[data-nearby-canvas]').dataset.baseLoaded === '1');
    assert.equal(await page.locator('[data-geo-picker]').count(), 0, 'TA.CARE only displays matches');
    for (const width of [320, 375, 768, 1024, 1440, 1920]) {
      await page.setViewportSize({width, height: 1100});
      assert(!await page.evaluate(() => document.documentElement.scrollWidth > innerWidth + 1), 'Authenticated overflow ' + width);
      if ([375, 1440].includes(width)) await page.locator('#nearby-connections').screenshot({path: output + '/business-' + width + '.png'});
    }
    const writeDenied = await context.request.post(hub + '/kvl/flexible/save', {form: {view: 'hire', source_id: String(hire.source.id)}});
    assert.equal(writeDenied.status(), 400, 'Missing CSRF token must fail');
    await fresh('other_business');
    const foreign = await context.request.get(hub + '/tacare/nearby/data?view=hire&source_id=' + hire.source.id);
    assert([403, 404].includes(foreign.status()));
    assert([403, 404].includes((await context.request.get(hub + pairUrl)).status()));

    await fresh('provider');
    await page.locator('[data-geo-view=receive]').click();
    await page.waitForFunction(() => document.querySelector('[data-geo-results-status]').textContent.includes('gợi ý phù hợp trong'));
    const receive = await payload('receive'); assert(receive.markers.length > 0);
    await page.setViewportSize({width: 375, height: 1100});
    assert.match(receive.source.edit_url, /^http:\/\/tuhoso.localhost:8069\/tuhoso\/work\/\d+\/edit$/);
    await page.locator('[data-geo-edit]').click();
    await page.waitForLoadState('networkidle');
    assert.equal(new URL(page.url()).hostname, 'tuhoso.localhost');
    const form = page.locator('form[data-work-form]');
    await form.locator('.gm-address-editor, .gm-picker-advanced').evaluateAll(nodes => nodes.forEach(n => n.open = true));
    assert.equal(await form.locator('[data-geo-picker]').count(), 1);
    receive.source.form_address = await form.locator('[name=flex_location]').inputValue();
    await form.locator('[name=geo_lat]').fill('7');
    await form.locator('[name=intent][value=draft]').click();
    assert.equal(await page.locator('#work-form-error').count(), 1);
    assert.equal(await form.locator('[name=geo_lat]').inputValue(), '7', 'Invalid form retains values');
    await form.locator('.gm-address-editor, .gm-picker-advanced').evaluateAll(nodes => nodes.forEach(n => n.open = true));
    const changedLat = Number((receive.source.point[0] + .002).toFixed(6));
    await form.locator('[name=geo_lat]').fill(String(changedLat));
    await form.locator('[name=geo_lon]').fill(String(receive.source.point[1]));
    await form.locator('[data-geo-address-manual]').fill('Điểm QA tạm thời');
    await form.locator('.gm-picker-details').evaluate(n => n.open = true);
    await page.waitForFunction(() => document.querySelector('[data-geo-canvas]').dataset.baseLoaded === '1');
    await form.locator('[data-geo-gps]').click();
    await page.waitForFunction(() => document.querySelector('[data-geo-status]').textContent.includes('Chưa lấy được'));
    await page.locator('#work-place').screenshot({path: output + '/tuhoso-picker-375.png'});
    restore = receive.source;
    fs.writeFileSync('runtime/tacare/nearby_browser_restore.json', JSON.stringify({id: receive.source.id, sample: receive.source.sample, address: receive.source.address, location: receive.source.form_address, point: receive.source.point, shared: receive.source.shared}), {mode: 0o600});
    await form.locator('[name=intent][value=publish]').click();
    await page.waitForURL(url => /\/tuhoso\/work\/\d+$/.test(url.pathname));
    const changed = await payload('receive', receive.source.id);
    assert.equal(changed.source.point[0], changedLat); assert(!changed.source.sample);
    await page.goto(hub + '/#nearby-connections');
    await page.locator('#nearby-connections').scrollIntoViewIfNeeded();
    await page.locator('[data-geo-view=receive]').click();
    await page.waitForFunction(() => document.querySelector('[data-geo-results-status]').textContent.includes('gợi ý phù hợp trong'));
    await page.locator('#nearby-connections').screenshot({path: output + '/provider-375.png'});
    await restoreLocation(receive.source); restore = null;
    await page.route('https://tiles.openfreemap.org/**', route => route.abort());
    await page.goto(hub + '/#nearby-connections');
    await page.locator('#nearby-connections').scrollIntoViewIfNeeded();
    await page.locator('[data-geo-view=receive]').click();
    await page.waitForFunction(() => document.querySelector('[data-geo-results-status]').textContent.includes('gợi ý phù hợp trong'));
    assert(await page.locator('.gm-results .gm-result').count() > 0);
    assert.deepEqual(errors, []);
    console.log('PASS Chrome: real OpenFreeMap/MapLibre map, guest privacy/login, native business/provider sessions, bilateral matches and honest empty states, foreign denial/CSRF, marker keyboard/popups, TA.CARE display-only, Tủ owner form source IDs and persistent location save/validation/restore, GPS denial, offline tiles/list fallback, 7 widths and reduced motion');
  } finally {
    if (restore) await restoreLocation(restore).catch(() => {});
    await browser.close();
  }
})().catch(e => {console.error(e.stack); process.exit(1);});
