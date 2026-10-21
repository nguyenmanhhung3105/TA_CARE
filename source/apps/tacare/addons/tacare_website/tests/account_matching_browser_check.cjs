/** Local end-to-end QA; run after seed_account_matching_qa.py and always clean up. */
const {chromium}=require('playwright');
const fs=require('node:fs'); const assert=require('node:assert/strict');
const qa=JSON.parse(fs.readFileSync('runtime/tacare/refresh_qa.json','utf8'));
const roots={k:'http://khovieclam.localhost:8069',p:'http://tuhoso.localhost:8069',h:'http://tacare.localhost:8069'};
(async()=>{
 const browser=await chromium.launch({channel:'chrome',headless:true});
 const ctx=await browser.newContext();const p=await ctx.newPage();
 const errors=[];p.on('pageerror', e=>errors.push(e.message));
 async function go(url){const r=await p.goto(url);assert(r&&r.status()<400,`GET failed ${r?.status()} ${new URL(url).pathname}`);await p.waitForLoadState('networkidle');}
 async function login(role,site){await ctx.clearCookies();await go(site+'/web/login');
  const account=qa.accounts.find(x=>x.role===role);const token=await p.locator('[name=csrf_token]').first().inputValue();
  const response=await ctx.request.post(site+'/web/login',{form:{csrf_token:token,login:account.login,password:account.password,redirect:'/'}});
  assert(!new URL(response.url()).pathname.includes('/web/login'),'Native authentication failed');
  await go(site+'/');await p.waitForTimeout(700);
 }
 async function post(url,form){const token=await p.locator('[name=csrf_token]').first().inputValue();return ctx.request.post(url,{form:{csrf_token:token,...form},maxRedirects:0});}
 async function fit(){await p.evaluate(()=>document.fonts.ready);assert(!await p.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1),'Horizontal overflow');}
 await login('business',roots.k);
 await go(roots.k+'/kvl/jobs');assert(await p.getByRole('link',{name:'Xem chi tiết',exact:true}).count()>=20);
 assert(await p.locator('.fw-recruitment-card img').count()>=5);
 for(const width of [1440,375,320]){
  await p.setViewportSize({width,height:900});
  await go(roots.k+`/kvl/flexible/${qa.job_id}`);await fit();
  assert(await p.locator('.fw-detail-photo img').evaluate(n=>n.complete&&n.naturalWidth>0));
  assert.equal(await p.locator('.fw-status-actions button').count(),2);
  assert.equal(await p.locator('.fw-status-actions button[value=published]').count(),0);
  const buttons=await p.locator('.fw-status-actions button').evaluateAll(ns=>ns.map(n=>{const r=n.getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height};}));
  assert(buttons.every(r=>r.h>=44));
  if(buttons.length===2){const [a,b]=buttons;assert(a.x+a.w+7<=b.x||a.y+a.h+7<=b.y||b.x+b.w+7<=a.x,'Button spacing '+JSON.stringify(buttons)+' gap '+await p.locator('.fw-status-actions').evaluate(n=>getComputedStyle(n).gap));}
  await p.getByRole('link',{name:'Chỉnh sửa',exact:true}).click();await p.waitForLoadState('networkidle');
  assert(await p.locator('form[data-work-form]').count());await fit();
  assert(await p.locator('select[name=flex_category_id]').inputValue());
 }
 await p.setViewportSize({width:1440,height:900});
 await go(roots.k+`/vi/kvl/flexible/${qa.job_id}/edit`);
 assert(await p.locator('form[data-work-form]').count(),'Vietnamese edit route');
 await go(roots.k+`/kvl/flexible/${qa.job_id}/edit`);
 await p.locator('input[name=name]').fill('QA dọn căn hộ đã chỉnh sửa');
 await p.getByRole('button',{name:'Đăng việc',exact:true}).click();await p.waitForLoadState('networkidle');
 assert(new URL(p.url()).pathname.includes('/kvl/flexible/mine'),'Save job failed');
 await go(roots.k+`/kvl/flexible/${qa.job_id}`);
 let response=await post(roots.k+`/kvl/flexible/${qa.job_id}/status`,{state:'published'});assert.equal(response.status(),400);
 response=await post(roots.k+`/kvl/flexible/${qa.job_id}/status`,{state:'paused'});assert.equal(response.status(),303);
 await go(roots.k+`/kvl/flexible/${qa.job_id}`);assert.equal(await p.locator('.fw-status-actions button[value=published]').count(),1);
 response=await post(roots.k+`/kvl/flexible/${qa.job_id}/status`,{state:'published'});assert.equal(response.status(),303);
 await go(roots.k+`/kvl/job/${qa.recruitment_job_id}`);assert(await p.locator('.fw-detail-photo img').evaluate(n=>n.complete&&n.naturalWidth>0));
 // Namespace/record checks remain server enforced.
 await login('other',roots.p);await go(roots.p+'/');
 let unauthorized=await ctx.request.get(roots.p+`/tuhoso/profile/${qa.profile_id}`);assert.equal(unauthorized.status(),404);
 unauthorized=await ctx.request.get(roots.k+`/kvl/flexible/${qa.job_id}/edit`,{maxRedirects:0});assert([303,403].includes(unauthorized.status()));
 await login('candidate',roots.p);await go(roots.p+'/tuhoso/profiles');assert.equal(await p.locator('.pv-profile-card').count(),2);
 await go(roots.p+`/tuhoso/work/${qa.cap_id}/edit`);await fit();
 await p.locator('input[name=name]').fill('QA nhận dọn căn hộ đã chỉnh sửa');
 await p.getByRole('button',{name:'Lưu và bật nhận việc',exact:true}).click();await p.waitForLoadState('networkidle');
 assert(new URL(p.url()).pathname.includes(`/tuhoso/work/${qa.cap_id}`));
 await go(roots.p+`/tuhoso/profile/${qa.profile_id}`);assert(await p.getByRole('heading',{name:'Đối chiếu và quyền chia sẻ'}).count());
 await go(roots.h+`/tacare/matching?profile_id=${qa.profile_id}`);
 assert(await p.locator('.tc-match-card').count()>0);assert(await p.locator(`a[href*='/tacare/job/${qa.job_id}?']`).count(), 'QA suggestion missing; selected profile '+await p.locator('select[name=profile_id]').inputValue()+' titles '+JSON.stringify(await p.locator('.tc-match-main h2').allTextContents()));
 await go(roots.h+`/tacare/job/${qa.job_id}?profile_id=${qa.profile_id}`);
 await p.locator('textarea[name=message]').fill('QA mong muốn nhận việc; đề nghị xác nhận lịch.');
 await p.getByRole('button',{name:'Gửi mong muốn nhận việc'}).click();await p.waitForLoadState('networkidle');
 assert(new URL(p.url()).pathname.includes('/tacare/connection/'));
 const connectionUrl=p.url();
 await login('business',roots.h);await go(roots.h+'/tacare/notifications');assert(await p.locator(`a[href*='${new URL(connectionUrl).pathname}']`).count(),'Notification must link to the new connection');
 await go(connectionUrl);assert(await p.getByRole('button',{name:'Đồng ý trao đổi',exact:true}).count());
 await p.getByRole('button',{name:'Đồng ý trao đổi',exact:true}).click();await p.waitForLoadState('networkidle');
 assert((await p.locator('#tc-main').innerText()).includes('Đồng ý trao đổi'));
 await go(roots.h+`/tacare/matching?job=${qa.job_id}`);assert((await p.locator('#tc-main').innerText()).includes('QA người nhận việc'));
 await go(roots.h+'/tacare/examples');assert.equal(await p.locator('.tc-match-card').count(),3);
 for(const width of [1440,375,320]){await p.setViewportSize({width,height:900});await fit();}
 await p.setViewportSize({width:1440,height:1000});
 fs.mkdirSync('docs/screenshots/account-refresh-20261021',{recursive:true});
 await p.screenshot({path:'docs/screenshots/account-refresh-20261021/tacare-examples.png',fullPage:true});
 assert.deepEqual(errors,[],'Browser errors');
 await browser.close();console.log('PASS HTTP/browser: edit and save both products, vi edit, status transitions, photos, detail buttons, role/owner isolation, matching, request, response, notification and 320/375/1440 layouts');
})().catch(e=>{console.error(e.message);process.exit(1)});
