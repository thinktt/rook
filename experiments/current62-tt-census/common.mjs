import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
export const H='0-5,8-13';
export const read=p=>JSON.parse(fs.readFileSync(p,'utf8'));
export const save=(p,v)=>fs.writeFileSync(p,JSON.stringify(v,null,2)+'\n',{flag:'wx'});
export const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
export {census} from './counters.mjs';
export function pins(plan){
 assert(plan.source_inputs&&Object.keys(plan.source_inputs).length>=74,'actual compiled source closure pending');
 for(const [p,h]of Object.entries({...plan.immutable_inputs,...plan.source_inputs,...plan.helper_inputs}))assert.equal(sha(p),h,p);
 assert.equal(sha(plan.engine.path),plan.engine.sha256);
 for(const k of ['compiled_source_manifest','build_receipt','actual_build_terminal','source_review','schema_contract','parent_activation','runtime_binding','quiet_resources']){
  assert(plan[k]?.path&&plan[k]?.sha256,'actual metadata binding '+k);assert.equal(sha(plan[k].path),plan[k].sha256);
 }
}
export function context(){
 const take=p=>{try{return fs.readFileSync(p,'utf8');}catch(e){return {error:e.code};}};
 const membership=take('/proc/self/cgroup');const groups={};
 if(typeof membership==='string')for(const line of membership.split('\n'))if(line.startsWith('0::/')){
  const relative=line.slice(4);assert(!relative.split('/').includes('..'));
  let p=path.join('/sys/fs/cgroup',relative);
  for(let n=0;n<32;n++){
   groups[p]=Object.fromEntries(['cpu.max','cpuset.cpus.effective','memory.max','memory.swap.max'].map(k=>[k,take(path.join(p,k))]));
   if(p==='/sys/fs/cgroup')break;p=path.dirname(p);assert(p.startsWith('/sys/fs/cgroup'));
  }
 }
 return {utc:new Date().toISOString(),proc_stat:take('/proc/stat'),self_status:take('/proc/self/status'),loadavg:take('/proc/loadavg'),membership,cgroups:groups,scope:'Point guest/cgroup/CPU15 tick observations only; not continuous sibling ownership or exclusive host proof.'};
}
