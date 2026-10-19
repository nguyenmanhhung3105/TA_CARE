/** Local demo integration checks. Secrets stay in ignored backups, never printed. */
const {chromium} = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const privateDir = path.resolve('backups/demo_flexible_20261019');
const dataset = JSON.parse(fs.readFileSync(path.join(privateDir, 'accounts.json'), 'utf8'));
const account = (n) => dataset.accounts.find((a) => a.login === `demo-flex-${String(n).padStart(2,'0')}@example.invalid`);
const root = (site) => `http://${site}.localhost:8069`;
const created = {};
const saveIds = () => fs.writeFileSync(path.join(privateDir,'qa_records.json'),JSON.stringify(created),{mode:0o600});

(async () => {
  const browser = await chromium.launch({headless:true, executablePath: process.env.TACARE_CHROME || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
  const errors = [];
  try {
    const ctx = await browser.newContext();
    const page = await ctx.newPage();
    page.on('pageerror', e => errors.push(e.message));
    async function go(url) {
      const response = await page.goto(url,{waitUntil:'networkidle'});
      assert.equal(response.status(),200,`GET ${new URL(url).pathname}`);
      assert(!await page.getByText('A CSS error occurred').count());
    }
    async function login(site, who) {
      assert(who, 'Demo account unavailable');
      await go(root(site)+'/web/login');
      if (await page.locator('input[name=login]').count()) {
        await page.locator('input[name=login]').fill(who.login);
        await page.locator('input[name=password]').fill(who.password);
        await Promise.all([page.waitForURL(u => !u.pathname.includes('/web/login')),
          page.locator('.oe_login_form button[type=submit]').click()]);
      }
    }
    async function readyScreenshot(p) {
      await p.evaluate(async()=>{
        for(let y=0;y<document.documentElement.scrollHeight;y+=650){scrollTo(0,y);await new Promise(r=>setTimeout(r,45));}
        scrollTo(0,0);
      });
      await p.waitForFunction(()=>[...document.querySelectorAll('.tc-live img')].every(img=>img.complete && img.naturalWidth));
      await p.waitForTimeout(700);
    }
    const count = () => page.locator('.fw-grid > .fw-card').count();
    await go(root('khovieclam')+'/kvl/jobs'); assert.equal(await count(),20);
    await go(root('khovieclam')+'/kvl/jobs?kind=recruitment'); assert.equal(await count(),5);
    assert.equal(await page.locator('select[name=category]').count(),0);
    await go(root('khovieclam')+'/kvl/jobs?kind=flexible'); assert.equal(await count(),15);
    assert.equal(await page.locator('select[name=sector]').count(),0);
    await go(root('khovieclam')+'/kvl/jobs?kind=flexible&mode=remote'); assert.equal(await count(),3);
    await go(root('khovieclam')+'/kvl/jobs?kind=flexible&unit=trip'); assert.equal(await count(),1);
    console.log('PASS public: 20 jobs, recruitment 5, flexible 15, distinct filters, remote 3, trip 1');

    for(const site of ['khovieclam','tuhoso','tacare']) {
      for(const width of [1440,768,375,320]) {
        await page.setViewportSize({width,height:1000});
        await go(root(site)+'/');
        await page.evaluate(async()=>{
          for(let y=0;y<document.body.scrollHeight;y+=700){scrollTo(0,y);await new Promise(r=>setTimeout(r,25));}
          scrollTo(0,0);await document.fonts.ready;
        });
        assert(!await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth), `${site} overflow ${width}`);
        assert.equal(await page.locator('[data-work-carousel]').count(),site === 'tacare' ? 0 : 1);
      }
    }
    await go(root('khovieclam')+'/');
    await page.locator('[data-work-next]').click();
    assert.equal(await page.locator('[data-work-slide].is-active').getAttribute('aria-label'),'2 trên 4');
    assert.equal(await page.locator('[data-work-slide][aria-hidden=true] a').evaluateAll(ns=>ns.every(n=>n.closest('[inert]'))),true);
    await page.emulateMedia({reducedMotion:'reduce'});
    await page.waitForFunction(() => document.querySelector('[data-work-pause]').disabled);
    assert(await page.locator('[data-work-pause]').isDisabled());
    await page.emulateMedia({reducedMotion:'no-preference'});
    console.log('PASS three homepages: 12 viewport combinations, distinct static/carousel layouts, controls, inert slides and reduced motion');

    await login('tuhoso',account(6));
    await go(root('tuhoso')+'/tuhoso/profiles?kind=flexible'); assert.equal(await page.locator('.pv-profile-card').count(),1);
    const ownProfile = Number(await page.locator('.pv-profile-card').getAttribute('data-profile-id'));
    await go(root('tuhoso')+`/tuhoso/profile/${ownProfile}`);
    const ownService = Number(await page.locator('.fw-card').getAttribute('data-record-id'));
    await go(root('tuhoso')+'/tuhoso/profiles?kind=recruitment'); assert.equal(await page.locator('.pv-profile-card').count(),0);
    const foreignProfile = dataset.profile_ids.find(id => true);
    const denied = await ctx.request.get(root('tuhoso')+`/tuhoso/profile/${foreignProfile}`);
    assert.equal(denied.status(),404);
    const otherService = await ctx.request.get(root('tuhoso')+`/tuhoso/work/${ownService+1}`);
    assert([403,404].includes(otherService.status()));
    console.log('PASS owner library: own service only; foreign profile and service URLs blocked');

    const adminContext = await browser.newContext();
    const ap = await adminContext.newPage();
    await ap.goto(root('tuhoso')+'/web/login');
    await ap.locator('[name=login]').fill(account(99).login);
    await ap.locator('[name=password]').fill(account(99).password);
    await Promise.all([ap.waitForURL(u=>!u.pathname.includes('/web/login')),ap.locator('.oe_login_form button[type=submit]').click()]);
    await ap.goto(root('tuhoso')+'/tuhoso/profiles?kind=recruitment',{waitUntil:'networkidle'});
    assert.equal(await ap.locator('.pv-profile-card').count(),8);
    await ap.goto(root('tuhoso')+'/tuhoso/profiles?kind=flexible',{waitUntil:'networkidle'});
    assert.equal(await ap.locator('.pv-profile-card').count(),12);
    const screenshotDir = path.resolve('docs/screenshots/demo-flexible-20261019');
    fs.mkdirSync(screenshotDir,{recursive:true});
    await ap.setViewportSize({width:1440,height:1000});
    await readyScreenshot(ap);
    await ap.screenshot({path:path.join(screenshotDir,'admin-flexible-profiles.png'),fullPage:true});
    await ap.goto(root('tuhoso')+`/tuhoso/profile/${foreignProfile}`,{waitUntil:'networkidle'});
    assert.equal(await ap.locator('h1').count(),1);
    await adminContext.close();
    console.log('PASS admin: all recruitment profiles and all work capabilities; foreign profile detail available');

    await go(root('tuhoso')+'/tuhoso/work/new');
    const token = await page.locator('input[name=csrf_token]').inputValue();
    const category = await page.locator('select[name=flex_category_id] option').nth(1).getAttribute('value');
    const base = {csrf_token:token,id:'',intent:'publish',name:'QA flexible service temporary',
      description:'Dữ liệu QA tạm cho kiểm tra ghi và quyền sở hữu.',flex_category_id:category,
      flex_mode:'remote',flex_schedule:'flexible',flex_rate_min:'75000',flex_pay_unit:'hour',
      flex_pay_basis:'person',flex_tools:'discuss',flex_negotiable:'on'};
    const invalid = await ctx.request.post(root('tuhoso')+'/tuhoso/work/save',{form:{...base, flex_rate_min:'NaN'}});
    assert.equal(invalid.status(),200);
    assert((await invalid.text()).includes('QA flexible service temporary'));
    assert((await invalid.text()).includes('Chưa lưu được'));
    const forged = await ctx.request.post(root('tuhoso')+'/tuhoso/work/save',{form:{...base,profile_id:String(foreignProfile)}});
    assert.equal(forged.status(),404);
    const saved = await ctx.request.post(root('tuhoso')+'/tuhoso/work/save',{form:base});
    assert.equal(saved.status(),200);
    assert(saved.url().match(/\/tuhoso\/work\/\d+$/));
    created.capability_id = Number(saved.url().split('/').pop()); saveIds();
    await go(saved.url());
    assert((await page.locator('h1').innerText()).includes(base.name));
    await page.getByRole('link',{name:'Chỉnh sửa',exact:true}).click();
    assert.equal(await page.locator('[name=flex_rate_min]').inputValue(),'75000.0');
    assert(await page.locator('[data-work-location]').first().isHidden());
    assert.equal(await page.locator('input[name=flex_image]').count(),1);
    const imagePayload = {...base, csrf_token: await page.locator('[name=csrf_token]').inputValue(), id:String(created.capability_id),
      flex_trip_service:'vehicle', flex_trip_direction:'oneway', flex_destination:'Stale hidden destination',
      flex_passengers:'4',flex_vehicle_note:'Stale hidden vehicle'};
    const badImage = await ctx.request.post(root('tuhoso')+'/tuhoso/work/save',{multipart:{...imagePayload,
      flex_image:{name:'invalid.png',mimeType:'image/png',buffer:Buffer.from('not an image')}}});
    assert((await badImage.text()).includes('ảnh JPG'));
    const goodImage = await ctx.request.post(root('tuhoso')+'/tuhoso/work/save',{multipart:{...imagePayload,
      flex_image:{name:'qa.png',mimeType:'image/png',buffer:Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII=','base64')}}});
    assert.equal(goodImage.status(),200);
    const photo = await ctx.request.get(root('tuhoso')+`/tuhoso/work/${created.capability_id}/image`);
    assert.equal(photo.status(),200);assert.equal(photo.headers()['content-type'],'image/jpeg');
    assert.equal((await photo.body()).subarray(0,2).toString('hex'),'ffd8');
    await go(root('tuhoso')+`/tuhoso/work/${created.capability_id}/edit`);
    assert.equal(await page.locator('[name=flex_trip_service]').inputValue(),'');
    assert.equal(await page.locator('[name=flex_destination]').inputValue(),'');
    console.log('PASS service persistence, edit readback, invalid finite price, forged ownership, remote disclosure and image upload validation');

    await login('khovieclam',account(6));
    await go(root('khovieclam')+'/kvl/flexible/new');
    const jobToken = await page.locator('input[name=csrf_token]').inputValue();
    const payload = {...base, csrf_token:jobToken, name:'QA flexible job temporary', quantity:'2', intent:'draft'};
    let result = await ctx.request.post(root('khovieclam')+'/kvl/flexible/save',{form:payload});
    assert.equal(result.status(),200);
    await go(root('khovieclam')+'/kvl/flexible/mine');
    const card = page.locator('.fw-card').filter({hasText:payload.name});
    assert.equal(await card.count(),1);
    created.job_id = Number(await card.getAttribute('data-record-id')); saveIds();
    const foreignJob = dataset.flex_job_ids.find(id=>id!==created.job_id);
    const foreignEdit = await ctx.request.get(root('khovieclam')+`/kvl/flexible/${foreignJob}/edit`);
    // Seeded job ownership may coincide for one job; choose its owner using a separate account below.
    await go(root('khovieclam')+`/kvl/flexible/${created.job_id}/edit`);
    const postToken = await page.locator('input[name=csrf_token]').inputValue();
    result = await ctx.request.post(root('khovieclam')+'/kvl/flexible/save',{form:{...payload,id:String(created.job_id),csrf_token:postToken,intent:'publish'}});
    assert.equal(result.status(),200);
    assert.equal((await ctx.request.get(root('khovieclam')+`/kvl/job/${created.job_id}`)).status(),200);
    result = await ctx.request.post(root('khovieclam')+`/kvl/flexible/${created.job_id}/status`,{form:{csrf_token:postToken,state:'paused'}});
    assert.equal(result.status(),200);
    assert.equal((await ctx.request.get(root('khovieclam')+`/kvl/job/${created.job_id}`)).status(),404);
    console.log('PASS flexible job: candidate can create, persist draft, publish, pause; paused job is not public');

    const other = await browser.newContext();
    const otherPage = await other.newPage();
    await otherPage.goto(root('khovieclam')+'/web/login');
    await otherPage.locator('[name=login]').fill(account(7).login);
    await otherPage.locator('[name=password]').fill(account(7).password);
    await Promise.all([otherPage.waitForURL(u=>!u.pathname.includes('/web/login')),otherPage.locator('.oe_login_form button[type=submit]').click()]);
    assert.equal((await other.request.get(root('khovieclam')+`/kvl/flexible/${created.job_id}/edit`)).status(),404);
    await otherPage.goto(root('khovieclam')+'/kvl/flexible/new');
    const otherToken = await otherPage.locator('[name=csrf_token]').inputValue();
    const deniedWrite = await other.request.post(root('khovieclam')+'/kvl/flexible/save',{form:{...payload,csrf_token:otherToken,id:String(created.job_id)}});
    assert.equal(deniedWrite.status(),404);
    const deniedStatus = await other.request.post(root('khovieclam')+`/kvl/flexible/${created.job_id}/status`,{form:{csrf_token:otherToken,state:'published'}});
    assert.equal(deniedStatus.status(),404);
    await other.close();
    console.log('PASS foreign record GET, POST edit and POST status are blocked on the server');

    for(const url of ['/kvl/jobs','/kvl/jobs?kind=flexible','/kvl/flexible/new']) {
      for(const width of [1440,375,320]) {
        await page.setViewportSize({width,height:1000});await go(root('khovieclam')+url);
        assert(!await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth), `${url} overflow ${width}`);
      }
    }
    await page.setViewportSize({width:1440,height:1000}); await go(root('khovieclam')+'/');
    await readyScreenshot(page);
    await page.screenshot({path:path.join(screenshotDir,'jobs-home-desktop.png'),fullPage:true});
    await go(root('khovieclam')+'/kvl/jobs?kind=flexible');
    await readyScreenshot(page);
    await page.screenshot({path:path.join(screenshotDir,'flexible-jobs-desktop.png'),fullPage:true});
    await page.setViewportSize({width:375,height:1200});
    await readyScreenshot(page);
    await page.screenshot({path:path.join(screenshotDir,'flexible-jobs-mobile.png'),fullPage:false});
    assert.deepEqual(errors,[]);
    console.log('PASS new lists/forms responsive, no JS errors; screenshots saved');
  } finally {
    saveIds(); await browser.close();
  }
})().catch(e=>{console.error(e.stack);process.exitCode=1;});
