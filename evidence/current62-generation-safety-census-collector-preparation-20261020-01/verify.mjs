#!/usr/bin/env node
// Offline only. Re-read original raw rows and original released oracle; no engine launch.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {checkReplay,workloads,oracle} from '/home/legolas/king-spec/conformance/profiling/replay-check.mjs';
import {read,save,sha,pins} from './common.mjs';

function independentCensus(c,pid){
 const scalars=["calls", "safety_new", "prefix_limit_before_safety", "pin_summary_calls", "pin_summary_zero", "pin_summary_nonzero", "single_check_pawn_prefix_calls", "threshold_returns", "exhausted_returns", "emitted_moves", "output_len_sum", "promotion_destination_trials", "promotion_destination_accepts", "promotion_choices_emitted", "projection_calls"];
 const arrays={"source_entered": 6, "piece_cursor_destinations": 6, "piece_blocker_rejects": 6, "safety_trials_by_source": 6};
 const objects={"routes": ["unchecked_unpinned_accept", "unchecked_pinned_projection_accept", "unchecked_pinned_projection_reject", "checked_offmask_reject", "checked_onmask_projection_accept", "checked_onmask_projection_reject", "king_projection_accept", "king_projection_reject", "unexpected_special_accepts_route"], "special_routes": ["ep_projection_accept", "ep_projection_reject", "castle_transit_projection_accept", "castle_transit_projection_reject", "castle_final_projection_accept", "castle_final_projection_reject"], "threshold_stage": ["ep", "castle", "early_king", "pawns", "knight", "bishop", "rook", "queen", "king"], "pawn_geometry_counters": ["capture_offsets_inboard", "capture_victim_eligible", "single_forward_offsets_inboard", "single_forward_empty", "double_forward_empty"]};
 assert.equal(c.schema,'rook2-generation-safety-demand-v1');assert.equal(c.pid,pid);assert.equal(c.complete,true);assert.equal(c.overflow,false);assert.equal(c.invalid,false);
 assert.deepEqual(Object.keys(c).sort(),['schema','pid','complete','overflow','invalid','calls_rows'].sort());assert.equal(c.calls_rows.length,6);
 const num=v=>{assert(Number.isSafeInteger(v)&&v>=0);return BigInt(v);};
 const add=vs=>vs.reduce((total,v)=>total+num(v),0n);const keys=[];let totalCalls=0n;
 for(const row of c.calls_rows){
  assert(['full512','limit2'].includes(row.limit)&&['0','1','2plus_saturated'].includes(row.checkers));keys.push(row.limit+':'+row.checkers);
  assert.deepEqual(Object.keys(row).sort(),['limit','checkers',...scalars,...Object.keys(arrays),...Object.keys(objects),'bounded_final_count_histogram'].sort());
  scalars.forEach(k=>num(row[k]));for(const[k,n]of Object.entries(arrays)){assert.equal(row[k].length,n);row[k].forEach(num);}
  for(const[k,names]of Object.entries(objects)){assert.deepEqual(Object.keys(row[k]).sort(),names.slice().sort());Object.values(row[k]).forEach(num);}
  const routes=row.routes,special=row.special_routes,h=row.bounded_final_count_histogram;assert.equal(h.length,3);h.forEach(num);
  const calls=num(row.calls);totalCalls+=calls;
  assert.equal(calls,num(row.safety_new)+num(row.prefix_limit_before_safety));assert.equal(calls,num(row.threshold_returns)+num(row.exhausted_returns));
  assert.equal(num(row.pin_summary_calls),num(row.pin_summary_zero)+num(row.pin_summary_nonzero));assert(row.pin_summary_calls<=row.safety_new&&row.single_check_pawn_prefix_calls<=row.safety_new);
  assert.equal(add(row.safety_trials_by_source),add(Object.values(routes)));assert.equal(routes.unexpected_special_accepts_route,0);
  const accepts=add([routes.unchecked_unpinned_accept,routes.unchecked_pinned_projection_accept,routes.checked_onmask_projection_accept,routes.king_projection_accept]);
  const projected=add([routes.unchecked_pinned_projection_accept,routes.unchecked_pinned_projection_reject,routes.checked_onmask_projection_accept,routes.checked_onmask_projection_reject,routes.king_projection_accept,routes.king_projection_reject,...Object.values(special)]);
  assert.equal(num(row.projection_calls),projected);assert(num(row.promotion_destination_accepts)<=accepts&&row.promotion_destination_accepts<=row.promotion_destination_trials);
  const promos=num(row.promotion_choices_emitted),pa=num(row.promotion_destination_accepts);assert(pa<=promos&&promos<=4n*pa);
  const pushes=accepts-pa+promos+num(special.ep_projection_accept)+num(special.castle_final_projection_accept);
  assert.equal(num(row.emitted_moves),pushes);assert.equal(num(row.output_len_sum),pushes);assert.equal(num(row.threshold_returns),add(Object.values(row.threshold_stage)));
  if(row.checkers==='0'){assert.equal(add([routes.checked_offmask_reject,routes.checked_onmask_projection_accept,routes.checked_onmask_projection_reject,row.single_check_pawn_prefix_calls]),0n);}
  else{assert.equal(add([row.pin_summary_calls,routes.unchecked_unpinned_accept,routes.unchecked_pinned_projection_accept,routes.unchecked_pinned_projection_reject]),0n);}
  if(row.checkers!=='1')assert.equal(row.single_check_pawn_prefix_calls,0);
  if(row.limit==='limit2'){assert.equal(add(h),calls);assert.equal(pushes,num(h[1])+2n*num(h[2]));assert.equal(h[2],row.threshold_returns);assert.equal(num(row.exhausted_returns),num(h[0])+num(h[1]));}
  else{assert.equal(add(h),0n);assert.equal(row.threshold_returns,0);assert(pushes<=512n*calls);}
 }
 assert.equal(new Set(keys).size,6);assert(totalCalls>0n);
}

