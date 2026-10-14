import test from 'node:test';
import assert from 'node:assert/strict';
import {createStore, match} from '../state.js';
import {seed} from '../data.js';

test('ownership and job lifecycle are checked in state actions',()=>{
 const s=createStore(seed());s.switchUser('u-sen');
 assert.throws(()=>s.setJobStatus('j-03','paused'),/không quản lý/);
 const id=s.saveJob({title:'Tin mẫu',sector:'Công nghệ thông tin',type:'Task',mode:'Từ xa',location:'Toàn quốc',description:'Đầu việc mẫu',required:['SQL'],deadline:'2026-12-31'},null,false);
 assert.equal(s.get().jobs.find(j=>j.id===id).status,'draft');
 s.setJobStatus(id,'published');s.setJobStatus(id,'paused');s.setJobStatus(id,'closed');
 assert.throws(()=>s.setJobStatus(id,'published'),/Không thể/);
});

test('recipient alone responds, duplicates and second responses are blocked',()=>{
 const s=createStore(seed());s.switchUser('u-binh');
 const id=s.createRequest('application','j-06','p-binh','Em muốn thử task này.');
 assert.throws(()=>s.respondRequest(id,'accepted'),/Chỉ bên nhận/);
 assert.throws(()=>s.createRequest('application','j-06','p-binh','Gửi lại'),/đã có đề nghị/);
 s.switchUser('u-sen');s.respondRequest(id,'accepted');
 assert.throws(()=>s.respondRequest(id,'declined'),/đã được phản hồi/);
 assert.equal(s.get().requests.find(r=>r.id===id).status,'accepted');
 assert(s.get().notifications.some(n=>n.userId==='u-binh'&&n.requestId===id));
});

test('profile visibility controls invitations and matching changes with skills',()=>{
 const s=createStore(seed()),j=s.get().jobs.find(j=>j.id==='j-01');
 const before=match(j,s.get().profiles.find(p=>p.id==='p-binh')).score;
 s.switchUser('u-binh');s.addSkill('JavaScript','Cơ bản','');s.addSkill('HTML/CSS','Cơ bản','');
 const after=match(j,s.get().profiles.find(p=>p.id==='p-binh')).score;
 assert(after>before);
 s.setVisibility({scope:'private',visible:false,shareContact:false});
 s.switchUser('u-sen');
 assert.throws(()=>s.createRequest('invitation','j-01','p-binh','Mời bạn'),/không sẵn sàng/);
});

test('closing a job preserves pending history and permits recipient response',()=>{
 const s=createStore(seed());s.switchUser('u-sen');s.setJobStatus('j-01','closed');
 const r=s.get().requests.find(x=>x.id==='r-01');assert.equal(r.status,'pending');
 s.respondRequest('r-01','declined');assert.equal(s.get().requests.find(x=>x.id==='r-01').status,'declined');
 assert.throws(()=>s.createRequest('invitation','j-01','p-chi','Mời'),/không còn nhận/);
});

test('sender can cancel a pending request and reset restores the shared seed',()=>{
 const s=createStore(seed());s.switchUser('u-binh');
 const id=s.createRequest('application','j-06','p-binh','Xin trao đổi.');
 s.cancelRequest(id);
 assert.equal(s.get().requests.find(r=>r.id===id).status,'cancelled');
 assert.throws(()=>s.cancelRequest(id),/đang chờ/);
 s.reset();
 assert.equal(s.get().jobs.length,12);
 assert.equal(s.get().requests.length,3);
 assert.equal(s.current().id,'u-an');
});
