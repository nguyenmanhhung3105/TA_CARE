/** Local UI/security check using disposable fictional records only. Always run cleanup. */
const {chromium}=require('playwright');const fs=require('node:fs');const assert=require('node:assert/strict');
const qa=JSON.parse(fs.readFileSync('runtime/tacare/refresh_qa.json','utf8'));
const roots={k:'http://khovieclam.localhost:8069',p:'http://tuhoso.localhost:8069',h:'http://tacare.localhost:8069'};
(async()=>{
 const browser=await chromium.launch({channel:'chrome',headless:true});const ctx=await browser.newContext();const p=await ctx.newPage();p.setDefaultTimeout(12000);
 const errors=[];p.on('pageerror',e=>errors.push(e.message));const shots='docs/screenshots/admin-polish-20261021';fs.mkdirSync(shots,{recursive:true});
 async function go(url){const r=await p.goto(url);assert(r&&r.status()<400,`GET ${r?.status()} ${new URL(url).pathname}`);await p.waitForLoadState('networkidle');}
 async function login(role,site){await ctx.clearCookies();await go(site+'/web/login');const a=qa.accounts.find(x=>x.role===role);const csrf=await p.locator('[name=csrf_token]').first().inputValue();const r=await ctx.request.post(site+'/web/login',{form:{csrf_token:csrf,login:a.login,password:a.password,redirect:'/'}});assert(!new URL(r.url()).pathname.includes('/web/login'));await go(site+'/');}
 async function fit(){await p.evaluate(()=>document.fonts.ready);assert(!await p.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1),'Horizontal overflow at '+new URL(p.url()).pathname+' width '+p.viewportSize().width);}
 async function dropdowns(){const controls=p.locator('select:visible');for(let i=0;i<await controls.count();i++){
  const css=await controls.nth(i).evaluate(n=>{const s=getComputedStyle(n);return {appearance:s.appearance,position:s.backgroundPosition,padding:parseFloat(s.paddingRight),font:parseFloat(s.fontSize)};});
  assert.equal(css.appearance,'none');assert(css.position.includes('16px'),JSON.stringify(css));assert(css.padding>=44);assert(css.font>=16);
 }}
 async function confirmRemove(url){await go(url);assert(await p.locator('.tc-removal-panel').count());await p.locator('input[name=confirm]').check();await p.getByRole('button',{name:'Xác nhận xóa',exact:true}).click();await p.waitForLoadState('networkidle');}
 // Public pages keep their original compositions with consistent legible typography.
 for(const [key,root] of Object.entries(roots))for(const width of [1440,375,320]){
  await p.setViewportSize({width,height:1000});await go(root+'/');await fit();await dropdowns();
  const h1=await p.locator('.tc-live h1').first().evaluate(n=>({size:parseFloat(getComputedStyle(n).fontSize),weight:parseInt(getComputedStyle(n).fontWeight)}));assert(h1.size>=30&&h1.weight>=600);
  assert.equal(await p.locator('#admin-matching').count(),0);
  if(width!==320)await p.screenshot({path:`${shots}/${key}-guest-${width}.png`,fullPage:false});
 }
 console.log('PASS public typography, dropdown chevrons and 320/375/1440 layouts on all sites');
 await login('candidate',roots.p);await go(roots.p+`/tuhoso/profile/${qa.profile_id}`);assert.equal(await p.locator('a.tc-delete-link').count(),0);
 let r=await ctx.request.get(roots.p+`/tuhoso/profile/${qa.profile_id}/remove`);assert.equal(r.status(),403);
 r=await ctx.request.get(roots.p+`/tuhoso/work/${qa.cap_id}/remove`);assert.equal(r.status(),403);
 await login('business',roots.k);await go(roots.k+'/kvl/flexible/mine');assert.equal(await p.locator('.tc-nav a[href*="/kvl/candidates"]').count(),0);
 r=await ctx.request.get(roots.k+`/kvl/job/${qa.job_id}/remove`);assert.equal(r.status(),403);
 console.log('PASS non-admin deletion denied and Kho candidate tab removed');
 await login('admin',roots.h);await go(roots.h+'/');assert.equal(await p.locator('#admin-matching .tc-home-example').count(),3);
 assert(await p.locator('#admin-matching [data-match-profile]').count()>0);
 const disclosed=await p.locator('#admin-matching [data-match-profile]').evaluateAll(ns=>ns.map(n=>Number(n.dataset.matchProfile)));
 assert(disclosed.every(id=>[qa.profile_id,qa.recruitment_profile_id].includes(id)),'Unconsented profile disclosed');
 for(const width of [1440,375,320]){await p.setViewportSize({width,height:1000});await go(roots.h+'/#admin-matching');await fit();await dropdowns();if(width!==320)await p.locator('#admin-matching').screenshot({path:`${shots}/admin-matching-${width}.png`});}
 await p.setViewportSize({width:1440,height:1000});await go(roots.h+`/?home_job=${qa.job_id}#admin-matching`);
 assert(await p.locator(`[data-match-job='${qa.job_id}'][data-match-profile='${qa.profile_id}']`).count());
 console.log('PASS admin homepage real matching uses current consent; three sample cards and job selector');
 await go(roots.p+`/tuhoso/profile/${qa.delete_profile_id}`);assert.equal(await p.getByRole('link',{name:'Xóa hồ sơ',exact:true}).count(),1);
 await go(roots.p+`/tuhoso/work/${qa.delete_cap_id}/remove`);const csrf=await p.locator('[name=csrf_token]').first().inputValue();
 r=await ctx.request.post(roots.p+`/tuhoso/work/${qa.delete_cap_id}/remove`,{form:{csrf_token:csrf},maxRedirects:0});assert.equal(r.status(),400);
 r=await ctx.request.post(roots.p+`/tuhoso/work/${qa.delete_cap_id}/remove`,{form:{confirm:'delete'},maxRedirects:0});assert.equal(r.status(),400);
 r=await ctx.request.post(roots.p+`/tuhoso/work/${qa.delete_cap_id}/remove`,{form:{csrf_token:csrf,confirm:'delete',user_id:'2'},maxRedirects:0});assert.equal(r.status(),400);
 await confirmRemove(roots.p+`/tuhoso/work/${qa.delete_cap_id}/remove`);
 r=await ctx.request.get(roots.p+`/tuhoso/work/${qa.delete_cap_id}`);assert.equal(r.status(),404);
 await go(roots.p+`/tuhoso/profile/${qa.delete_profile_id}`);
 await confirmRemove(roots.p+`/tuhoso/profile/${qa.delete_profile_id}/remove`);
 r=await ctx.request.get(roots.p+`/tuhoso/profile/${qa.delete_profile_id}`);assert.equal(r.status(),404);
 await confirmRemove(roots.k+`/kvl/job/${qa.delete_job_id}/remove`);
 r=await ctx.request.get(roots.k+`/kvl/job/${qa.delete_job_id}`);assert.equal(r.status(),404);
 console.log('PASS unlinked offer/profile/job deletion, GET confirmation, CSRF, field allowlist and confirmation required');
 // A linked record is removed from the live product while its conversation survives.
 await login('candidate',roots.h);await go(roots.h+`/tacare/job/${qa.job_id}?profile_id=${qa.profile_id}`);
 await p.locator('textarea[name=message]').fill('QA kiểm tra gỡ tin có lịch sử.');await p.getByRole('button',{name:'Gửi mong muốn nhận việc'}).click();await p.waitForLoadState('networkidle');const connectionUrl=p.url();assert(connectionUrl.includes('/tacare/connection/'));
 await login('admin',roots.k);await go(roots.k+`/kvl/job/${qa.job_id}/remove`);assert((await p.locator('.tc-removal-panel').innerText()).includes('lịch sử'));
 await confirmRemove(roots.k+`/kvl/job/${qa.job_id}/remove`);
 r=await ctx.request.get(roots.k+`/kvl/flexible/${qa.job_id}`);assert.equal(r.status(),404);
 await go(connectionUrl);assert((await p.locator('#tc-main').innerText()).includes('Đã hủy'));
 await confirmRemove(roots.p+`/tuhoso/profile/${qa.profile_id}/remove`);
 r=await ctx.request.get(roots.p+`/tuhoso/profile/${qa.profile_id}`);assert.equal(r.status(),404);
 await login('candidate',roots.p);await go(roots.p+'/tuhoso/profiles');assert.equal(await p.locator('.pv-profile-card').count(),1);
 assert.deepEqual(errors,[],'Browser errors');await browser.close();
 console.log('PASS linked removal retains conversation, cancels pending request, removes archived profile from library and preserves candidate login');
})().catch(e=>{console.error(e.message);process.exit(1)});
