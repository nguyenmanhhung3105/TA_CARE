/** Local recruitment editing, consent boundaries and structured timeline regression. */
const {chromium}=require('playwright');const fs=require('node:fs');const assert=require('node:assert/strict');
const qa=JSON.parse(fs.readFileSync('runtime/tacare/refresh_qa.json','utf8'));const root='http://tuhoso.localhost:8069';const pid=qa.recruitment_profile_id;
(async()=>{
 const browser=await chromium.launch({channel:'chrome',headless:true});const ctx=await browser.newContext();const p=await ctx.newPage();p.setDefaultTimeout(15000);
 p.on('response',r=>{if(r.status()>=400)console.log('HTTP',r.status(),new URL(r.url()).pathname)});
 const errors=[];p.on('pageerror',e=>errors.push(e.message));p.on('dialog',d=>d.accept());const shots='docs/screenshots/recruitment-profile-20261021';fs.mkdirSync(shots,{recursive:true});
 async function go(path){const r=await p.goto(path.startsWith('http')?path:root+path);assert(r&&r.status()<400,'GET failed '+r?.status()+' '+path);await p.waitForLoadState('networkidle');}
 async function login(role){await ctx.clearCookies();await go('/web/login');const a=qa.accounts.find(x=>x.role===role);const csrf=await p.locator('[name=csrf_token]').first().inputValue();const r=await ctx.request.post(root+'/web/login',{form:{csrf_token:csrf,login:a.login,password:a.password,redirect:'/'}});assert(!new URL(r.url()).pathname.includes('/web/login'));await go('/');}
 async function fit(){await p.evaluate(()=>document.fonts.ready);assert(!await p.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1),'Overflow '+p.viewportSize().width+' '+new URL(p.url()).pathname);}
 const main=()=>p.locator('form[action="/tuhoso/profile/save"]');
 async function saveMain(){await main().getByRole('button',{name:'Lưu thông tin hồ sơ',exact:true}).click();await p.waitForLoadState('networkidle');}
 await login('other');let r=await ctx.request.get(root+`/tuhoso/profile/${pid}/edit`);assert.equal(r.status(),404);
 await login('admin');await go('/tuhoso/profiles?scope=all');const card=p.locator(`.pv-profile-card[data-profile-id='${pid}']`);assert(await card.getByRole('link',{name:'Chỉnh sửa',exact:true}).count());
 await card.getByRole('link',{name:'Chỉnh sửa',exact:true}).click();await p.waitForLoadState('networkidle');
 assert(await p.locator('.rp-admin-notice').count());assert.equal(await p.locator('form[action="/tuhoso/sharing/save"]').count(),0);
 await main().locator('[name=profile_title]').fill('QA Frontend có thông tin chi tiết');await main().locator('[name=headline]').fill('QA Frontend Junior');
 await main().locator('[name=bio]').fill('QA hư cấu: có kinh nghiệm thực hành giao diện web, làm việc nhóm và kiểm thử trên điện thoại. Tập trung mô tả công việc và kết quả có thể giải thích.');
 await main().locator('[name=sector]').selectOption('it');
 const position=await main().locator('[name=desired_position_id] option').evaluateAll(ns=>ns.find(n=>n.value&&n.dataset.sector==='it'&&/frontend/i.test(n.textContent))?.value);assert(position);
 await main().locator('[name=desired_position_id]').selectOption(position);
 await main().locator('[name=career_level]').selectOption('junior');await main().locator('[name=relocation]').selectOption('discuss');
 await main().locator('[name=portfolio_url]').fill('https://example.invalid/qa-portfolio');
 await main().locator('[name=preferred_conditions]').fill('QA: lịch rõ, có người review và thống nhất phạm vi công việc.');
 await main().locator('[name=salary_min]').fill('13000000');await main().locator('[name=salary_max]').fill('9000000');await saveMain();
 assert(await p.locator('#profile-editor-error').count());assert.equal(await main().locator('[name=salary_max]').inputValue(),'9000000');assert.equal(await main().locator('[name=headline]').inputValue(),'QA Frontend Junior');
 await main().locator('[name=salary_min]').fill('9000000');await main().locator('[name=salary_max]').fill('13000000');await saveMain();
 assert(new URL(p.url()).pathname.includes(`/tuhoso/profile/${pid}/edit`));assert.equal(Number(await main().locator('[name=salary_max]').inputValue()),13000000);
 const skillForm=p.locator('#profile-skills form[action="/tuhoso/skill/add"]');
 await skillForm.locator('[name=name]').fill('QA Kiểm thử bàn phím');await skillForm.locator('[name=use]').fill('QA: kiểm tra biểu mẫu và điều hướng trong bài thực hành.');await skillForm.getByRole('button',{name:'Thêm kỹ năng',exact:true}).click();await p.waitForLoadState('networkidle');
 assert((await p.locator('#profile-skills').innerText()).includes('QA Kiểm thử bàn phím'));
 const evidenceForm=p.locator('#profile-evidence form[action="/tuhoso/evidence/add"]');await evidenceForm.locator('[name=title]').fill('QA Dự án giao diện mẫu');await evidenceForm.locator('[name=role]').fill('QA Frontend');await evidenceForm.locator('[name=description]').fill('QA: biểu mẫu responsive và bảng kiểm thử.');await evidenceForm.getByRole('button',{name:'Thêm minh chứng',exact:true}).click();await p.waitForLoadState('networkidle');
 const evidenceEdit=p.locator('#profile-evidence form[action$="/save"]').first();const evidenceData=await evidenceEdit.evaluate(f=>Object.fromEntries(new FormData(f)));const evidenceAction=await evidenceEdit.getAttribute('action');
 r=await ctx.request.post(root+evidenceAction,{form:{...evidenceData,visibility:'public'},maxRedirects:0});assert.equal(r.status(),403);
 const stale=await main().evaluate(f=>Object.fromEntries(new FormData(f)));
 const experience=p.locator('#profile-experience-records .rp-add-history form');
 await experience.locator('[name=organization]').fill('QA Studio hư cấu');await experience.locator('[name=position]').fill('QA Frontend thực hành');
 await experience.locator('[name=start_date]').fill('2025-01');await experience.locator('[name=end_date]').fill('2025-06');
 await experience.locator('[name=responsibilities]').fill('QA: phát triển biểu mẫu responsive, phối hợp backend và kiểm thử.');
 await experience.locator('[name=achievements]').fill('QA: hoàn thành bốn màn hình và checklist bàn giao.');await experience.locator('[name=tools]').fill('HTML/CSS, JavaScript, Git');
 await experience.getByRole('button',{name:'Lưu mục kinh nghiệm'}).click();await p.waitForLoadState('networkidle');assert((await p.locator('#profile-experience-records').innerText()).includes('QA Studio hư cấu'));
 const experienceId=Number(await p.locator('#profile-experience-records [data-history-id]').first().getAttribute('data-history-id'));
 let education=p.locator('#profile-education-records .rp-add-history form');await education.locator('[name=school]').fill('QA Chương trình phần mềm');await education.locator('[name=major]').fill('QA Kỹ thuật phần mềm');
 await education.locator('[name=start_date]').fill('2025-06');await education.locator('[name=end_date]').fill('2025-01');await education.getByRole('button',{name:'Lưu mục học tập'}).click();await p.waitForLoadState('networkidle');
 assert(await p.locator('#profile-editor-error').count());education=p.locator('#profile-education-records .rp-add-history form');assert.equal(await education.locator('[name=school]').inputValue(),'QA Chương trình phần mềm');
 await education.locator('[name=is_current]').check();assert(await education.locator('[name=end_date]').isDisabled());await education.locator('[name=description]').fill('QA: đồ án và môn học liên quan, chưa xác minh văn bằng.');await education.getByRole('button',{name:'Lưu mục học tập'}).click();await p.waitForLoadState('networkidle');
 assert((await p.locator('#profile-education-records').innerText()).includes('Hiện tại'));
 r=await ctx.request.post(root+'/tuhoso/profile/save',{form:stale});assert.equal(r.status(),200);assert((await r.text()).includes('phiên khác'));
 await go(`/tuhoso/profile/${pid}/edit`);const csrf=await p.locator('[name=csrf_token]').first().inputValue();
 r=await ctx.request.post(root+'/tuhoso/sharing/save',{form:{csrf_token:csrf,profile_id:String(pid),scope:'public',visible:'on',matching:'on'},maxRedirects:0});assert.equal(r.status(),404);
 r=await ctx.request.post(root+'/tuhoso/profile/save',{form:{...stale,csrf_token:csrf,user_id:'2'},maxRedirects:0});assert.equal(r.status(),400);
 await go(`/tuhoso/profile/${pid}`);assert((await p.locator('#tc-main').innerText()).includes('QA Studio hư cấu'));assert((await p.locator('#tc-main').innerText()).includes('QA Chương trình phần mềm'));assert(await p.getByRole('link',{name:'Chỉnh sửa hồ sơ',exact:true}).count());
 for(const width of [1440,375,320]){await p.setViewportSize({width,height:1000});await fit();if(width!==320)await p.locator('.pv-detail').screenshot({path:`${shots}/profile-detail-${width}.png`});await go(`/tuhoso/profile/${pid}/edit`);await fit();if(width!==320)await p.screenshot({path:`${shots}/profile-editor-${width}.png`,fullPage:true});await go(`/tuhoso/profile/${pid}`);}
 console.log('PASS admin edits foreign profile, detailed preferences, retained invalid input, history/education dates, optimistic version and consent/owner protection; desktop/mobile layouts');
 await login('candidate');await go(`/tuhoso/profile/${pid}/edit`);assert(await p.locator('form[action="/tuhoso/sharing/save"]').count());
 let token=await p.locator('[name=csrf_token]').first().inputValue();
 r=await ctx.request.post(root+`/tuhoso/history/experience/${experienceId}/delete`,{form:{csrf_token:token,profile_id:String(qa.profile_id),confirm:'delete'},maxRedirects:0});assert.equal(r.status(),403);
 await login('other');await go('/tuhoso/profiles');token=await p.locator('[name=csrf_token]').first().inputValue();
 r=await ctx.request.post(root+'/tuhoso/history/experience/save',{form:{csrf_token:token,profile_id:String(pid),id:String(experienceId),organization:'Forbidden',position:'Forbidden'},maxRedirects:0});assert.equal(r.status(),404);
 await go('/tuhoso/profiles/new?kind=recruitment');assert(await p.locator('[data-recruitment-start]').isVisible());
 const create=p.locator('[data-profile-create]');await create.locator('[name=profile_title]').fill('QA hồ sơ tạo mới đầy đủ');await create.locator('[name=headline]').fill('QA hướng Frontend');await create.locator('[name=bio]').fill('QA: định hướng và thế mạnh được giữ sau khi tạo hồ sơ.');
 await create.locator('[name=sector]').selectOption('it');await create.locator('[name=desired_position_id]').selectOption(position);await create.getByRole('button',{name:'Tạo và bổ sung thông tin',exact:true}).click();await p.waitForLoadState('networkidle');
 assert.equal(await main().locator('[name=headline]').inputValue(),'QA hướng Frontend');assert((await main().locator('[name=bio]').inputValue()).includes('được giữ'));
 assert.deepEqual(errors,[]);await browser.close();console.log('PASS owner content edit and sharing, cross-profile/foreign-write denial, creation carries recruitment details into full editor');
})().catch(e=>{console.error(e.message);process.exit(1)});
