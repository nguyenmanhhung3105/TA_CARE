/* Guest navigation must reach public needs before any authentication prompt. */
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
(async()=>{
  const browser=await chromium.launch({channel:'chrome',headless:true});
  try {
    const context=await browser.newContext({viewport:{width:1440,height:1000}});
    const page=await context.newPage();
    const root='http://khovieclam.localhost:8069';
    const errors=[];page.on('pageerror',e=>errors.push(e.message));
    for (const prefix of ['/vi','']) {
      for (const selector of ['.sx-work-bottom .sx-text-link','.sx-work-body h3 a','.sx-work-photo']) {
        await page.goto(root+prefix+'/kvl/jobs');
        await page.waitForLoadState('networkidle');
        assert.equal(await page.locator('#tc-login-dialog[open]').count(),0);
        const link=page.locator('.sx-work-card').first().locator(selector);
        const expected=new URL(await link.getAttribute('href'),page.url()).pathname;
        await link.click();await page.waitForLoadState('networkidle');
        assert.match(new URL(page.url()).pathname,/\/kvl\/job\/\d+$/,'Guest click must navigate to job detail');
        assert.equal(await page.locator('#tc-login-dialog[open]').count(),0,'Public detail must not prompt login');
        assert(await page.locator('.fw-detail-photo').count(),expected);
        assert.equal(await page.locator('a[href$="/edit"],a[href$="/remove"]').count(),0);
      }
    }
    await page.goto(root+'/vi/');await page.waitForLoadState('networkidle');
    await page.locator('.sx-main-nav a[href$="/kvl/jobs"]').click();await page.waitForLoadState('networkidle');
    assert.match(new URL(page.url()).pathname,/\/kvl\/jobs$/);
    assert.equal(await page.locator('#tc-login-dialog[open]').count(),0);
    await page.locator('.sx-work-card').first().locator('.sx-work-bottom .sx-text-link').click();
    await page.waitForLoadState('networkidle');
    await page.getByRole('link',{name:'Tạo hồ sơ từ công việc này',exact:true}).click();
    await page.waitForLoadState('networkidle');
    assert.equal(await page.locator('#tc-login-dialog[open]').count(),1,'Creating a profile still requires login');
    await page.goto(root+'/vi/kvl/jobs');await page.waitForLoadState('networkidle');
    await page.locator('.sx-header-actions a[href$="/kvl/flexible/new"]').click();
    assert.equal(await page.locator('#tc-login-dialog[open]').count(),1,'Posting a need still requires login');
    assert.deepEqual(errors,[]);
    console.log('PASS guest navbar, details button, title and image clicks with/without language prefix; no edit/delete controls; profile creation and posting still prompt login');
  } finally { await browser.close(); }
})().catch(e=>{console.error(e.stack);process.exit(1)});
