/** Local-only regression: native login dialog, role/host gates and profile visibility. */
const {chromium} = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const saved = JSON.parse(fs.readFileSync('runtime/tacare/profile_refresh_accounts.json','utf8'));
const demo = JSON.parse(fs.readFileSync('backups/demo_flexible_20261019/accounts.json','utf8'));
const candidate = saved.accounts[0], other = saved.accounts[1];
const business = demo.accounts.find(a=>a.login.startsWith('demo-flex-00@'));
const admin = demo.accounts.find(a=>a.login.startsWith('demo-flex-99@'));
const base = site=>`http://${site}.localhost:8069`;
const shots = path.resolve('docs/screenshots/auth-restore-20261020');
fs.mkdirSync(shots,{recursive:true});

(async()=>{
 const browser = await chromium.launch({headless:true,executablePath:process.env.TACARE_CHROME||'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
 const errors=[];
 async function pageFor(){const ctx=await browser.newContext();const p=await ctx.newPage();p.on('pageerror',e=>errors.push(e.message));return p;}
 async function go(p,url){const r=await p.goto(url,{waitUntil:'networkidle'});assert.equal(r.status(),200,new URL(url).pathname);return r;}
 async function apiLogin(p,who,site,allowed=true){
  await go(p,base(site)+'/');
  const token=await p.locator('#tc-login-dialog [name=csrf_token]').inputValue();
  const r=await p.context().request.post(base(site)+'/web/login',{form:{csrf_token:token,login:who.login,password:who.password,redirect:'/'}});
  assert.equal(r.status(),200);assert.equal(new URL(r.url()).pathname.includes('/web/login'),!allowed,'Role login result');
  await go(p,base(site)+'/');
 }
 try {
  // Guests can view each homepage. A function opens the dialog, including direct URLs.
  const guest=await pageFor();
  for(const [site,feature] of [['khovieclam','/kvl/jobs'],['tuhoso','/tuhoso/profiles'],['tacare','/tacare/matching']]){
   await go(guest,base(site)+'/');
   assert.equal(await guest.locator('.tc-system-links a').count(),3);
   for(const width of [1440,375,320]){
    await guest.setViewportSize({width,height:900});
    await guest.locator('.tc-sitebar-login').click();
    const d=guest.locator('#tc-login-dialog');assert(await d.isVisible());
    assert.equal(await guest.evaluate(()=>document.activeElement.id),'tc-login-identity');
    assert(await d.evaluate(n=>{let b=n.getBoundingClientRect();return b.left>=0&&b.right<=innerWidth&&b.top>=0&&b.bottom<=innerHeight;}));
    assert(!await d.evaluate(n=>n.scrollWidth>n.clientWidth));
    if(width!==320)await guest.screenshot({path:path.join(shots,`${site}-login-${width}.png`)});
    await guest.keyboard.press('Escape');assert(!await d.isVisible());
    assert.equal(await guest.evaluate(()=>document.activeElement.className),'tc-sitebar-login');
   }
   await go(guest,base(site)+feature);
   assert(await guest.locator('#tc-login-dialog').isVisible());
   assert.equal(await guest.locator('#tc-login-dialog [name=redirect]').inputValue(),feature);
   assert.equal(await guest.locator('.pv-profile-card').count(),0);
  }
  const fallback=await guest.context().request.get('http://localhost:8069/kvl/jobs',{maxRedirects:0});
  assert.equal(fallback.status(),303,'Unknown-host fallback cannot expose public product functions');
  await guest.context().close();
  console.log('PASS guest: three public homepages; functions/direct URLs open accessible login popup, desktop/mobile focus and Escape');

  // Submit the actual native form: failed password retains login, clears password.
  const p=await pageFor();await go(p,base('tuhoso')+'/web/login?redirect=/tuhoso/profiles');
  await p.evaluate(({login})=>{document.querySelector('#tc-login-identity').value=login;document.querySelector('#tc-login-password').value='invalid-qa-password';},candidate);
  await Promise.all([p.waitForNavigation({waitUntil:'networkidle'}),p.locator('.tc-login-form button[type=submit]').click()]);
  assert(await p.locator('#tc-login-dialog').isVisible());assert(await p.locator('.tc-login-error').isVisible());
  assert.equal(await p.locator('#tc-login-identity').inputValue(),candidate.login);assert.equal(await p.locator('#tc-login-password').inputValue(),'');
  await p.evaluate(({login,password})=>{document.querySelector('#tc-login-identity').value=login;document.querySelector('#tc-login-password').value=password;},candidate);
  await p.locator('[data-login-password]').click();assert.equal(await p.locator('#tc-login-password').getAttribute('type'),'text');await p.locator('[data-login-password]').click();
  await Promise.all([p.waitForNavigation({waitUntil:'networkidle'}),p.locator('.tc-login-form button[type=submit]').click()]);
  assert.equal(await p.locator('.pv-profile-card').count(),2);
  assert.equal(await p.locator('.tc-system-links a').count(),2);
  assert.deepEqual(await p.locator('.tc-system-links a').allTextContents(),['Tủ Hồ Sơ','TA.CARE']);
  assert(await p.locator('.pv-to-tacare').isVisible());
  assert.equal((await p.context().request.get(base('tuhoso')+`/tuhoso/profile/${other.profile_ids[0]}`)).status(),404);
  assert.equal((await p.context().request.get(base('tuhoso')+'/tuhoso/profiles?scope=all')).status(),403);
  await go(p,base('tuhoso')+'/kvl/jobs');assert(await p.locator('#tc-login-dialog').isVisible());
  await go(p,base('tuhoso')+'/');
  assert(await p.evaluate(()=>document.querySelector('.pv-carousel').compareDocumentPosition(document.querySelector('.pv-library'))&Node.DOCUMENT_POSITION_FOLLOWING));
  await p.screenshot({path:path.join(shots,'candidate-home.png'),fullPage:true});
  await apiLogin(p,candidate,'tacare');assert.equal(await p.locator('.tc-system-links a').count(),2);
  await go(p,base('tacare')+`/tacare/job/${demo.recruitment_job_ids[0]}?profile_id=${candidate.profile_ids[0]}`);
  assert.equal(await p.locator('select[name=profile_id]').inputValue(),String(candidate.profile_ids[0]));
  assert.equal(await p.locator('form[action$="/tacare/request/send"] [name=profile_id]').inputValue(),String(candidate.profile_ids[0]));
  assert.equal(await p.locator('.tc-nav a[aria-current]').innerText(),'Đối chiếu');
  assert.equal(await p.locator('.tc-hub').count(),1);
  assert.equal((await p.context().request.get(base('tacare')+`/tacare/job/${demo.recruitment_job_ids[0]}?profile_id=${other.profile_ids[0]}`)).status(),404);
  await apiLogin(p,candidate,'khovieclam',false);assert.equal(await p.locator('[data-access-guest]').getAttribute('data-access-guest'),'1');
  await p.context().close();
  console.log('PASS candidate: native login, two own profiles/systems, recruitment detail/application remains in TA.CARE with explicit own profile; foreign-profile and third-system restrictions');

  const bp=await pageFor();await apiLogin(bp,business,'khovieclam');
  assert.deepEqual(await bp.locator('.tc-system-links a').allTextContents(),['Kho Việc Làm','TA.CARE']);
  await go(bp,base('khovieclam')+'/kvl/jobs');assert.equal(await bp.locator('.fw-card').count(),20);
  await apiLogin(bp,business,'tacare');await apiLogin(bp,business,'tuhoso',false);await bp.context().close();
  console.log('PASS business: two systems; 20 jobs remain; Tủ login rejected');

  const ap=await pageFor();
  for(const site of ['khovieclam','tacare','tuhoso']){await apiLogin(ap,admin,site);assert.equal(await ap.locator('.tc-system-links a').count(),3);}
  assert.equal(await ap.locator('.pv-profile-card').count(),saved.expected_profile_count);
  assert.equal(await ap.locator('.pv-scope-tabs a[aria-current]').innerText(),'Tất cả hồ sơ');
  // Selecting a different active company must not empty the admin library.
  const cookies=await ap.context().cookies(base('tuhoso'));assert(cookies.some(c=>c.name==='session_id'));
  await ap.context().addCookies([{name:'cids',value:'2',url:base('tuhoso')}]);
  await go(ap,base('tuhoso')+'/tuhoso/profiles?scope=all');assert.equal(await ap.locator('.pv-profile-card').count(),saved.expected_profile_count);
  const demoIds=new Set([...demo.profile_ids,...saved.accounts.flatMap(a=>a.profile_ids)]);
  const ids=await ap.locator('.pv-profile-card').evaluateAll(ns=>ns.map(n=>Number(n.dataset.profileId)));
  await ap.screenshot({path:path.join(shots,'admin-all-profiles.png'),fullPage:true,mask:ids.filter(id=>!demoIds.has(id)).map(id=>ap.locator(`[data-profile-id="${id}"]`)),maskColor:'#e8ece7'});
  await ap.context().close();

  // A valid session cookie on a forbidden host must not expose profiles/features.
  const stale=await pageFor();await apiLogin(stale,business,'khovieclam');
  const sid=(await stale.context().cookies(base('khovieclam'))).find(c=>c.name==='session_id').value;
  await stale.context().addCookies([{name:'session_id',value:sid,url:base('tuhoso')}]);
  await go(stale,base('tuhoso')+'/');assert.equal(await stale.locator('.pv-profile-card').count(),0);assert.equal(await stale.locator('[data-access-guest]').getAttribute('data-access-guest'),'1');
  await go(stale,base('tuhoso')+'/tuhoso/profiles');assert(await stale.locator('#tc-login-dialog').isVisible());
  const token=await stale.locator('#tc-login-dialog [name=csrf_token]').inputValue();
  const denied=await stale.context().request.post(base('tuhoso')+'/tuhoso/profiles/create',{form:{csrf_token:token,profile_title:'Should never create',kind:'recruitment'}});assert.equal(denied.status(),403);
  await stale.context().close();
  assert.deepEqual(errors,[]);console.log('PASS admin: three systems, all 20 profiles, company selection; forbidden-host stale sessions cannot read/write functions');
 }finally{await browser.close();}
})().catch(e=>{console.error(e.stack);process.exitCode=1;});
