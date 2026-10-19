/** Existing native/RPC sessions are synchronized on their first product page. */
const {request}=require('playwright'),assert=require('node:assert/strict'),fs=require('node:fs');
const account=JSON.parse(fs.readFileSync('runtime/tacare/profile_refresh_accounts.json','utf8')).accounts[0];
const root='http://tuhoso.localhost:8069';
(async()=>{const c=await request.newContext();try{
 const r=await c.post(root+'/web/session/authenticate',{data:{jsonrpc:'2.0',method:'call',id:1,
  params:{db:'tacare_local',login:account.login,password:account.password}}})
  .catch(()=>{throw Error('Native RPC authentication failed; sensitive details suppressed');});
 assert.equal(r.status(),200);const result=await r.json();assert(!result.error);const uid=result.result.uid;assert(uid);
 const before=await c.get('http://tacare.localhost:8069/care/sso/status');assert.equal((await before.json()).uid,false);
 const home=await c.get(root+'/');assert.equal(home.status(),200);
 for(const site of ['tuhoso','tacare']){const s=await c.get(`http://${site}.localhost:8069/care/sso/status`);assert.equal((await s.json()).uid,uid);}
 const excluded=await c.get('http://khovieclam.localhost:8069/care/sso/status');assert.equal((await excluded.json()).uid,false);
 await c.get(root+'/web/session/logout?redirect=/');
 console.log('PASS legacy/RPC native session upgrades to role-scoped SSO on the first homepage visit');
}finally{await c.dispose();}})().catch(e=>{console.error(e.message);process.exitCode=1;});
