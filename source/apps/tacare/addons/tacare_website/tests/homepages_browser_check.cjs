/** Read-only local browser regression. Requires Playwright in the test environment. */
const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

(async () => {
  const executablePath = process.env.TACARE_CHROME;
  const browser = await chromium.launch({headless: true, ...(executablePath ? {executablePath} : {})});
  try {
    const page = await browser.newPage();
    const problems = [];
    page.on('pageerror', (error) => problems.push(error.message));
    const sites = {khovieclam: ['jobs', 'tc-jobs'], tuhoso: ['profiles', 'tc-profiles'], tacare: ['hub', 'tc-hub']};
    for (const [site, [kind, marker]] of Object.entries(sites)) {
      for (const width of [1440, 768, 375, 320]) {
        await page.setViewportSize({width, height: 1000});
        const response = await page.goto(`http://${site}.localhost:8069/`, {waitUntil: 'networkidle'});
        assert.equal(response.status(), 200);
        await page.evaluate(async () => {
          await document.fonts.ready;
          for (let y = 0; y < document.documentElement.scrollHeight; y += 600) {
            scrollTo(0, y);
            await new Promise((resolve) => setTimeout(resolve, 40));
          }
          scrollTo(0, 0);
        });
        await page.waitForTimeout(800);
        const actual = await page.evaluate(() => ({
          overflow: document.documentElement.scrollWidth > innerWidth,
          kind: document.querySelector('[data-care-home]')?.dataset.careHome,
          classes: document.querySelector('#wrap').className.split(' '),
          headings: document.querySelectorAll('h1').length,
          font: getComputedStyle(document.querySelector('h1')).fontFamily,
          fontReady: document.fonts.check('400 16px "Be Vietnam Pro"'),
          imagesReady: [...document.querySelectorAll('.tc-live img')].filter(img=>!img.closest('dialog:not([open])')).every((img) => img.complete && img.naturalWidth),
          styleError: document.body.innerText.includes('A CSS error occurred'),
          brokenAnchors: [...document.querySelectorAll('a[href^="#"]')].filter((a) =>
            a.hash && !document.getElementById(decodeURIComponent(a.hash.slice(1)))).length,
        }));
        assert.equal(actual.kind, kind);
        assert(actual.classes.includes(marker));
        assert.equal(actual.headings, 1);
        assert(!actual.overflow, `${site} overflow at ${width}`);
        assert(actual.fontReady && actual.imagesReady && !actual.styleError);
        assert.equal(actual.brokenAnchors, 0);
        assert.equal(await page.locator('[data-work-carousel]').count(), site === 'tacare' ? 0 : 1);
        if (site === 'tuhoso') assert.equal(await page.locator('[data-carousel-kind=profiles]').count(),1);
        if (process.env.TACARE_SCREENSHOTS) {
          fs.mkdirSync(process.env.TACARE_SCREENSHOTS, {recursive: true});
          await page.screenshot({path: path.join(process.env.TACARE_SCREENSHOTS, `${site}-${width}.png`), fullPage: true});
        }
        console.log(`PASS ${site} ${width}px: marker, font, images, anchors, layout`);
      }
    }
    await page.goto('http://khovieclam.localhost:8069/', {waitUntil: 'networkidle'});
    await page.locator('[data-sector-tab="it"]').click();
    assert(await page.locator('[data-sector-panel="it"]').isVisible());
    await page.goto('http://tuhoso.localhost:8069/', {waitUntil:'networkidle'});
    await page.locator('[data-work-next]').click();
    assert.equal(await page.locator('[data-work-slide].is-active').getAttribute('aria-label'),'2 trên 3');
    await page.emulateMedia({reducedMotion:'reduce'});
    await page.waitForFunction(()=>document.querySelector('[data-work-pause]').disabled);
    assert(await page.locator('[data-work-pause]').isDisabled());
    await page.goto('http://tacare.localhost:8069/', {waitUntil:'networkidle'});
    assert.equal(await page.locator('[data-work-carousel]').count(),0);
    assert.equal(await page.locator('.h-map article').count(),3);
    assert.deepEqual(problems, []);
    console.log('PASS distinct homepages: Kho sector selection, Tủ carousel and reduced motion, static TA.CARE');
  } finally {
    await browser.close();
  }
})().catch((error) => { console.error(error.message); process.exitCode = 1; });
