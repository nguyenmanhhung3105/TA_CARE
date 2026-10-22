/** Focused UI regression: shared category language, real links and private workspace. */
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const qa=JSON.parse(fs.readFileSync('runtime/tacare/seasonal_qa.json','utf8'));
const root={k:'http://khovieclam.localhost:8069',p:'http://tuhoso.localhost:8069'};
const shots='docs/screenshots/everyday-services-20261022';
(async()=>{
 const browser=await chromium.launch({channel:'chrome',headless:true});
 let ctx=await browser.newContext(),page=await ctx.newPage();
 const errors=[];const badAssets=[];
 function watch(){page.setDefaultTimeout(20000);page.on('pageerror',e=>errors.push(e.message));page.on('response',r=>{if(r.status()>=400&&/\/static\/src\/(img\/services|icons\/phosphor)\//.test(r.url()))badAssets.push(new URL(r.url()).pathname);});}watch();
 async function go(url){const r=await page.goto(url);assert(r&&r.status()<400,'GET '+new URL(url).pathname);await page.waitForLoadState('networkidle');}
 async function fit(){await page.evaluate(()=>document.fonts.ready);assert(!await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1),'Overflow '+new URL(page.url()).pathname+' at '+page.viewportSize().width);}
 async function loadImages(){await page.evaluate(async()=>{for(let y=0;y<document.documentElement.scrollHeight;y+=700){scrollTo(0,y);await new Promise(r=>setTimeout(r,70));}scrollTo(0,0);});await page.waitForLoadState('networkidle');}
 async function login(role,site){await ctx.close();ctx=await browser.newContext({viewport:{width:1440,height:1000}});page=await ctx.newPage();watch();await go(site+'/web/login');const a=qa.accounts.find(a=>a.role===role);const csrf=await page.locator('[name=csrf_token]').first().inputValue();const r=await ctx.request.post(site+'/web/login',{form:{csrf_token:csrf,login:a.login,password:a.password,redirect:'/'}});assert(!new URL(r.url()).pathname.includes('/web/login'));await go(site+'/');assert.equal(await page.locator('.sx-account-actions a[href^="/web/session/logout"]').count(),1);}
 const categories=[];
 for(const site of Object.values(root)){
  await go(site+'/');const grid=page.locator('.sx-category-grid').first();assert.equal(await grid.locator('.sx-category').count(),9);
  categories.push(await grid.locator('a').evaluateAll(nodes=>nodes.map(n=>({code:n.dataset.categoryCode,label:n.textContent.trim(),icon:n.querySelector('img').getAttribute('src')}))));
  assert.equal(await page.locator('.sm-hero').count(),0);
  for(const width of [1440,768,375,320]){await page.setViewportSize({width,height:1000});await fit();const size=await page.locator('h1').evaluate(n=>parseFloat(getComputedStyle(n).fontSize));assert(size>=34);}
  assert.equal(await page.locator('[data-work-pause][aria-pressed="true"]').count(),1,'Gallery starts paused');
  await page.locator('[data-work-next]').click();assert.equal(await page.locator('[data-work-slide].is-active').count(),1);
  await page.locator('[data-work-carousel]').focus();await page.keyboard.press('ArrowRight');assert.equal(await page.locator('[data-work-slide][aria-hidden="false"]').count(),1);
  const iconSemantics=await page.locator('.sx-icon').evaluateAll(nodes=>nodes.every(n=>n.getAttribute('aria-hidden')==='true'&&n.getAttribute('alt')===''));assert(iconSemantics);
 }
 assert.deepEqual(categories[0],categories[1]);
 console.log('PASS shared nine-category icon language, rebuilt structures, paused galleries, keyboard controls and 320/375/768/1440 layouts');
 await login('client',root.k);await go(root.k+'/kvl/jobs');await page.locator('.fw-filters [name=category]').selectOption(String(qa.category_id));await page.getByRole('button',{name:'Áp dụng bộ lọc',exact:true}).click();await page.waitForLoadState('networkidle');assert.equal(new URL(page.url()).searchParams.get('category'),String(qa.category_id));assert(await page.locator('.sx-work-card').count()>0);
 for(const width of [1440,375,320]){await page.setViewportSize({width,height:1000});await fit();const select=await page.locator('.fw-filters select').first().evaluate(n=>{const s=getComputedStyle(n);return {appearance:s.appearance,padding:parseFloat(s.paddingRight),font:parseFloat(s.fontSize)}});assert.equal(select.appearance,'none');assert(select.padding>=44);assert(select.font>=16);}
 await page.setViewportSize({width:1440,height:1000});await page.locator('.sx-work-card .sx-text-link').first().click();await page.waitForLoadState('networkidle');assert(await page.locator('.fw-detail-photo img').evaluate(n=>n.complete&&n.naturalWidth>0));await fit();await page.screenshot({path:shots+'/job-detail-1440.png',fullPage:true});
 await login('provider',root.p);await go(root.p+'/tuhoso/profiles?scope=mine');assert.equal(await page.locator('.sx-profile-shelf').count(),1);assert.equal(await page.locator('.sx-view-tabs a[href*="scope=all"]').count(),0);assert.equal(await page.locator('.sx-profile-shelf[data-profile-id="'+qa.profile_id+'"]').count(),1);
 for(const width of [1440,768,375,320]){await page.setViewportSize({width,height:1000});await fit();}await page.setViewportSize({width:1440,height:1000});await loadImages();await page.screenshot({path:shots+'/provider-workspace-1440.png',fullPage:true});
 await go(root.p+'/tuhoso/profiles/new?kind=flexible&profile_title='+encodeURIComponent('Nhận chăm cây cuối tuần'));assert.equal(await page.locator('[name=profile_title]').inputValue(),'Nhận chăm cây cuối tuần');assert.equal(await page.locator('[name=kind]').inputValue(),'flexible');for(const width of [1440,375,320]){await page.setViewportSize({width,height:1000});await fit();}
 const denied=await ctx.request.get(root.p+'/tuhoso/profiles?scope=all');assert.equal(denied.status(),403);
 await login('admin',root.p);await go(root.p+'/tuhoso/profiles?scope=all');assert(await page.locator('.sx-profile-shelf').count()>=3);assert(await page.locator('.sx-profile-shelf .tc-delete-link').count()>=3);await fit();
 await ctx.close();ctx=await browser.newContext({reducedMotion:'reduce',viewport:{width:375,height:1000}});page=await ctx.newPage();watch();await go(root.k+'/');assert(await page.locator('[data-work-pause]').isDisabled());await fit();
 assert.deepEqual(errors,[]);assert.deepEqual(badAssets,[]);await browser.close();console.log('PASS filters, real detail images, personal/admin workspace isolation, prefilled profile creation, dropdowns, reduced motion and error-free assets');
})().catch(e=>{console.error(e.stack);process.exit(1)});
