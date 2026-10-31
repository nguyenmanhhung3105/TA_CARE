/* Local, read-only Chrome check. No token, record, consent or settings writes. */
const fs = require('node:fs'), assert = require('node:assert/strict');
const {chromium} = require(process.env.TACARE_PLAYWRIGHT_MODULE || 'playwright');
const hub = 'http://tacare.localhost:8069';
const identities = JSON.parse(fs.readFileSync('runtime/tacare/map_test_accounts_20261027/map_test_accounts_20261027.json', 'utf8'));
(async () => {
    const browser = await chromium.launch({channel: 'chrome', headless: true});
    try {
        const guest = await browser.newContext();
        for (const [host, marker] of [['tacare', 'tc-hub'], ['khovieclam', 'tc-jobs'], ['tuhoso', 'tc-profiles']]) {
            const response = await guest.request.get(`http://${host}.localhost:8069/`);
            assert.equal(response.status(), 200); assert((await response.text()).includes(marker));
        }
        await guest.close();
        for (const width of [1366, 375]) {
            const ctx = await browser.newContext({viewport: {width, height: 768}, reducedMotion: 'reduce'});
            const page = await ctx.newPage(), errors = [];
            let externalSDK = 0;
            page.on('pageerror', error => errors.push(error.name));
            page.on('request', request => {
                if (request.url().includes('api.mapbox.com/mapbox-gl-js')) externalSDK++;
            });
            const who = identities.find(item => item.key === (width === 1366 ? 'home' : 'provider_home'));
            const loginOrigin = width === 1366 ? 'http://khovieclam.localhost:8069' : 'http://tuhoso.localhost:8069';
            await page.goto(loginOrigin + '/web/login');
            const form = page.locator('.tc-login-form');
            await form.locator('[name=login]').fill(who.login);
            await form.locator('[name=password]').fill(who.password);
            await form.getByRole('button', {name: 'Đăng nhập', exact: true}).click();
            await page.waitForTimeout(4000);
            let authenticated = false;
            for (let attempt = 0; attempt < 20; attempt++) {
                const session = await ctx.request.get(hub + '/care/sso/status');
                if ((await session.json()).uid === who.user_id) {authenticated = true; break;}
                await page.waitForTimeout(500);
            }
            assert(authenticated, 'Native login and browser SSO completed');
            await page.goto(hub + '/', {waitUntil: 'domcontentloaded'});
            const canvas = page.locator('[data-nearby-canvas]');
            assert.equal(await canvas.evaluate(node => !!node.careMap), false);
            await canvas.scrollIntoViewIfNeeded();
            await page.waitForFunction(() => document.querySelector('[data-nearby-canvas]')?.dataset.baseLoaded === '1', null, {timeout: 45000});
            assert.equal(await canvas.getAttribute('data-map-provider'), 'openfreemap', 'Default stays available without Mapbox token');
            assert.equal(externalSDK, 0);
            const camera = await canvas.evaluate(node => {
                const map = node.careMap, bounds = map.options.maxBounds;
                window.careProviderTestMap = map;
                return {bounds: [[bounds.getSouth(), bounds.getWest()], [bounds.getNorth(), bounds.getEast()]],
                    viscosity: map.options.maxBoundsViscosity, minZoom: map.getMinZoom()};
            });
            assert.deepEqual(camera.bounds, [[8, 102], [24, 110]]);
            assert.equal(camera.viscosity, 1); assert.equal(camera.minZoom, 6);
            await canvas.evaluate(node => node.careMap.setView([0, 0], 10, {animate: false}));
            await page.waitForTimeout(500);
            assert(await canvas.evaluate(node => {
                const center = node.careMap.getCenter();
                return center.lat >= 8 && center.lat <= 24 && center.lng >= 102 && center.lng <= 110;
            }), 'Programmatic camera is clamped back to service rectangle');
            await page.waitForFunction(() => {
                const text = document.querySelector('[data-geo-results-status]')?.textContent;
                return text && !text.includes('Đang đối chiếu');
            }, null, {timeout: 30000});
            assert(await page.locator('.gm-results .gm-result').count() > 0,
                'Matching list at ' + width + ': ' + await page.locator('[data-geo-results-status]').textContent());
            assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth + 1), false);
            assert(await canvas.evaluate(node => node.careMap === window.careProviderTestMap));
            const edit = page.locator('[data-geo-edit]');
            await edit.click();
            await page.waitForLoadState('domcontentloaded');
            const picker = page.locator('[data-geo-picker]');
            await picker.locator('[data-geo-canvas]').scrollIntoViewIfNeeded();
            await page.waitForFunction(() => document.querySelector('[data-geo-canvas]')?.dataset.baseLoaded === '1', null, {timeout: 45000});
            assert.equal(await picker.getAttribute('data-map-provider'), 'openfreemap');
            assert.equal(await page.locator('form[data-work-form] input[name=flex_location][type=hidden]').count(), 1, 'Canonical address field');
            assert.equal(await page.locator('form[data-work-form] input[name=csrf_token]').count(), 1, 'Native work-form CSRF');
            assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth + 1), false);
            assert.deepEqual(errors, []);
            console.log(`PASS local ${width}: native login, default map without token, Vietnam camera clamp, matching list, owner location form/CSRF, no overflow/errors`);
            await ctx.close();
        }
    } finally { await browser.close(); }
})().catch(error => {console.error('FAILED local provider browser check:', error.name, error.message); process.exitCode = 1;});