const plan=read(process.argv[2]),out=plan.output;
assert.deepEqual(plan.cases,['profile-04','profile-35']);assert.deepEqual(plan.limits,{setupMs:15000,searchMs:60000,cleanupMs:5000,aggregateMs:180000,byteCap:4194304,aggregateCap:8388608,censusBytes:65536});
pins(plan);assert.deepEqual(read(path.join(out,'plan.json')),plan);
const terminal=read(path.join(out,'tool-terminal.json'));
assert(terminal.actual_tool_terminal_observed&&terminal.exit_code===0);
const result=read(path.join(out,'result.json'));
assert(result.complete&&result.failure===null&&result.engine_runs===2&&result.input_closure_after===true);
const cases=[];let rawTotal=0;
for(const id of ['profile-04','profile-35']){
 const dir=path.join(out,id),input=workloads.cases.find(c=>c.id===id),expected=oracle.cases.find(c=>c.id===id);
 assert.deepEqual(read(path.join(dir,'input.json')),input);assert.deepEqual(read(path.join(dir,'expected.json')),expected);
 const command=['/usr/bin/python3','/home/legolas/rook2/tools/account_native.py','--engine',plan.engine.path,'--record',path.join(dir,'native.json'),'--known-single-process',...oracle.mode];
 assert.deepEqual(read(path.join(dir,'command.json')),{command,env:{ROOK2_GENERATION_SAFETY_CENSUS_PATH:path.join(dir,'census.json')},limits:plan.limits});
 assert.equal(fs.readFileSync(path.join(dir,'stdin-derived-from-released-api.txt'),'utf8'),input.protocol.recordsBeforeSearch.concat('cm_parm rnd',input.protocol.searchRecord,input.protocol.cleanupRecord).join('\n')+'\n');
 const row=read(path.join(dir,'replay.json')),stdout=fs.readFileSync(path.join(dir,'stdout')),stderr=fs.readFileSync(path.join(dir,'stderr'));
 assert(stdout.every(x=>x<128)&&stderr.every(x=>x<128));assert.equal(stdout.toString('ascii'),row.stdout);assert.equal(stderr.toString('ascii'),row.stderr);
 assert.equal(stdout.length+stderr.length,row.retainedBytes);assert(row.retainedBytes<=4194304);
 assert.equal(row.discardedObservedBytes,0);assert.equal(row.truncated,false);assert(!row.cleanupUnconfirmed);assert.equal(row.status,'pass');assert.equal(row.case,id);checkReplay(row,input,expected);rawTotal+=row.retainedBytes;
 const api=read(path.join(dir,'api-child-terminal.json'));assert.equal(api.pid,row.pid);assert.deepEqual(api.exit,{code:0,signal:null});assert(api.complete&&!api.error&&!api.cleanupUnconfirmed);
 const n=read(path.join(dir,'native.json'));assert.equal(n.failure,null);assert.equal(n.native_wait_status,0);assert.equal(n.native_exit_code,0);assert.equal(n.supervisor_pid,row.pid);
 assert.equal(n.engine_sha256_before,plan.engine.sha256);assert.equal(n.engine_sha256_after,plan.engine.sha256);
 assert.deepEqual(n.argv,[plan.engine.path,...oracle.mode]);assert.deepEqual(n.native_pre_exec.affinity,[14]);assert.deepEqual(n.native_post_exec.affinity,[14]);assert.deepEqual(n.native_post_exec.tasks,[String(n.native_pid)]);
 assert.deepEqual(n.supervisor_affinity,[0,1,2,3,4,5,8,9,10,11,12,13]);assert.equal(n.native_pre_exec.pgid,row.pid);assert.equal(n.native_post_exec.pgid,row.pid);
 assert.equal(n.total_cpu_s,n.user_cpu_s+n.system_cpu_s);assert(n.wall_ns>=0&&n.reaped_monotonic_ns>=n.start_monotonic_ns);
 const censusStat=fs.lstatSync(path.join(dir,'census.json'));assert(censusStat.isFile()&&!censusStat.isSymbolicLink()&&censusStat.size<=65536);
 const raw=fs.readFileSync(path.join(dir,'census.json'));assert(raw.length<=65536&&raw.every(x=>x<128));const c=JSON.parse(raw.toString('ascii'));
 independentCensus(c,n.native_pid);
 const summary={id,native_pid:n.native_pid,census_sha256:sha(path.join(dir,'census.json')),census_bytes:raw.length,rows:c.calls_rows};
 assert.deepEqual(read(path.join(dir,'case-summary.json')),summary);cases.push(summary);
}
assert.equal(new Set(cases.map(c=>c.native_pid)).size,2);assert(rawTotal<=8388608&&rawTotal===result.retained_protocol_bytes);assert.deepEqual(result.cases,cases);
pins(plan);
const before=read(path.join(out,'context-before.json')),after=read(path.join(out,'context-after.json'));
const ticks=c=>{const line=c.proc_stat.split('\n').find(l=>/^cpu15\s/.test(l));assert(line);return line.trim().split(/\s+/).slice(1).map(Number);};
const bt=ticks(before),at=ticks(after);assert(bt.length===at.length&&bt.length>=8);
const delta=at.map((v,i)=>v-bt[i]);assert(delta.every(v=>Number.isSafeInteger(v)&&v>=0));
const cpu15={tick_deltas:delta,idle_ticks:delta[3],iowait_ticks:delta[4],nonidle_ticks:delta[0]+delta[1]+delta[2]+delta[5]+delta[6]+delta[7],scope:'Point interval guest ticks; no continuous sibling ownership or host exclusivity proof.'};
const proof={complete:true,cases,cpu15,originalCheckReplayCount:2,engineRuns:0,protocol_bytes:rawTotal,census_body_bytes:cases.reduce((s,c)=>s+c.census_bytes,0),performance_claim:false,scope:'Two whole-process diagnostic observations only; no CPU/cost interpretation, caller attribution, optimization admission or speed prediction.'};
save(path.join(out,'independent-verification.json'),proof);
console.log(JSON.stringify({complete:true,originalCheckReplayCount:2,engineRuns:0,performance_claim:false}));
