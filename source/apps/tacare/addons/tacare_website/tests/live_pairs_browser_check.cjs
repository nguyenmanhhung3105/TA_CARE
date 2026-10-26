/* Uses existing local accounts; creates no user, contact, profile or connection. */
const {chromium}=require('playwright');
const fs=require('node:fs');const assert=require('node:assert/strict');
const accounts=JSON.parse(fs.readFileSync('runtime/tacare/live_pair_test_identities.json','utf8'));
const expected=JSON.parse(fs.readFileSync('runtime/tacare/live_pair_test_expected.json','utf8'));
const hub='http://tacare.localhost:8069';
(async()=>{
 const browser=await chromium.launch({channel:'chrome',headless:true});let ctx,p;
 const errors=[],shots='runtime/live-pair-review';fs.mkdirSync(shots,{recursive:true});
 async function fresh(){if(ctx)await ctx.close();ctx=await browser.newContext({viewport:{width:1440,height:1100}});p=await ctx.newPage();p.setDefaultTimeout(25000);p.on('pageerror',e=>errors.push(e.message));}
 async function go(url){const r=await p.goto(url);assert(r&&r.status()<400,'GET '+new URL(url).pathname+' '+r?.status());await p.waitForLoadState('networkidle');return r;}
 async function login(role){await fresh();await go(hub+'/web/login');const a=accounts.find(a=>a.role===role);assert(a);const f=p.locator('.tc-login-form');await f.locator('[name=login]').fill(a.login);await f.locator('[name=password]').fill(a.password);await f.getByRole('button',{name:'Đăng nhập',exact:true}).click();await p.waitForURL(u=>!u.pathname.startsWith('/care/sso/')&&!u.searchParams.has('login'));await p.waitForLoadState('networkidle');}
 async function responsive(){for(const width of [1440,768,375,320]){await p.setViewportSize({width,height:1100});const over=await p.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1);if(over){console.log('OVERFLOW_ELEMENTS',JSON.stringify(await p.evaluate(()=>[...document.querySelectorAll('#tc-main *')].map(n=>({tag:n.tagName,cls:n.className,x:n.getBoundingClientRect().x,right:n.getBoundingClientRect().right,width:n.getBoundingClientRect().width})).filter(r=>r.right>innerWidth+1||r.x < -1).slice(0,20))));await p.screenshot({path:shots+'/overflow-'+width+'.png',fullPage:true});}assert(!over,'Overflow '+width+' '+new URL(p.url()).pathname);}await p.setViewportSize({width:1440,height:1100});}
 await fresh();await go(hub+'/');assert.equal(await p.locator('.hx-hero .hx-connection-scene').count(),1,'Original illustrative hero is retained');assert.equal(await p.locator('.hx-hero .lp-pair').count(),0,'Live pairs belong below the hero');assert.equal(await p.locator('.lp-pair').count(),0,'Guest cannot see private pair records');assert.equal(await p.locator('[data-example]').count(),0,'No authored matching result cards');await responsive();
 for(const role of ['business','provider',...(accounts.some(a=>a.role==='admin')?['admin']:[])]){
  await login(role);const cards=p.locator('.lp-pair');
  assert.equal(await p.locator('.hx-hero .hx-connection-scene').count(),1);assert.equal(await p.locator('.hx-hero .lp-pair').count(),0);
  if(!expected[role].length){assert.equal(await cards.count(),0,'No invented pairs for an account without authorized results');assert(await p.locator('.lp-empty').count());await responsive();console.log('PASS '+role+': honest empty state matches allowed-company results; no fabricated pairs');continue;}
  assert(await cards.count(),'Live suggestions on home '+role);
  const allowed=new Map(expected[role].map(x=>[x.job_id+':'+x.profile_id,x]));
  for(let i=0;i<await cards.count();i++){
   const c=cards.nth(i);const key=await c.getAttribute('data-job-id')+':'+await c.getAttribute('data-profile-id');assert(allowed.has(key),'Unauthorized/uncomputed home pair '+role);
   const data=allowed.get(key);assert.equal(await c.getAttribute('data-capability-id'),String(data.capability_id));assert((await c.innerText()).includes(data.job));assert((await c.innerText()).includes(data.profile));
   for(const image of await c.locator('img').all()){await image.scrollIntoViewIfNeeded();await image.evaluate(n=>n.decode());assert(await image.evaluate(n=>n.complete&&n.naturalWidth>0));}
  }
  assert.equal(await p.locator('[data-example]').count(),0);
  assert(!/\[Demo|Mẫu thử|Hồ sơ hư cấu/i.test(await p.locator('#tc-main').innerText()));
  const need=await cards.first().locator('.lp-need').boundingBox(),offer=await cards.first().locator('.lp-provider').boundingBox();assert(need.x+need.width<offer.x,'Two distinct desktop columns');
  await cards.first().screenshot({path:shots+'/'+role+'-pair-1440.png'});await responsive();
  const first=allowed.get(await cards.first().getAttribute('data-job-id')+':'+await cards.first().getAttribute('data-profile-id'));
  await cards.first().getByRole('link',{name:'Đối chiếu hai phía',exact:true}).click();await p.waitForLoadState('networkidle');assert.match(new URL(p.url()).pathname,/\/tacare\/pair\/\d+\/\d+$/);
  const rows=p.locator('.lp-comparison tbody tr');assert.equal(await rows.count(),first.rows.length);
  for(let i=0;i<first.rows.length;i++){
   const r=rows.nth(i),data=first.rows[i];assert.equal(await r.getAttribute('data-result'),data.result);assert.equal(await r.locator('td').nth(0).innerText(),data.need_value);assert.equal(await r.locator('td').nth(1).innerText(),data.offer_value);
  }
  assert.equal(await p.locator('form[action$="/tacare/request/send"] [name=job_id]').inputValue(),String(first.job_id));assert.equal(await p.locator('form[action$="/tacare/request/send"] [name=profile_id]').inputValue(),String(first.profile_id));
  await p.screenshot({path:shots+'/'+role+'-detail-1440.png',fullPage:true});await responsive();await p.setViewportSize({width:375,height:1100});await p.screenshot({path:shots+'/'+role+'-detail-375.png',fullPage:true});
  if(role==='provider'){await go(hub+'/tacare/matching?view=receive');assert(await p.locator('.lp-pair').count(),'Default receive selection finds an authorized matching profile');}
  console.log('PASS '+role+': home pairs from live scoped results, winning offer, credited photos, exact algorithm source columns, correct connection IDs and responsive layouts');
 }
 const pair=expected.business[0];await login('other_business');let r=await ctx.request.get(hub+`/tacare/pair/${pair.job_id}/${pair.profile_id}`);assert([403,404].includes(r.status()),'Cross-organization detail blocked');
 await fresh();await go(hub+`/tacare/pair/${pair.job_id}/${pair.profile_id}`);assert.equal(await p.locator('#tc-login-dialog[open]').count(),1);assert.equal(await p.locator('.lp-pair').count(),0);
 assert.deepEqual(errors,[]);await browser.close();console.log('PASS guest/private pair boundary and cross-organization denial; no data created');
})().catch(e=>{console.error(e.stack);process.exit(1)});
