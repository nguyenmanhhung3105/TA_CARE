/* Native local editor UI; only invalid submissions, no business-data writes. */
const {chromium} = require('playwright');
const fs = require('node:fs'), assert = require('node:assert/strict');
const identities = JSON.parse(fs.readFileSync(process.env.TACARE_UI_IDENTITY_FILE || 'runtime/tacare/nearby_test_identities.json', 'utf8'));
const hub = 'http://tacare.localhost:8069', shots = 'runtime/form-workspace-review';
fs.mkdirSync(shots, {recursive:true});
(async () => {
  const browser = await chromium.launch({channel:'chrome', headless:true});
  let context, page, sourceJob;
  const errors = [];
  async function login(role) {
    if (context) await context.close();
    context = await browser.newContext({viewport:{width:1440,height:1100}, reducedMotion:'reduce'});
    page = await context.newPage(); page.on('pageerror', e => errors.push(e.message));
    const who = identities.find(i => i.role === role); assert(who);
    await page.goto(hub + '/web/login'); await page.waitForLoadState('networkidle');
    const form = page.locator('.tc-login-form');
    await form.locator('[name=login]').fill(who.login); await form.locator('[name=password]').fill(who.password);
    await form.getByRole('button',{name:'Đăng nhập',exact:true}).click();
    await page.waitForURL(u => !u.pathname.startsWith('/care/sso/') && !u.pathname.startsWith('/web/login') && !u.searchParams.has('login'));
    await page.waitForLoadState('networkidle');
  }
  async function responsive(label, root) {
    for (const width of [320,375,390,767,768,1024,1440,1920]) {
      await page.setViewportSize({width,height:1100});
      assert(!await page.evaluate(() => document.documentElement.scrollWidth > innerWidth+1), label+' overflow '+width);
      if ([375,1440].includes(width)) {
        await root.scrollIntoViewIfNeeded();
        await page.screenshot({path:shots+'/'+label+'-'+width+'.png'});
      }
    }
    await page.setViewportSize({width:1440,height:1100});
  }
  async function detailsOpen(selector) { await page.locator(selector).evaluate(n => n.open=true); }
  try {
    for (const role of ['business','provider']) {
      await login(role);
      const view = role === 'business' ? 'hire' : 'receive';
      const response = await context.request.get(hub+'/tacare/nearby/data?view='+view+'&radius=50');
      assert.equal(response.status(),200); const payload = await response.json(); assert(payload.source);
      if (role === 'business') sourceJob = payload.source.id;
      await page.goto(payload.source.edit_url); await page.waitForLoadState('networkidle');
      const form = page.locator('[data-work-form]');
      assert(await form.evaluate(n => n.classList.contains('ff-editor')));
      assert.equal(await form.getAttribute('method'),'post'); assert(await form.locator('[name=csrf_token]').inputValue());
      assert.equal(await form.locator('[name=id]').inputValue(),String(payload.source.id));
      const profile = role === 'provider' ? await form.locator('[name=profile_id]').inputValue() : null;
      if (profile) assert(Number(profile)>0);
      assert.equal(await form.locator('[name=flex_location]').getAttribute('type'),'hidden');
      assert.equal(await form.locator('input[name=flex_location]:visible').count(),0);
      assert.equal(await form.locator('.gm-picker-details').getAttribute('open'),'open');
      assert.equal(await form.locator('[data-geo-address-preview]').innerText(),await form.locator('[name=flex_location]').inputValue());
      assert.equal(await form.locator('.ix-editor-guide nav a').count(),5);
      await responsive(role+'-work',page.locator('.ff-page-head'));
      assert.equal(await form.evaluate(n => getComputedStyle(n).gridTemplateColumns.split(' ').length),2,'Desktop editor columns');
      const publish = form.locator('[name=intent][value=publish]'), draft = form.locator('[name=intent][value=draft]');
      assert.equal(await publish.evaluate(n => getComputedStyle(n).color),'rgb(255, 255, 255)');
      assert((await publish.boundingBox()).height>=48); assert((await draft.boundingBox()).height>=48);
      assert(await draft.getAttribute('formnovalidate'));
      await draft.focus(); await page.keyboard.press('Tab'); assert.equal(await page.locator(':focus').getAttribute('value'),'publish');
      assert(parseFloat(await publish.evaluate(n => getComputedStyle(n).outlineWidth))>=3);
      await form.locator('.ix-editor-guide a[href="#work-place"]').click();
      await page.waitForFunction(() => document.querySelector('[data-geo-canvas]')?.dataset.baseLoaded==='1');
      assert(await form.locator('[data-geo-canvas]').isVisible());
      await detailsOpen('.gm-picker-advanced');
      // One explicit coordinate action exercises the real reverse service in the new picker.
      const point = role==='business' ? [10.7769,106.7009] : [21.0273,105.8524];
      await form.locator('[name=geo_lat]').fill(String(point[0]));
      await form.locator('[name=geo_lon]').fill(String(point[1]));
      await form.locator('[name=geo_lon]').dispatchEvent('change');
      await page.waitForFunction(() => document.querySelector('[data-geo-status]').textContent.startsWith('Đã lấy địa chỉ'),{timeout:20000});
      const full = await form.locator('[name=flex_location]').inputValue();
      assert(full.includes('Việt Nam')); assert.equal(await form.locator('[data-geo-address-preview]').innerText(),full);
      assert.equal(await form.locator('[name=geo_address]').inputValue(),full);
      assert.equal(new URL(await form.locator('[data-geo-url]').inputValue()).searchParams.get('query'),point.join(','));
      await detailsOpen('.gm-address-editor');
      const manual = form.locator('[data-geo-address-manual]');
      const longAddress = full+', Cổng phụ, số nhà và hẻm được bổ sung, '+ 'ghi chú điểm hẹn để lưu đủ địa chỉ '.repeat(8);
      assert(longAddress.length>250 && longAddress.length<1000);
      await manual.fill(longAddress);
      assert.equal(await form.locator('[data-geo-address-preview]').innerText(),longAddress.trim());
      assert.equal(await form.evaluate(n => new FormData(n).get('flex_location')),longAddress);
      assert.equal(await form.evaluate(n => new FormData(n).get('geo_address')),longAddress);
      // A delayed response cannot replace the user's corrected address.
      await page.route('https://photon.komoot.io/**',async route => {
        await new Promise(r => setTimeout(r,1200));
        await route.fulfill({json:{features:[{properties:{street:'Địa chỉ chậm',country:'Việt Nam',countrycode:'VN'}}]}}).catch(()=>{});
      });
      await form.locator('[name=geo_lat]').fill(String(point[0]+.001));
      const reverse = page.waitForRequest(r => r.url().startsWith('https://photon.komoot.io/'));
      await form.locator('[name=geo_lat]').dispatchEvent('change'); await reverse;
      await manual.fill(longAddress); await page.waitForTimeout(1600);
      assert.equal(await form.locator('[name=flex_location]').inputValue(),longAddress);
      await page.unroute('https://photon.komoot.io/**');
      await page.setViewportSize({width:375,height:1100});
      await page.locator('#work-place').screenshot({path:shots+'/'+role+'-map-picker-375.png'});
      await form.locator('.ff-save-panel').screenshot({path:shots+'/'+role+'-save-375.png'});
      // Remote mode still hides map controls; switching back preserves unsaved values.
      await form.locator('[name=flex_mode]').selectOption('remote'); assert(!await form.locator('[data-geo-picker]').isVisible());
      await form.locator('[name=flex_mode]').selectOption('onsite'); assert(await form.locator('[data-geo-picker]').isVisible());
      await form.locator('[name=name]').fill('A'); await draft.click();
      await page.waitForLoadState('networkidle'); assert(await page.locator('#work-form-error').isVisible());
      assert.equal(await form.locator('[name=name]').inputValue(),'A');
      assert.equal(await form.locator('[name=flex_location]').inputValue(),longAddress);
      assert.equal(await form.locator('[data-geo-address-preview]').innerText(),longAddress.trim());
      if(profile) assert.equal(await form.locator('[name=profile_id]').inputValue(),profile);
      assert.equal((await context.request.post(new URL(await form.getAttribute('action'),page.url()).href,{form:{id:String(payload.source.id)}})).status(),400,'CSRF retained');
      const fresh = await context.request.get(hub+'/tacare/nearby/data?view='+view+'&source_id='+payload.source.id);
      assert.equal((await fresh.json()).source.address,payload.source.address,'Invalid submit leaves stored source unchanged');
      const newUrl = role==='business' ? 'http://khovieclam.localhost:8069/kvl/flexible/new' : 'http://tuhoso.localhost:8069/tuhoso/work/new?profile_id='+profile;
      await page.goto(newUrl); await page.waitForLoadState('networkidle');
      assert.equal(await form.locator('[name=id]').inputValue(),'');
      if(profile) assert.equal(await form.locator('[name=profile_id]').inputValue(),profile);
      assert.equal(await form.locator('[data-geo-address-preview]').innerText(),'Chưa chọn vị trí trên bản đồ');
      if(role==='provider') {
        await page.goto('http://tuhoso.localhost:8069/tuhoso/profile/'+profile+'/edit'); await page.waitForLoadState('networkidle');
        const meta=page.locator('.ff-metadata-form');
        assert.equal(await meta.locator('[name=profile_id]').inputValue(),profile); assert(Number(await meta.locator('[name=profile_version]').inputValue())>0);
        await responsive('profile-introduction',page.locator('.ff-page-head'));
        await meta.locator('[name=name]').fill('A'); await meta.evaluate(n=>n.noValidate=true);
        await meta.getByRole('button',{name:'Lưu hồ sơ',exact:true}).click(); await page.waitForLoadState('networkidle');
        assert(await page.locator('#profile-editor-error').isVisible()); assert.equal(await meta.locator('[name=name]').inputValue(),'A');
        assert.equal(await meta.locator('[name=profile_id]').inputValue(),profile);
      }
    }
    await page.goto('http://tuhoso.localhost:8069/tuhoso/profiles/new?kind=flexible&source_job_id='+sourceJob); await page.waitForLoadState('networkidle');
    const create=page.locator('form[action="/tuhoso/profiles/create"]');
    assert.equal(await create.locator('[name=source_job_id]').inputValue(),String(sourceJob),'Source job context preserved');
    assert.equal(await create.locator('[name=kind]').inputValue(),'flexible');
    assert(await create.locator('[name=csrf_token]').inputValue());
    await responsive('profile-create',page.locator('.ff-profile-create'));
    assert.equal(await page.locator('.ff-create-steps [aria-current=step]').count(),1);
    assert((await create.getByRole('button').boundingBox()).height>=48);
    await create.locator('[name=profile_title]').fill('A'); await create.evaluate(n=>n.noValidate=true);
    await create.getByRole('button').click(); await page.waitForLoadState('networkidle');
    assert(await page.locator('[role=alert]').isVisible()); assert.equal(await create.locator('[name=profile_title]').inputValue(),'A');
    assert.equal(await create.locator('[name=source_job_id]').inputValue(),String(sourceJob));
    const guest=await browser.newContext();
    for(const url of ['http://khovieclam.localhost:8069/kvl/flexible/new','http://tuhoso.localhost:8069/tuhoso/profiles/new?kind=flexible']) {
      const r=await guest.request.get(url,{maxRedirects:0}); assert([302,303,403].includes(r.status()));
    }
    await guest.close(); assert.deepEqual(errors,[]);
    console.log('PASS Kho and Tủ new/edit work, profile creation/introduction; 8 widths 320–1920; buttons/focus/48px targets; map-only address, real Photon, full >250 chars in serialized native form and retained validation, stale response protection, remote toggles, explicit owner/source/version IDs, CSRF and guest gates; invalid submissions only, no business-data writes');
  } finally {await browser.close();}
})().catch(e=>{console.error(e.stack);process.exit(1);});
