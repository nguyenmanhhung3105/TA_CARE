import {seed, VERSION} from './data.js';
const KEY = `tacare-prototype-v${VERSION}`;
const copy = value => structuredClone(value);
const fail = message => { throw new Error(message); };

export function createStore(initial = seed(), persist = false) {
  let data = copy(initial);
  const save = () => { if (persist) localStorage.setItem(KEY, JSON.stringify(data)); };
  const current = () => data.accounts.find(a => a.id === data.currentUserId);
  const job = id => data.jobs.find(x => x.id === id) || fail('Không tìm thấy tin.');
  const profile = id => data.profiles.find(x => x.id === id) || fail('Không tìm thấy hồ sơ.');
  const ownJob = id => { const x=job(id),u=current(); if(u.role!=='admin' && (u.role!=='business'||u.orgId!==x.orgId)) fail('Bạn không quản lý tin của tổ chức này.'); return x; };
  const ownProfile = id => { const x=profile(id),u=current(); if(u.role!=='admin' && (u.role!=='candidate'||u.profileId!==x.id)) fail('Bạn không quản lý hồ sơ này.'); return x; };
  const notify = (userId, message, requestId='') => data.notifications.unshift({id:`n-${data.nextId++}`,userId,message,requestId,read:false});
  const id = prefix => `${prefix}-${data.nextId++}`;
  const commit = result => {save();return result;};
  return {
    get:()=>copy(data), current,
    switchUser(userId){if(!data.accounts.some(a=>a.id===userId))fail('Tài khoản demo không tồn tại.');data.currentUserId=userId;return commit();},
    reset(){data=seed();return commit();},
    createCandidate(name){name=name.trim();if(name.length<2)fail('Nhập tên có ít nhất 2 ký tự.');const uid=id('u'),pid=id('p');data.accounts.push({id:uid,name,role:'candidate',profileId:pid});data.profiles.push({id:pid,userId:uid,name,headline:'Hồ sơ mới',education:'',sector:'',location:'',goal:'',mode:'',availability:'',pay:'',visible:true,scope:'private',shareContact:false,email:'',skillItems:[],evidence:[],cvName:''});data.currentUserId=uid;return commit(pid);},
    saveJob(values, existingId, publish=false){
      const u=current();if(u.role!=='business'&&u.role!=='admin')fail('Chỉ doanh nghiệp được quản lý tin.');
      const old=existingId?ownJob(existingId):null;if(old?.status==='closed')fail('Tin đã đóng chỉ được xem lại.');
      if(publish && (!values.title?.trim()||!values.sector||!values.type||!values.mode||!values.location?.trim()||!values.description?.trim()||!values.required?.length||!values.deadline))fail('Vui lòng điền các trường bắt buộc trước khi đăng.');
      if(publish && values.start && values.deadline < values.start)fail('Hạn nhận đề nghị phải từ ngày bắt đầu trở đi.');
      if(values.quantity!==undefined && (!Number.isInteger(Number(values.quantity))||Number(values.quantity)<1))fail('Số lượng phải là số nguyên dương.');
      const orgId=old?.orgId||u.orgId;if(!orgId)fail('Chọn tài khoản doanh nghiệp để tạo tin.');
      const item={...old,...values,id:old?.id||id('j'),orgId,status:publish?'published':old?.status||'draft'};
      if(old)Object.assign(old,item);else data.jobs.unshift(item);
      notify(u.id, publish?`Tin “${item.title}” đã hiển thị.`:`Đã lưu nháp “${item.title||'Tin mới'}”.`);
      return commit(item.id);
    },
    setJobStatus(jobId,status){const x=ownJob(jobId);const allowed={draft:['published','deleted'],published:['paused','closed'],paused:['published','closed'],closed:[]};if(!allowed[x.status]?.includes(status))fail('Không thể chuyển trạng thái tin theo cách này.');if(status==='published'&&(!x.title?.trim()||!x.sector||!x.type||!x.mode||!x.location?.trim()||!x.description?.trim()||!x.required?.length||!x.deadline||x.start&&x.deadline<x.start))fail('Tin chưa đủ thông tin hợp lệ để đăng.');if(status==='deleted'){data.jobs=data.jobs.filter(j=>j.id!==jobId);return commit();}x.status=status;notify(current().id,`Tin “${x.title}” chuyển sang ${jobStatus(status)}.`);if(['paused','closed'].includes(status)){const ids=new Set(data.requests.filter(r=>r.jobId===jobId).flatMap(r=>[r.senderId,r.receiverId]));ids.delete(current().id);for(const uid of ids)notify(uid,`Tin “${x.title}” đã ${status==='closed'?'đóng':'tạm ngừng'}; lịch sử kết nối vẫn được giữ.`);}return commit();},
    saveProfile(values){const u=current();if(u.role!=='candidate')fail('Chỉ ứng viên được sửa hồ sơ của mình.');const p=ownProfile(u.profileId);Object.assign(p,values);if(values.name){u.name=values.name;}return commit();},
    addSkill(name,level,use){const p=ownProfile(current().profileId);if(!name)fail('Chọn kỹ năng.');if(p.skillItems.some(s=>s.name===name))fail('Kỹ năng đã có trong hồ sơ.');p.skillItems.push({name,level:level||'Cơ bản',use:use||''});return commit();},
    updateSkill(originalName,name,level,use){const p=ownProfile(current().profileId),item=p.skillItems.find(s=>s.name===originalName);if(!item)fail('Không tìm thấy kỹ năng.');if(!name)fail('Chọn kỹ năng.');if(name!==originalName&&p.skillItems.some(s=>s.name===name))fail('Kỹ năng đã có trong hồ sơ.');Object.assign(item,{name,level:level||'Cơ bản',use:use||''});return commit();},
    removeSkill(name){const p=ownProfile(current().profileId);p.skillItems=p.skillItems.filter(s=>s.name!==name);return commit();},
    addEvidence(values){const p=ownProfile(current().profileId);if(!values.title?.trim()||!values.role?.trim())fail('Nhập tên và vai trò trong minh chứng.');p.evidence.push({...values,id:id('e'),status:'unverified'});return commit();},
    updateEvidence(evidenceId,values){const p=ownProfile(current().profileId),item=p.evidence.find(e=>e.id===evidenceId);if(!item)fail('Không tìm thấy minh chứng.');if(!values.title?.trim()||!values.role?.trim())fail('Nhập tên và vai trò trong minh chứng.');Object.assign(item,values);return commit();},
    removeEvidence(evidenceId){const p=ownProfile(current().profileId);p.evidence=p.evidence.filter(e=>e.id!==evidenceId);return commit();},
    setEvidencePending(evidenceId){const p=ownProfile(current().profileId),e=p.evidence.find(x=>x.id===evidenceId);if(!e||e.status!=='unverified')fail('Minh chứng này không thể gửi xác minh.');e.status='pending';return commit();},
    setVisibility(values){const p=ownProfile(current().profileId);if(!['public','members','private'].includes(values.scope))fail('Phạm vi chia sẻ không hợp lệ.');p.visible=!!values.visible;p.scope=values.scope;p.shareContact=!!values.shareContact;return commit();},
    setCVMeta(name,size,type){const p=ownProfile(current().profileId);p.cvName=name||'';p.cvSize=Number(size)||0;p.cvType=type||'Không xác định';return commit();},
    createRequest(type,jobId,profileId,message,shareContact=false){
      const u=current(),j=job(jobId),p=profile(profileId);
      if(!['application','invitation'].includes(type))fail('Loại đề nghị không hợp lệ.');
      if(j.status!=='published')fail('Tin không còn nhận đề nghị mới.');
      if(data.requests.some(r=>r.type===type&&r.jobId===jobId&&r.profileId===profileId))fail('Cặp tin và hồ sơ này đã có đề nghị cùng loại trong bản thử.');
      let receiverId;
      if(type==='application'){
        if(u.role!=='candidate'||u.profileId!==profileId)fail('Chỉ chủ hồ sơ được gửi đề nghị ứng tuyển.');
        receiverId=data.accounts.find(a=>a.role==='business'&&a.orgId===j.orgId)?.id;
      }else{
        if(u.role!=='business'||u.orgId!==j.orgId)fail('Chỉ doanh nghiệp sở hữu tin được gửi lời mời.');
        if(!p.visible||p.scope==='private')fail('Hồ sơ không sẵn sàng nhận lời mời.');
        receiverId=p.userId;
      }
      if(!receiverId)fail('Không tìm thấy bên nhận demo.');
      const r={id:id('r'),type,jobId,profileId,senderId:u.id,receiverId,message:message.trim(),status:'pending',created:new Date().toISOString().slice(0,10),shareContact:!!shareContact,history:[type==='application'?'Ứng viên gửi đề nghị ứng tuyển':'Doanh nghiệp gửi lời mời trao đổi'],snapshot:{name:p.name,headline:p.headline,skills:p.skillItems.map(s=>s.name),evidence:p.evidence.filter(e=>e.status==='verified').map(e=>e.title)}};
      data.requests.unshift(r);notify(receiverId,`${u.name} đã ${type==='application'?'gửi đề nghị ứng tuyển':'mời bạn trao đổi'} cho “${j.title}”.`,r.id);return commit(r.id);
    },
    respondRequest(requestId,status){const r=data.requests.find(x=>x.id===requestId)||fail('Không tìm thấy đề nghị.');if(r.receiverId!==current().id)fail('Chỉ bên nhận mới được phản hồi.');if(r.status!=='pending')fail('Đề nghị đã được phản hồi.');if(!['accepted','declined'].includes(status))fail('Phản hồi không hợp lệ.');r.status=status;r.history.push(status==='accepted'?'Bên nhận đồng ý trao đổi':'Bên nhận từ chối');notify(r.senderId,`${current().name} đã ${status==='accepted'?'đồng ý trao đổi':'từ chối'} đề nghị cho “${job(r.jobId).title}”.`,r.id);return commit();},
    cancelRequest(requestId){const r=data.requests.find(x=>x.id===requestId)||fail('Không tìm thấy đề nghị.');if(r.senderId!==current().id||r.status!=='pending')fail('Chỉ bên gửi được hủy đề nghị đang chờ.');r.status='cancelled';r.history.push('Bên gửi hủy đề nghị');notify(r.receiverId,`${current().name} đã hủy đề nghị cho “${job(r.jobId).title}”.`,r.id);return commit();},
    markRead(notificationId){const n=data.notifications.find(x=>x.id===notificationId);if(!n||n.userId!==current().id)fail('Thông báo không thuộc tài khoản này.');n.read=true;return commit();},
    addFeedback(requestId,result,note){const r=data.requests.find(x=>x.id===requestId)||fail('Không tìm thấy kết nối.');if(r.status!=='accepted'||![r.senderId,r.receiverId].includes(current().id))fail('Chỉ hai bên trong kết nối đã đồng ý trao đổi được cập nhật kết quả.');if(!result)fail('Chọn kết quả trao đổi.');data.feedback.unshift({id:id('f'),requestId,userId:current().id,result,note:note.trim(),date:new Date().toISOString().slice(0,10)});notify(r.senderId===current().id?r.receiverId:r.senderId,`${current().name} đã cập nhật kết quả trao đổi cho “${job(r.jobId).title}”.`,r.id);return commit();}
  };
}
export function loadStore(){try{const raw=JSON.parse(localStorage.getItem(KEY));if(raw?.version===VERSION&&Array.isArray(raw.jobs))return createStore(raw,true);}catch{}return createStore(seed(),true);}
export const jobStatus = s => ({draft:'Nháp',published:'Đang hiển thị',paused:'Tạm ngừng',closed:'Đã đóng'})[s]||s;
export const requestStatus = s => ({pending:'Chờ phản hồi',accepted:'Đồng ý trao đổi',declined:'Từ chối',cancelled:'Đã hủy'})[s]||s;
export function match(j,p){const names=p.skillItems.map(s=>s.name), required=j.required||[],preferred=j.preferred||[];const matched=required.filter(x=>names.includes(x)), missing=required.filter(x=>!names.includes(x)), extra=preferred.filter(x=>names.includes(x));const sameMode=!j.mode||!!p.mode&&(j.mode===p.mode||j.mode==='Kết hợp'||p.mode==='Kết hợp');const sameLocation=!j.location||!!p.location&&(j.location===p.location||j.mode==='Từ xa');const score=Math.round(65*(required.length?matched.length/required.length:1)+20*(preferred.length?extra.length/preferred.length:1)+10*(sameMode?1:0)+5*(sameLocation?1:0));return {score,matched,missing,extra,sameMode,sameLocation,incomplete:!p.mode||!p.location};}
