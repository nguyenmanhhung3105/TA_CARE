/* Simultaneous final-slot confirmations against dedicated local QA records. */
const {chromium}=require('playwright');const fs=require('node:fs');const assert=require('node:assert/strict');
const qa=JSON.parse(fs.readFileSync('runtime/tacare/seasonal_qa.json','utf8'));
(async()=>{
 const browser=await chromium.launch({channel:'chrome',headless:true});const ctx=await browser.newContext();const p=await ctx.newPage();const root='http://tacare.localhost:8069';
 await p.goto(root+'/web/login');await p.waitForLoadState('networkidle');const a=qa.accounts.find(a=>a.role==='client');const f=p.locator('.tc-login-form');await f.locator('[name=login]').fill(a.login);await f.locator('[name=password]').fill(a.password);await f.getByRole('button',{name:'Đăng nhập',exact:true}).click();await p.waitForURL(u=>!u.pathname.startsWith('/care/sso/')&&!u.searchParams.has('login'));await p.waitForLoadState('networkidle');
 const ids=qa.capacity_connections;await p.goto(root+'/tacare/connection/'+ids[0]);const csrf=await p.locator('[name=csrf_token]').first().inputValue();
 const act=(id,action,note='')=>ctx.request.post(root+`/tacare/connection/${id}/work/action`,{form:{csrf_token:csrf,action,note},maxRedirects:0});
 const responses=await Promise.all(ids.map(id=>act(id,'confirm')));assert.deepEqual(responses.map(r=>r.status()).sort(),[200,303]);const winner=responses.findIndex(r=>r.status()===303),loser=1-winner;
 assert((await responses[loser].text()).includes('đã đủ người'));assert.equal((await act(ids[winner],'cancel')).status(),303);
 assert.equal((await act(ids[loser],'confirm')).status(),303,'Cancel releases the occupied slot');assert.equal((await act(ids[loser],'start')).status(),303);
 assert.equal((await act(ids[loser],'dispute','QA hai phía cần làm rõ phạm vi công việc.')).status(),303);
 const r=await ctx.request.post(root+`/tacare/connection/${ids[loser]}/review`,{form:{csrf_token:csrf,rating:'5',comment:'QA blocked disputed review'},maxRedirects:0});assert.equal(r.status(),200);assert((await r.text()).includes('Chỉ đánh giá sau khi hai bên xác nhận hoàn thành'));
 await browser.close();console.log('PASS simultaneous last-slot confirmation: exactly one succeeds; cancellation releases capacity; disputed work cannot receive review');
})().catch(e=>{console.error(e.stack);process.exit(1)});
