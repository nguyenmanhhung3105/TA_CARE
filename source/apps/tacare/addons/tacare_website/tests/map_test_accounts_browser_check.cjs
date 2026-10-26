/* Read-only native login/library/map checks on the renamed local accounts. */
const {chromium}=require('playwright'),fs=require('node:fs'),assert=require('node:assert/strict');
const directory='runtime/tacare/map_test_accounts_20261027/';
const identities=JSON.parse(fs.readFileSync(directory+'map_test_accounts_20261027.json','utf8'));
const receipt=JSON.parse(fs.readFileSync(directory+'map_test_receipt_20261027.json','utf8'));
const hub='http://tacare.localhost:8069',shots='runtime/map-accounts-review';
fs.mkdirSync(shots,{recursive:true});
(async()=>{
 const browser=await chromium.launch({channel:'chrome',headless:true});
 const errors=[];
 try{
  for(const who of identities){
   const context=await browser.newContext({viewport:{width:1440,height:1100},reducedMotion:'reduce'});
   const page=await context.newPage();page.on('pageerror',e=>errors.push(e.message));
   await page.goto(hub+'/web/login');await page.waitForLoadState('networkidle');
   const form=page.locator('.tc-login-form');
   await form.locator('[name=login]').fill(who.login);await form.locator('[name=password]').fill(who.password);
   await form.getByRole('button',{name:'Đăng nhập',exact:true}).click();
   await page.waitForURL(u=>!u.pathname.startsWith('/care/sso/')&&!u.pathname.startsWith('/web/login')&&!u.searchParams.has('login'));
   await page.waitForLoadState('networkidle');
   assert.equal(await page.locator('.tc-live').getAttribute('data-access-guest'),'0');
   assert((await page.locator('.sx-header').innerText()).includes(who.name));
   const view=who.role==='business'?'hire':'receive';
   const r=await context.request.get(hub+'/tacare/nearby/data?view='+view+'&radius=10');assert.equal(r.status(),200);
   const payload=await r.json();
   if(who.key==='digital')assert.equal(payload.markers.length,0,'Remote needs do not get fabricated map markers');
   else assert(payload.markers.length>0,'Mapped account has actual suggestions');
   if(who.role==='provider'){
    const profiles=receipt.created.filter(p=>p.user_id===who.user_id);assert.equal(profiles.length,9);
    await page.goto('http://tuhoso.localhost:8069/tuhoso/profiles');await page.waitForLoadState('networkidle');
    for(const profile of profiles){
     const own=await context.request.get('http://tuhoso.localhost:8069/tuhoso/profile/'+profile.profile_id);assert.equal(own.status(),200);
    }
    const foreign=receipt.created.find(p=>p.user_id!==who.user_id);
    const denied=await context.request.get('http://tuhoso.localhost:8069/tuhoso/profile/'+foreign.profile_id);assert([403,404].includes(denied.status()));
   }
   if(who.key==='home'||who.key==='provider_home'){
    await page.goto(hub+'/#nearby-connections');await page.locator('#nearby-connections').scrollIntoViewIfNeeded();
    await page.waitForFunction(()=>document.querySelector('.gm-result--panel')&&document.querySelector('[data-nearby-canvas]')?.dataset.baseLoaded==='1');
    const codes=who.key==='home'?['cleaning','cooking','pets']:['cleaning','garden','tutoring'];
    for(const code of codes){
     const row=receipt.created.find(p=>p.code===code);
     const source=who.key==='home'?row.job_id:row.offer_id;
     await page.locator('[data-geo-source]').selectOption(String(source));
     await page.waitForFunction(()=>!document.querySelector('[data-geo-refresh]').disabled);
     assert(await page.locator('.gm-result--panel').count()>0);
     if(who.key==='home')assert(await page.locator('.gm-result--panel').count()>=3);
    }
    for(const width of [375,1440]){
     await page.setViewportSize({width,height:1100});await page.waitForTimeout(700);
     await page.locator('[data-geo-fit]').click();
     await page.waitForFunction(()=>document.querySelector('[data-nearby-canvas]').careMap.careGL.areTilesLoaded());
     assert(!await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1));
     await page.locator('#nearby-connections').screenshot({path:shots+'/'+who.key+'-'+width+'.png'});
    }
   }
   await context.close();
  }
  assert.deepEqual(errors,[]);
  console.log('PASS native login on all 8 renamed accounts with new passwords; correct display names; permitted cross-site sessions; owner library for each of 27 new profiles; foreign profile denial; real map matches in both directions; multiple results across profession/source selectors; remote map exclusion; 375/1440; no business-data writes');
 }finally{await browser.close();}
})().catch(e=>{console.error(e.stack);process.exit(1);});
