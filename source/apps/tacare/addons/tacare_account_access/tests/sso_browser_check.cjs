/** Local SSO integration checks. Never print credentials, cookies or flow handles. */
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const saved=JSON.parse(fs.readFileSync('runtime/tacare/profile_refresh_accounts.json','utf8'));
const demo=JSON.parse(fs.readFileSync('backups/demo_flexible_20261019/accounts.json','utf8'));
const sites=['khovieclam','tuhoso','tacare'];
const base=s=>`http://${s}.localhost:8069`;
const roles=[
 {name:'admin',account:demo.accounts.find(a=>a.login.startsWith('demo-flex-99@')),allowed:sites},
 {name:'business',account:demo.accounts.find(a=>a.login.startsWith('demo-flex-00@')),allowed:['khovieclam','tacare']},
 {name:'candidate',account:saved.accounts[0],allowed:['tuhoso','tacare']},
];

(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:process.env.TACARE_CHROME||'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
 const errors=[];
 async function context(){return browser.newContext();}
 async function status(ctx,site){const r=await ctx.request.get(base(site)+'/care/sso/status');assert.equal(r.status(),200);assert(r.headers()['cache-control'].includes('no-store'));return r.json();}
 async function login(ctx,site,account,{next='/',follow=true}={}){
  const home=await ctx.request.get(base(site)+'/');assert.equal(home.status(),200);
  const tag=(await home.text()).match(/<input\b[^>]*name="csrf_token"[^>]*>/)?.[0];
  const token=tag?.match(/\bvalue="([^"]+)"/)?.[1];assert(token,'CSRF form must exist');
  return ctx.request.post(base(site)+'/web/login',{form:{csrf_token:token,login:account.login,password:account.password,redirect:next},maxRedirects:follow?20:0})
   .catch(()=>{throw new Error('Native login request failed; sensitive request details suppressed');});
 }
 async function verify(ctx,allowed,expected){
  let uid=expected;
  for(const site of sites){const s=await status(ctx,site);if(allowed.includes(site)){uid=uid||s.uid;assert(uid);assert.equal(s.uid,uid,site+' same account');assert.equal(s.syncing,false);}else assert.equal(s.uid,false,site+' outside role must stay signed out');}
  const ids=await Promise.all(allowed.map(async site=>(await ctx.cookies(base(site))).find(c=>c.name==='session_id')?.value));
  assert.equal(new Set(ids).size,allowed.length,'Use separate host cookies, never copy native session IDs');
  return uid;
 }
 try{
  // Every permitted login entry x every permitted logout entry, in one browser.
  for(const role of roles){
   for(const entry of role.allowed){
    for(const exit of role.allowed){
     const ctx=await context();const r=await login(ctx,entry,role.account);assert.equal(r.status(),200);
     assert(!new URL(r.url()).pathname.includes('/web/login'),'Native sign-in must complete');
     await verify(ctx,role.allowed);
     const out=await ctx.request.get(base(exit)+'/web/session/logout?redirect=/');assert.equal(out.status(),200);
     for(const site of sites)assert.equal((await status(ctx,site)).uid,false,'Global logout '+site);
     await ctx.close();
    }
   }
   console.log(`PASS ${role.name}: login from every permitted site, same account on ${role.allowed.length} sites, global logout from every permitted site`);
  }

  // Actual popup form, open tabs, and immediate server denial after logout.
  const ctx=await context();const pages=[];
  for(const site of sites){const p=await ctx.newPage();p.on('pageerror',e=>errors.push(e.message));await p.goto(base(site)+'/',{waitUntil:'networkidle'});pages.push(p);}
  const first=pages[0];await first.bringToFront();await first.locator('.tc-sitebar-login').click();
  await first.evaluate(({login,password})=>{document.querySelector('#tc-login-identity').value=login;document.querySelector('#tc-login-password').value=password;},roles[0].account);
  await Promise.all([first.waitForNavigation({waitUntil:'networkidle'}),first.locator('.tc-login-form button[type=submit]').click()]);
  const adminUID=await verify(ctx,sites);
  for(const p of pages){await p.bringToFront();await p.waitForFunction(uid=>Number(document.querySelector('.tc-live')?.dataset.sessionUser)===uid,adminUID,{timeout:12000});}
  assert.equal(await pages[1].locator('.pv-profile-card').count(),saved.expected_profile_count);
  await pages[1].bringToFront();await pages[1].locator('.tc-sitebar-account a').click();await pages[1].waitForLoadState('networkidle');
  const denied=await ctx.request.get(base('tacare')+'/tacare/matching',{maxRedirects:0});assert([302,303].includes(denied.status()));
  for(const p of pages){await p.bringToFront();await p.waitForFunction(()=>Number(document.querySelector('.tc-live')?.dataset.sessionUser)===0,null,{timeout:12000});}
  await ctx.close();console.log('PASS native popup and open tabs: sign-in/out synchronizes, stale server sessions rejected immediately');

  // Switching role/account clears the previous admin at the excluded third site.
  const switched=await context();await login(switched,'tacare',roles[0].account);await verify(switched,sites);
  await login(switched,'khovieclam',roles[1].account);await verify(switched,roles[1].allowed);
  await login(switched,'tacare',roles[2].account);await verify(switched,roles[2].allowed);
  await switched.close();console.log('PASS account switching admin -> business -> candidate leaves only the correct sites signed in');

  // Logging out this browser does not log the same user out of another device.
  const one=await context(),two=await context();await login(one,'tacare',roles[2].account);await login(two,'tuhoso',roles[2].account);
  const uid=await verify(two,roles[2].allowed);await one.request.get(base('tacare')+'/web/session/logout?redirect=/');await verify(two,roles[2].allowed,uid);
  await one.close();await two.close();console.log('PASS logout scope: all sites in this browser; independent browser/device remains signed in');
  const rpc=await context();await login(rpc,'tacare',roles[2].account);
  const destroyed=await rpc.request.post(base('tacare')+'/web/session/destroy',{data:{jsonrpc:'2.0',id:1,method:'call',params:{}}});
  assert.equal(destroyed.status(),200);assert(!(await destroyed.json()).error);
  for(const site of sites)assert.equal((await status(rpc,site)).uid,false);
  await rpc.close();console.log('PASS native JSON-RPC session destruction also revokes the full browser group');

  // Stop the redirect chain to exercise browser binding, source proof and replay.
  const source=await context(),attacker=await context();
  let r=await login(source,'tuhoso',roles[2].account,{next:'/en/tacare/matching',follow:false});assert.equal(r.status(),303);
  r=await source.request.get(new URL(r.headers().location,base('tuhoso')).href,{maxRedirects:0});assert.equal(r.status(),303);
  const prepare=r.headers().location;
  r=await source.request.get(prepare,{maxRedirects:0});assert.equal(r.status(),303);const authorize=r.headers().location;
  const badAuth=await attacker.request.get(authorize,{maxRedirects:0});assert([302,303,403].includes(badAuth.status()));
  assert.equal((await status(attacker,'tuhoso')).uid,false);
  r=await source.request.get(authorize,{maxRedirects:0});assert.equal(r.status(),303);const finish=r.headers().location;
  assert.equal((await attacker.request.get(finish,{maxRedirects:0})).status(),403,'A copied flow URL must not sign another browser in');
  r=await source.request.get(finish);assert.equal(r.status(),200);await verify(source,roles[2].allowed);
  assert.equal((await source.request.get(finish,{maxRedirects:0})).status(),403,'Consumed handoff cannot be replayed');
  await source.close();await attacker.close();console.log('PASS handoff security: target browser binding, authenticated source required, one-time consumption, allowed return path');
  assert.deepEqual(errors,[]);
 }finally{await browser.close();}
})().catch(e=>{console.error(e.stack);process.exitCode=1;});
