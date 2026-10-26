/* No database writes. Camera movement must preserve route data and labels. */
const {chromium} = require('playwright');
const fs = require('node:fs'), assert = require('node:assert/strict');
const accounts = JSON.parse(fs.readFileSync(process.env.TACARE_UI_IDENTITY_FILE || 'runtime/tacare/nearby_test_identities.json', 'utf8'));
(async () => {
  const browser = await chromium.launch({channel: 'chrome', headless: true});
  try {
    const context = await browser.newContext({viewport: {width: 1440, height: 1100}});
    const page = await context.newPage();
    const errors = []; let routingRequests = 0, reportedRoute;
    page.on('pageerror', e => errors.push(e.message));
    page.on('request', r => { if (r.url().startsWith('https://router.project-osrm.org/')) ++routingRequests; });
    page.on('response', async response => {
      if (response.url().startsWith('https://router.project-osrm.org/') && response.ok()) reportedRoute = (await response.json()).routes?.[0];
    });
    const hub = 'http://tacare.localhost:8069';
    await page.goto(hub + '/web/login'); await page.waitForLoadState('networkidle');
    const identity = accounts.find(a => a.role === 'provider'), form = page.locator('.tc-login-form');
    await form.locator('[name=login]').fill(identity.login); await form.locator('[name=password]').fill(identity.password);
    await form.getByRole('button', {name: 'Đăng nhập', exact: true}).click();
    await page.waitForURL(u => !u.pathname.startsWith('/care/sso/') && !u.pathname.startsWith('/web/login') && !u.searchParams.has('login'));
    await page.waitForLoadState('networkidle'); await page.goto(hub + '/#nearby-connections');
    await page.locator('#nearby-connections').scrollIntoViewIfNeeded();
    await page.waitForFunction(() => document.querySelector('.gm-results .gm-result'));
    await page.locator('.gm-results .gm-result').first().getByRole('button', {name: 'Xem đường đi', exact: true}).click();
    await page.waitForFunction(() => document.querySelector('[data-nearby-canvas]').dataset.routeVisible === '1');
    const original = await page.evaluate(() => {
      const m = document.querySelector('[data-nearby-canvas]').careMap, gl = m.careGL, style = gl.getStyle();
      const routeIndex = style.layers.findIndex(l => l.id === 'tacare-route-line');
      const text = style.layers.map((l, i) => ({...l, index: i})).filter(l => l.type === 'symbol' && l.layout?.['text-field']);
      const colorAtCurrentZoom = expression => {
        if (typeof expression === 'string') return expression;
        let color = expression[4];
        for (let i = 3; i < expression.length; i += 2) if (expression[i] <= gl.getZoom()) color = expression[i + 1];
        return color;
      };
      return {data: JSON.stringify(style.sources['tacare-route'].data), labelsAbove: text.every(l => l.index > routeIndex),
        bridgesBelow: style.layers.every((l, i) => !l.id.startsWith('bridge_') || i < routeIndex),
        mainRoad: colorAtCurrentZoom(gl.getPaintProperty('road_trunk_primary', 'line-color')),
        minorRoad: colorAtCurrentZoom(gl.getPaintProperty('road_minor', 'line-color')),
        center: [m.getCenter().lat, m.getCenter().lng], zoom: m.getZoom()};
    });
    assert(original.labelsAbove, 'All road/place labels must render above route');
    assert(original.bridgesBelow, 'Bridge decks must never cover route');
    const brightness = hex => [1, 3, 5].reduce((sum, i) => sum + parseInt(hex.slice(i, i + 2), 16), 0);
    assert(brightness(original.mainRoad) < brightness(original.minorRoad), 'Main roads must be darker than minor roads');
    await page.waitForFunction(() => !document.querySelector('[data-geo-route-metrics]').hidden);
    assert(reportedRoute);
    const expectedKm = new Intl.NumberFormat('vi-VN', {maximumFractionDigits: reportedRoute.distance < 100 ? 3 : 2}).format(reportedRoute.distance / 1000) + ' km';
    assert.equal(await page.locator('[data-geo-route-distance]').innerText(), expectedKm, 'Total km must use the full OSRM route length');
    const routeCount = routingRequests;
    for (const [zoom, dx, dy] of [[14, 190, 100], [16, -800, 300], [12, 1000, -700], [15, -900, -400]]) {
      await page.evaluate(({zoom, dx, dy}) => {
        const m = document.querySelector('[data-nearby-canvas]').careMap;
        m.setZoom(zoom, {animate: false}); m.panBy([dx, dy], {animate: false});
      }, {zoom, dx, dy});
      assert.equal(await page.evaluate(() => JSON.stringify(document.querySelector('[data-nearby-canvas]').careMap.careGL.getStyle().sources['tacare-route'].data)), original.data);
      assert.equal(await page.locator('[data-geo-route]').evaluate(n => n.hidden), false);
    }
    await page.evaluate(origin => {
      const m = document.querySelector('[data-nearby-canvas]').careMap;
      m.setView(origin.center, 15, {animate: false});
    }, original);
    await page.waitForFunction(() => document.querySelector('[data-nearby-canvas]').careMap.careGL.queryRenderedFeatures({layers: ['tacare-route-line']}).length > 0);
    assert.equal(routingRequests, routeCount, 'Pan/zoom must never recalculate the route');
    await page.locator('.gm-map .leaflet-control-zoom-in').click();
    await page.waitForTimeout(400);
    await page.locator('.gm-map .leaflet-control-zoom-out').click();
    await page.waitForTimeout(400);
    const box = await page.locator('.gm-map').boundingBox();
    await page.mouse.move(box.x + box.width * .7, box.y + box.height * .55);
    await page.mouse.down();
    await page.mouse.move(box.x + box.width * .7 - 160, box.y + box.height * .55 + 90, {steps: 12});
    await page.mouse.up();
    await page.evaluate(origin => document.querySelector('[data-nearby-canvas]').careMap.setView(origin.center, 16, {animate: false}), original);
    await page.waitForFunction(() => {
      const gl = document.querySelector('[data-nearby-canvas]').careMap.careGL;
      return gl.areTilesLoaded() && gl.queryRenderedFeatures({layers: ['highway-name-major', 'highway-name-minor']}).length > 0;
    });
    assert.equal(routingRequests, routeCount, 'Actual zoom controls and mouse dragging must not refetch route');
    const camera = await page.evaluate(() => {
      const m = document.querySelector('[data-nearby-canvas]').careMap;
      return [m.getCenter().lat, m.getCenter().lng, m.getZoom()];
    });
    const refresh = page.waitForResponse(r => r.url().includes('/tacare/nearby/data'));
    await page.evaluate(() => window.dispatchEvent(new Event('focus'))); await refresh;
    await page.waitForFunction(() => !document.querySelector('[data-geo-results-status]').textContent.startsWith('Đang'));
    assert.equal(await page.evaluate(() => JSON.stringify(document.querySelector('[data-nearby-canvas]').careMap.careGL.getStyle().sources['tacare-route'].data)), original.data);
    const cameraDrift = await page.evaluate(previous => {
      const m = document.querySelector('[data-nearby-canvas]').careMap;
      return {zoom: m.getZoom(), pixels: m.project(previous.slice(0, 2), previous[2]).distanceTo(m.project(m.getCenter(), previous[2]))};
    }, camera);
    assert.equal(cameraDrift.zoom, camera[2]);
    assert(cameraDrift.pixels < 1.5, 'Focus must preserve the camera within normal Leaflet pixel rounding');
    assert.equal(routingRequests, routeCount);
    await page.locator('#nearby-connections').screenshot({path: 'runtime/nearby-map-review/route-labels-persistent-1440.png'});
    await page.setViewportSize({width: 375, height: 1000});
    await page.waitForFunction(() => document.querySelector('[data-nearby-canvas]').dataset.routeVisible === '1');
    assert(!await page.evaluate(() => document.documentElement.scrollWidth > innerWidth + 1));
    await page.locator('#nearby-connections').screenshot({path: 'runtime/nearby-map-review/route-labels-persistent-375.png'});
    assert.equal(routingRequests, routeCount, 'Resize must not recalculate route');
    // Isolated visual probe of a REAL public road route over Saigon Bridge.
    // Only the transient GL source changes; no matching/record data is written.
    await page.setViewportSize({width: 1440, height: 1100});
    const bridgeProbe = await page.evaluate(async () => {
      const response = await fetch('https://router.project-osrm.org/route/v1/driving/106.718,10.797;106.739,10.802?overview=full&geometries=geojson&steps=false');
      const result = await response.json(); if (result.code !== 'Ok') throw new Error('Public bridge route unavailable');
      const m = document.querySelector('[data-nearby-canvas]').careMap;
      m.careGL.getSource('tacare-route').setData({type: 'Feature', properties: {}, geometry: result.routes[0].geometry});
      m.setView([10.799, 106.7255], 16, {animate: false});
      return result.routes[0].geometry.coordinates.length;
    });
    assert(bridgeProbe > 5);
    await page.waitForFunction(() => {
      const gl = document.querySelector('[data-nearby-canvas]').careMap.careGL;
      return gl.areTilesLoaded() && gl.queryRenderedFeatures({layers: ['tacare-route-line']}).length &&
        gl.queryRenderedFeatures({layers: ['bridge_trunk_primary', 'bridge_motorway', 'bridge_secondary_tertiary', 'bridge_street']}).length;
    });
    await page.locator('.gm-map').screenshot({path: 'runtime/nearby-map-review/gray-roads-saigon-bridge-1440.png'});
    assert(await page.evaluate(() => !!document.querySelector('[data-nearby-canvas]').careMap.careGL.getLayer('tacare-landcover-farmland')));
    await page.evaluate(() => document.querySelector('[data-nearby-canvas]').careMap.setView([10.66, 106.35], 12, {animate: false}));
    await page.waitForFunction(() => document.querySelector('[data-nearby-canvas]').careMap.careGL.areTilesLoaded());
    const greenCover = await page.evaluate(() => {
      const gl = document.querySelector('[data-nearby-canvas]').careMap.careGL;
      return gl.queryRenderedFeatures({layers: ['tacare-landcover-farmland', 'landcover_wood', 'landcover_grass']}).map(f => f.properties.class);
    });
    console.log('Rural cover classes visible:', [...new Set(greenCover)].join(', ') || 'No mapped cover in this viewport');
    await page.locator('.gm-map').screenshot({path: 'runtime/nearby-map-review/rural-green-cover-1440.png'});
    // A permission/state refresh that removes the pair MUST remove its route.
    await page.route('**/tacare/nearby/data?**', async route => {
      const actual = await route.fetch(); const payload = await actual.json(); payload.markers = [];
      await route.fulfill({response: actual, json: payload});
    });
    await page.locator('[data-geo-refresh]').click();
    await page.waitForFunction(() => document.querySelector('[data-geo-route]').hidden);
    assert.equal(await page.evaluate(() => document.querySelector('[data-nearby-canvas]').careMap.careGL.getStyle().sources['tacare-route'].data.features.length), 0);
    assert.deepEqual(errors, []);
    console.log('PASS darker gray main roads/light minor roads; route ABOVE bridge decks and BELOW street labels; real Saigon Bridge visual probe; prominent total km matches full OSRM road distance; pan/zoom/focus/resize preserve route with zero refetches; removed result clears it; 375/1440; no DB writes');
  } finally { await browser.close(); }
})().catch(e => {console.error(e.stack); process.exit(1);});
