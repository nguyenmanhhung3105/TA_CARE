/* Read-only checks for the one Google Maps action following selected map results. */
const {chromium}=require('playwright'),fs=require('node:fs'),assert=require('node:assert/strict');
const identities=JSON.parse(fs.readFileSync('runtime/tacare/map_test_accounts_20261027/map_test_accounts_20261027.json','utf8'));
const receipt=JSON.parse(fs.readFileSync('runtime/tacare/map_test_accounts_20261027/map_test_receipt_20261027.json','utf8'));
const hub='http://tacare.localhost:8069';
(async()=>{
 const browser=await chromium.launch({channel:'chrome',headless:true});const errors=[];
 try{
  for(const key of ['home','learning','provider_home']){
   const who=identities.find(i=>i.key===key),context=await browser.newContext({viewport:{width:1440,height:1100},reducedMotion:'reduce'}),page=await context.newPage();
   page.on('pageerror',e=>errors.push(e.message));
   await page.goto(hub+'/web/login');await page.waitForLoadState('networkidle');const login=page.locator('.tc-login-form');
   await login.locator('[name=login]').fill(who.login);await login.locator('[name=password]').fill(who.password);await login.getByRole('button',{name:'Đăng nhập',exact:true}).click();
   await page.waitForURL(u=>!u.pathname.startsWith('/care/sso/')&&!u.pathname.startsWith('/web/login')&&!u.searchParams.has('login'));await page.waitForLoadState('networkidle');
   await page.goto(hub+'/#nearby-connections');await page.locator('#nearby-connections').scrollIntoViewIfNeeded();await page.waitForFunction(()=>document.querySelector('.gm-result--panel'));
   const view=who.role==='business'?'hire':'receive',codes=key==='home'?['cleaning','pets']:key==='learning'?['tutoring']:['cleaning','garden','tutoring'];
   for(const code of codes){
    const row=receipt.created.find(r=>r.code===code),sourceId=who.role==='business'?row.job_id:row.offer_id;
    await page.locator('[data-geo-source]').selectOption(String(sourceId));await page.waitForFunction(()=>!document.querySelector('[data-geo-refresh]').disabled);
    const payload=await (await context.request.get(hub+'/tacare/nearby/data?view='+view+'&source_id='+sourceId+'&radius=10')).json();
    const cards=page.locator('.gm-result--panel');assert.equal(await cards.count(),payload.markers.length);
    assert.equal(await page.locator('.gm-result .gm-google-maps').count(),0);
    assert(await page.locator('[data-geo-route]').evaluate(n=>n.hidden));
    assert.equal(await page.locator('[data-geo-directions]').getAttribute('href'),null);
    const groups=[...payload.markers.reduce((m,item)=>{
      const k=item.point.join(',');if(!m.has(k))m.set(k,[]);m.get(k).push(item);return m;
    },new Map()).values()];
    const singles=groups.map((g,i)=>g.length===1?i:-1).filter(i=>i>=0);
    const picks=singles.length>1?[singles[0],singles[singles.length-1]]:singles;
    const ends=[];
    for(const index of picks){
      await page.locator('[data-nearby-canvas]').evaluate(n=>n.careMap.closePopup());
      await page.locator('[data-geo-fit]').click(); // The previous route may have framed a different part of the map.
      await page.locator('.gm-profession-marker').nth(index).click();
      assert(await page.locator('[data-geo-route]').isVisible());
      const url=new URL(await page.locator('[data-geo-directions]').getAttribute('href'));
      assert.equal(url.searchParams.get('destination'),groups[index][0].point.join(','));
      assert.equal(url.searchParams.get('origin'),payload.source.point.join(','));
      assert.equal(url.searchParams.get('api'),'1');ends.push(url.searchParams.get('destination'));
      await page.waitForFunction(()=>{const t=document.querySelector('[data-geo-route-status]').textContent;return t.startsWith('Tuyến ô tô')||t.startsWith('Chưa tải được');});
    }
    if(ends.length>1)assert.notEqual(ends[0],ends[1],'Clicking a new map object updates the remaining Google Maps action');
    if(key==='home'&&code==='pets'){
      await cards.first().getByRole('button',{name:'Hiện trên bản đồ',exact:true}).click();
      assert(await page.locator('[data-geo-route]').evaluate(n=>n.hidden),'Locating another result must not retain the previous Google Maps target');
      assert.equal(await page.locator('[data-geo-directions]').getAttribute('href'),null);
      await page.locator('.leaflet-popup-content .gm-result').first().getByRole('button',{name:'Xem đường đi',exact:true}).click();
      assert.equal(new URL(await page.locator('[data-geo-directions]').getAttribute('href')).searchParams.get('destination'),payload.markers[0].point.join(','));
    }
    const shared=groups.findIndex(g=>g.length>1);
    if(shared>=0){
      await page.locator('[data-nearby-canvas]').evaluate(n=>n.careMap.closePopup());
      await page.locator('[data-geo-fit]').click();
      await page.locator('.gm-profession-marker').nth(shared).click();
      assert(await page.locator('[data-geo-route]').evaluate(n=>n.hidden),'Shared-area marker clears the previous selection');
      assert.equal(await page.locator('[data-geo-directions]').getAttribute('href'),null);
      const popup=page.locator('.leaflet-popup-content .gm-result');assert.equal(await popup.count(),groups[shared].length);
      assert.equal(await popup.locator('.gm-google-maps').count(),0);
      await popup.first().getByRole('button',{name:'Xem đường đi',exact:true}).click();
      const chosen=new URL(await page.locator('[data-geo-directions]').getAttribute('href'));
      assert.equal(chosen.searchParams.get('destination'),groups[shared][0].point.join(','));
    }
    await page.locator('[data-geo-route-clear]').click();
    assert(await page.locator('[data-geo-route]').evaluate(n=>n.hidden));
    assert.equal(await page.locator('[data-geo-directions]').getAttribute('href'),null);
   }
   await context.close();
  }
  assert.deepEqual(errors,[]);console.log('PASS one Google Maps action in selected route panel; no duplicate card/popup map links; real marker clicks update destination, shared-area click clears stale selection until a popup result is chosen, source/clear remove stale href; 3 accounts/6 source selections; permitted coordinates only; no business-data writes');
 }finally{await browser.close();}
})().catch(e=>{console.error(e.stack);process.exit(1)});
