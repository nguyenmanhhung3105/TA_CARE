/** Verify native TOTP completes before any SSO session is issued. */
const {chromium}=require('playwright'),assert=require('node:assert/strict'),fs=require('node:fs'),crypto=require('node:crypto');
const qa=JSON.parse(fs.readFileSync('runtime/tacare/sso_mfa_qa.json','utf8'));
const admin=JSON.parse(fs.readFileSync('backups/demo_flexible_20261019/accounts.json','utf8')).accounts.find(a=>a.login.startsWith('demo-flex-99@'));
const sites=['khovieclam','tuhoso','tacare'],base=s=>`http://${s}.localhost:8069`;
function csrf(html){const tag=html.match(/<input\b[^>]*name="csrf_token"[^>]*>/)?.[0];return tag?.match(/\bvalue="([^"]+)"/)?.[1];}
function totp(secret){let bits='';for(const c of secret.replace(/=/g,''))bits+='ABCDEFGHIJKLMNOPQRSTUVWXYZ234567'.indexOf(c).toString(2).padStart(5,'0');const key=Buffer.from(bits.match(/.{8}/g).map(b=>parseInt(b,2)));const count=Buffer.alloc(8);count.writeBigUInt64BE(BigInt(Math.floor(Date.now()/30000)));const mac=crypto.createHmac('sha1',key).update(count).digest(),offset=mac[19]&15;return String((mac.readUInt32BE(offset)&0x7fffffff)%1000000).padStart(6,'0');}
(async()=>{const b=await chromium.launch({headless:true,executablePath:process.env.TACARE_CHROME||'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});const ctx=await b.newContext();
async function status(s){const r=await ctx.request.get(base(s)+'/care/sso/status');assert.equal(r.status(),200);return r.json();}
async function password(account){let r=await ctx.request.get(base('tuhoso')+'/');const token=csrf(await r.text());assert(token);return ctx.request.post(base('tuhoso')+'/web/login',{form:{csrf_token:token,login:account.login,password:account.password,redirect:'/tuhoso/profiles'}}).catch(()=>{throw Error('Native MFA login failed; sensitive request details suppressed');});}
try{
 let r=await password(qa);assert.equal(r.status(),200);assert(new URL(r.url()).pathname.endsWith('/web/login/totp'));
 for(const s of sites)assert.equal((await status(s)).uid,false,'Password alone cannot sign in '+s);
 const start=await ctx.request.get(base('tuhoso')+'/care/sso/start',{maxRedirects:0});assert([302,303].includes(start.status()));
 const token=csrf(await r.text());assert(token);
 r=await ctx.request.post(base('tuhoso')+'/web/login/totp',{form:{csrf_token:token,totp_token:totp(qa.totp_secret),redirect:'/tuhoso/profiles'}});
 assert.equal(r.status(),200);assert(new URL(r.url()).pathname.endsWith('/tuhoso/profiles'));
 for(const s of ['tuhoso','tacare'])assert.equal((await status(s)).uid,qa.user_id);assert.equal((await status('khovieclam')).uid,false);
 await ctx.request.get(base('tacare')+'/web/session/logout?redirect=/');for(const s of sites)assert.equal((await status(s)).uid,false);
 console.log('PASS native TOTP: password-only sessions stay signed out; correct OTP synchronizes only Tủ + TA.CARE; global logout works');
 // A logout while changing an existing SSO account to an MFA account must also
 // revoke the earlier browser group, even though native uid is temporarily null.
 r=await password(admin);assert.equal(r.status(),200);for(const s of sites)assert((await status(s)).uid);
 r=await password(qa);assert(new URL(r.url()).pathname.endsWith('/web/login/totp'));
 await ctx.request.get(base('tuhoso')+'/web/session/logout?redirect=/');for(const s of sites)assert.equal((await status(s)).uid,false);
 console.log('PASS MFA cancellation/logout revokes an earlier browser group and never grants the pending account');
}finally{await ctx.close();await b.close();}})().catch(e=>{console.error(e.stack);process.exitCode=1;});
