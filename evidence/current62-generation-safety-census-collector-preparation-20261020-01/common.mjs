import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
export const H='0-5,8-13';
export const read=p=>JSON.parse(fs.readFileSync(p,'utf8'));
export const save=(p,v)=>fs.writeFileSync(p,JSON.stringify(v,null,2)+'\n',{flag:'wx'});
export const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
export function census(raw,pid){
 assert(raw.length<=65536,'census byte cap');
 assert(raw.every(x=>x<128),'census must be ASCII JSON');
 const c=JSON.parse(raw.toString('ascii'));
 assert.deepEqual(Object.keys(c).sort(),['schema','pid','complete','overflow','invalid','calls_rows'].sort());
 assert.equal(c.schema,'rook2-generation-safety-demand-v1');assert.equal(c.pid,pid);
 assert.equal(c.complete,true);assert.equal(c.overflow,false);assert.equal(c.invalid,false);
 const contract=read(new URL('./consumer-contract-proposal.json',import.meta.url));
 assert(Array.isArray(c.calls_rows)&&c.calls_rows.length===6);const seen=new Set();let calls=0n;
 const sum=a=>a.reduce((s,x)=>s+BigInt(x),0n), eq=(a,b)=>assert.equal(BigInt(a),BigInt(b));
 const nonnegative=x=>assert(Number.isSafeInteger(x)&&x>=0,'counter must be exact nonnegative JSON integer');
 for(const r of c.calls_rows){
  assert(contract.row_dimensions.limit.includes(r.limit)&&contract.row_dimensions.checkers.includes(r.checkers));
  const key=r.limit+'/'+r.checkers;assert(!seen.has(key));seen.add(key);
  assert.deepEqual(Object.keys(r).sort(),['limit','checkers',...contract.scalar_fields,...Object.keys(contract.array_fields),...Object.keys(contract.object_fields),contract.histogram_field].sort());
  for(const k of contract.scalar_fields)nonnegative(r[k]);
  for(const [k,n]of Object.entries(contract.array_fields)){assert(Array.isArray(r[k])&&r[k].length===n);r[k].forEach(nonnegative);}
  for(const [k,keys]of Object.entries(contract.object_fields)){assert.deepEqual(Object.keys(r[k]).sort(),[...keys].sort());Object.values(r[k]).forEach(nonnegative);}
  const hist=r.bounded_final_count_histogram;assert(Array.isArray(hist)&&hist.length===3);hist.forEach(nonnegative);
  const a=r.routes,s=r.special_routes;
  eq(r.calls,BigInt(r.safety_new)+BigInt(r.prefix_limit_before_safety));
  eq(r.calls,BigInt(r.threshold_returns)+BigInt(r.exhausted_returns));
  eq(r.pin_summary_calls,BigInt(r.pin_summary_zero)+BigInt(r.pin_summary_nonzero));
  assert(r.pin_summary_calls<=r.safety_new&&r.single_check_pawn_prefix_calls<=r.safety_new);
  eq(sum(r.safety_trials_by_source),sum(Object.values(a)));eq(a.unexpected_special_accepts_route,0);
  const accepted=['unchecked_unpinned_accept','unchecked_pinned_projection_accept','checked_onmask_projection_accept','king_projection_accept'].map(k=>BigInt(a[k])).reduce((x,y)=>x+y,0n);
  const projections=Object.entries(a).filter(([k])=>k.includes('_projection_')).map(([,v])=>BigInt(v)).reduce((x,y)=>x+y,0n)+sum(Object.values(s));
  eq(r.projection_calls,projections);assert(BigInt(r.promotion_destination_accepts)<=accepted);
  assert(r.promotion_destination_accepts<=r.promotion_destination_trials);
  assert(BigInt(r.promotion_choices_emitted)>=BigInt(r.promotion_destination_accepts)&&BigInt(r.promotion_choices_emitted)<=4n*BigInt(r.promotion_destination_accepts));
  eq(r.emitted_moves,accepted-BigInt(r.promotion_destination_accepts)+BigInt(r.promotion_choices_emitted)+BigInt(s.ep_projection_accept)+BigInt(s.castle_final_projection_accept));
  eq(r.emitted_moves,r.output_len_sum);eq(r.threshold_returns,sum(Object.values(r.threshold_stage)));
  if(r.checkers!=='0'){eq(r.pin_summary_calls,0);eq(a.unchecked_unpinned_accept,0);eq(a.unchecked_pinned_projection_accept,0);eq(a.unchecked_pinned_projection_reject,0);}
  else{eq(a.checked_offmask_reject,0);eq(a.checked_onmask_projection_accept,0);eq(a.checked_onmask_projection_reject,0);eq(r.single_check_pawn_prefix_calls,0);}
  if(r.checkers!=='1')eq(r.single_check_pawn_prefix_calls,0);
  if(r.limit==='limit2'){eq(sum(hist),r.calls);eq(r.output_len_sum,BigInt(hist[1])+2n*BigInt(hist[2]));eq(hist[2],r.threshold_returns);eq(r.exhausted_returns,BigInt(hist[0])+BigInt(hist[1]));}
  else{eq(sum(hist),0);eq(r.threshold_returns,0);assert(BigInt(r.output_len_sum)<=512n*BigInt(r.calls));}
  calls+=BigInt(r.calls);
 }
 assert(calls>0n,'no observed generator calls');return c;
}
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
