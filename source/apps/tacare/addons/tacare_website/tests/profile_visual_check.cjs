/** Read-only final visual checks; never create test records or expose credentials. */
const {chromium}=require('playwright');const assert=require('node:assert/strict');const fs=require('node:fs');const path=require('node:path');
const accounts=JSON.parse(fs.readFileSync('runtime/tacare/profile_refresh_accounts.json','utf8'));
const old=JSON.parse(fs.readFileSync('backups/demo_flexible_20261019/accounts.json','utf8'));
const admin=old.accounts.find(a=>a.login.startsWith('demo-flex-99@'));
const shots=path.resolve('docs/screenshots/profile-refresh-20261020');fs.mkdirSync(shots,{recursive:true});
(async()=>{const b=await chromium.launch({headless:true,executablePath:process.env.TACARE_CHROME||'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});try{
 const p=await b.newPage();const errors=[];p.on('pageerror',e=>errors.push(e.message));
 async function go(url){const r=await p.goto(url,{waitUntil:'networkidle'});assert.equal(r.status(),200,new URL(url).pathname);assert(!await p.evaluate(()=>document.documentElement.scrollWidth>innerWidth));}
 async function ready(){await p.evaluate(async()=>{await document.fonts.ready;for(let y=0;y<document.documentElement.scrollHeight;y+=650){scrollTo(0,y);await new Promise(r=>setTimeout(r,40));}scrollTo(0,0);});await p.waitForFunction(()=>[...document.querySelectorAll('.tc-live img')].every(n=>n.complete&&n.naturalWidth));await p.waitForTimeout(650);}
 async function login(who,site){await go(site+'/web/login');const token=await p.locator('[name=csrf_token]').inputValue();const r=await p.context().request.post(site+'/web/login',{form:{csrf_token:token,login:who.login,password:who.password,redirect:'/'}});assert(!new URL(r.url()).pathname.includes('/web/login'));}
 const photos={};
 for(const site of ['khovieclam','tuhoso','tacare']){
  for(const width of [1440,375,320]){
   await p.setViewportSize({width,height:1000});await go(`http://${site}.localhost:8069/`);await ready();
   assert(!/[↗↘↙↖↑↓→←]/.test(await p.locator('.tc-live').innerText()),site+' decorative arrow');
   assert.equal(await p.locator('header nav a[aria-current]').count(),1);
   const carousel=p.locator('[data-work-carousel]');assert.equal(await carousel.count(),site==='tacare'?0:1);
   if(site!=='tacare'){
    photos[site]=await carousel.locator('[data-work-slide] img').evaluateAll(ns=>ns.map(n=>new URL(n.src).pathname));
    const n=await carousel.locator('[data-work-slide]').count();
    for(let i=0;i<n;i++){
     assert(await carousel.locator('[data-work-slide].is-active').evaluate(n=>{const c=n.querySelector('figcaption').getBoundingClientRect(),s=n.getBoundingClientRect();return c.left>=s.left-1&&c.right<=s.right+1&&c.top>=s.top-1&&c.bottom<=s.bottom+1;}),'Caption must fit '+site+' '+width);
     await carousel.locator('[data-work-next]').click();
    }
   }
   await p.waitForTimeout(900);
   if(width!==320)await p.screenshot({path:path.join(shots,`${site}-guest-${width}.png`),fullPage:width===1440});
  }
 }
 assert(!photos.khovieclam.some(x=>photos.tuhoso.includes(x)),'Carousel photo sets must be distinct');
 console.log('PASS visual: distinct Kho/Tủ photos and carousel structures, static hub, no decorative arrows, selected navigation, captions fit at desktop/mobile');
 const root='http://tuhoso.localhost:8069';await login(accounts.accounts[0],root);
 for(const width of [1440,375,320]){
  await p.setViewportSize({width,height:1000});await go(root+'/');await ready();assert.equal(await p.locator('.pv-profile-card').count(),2);
  if(width!==320)await p.screenshot({path:path.join(shots,`candidate-home-${width}.png`),fullPage:width===1440});
 }
 const recId=accounts.accounts[0].profile_ids[0];
 await p.setViewportSize({width:1440,height:1000});await go(root+`/tuhoso/profile/${recId}`);assert.equal(await p.locator('header nav a[aria-current]').innerText(),'Hồ sơ của tôi');assert((await p.locator('#tc-main').innerText()).includes('Thu nhập mong muốn'));await p.screenshot({path:path.join(shots,'candidate-profile-detail.png'),fullPage:true});
 await login(accounts.accounts[0],'http://tacare.localhost:8069');await go(`http://tacare.localhost:8069/tacare/matching?profile_id=${recId}`);assert.equal(await p.locator('select[name=profile_id]').inputValue(),String(recId));
 await login(accounts.accounts[0],'http://khovieclam.localhost:8069');await go('http://khovieclam.localhost:8069/kvl/jobs');assert.equal(await p.locator('.tc-nav a[aria-current]').innerText(),'Tìm việc');
 await go('http://khovieclam.localhost:8069/kvl/flexible/new');assert.equal(await p.locator('.tc-nav a[aria-current]').innerText(),'Đăng việc');
 await go('http://khovieclam.localhost:8069/kvl/flexible/mine');assert.equal(await p.locator('.tc-nav a[aria-current]').innerText(),'Quản lý tin');
 await go(`http://khovieclam.localhost:8069/kvl/job/${old.recruitment_job_ids[0]}?profile_id=${recId}`);assert.equal(await p.locator('.tc-nav a[aria-current]').innerText(),'Tìm việc');assert.equal(await p.locator('select[name=profile_id]').inputValue(),String(recId));
 console.log('PASS selected profile in recruitment/matching and navigation on detail/create/manage pages');
 await p.context().clearCookies();await login(admin,root);await go(root+'/tuhoso/profiles?scope=all');await ready();assert.equal(await p.locator('.pv-profile-card').count(),accounts.expected_profile_count);
 // Mask the one pre-existing non-demo record; screenshots contain only fictional profiles.
 const demoIds=new Set([...old.profile_ids,...accounts.accounts.flatMap(a=>a.profile_ids)]);
 const allIds=await p.locator('.pv-profile-card').evaluateAll(ns=>ns.map(n=>Number(n.dataset.profileId)));
 const privateIds=allIds.filter(id=>!demoIds.has(id));
 await p.screenshot({path:path.join(shots,'admin-all-profiles.png'),fullPage:true,mask:privateIds.map(id=>p.locator(`[data-profile-id="${id}"]`)),maskColor:'#e8ece7'});
 assert.deepEqual(errors,[]);console.log('PASS clean screenshots: two profiles per candidate, admin all-profiles tab; existing private record masked');
}finally{await b.close();}})().catch(e=>{console.error(e.stack);process.exitCode=1;});
