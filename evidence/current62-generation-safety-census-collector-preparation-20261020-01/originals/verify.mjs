#!/usr/bin/env node
// Offline only. Re-read original raw rows and original released oracle; no engine launch.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {checkReplay,workloads,oracle} from '/home/legolas/king-spec/conformance/profiling/replay-check.mjs';
import {read,save,sha,pins} from './common.mjs';
const plan=read(process.argv[2]),out=plan.output;
pins(plan);assert.deepEqual(read(path.join(out,'plan.json')),plan);
const terminal=read(path.join(out,'tool-terminal.json'));
assert(terminal.actual_tool_terminal_observed&&terminal.exit_code===0);
const result=read(path.join(out,'result.json'));
assert(result.complete&&result.failure===null&&result.engine_runs===2&&result.input_closure_after===true);
const cases=[];let rawTotal=0;
for(const id of ['profile-01','profile-35']){
 const dir=path.join(out,id),input=workloads.cases.find(c=>c.id===id),expected=oracle.cases.find(c=>c.id===id);
 assert.deepEqual(read(path.join(dir,'input.json')),input);assert.deepEqual(read(path.join(dir,'expected.json')),expected);
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
 const raw=fs.readFileSync(path.join(dir,'census.json'));assert(raw.length<=4096);const c=JSON.parse(raw.toString('utf8'));
 const fields=['epoch_allocations','full_calls','first_no_snapshot','first_new_epoch','exact_repeat','changed_input','equal_input_different_output','total_activity_r','exact_repeat_activity_r'];
 assert.deepEqual(Object.keys(c).sort(),['schema','pid','complete','overflow',...fields].sort());
 assert.equal(c.schema,'rook2-activity-repeat-census-v1');assert.equal(c.pid,n.native_pid);assert.equal(c.complete,true);assert.equal(c.overflow,false);
 for(const k of fields)assert(Number.isSafeInteger(c[k])&&c[k]>=0);
 let partition=0n;for(const k of ['first_no_snapshot','first_new_epoch','exact_repeat','changed_input','equal_input_different_output'])partition+=BigInt(c[k]);
 assert.equal(partition,BigInt(c.full_calls));assert.equal(c.equal_input_different_output,0);assert(c.epoch_allocations>0&&c.full_calls>0&&c.exact_repeat_activity_r<=c.total_activity_r);
 const share=c.full_calls?c.exact_repeat/c.full_calls:null;
 const summary={id,native_pid:n.native_pid,census_sha256:sha(path.join(dir,'census.json')),census_bytes:raw.length,full_calls:c.full_calls,exact_repeat:c.exact_repeat,exact_repeat_share:share,consider_design_only:share!==null&&share>=.05};
 assert.deepEqual(read(path.join(dir,'case-summary.json')),summary);cases.push(summary);
}
assert.equal(new Set(cases.map(c=>c.native_pid)).size,2);assert(rawTotal<=8388608&&rawTotal===result.retained_protocol_bytes);assert.deepEqual(result.cases,cases);
pins(plan);
const before=read(path.join(out,'context-before.json')),after=read(path.join(out,'context-after.json'));
const ticks=c=>{const line=c.proc_stat.split('\n').find(l=>/^cpu15\s/.test(l));assert(line);return line.trim().split(/\s+/).slice(1).map(Number);};
const bt=ticks(before),at=ticks(after);assert(bt.length===at.length&&bt.length>=8);
const delta=at.map((v,i)=>v-bt[i]);assert(delta.every(v=>Number.isSafeInteger(v)&&v>=0));
const cpu15={tick_deltas:delta,idle_ticks:delta[3],iowait_ticks:delta[4],nonidle_ticks:delta[0]+delta[1]+delta[2]+delta[5]+delta[6]+delta[7],scope:'Point interval guest ticks; no continuous sibling ownership or host exclusivity proof.'};
const proof={complete:true,cases,cpu15,originalCheckReplayCount:2,engineRuns:0,protocol_bytes:rawTotal,census_body_bytes:cases.reduce((s,c)=>s+c.census_bytes,0),consider_design_only:cases.some(c=>c.consider_design_only),performance_claim:false,scope:'Two diagnostic observations only; threshold is a design-consideration trigger, never cache adoption or speed prediction.'};
save(path.join(out,'independent-verification.json'),proof);
console.log(JSON.stringify({complete:true,originalCheckReplayCount:2,engineRuns:0,consider_design_only:proof.consider_design_only,performance_claim:false}));
