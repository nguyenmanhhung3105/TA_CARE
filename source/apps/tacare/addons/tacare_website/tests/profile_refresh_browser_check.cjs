/** Local integration QA. Credentials are read from ignored runtime files only. */
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const secrets=JSON.parse(fs.readFileSync('runtime/tacare/profile_refresh_accounts.json','utf8'));
const admin=JSON.parse(fs.readFileSync('backups/demo_flexible_20261019/accounts.json','utf8')).accounts.find(a=>a.login.startsWith('demo-flex-99@'));
const root='http://tuhoso.localhost:8069';
const created={};
const privatePath='runtime/tacare/profile_refresh_qa_records.json';
const saveIds=()=>fs.writeFileSync(privatePath,JSON.stringify(created),{mode:0o600});
const shots=path.resolve('docs/screenshots/profile-refresh-20261020');
fs.mkdirSync(shots,{recursive:true});
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:process.env.TACARE_CHROME||'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
 const jsErrors=[];
 try{
  const a=await browser.newContext();const p=await a.newPage();p.on('pageerror',e=>jsErrors.push(e.message));
  async function go(page,url){const r=await page.goto(url,{waitUntil:'networkidle'});assert.equal(r.status(),200,'GET '+new URL(url).pathname);}
  async function login(page,account,site=root){
   await go(page,site+'/web/login');const token=await page.locator('[name=csrf_token]').inputValue();
   const r=await page.context().request.post(site+'/web/login',{form:{csrf_token:token,login:account.login,password:account.password,redirect:'/'}});
   assert.equal(r.status(),200,'Login result');assert(!new URL(r.url()).pathname.includes('/web/login'),'Login must succeed');
  }
  const cards=()=>p.locator('.pv-profile-card');
  await login(p,secrets.accounts[0]);await go(p,root+'/');assert.equal(await cards().count(),2);
  assert.equal(await p.locator('h1').innerText(),'Hồ sơ của tôi');
  assert.equal(await p.locator('header nav a[aria-current]').innerText(),'Trang chủ');
  const ownIds=secrets.accounts[0].profile_ids;
  const foreignIds=secrets.accounts[1].profile_ids;
  assert.equal((await a.request.get(root+'/tuhoso/profiles?scope=all')).status(),403);
  for(const id of foreignIds){assert.equal((await a.request.get(root+`/tuhoso/profile/${id}`)).status(),404);assert.equal((await a.request.get(root+`/tuhoso/me?profile_id=${id}`)).status(),404);}
  await go(p,root+'/tuhoso/profiles?kind=recruitment&scope=mine');assert.equal(await cards().count(),1);
  assert.equal(await p.locator('header nav a[aria-current]').innerText(),'Hồ sơ của tôi');
  await go(p,root+'/tuhoso/profiles?kind=flexible&scope=mine');assert.equal(await cards().count(),1);
  console.log('PASS candidate: two own profiles visible, separate branches, admin all-tab and foreign GET blocked');
  await go(p,root+'/tuhoso/profiles/new');
  assert.equal(await p.locator('header [href="/tuhoso/profiles/new"][aria-current]').count(),1);
  const createToken=await p.locator('[name=csrf_token]').inputValue();
  let r=await a.request.post(root+'/tuhoso/profiles/create',{form:{csrf_token:createToken,profile_title:'QA profile temporary',kind:'recruitment'}});
  assert.equal(r.status(),200);const qaId=Number(new URL(r.url()).searchParams.get('profile_id'));assert(qaId);created.profile_id=qaId;saveIds();
  await go(p,r.url());
  assert(await p.locator('form').evaluateAll(forms=>forms.every(f=>f.querySelector('input[name=profile_id]')?.value===String(new URL(location.href).searchParams.get('profile_id')))));
  const editToken=await p.locator('form[action="/tuhoso/profile/save"] [name=csrf_token]').inputValue();
  const payload={csrf_token:editToken,profile_id:String(qaId),name:'Ứng viên demo 01',profile_title:'QA profile temporary',headline:'QA scoped headline',bio:'Nội dung riêng của hồ sơ QA.',salary_min:'0',salary_tax:'unknown'};
  r=await a.request.post(root+'/tuhoso/profile/save',{form:payload});assert.equal(r.status(),200);
  await go(p,root+`/tuhoso/me?profile_id=${qaId}`);assert.equal(await p.locator('[name=headline]').inputValue(),payload.headline);
  const bad=await a.request.post(root+'/tuhoso/profile/save',{form:{...payload,salary_min:'NaN'}});assert.equal(bad.status(),200);assert((await bad.text()).includes('QA profile temporary'));
  assert.equal((await a.request.post(root+'/tuhoso/profile/save',{form:{...payload,profile_id:String(foreignIds[0])}})).status(),404);
  const noId={...payload};delete noId.profile_id;assert.equal((await a.request.post(root+'/tuhoso/profile/save',{form:noId})).status(),400);
  r=await a.request.post(root+'/tuhoso/skill/add',{form:{csrf_token:editToken,profile_id:String(qaId),name:'JavaScript',level:'good',use:'QA scoped use'}});assert.equal(r.status(),200);assert.equal(new URL(r.url()).searchParams.get('profile_id'),String(qaId));
  await go(p,root+`/tuhoso/me?profile_id=${qaId}`);assert((await p.locator('#profile-skills').innerText()).includes('QA scoped use'));
  await go(p,root+`/tuhoso/me?profile_id=${ownIds[0]}`);assert(!(await p.locator('#profile-skills').innerText()).includes('QA scoped use'));
  console.log('PASS multiple profiles: explicit IDs across forms; create/save/readback; invalid input; foreign and missing-ID writes blocked; skills isolated');

  await go(p,root+`/tuhoso/work/new?profile_id=${ownIds[1]}`);
  const serviceToken=await p.locator('[name=csrf_token]').inputValue();
  assert.equal(await p.locator('[name=profile_id]').inputValue(),String(ownIds[1]));
  const cat=await p.locator('[name=flex_category_id] option').nth(1).getAttribute('value');
  const service={csrf_token:serviceToken,profile_id:String(ownIds[1]),name:'QA service temporary',description:'Dữ liệu tạm kiểm tra hồ sơ nhận việc.',flex_category_id:cat,flex_mode:'remote',flex_schedule:'flexible',flex_rate_min:'85000',flex_pay_unit:'hour',flex_pay_basis:'person',flex_tools:'discuss',intent:'publish'};
  const wrongService=await a.request.post(root+'/tuhoso/work/save',{form:{...service,profile_id:String(foreignIds[1])}});assert.equal(wrongService.status(),404);
  r=await a.request.post(root+'/tuhoso/work/save',{form:service});assert.equal(r.status(),200);created.capability_id=Number(new URL(r.url()).pathname.split('/').pop());assert(created.capability_id);saveIds();
  await go(p,root+`/tuhoso/profile/${ownIds[1]}`);assert((await p.locator('h1').innerText()).includes('Nhận chăm cây'));assert((await p.locator('.fw-grid').innerText()).includes('QA service temporary'));
  const transfer=await a.request.post(root+'/tuhoso/work/save',{form:{...service,id:String(created.capability_id),profile_id:String(ownIds[0])}});assert.equal(transfer.status(),403);
  console.log('PASS service: own profile selection persists; foreign profile and parent reassignment blocked');

  const b=await browser.newContext();const p2=await b.newPage();await login(p2,secrets.accounts[1]);await go(p2,root+'/');assert.equal(await p2.locator('.pv-profile-card').count(),2);
  assert.equal((await b.request.get(root+`/tuhoso/profile/${qaId}`)).status(),404);
  assert.equal((await b.request.get(root+`/tuhoso/work/${created.capability_id}`)).status(),404);
  await b.close();
  const ad=await browser.newContext();const ap=await ad.newPage();await login(ap,admin);
  await go(ap,root+'/tuhoso/profiles?scope=all');assert.equal(await ap.locator('.pv-profile-card').count(),secrets.expected_profile_count + 1);
  assert.equal(await ap.locator('header nav a[aria-current]').innerText(),'Tất cả hồ sơ');
  await go(ap,root+'/tuhoso/profiles?scope=mine');assert.equal(await ap.locator('.pv-profile-card').count(),0);
  await go(ap,root+`/tuhoso/profile/${foreignIds[0]}`);assert.equal(await ap.locator('h1').count(),1);
  await go(ap,root+'/tuhoso/profiles?scope=all');await ap.setViewportSize({width:1440,height:1000});await ap.screenshot({path:path.join(shots,'admin-all-profiles.png'),fullPage:true});
  await ad.close();
  console.log('PASS second candidate isolation and admin-only all-profiles tab');

  for(const url of ['/', '/tuhoso/profiles?scope=mine','/tuhoso/profiles/new',`/tuhoso/me?profile_id=${ownIds[0]}`,`/tuhoso/profile/${ownIds[1]}`]){
   for(const width of [1440,768,375,320]){await p.setViewportSize({width,height:1000});await go(p,root+url);assert(!await p.evaluate(()=>document.documentElement.scrollWidth>innerWidth),url+' overflow '+width);}
  }
  await go(p,root+'/');await p.setViewportSize({width:1440,height:1000});await p.screenshot({path:path.join(shots,'candidate-home-desktop.png'),fullPage:true});
  await p.setViewportSize({width:375,height:1000});await p.screenshot({path:path.join(shots,'candidate-home-mobile.png'),fullPage:false});
  assert.deepEqual(jsErrors,[]);console.log('PASS responsive profile pages/forms, selected navigation and no JS errors');
 }finally{saveIds();await browser.close();}
})().catch(e=>{console.error(e.stack);process.exitCode=1;});
