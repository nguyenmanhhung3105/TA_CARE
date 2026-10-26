/* Read-only candidate check: replace only this browser's bundled nearby component.
 * Uses existing production test credentials in memory; no password/cookie output.
 * Does not deploy code or write business data. Native login/SSO are unchanged.
 */
const fs=require('node:fs'),assert=require('node:assert/strict');
const {chromium}=require(process.env.TACARE_PLAYWRIGHT_MODULE || 'playwright');
const hub=process.env.TACARE_LAZY_CHECK_ORIGIN || 'http://tacare.localhost:8069';
const identities=JSON.parse(fs.readFileSync('runtime/tacare/map_test_accounts_20261027/map_test_accounts_20261027.json','utf8'));
const who=identities.find(u=>u.key==='home');
const candidate=fs.readFileSync('source/apps/tacare/addons/tacare_website/static/src/js/nearby.js','utf8');
const rootOrigin=new URL(hub).origin;
const results=[];
(async()=>{
 const browser=await chromium.launch({channel:'chrome',headless:true});
 try{
  for(const width of [1366,375]){
   const ctx=await browser.newContext({viewport:{width,height:768},deviceScaleFactor:2,reducedMotion:'reduce'});
   let replacements=0,mapScripts=0,apiRequests=0;const errors=[];
   await ctx.route(/\/web\/assets\/.*web\.assets_frontend_lazy\.min\.js(?:\?.*)?$/,async route=>{
    if(new URL(route.request().url()).origin!==rootOrigin)return route.continue();
    const response=await route.fetch();let body=await response.text();
    for(const name of ['data-nearby-map','data-geo-picker']){
     const selector=`document.querySelectorAll('[${name}]')`;
     assert.equal(body.split(selector).length-1,1,'Exactly one original map initializer');
     body=body.replace(selector,`document.querySelectorAll('[${name}-disabled-candidate]')`);
    }
    const headers={...response.headers(),'cache-control':'no-store'};
    delete headers['content-encoding'];delete headers['content-length'];delete headers.etag;
    await route.fulfill({status:response.status(),headers,body:body+'\n'+candidate});replacements++;
   });
   if(width===375)await ctx.addInitScript(()=>{window.requestIdleCallback=undefined;});
   const page=await ctx.newPage();
   page.on('pageerror',e=>errors.push(e.name));
   page.on('request',request=>{const u=new URL(request.url());if(u.pathname.endsWith('/maplibre-gl.js'))mapScripts++;if(u.pathname==='/tacare/nearby/data')apiRequests++;});
   await page.goto(hub+'/web/login',{waitUntil:'domcontentloaded',timeout:60000});
   const form=page.locator('.tc-login-form');await form.locator('[name=login]').fill(who.login);await form.locator('[name=password]').fill(who.password);
   await form.getByRole('button',{name:'Đăng nhập',exact:true}).click();await page.waitForTimeout(4000);
   const session=await ctx.request.get(hub+'/care/sso/status');assert.equal((await session.json()).uid,who.user_id);
   mapScripts=0;apiRequests=0;
   await page.goto(hub+'/',{waitUntil:'domcontentloaded',timeout:60000});await page.waitForTimeout(1800);
   const canvas=page.locator('[data-nearby-canvas]');
   const initial=await canvas.evaluate(n=>({top:n.getBoundingClientRect().top,initialized:!!n.careMap}));
   assert(initial.top>=768,'Test first fold leaves the actual map outside the viewport');
   assert.equal(initial.initialized,false);assert.equal(mapScripts,0);assert.equal(apiRequests,0);
   await canvas.scrollIntoViewIfNeeded();
   await page.waitForFunction(()=>document.querySelector('[data-nearby-canvas]')?.dataset.baseLoaded==='1',{timeout:30000});
   await page.waitForFunction(()=>document.querySelectorAll('.gm-results .gm-result').length>0,{timeout:20000});
   assert.equal(mapScripts,1);assert.equal(apiRequests,1);
   await canvas.evaluate(n=>{window.careLazyOriginalMap=n.careMap;});
   await page.evaluate(()=>scrollTo(0,0));await page.waitForTimeout(250);
   await canvas.scrollIntoViewIfNeeded();await page.waitForTimeout(500);
   assert(await canvas.evaluate(n=>n.careMap===window.careLazyOriginalMap));assert.equal(mapScripts,1);assert.equal(apiRequests,1);
   assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1),false);
   assert.deepEqual(errors,[]);assert(replacements>0);
   results.push({width,authenticated:true,initialMapLibraryRequests:0,initialMapApiRequests:0,mapAfterScroll:true,oneInitialization:true,idleFallback:width===375,overflow:false});
   await ctx.request.get(hub+'/web/session/logout?redirect=/',{timeout:15000});await ctx.close();
  }
 }finally{await browser.close();}
 console.log('PASS candidate lazy map:',JSON.stringify(results));
})().catch(e=>{console.error('FAILED candidate lazy map:',e.name);process.exitCode=1;});
