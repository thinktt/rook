#!/usr/bin/env node
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {runReplay,checkReplay,workloads,oracle} from '/home/legolas/king-spec/conformance/profiling/replay-check.mjs';
import {read,save,sha,pins,census,context,H} from './common.mjs';
const plan=read(process.argv[2]);
assert(plan.launch_authorized&&plan.parent_review_complete&&plan.all_owned_jobs_closed&&plan.quiet_point_verified,'INERT: no parent activation');
assert(plan.engine.path&&plan.engine.sha256&&plan.build_receipt&&plan.actual_build_terminal&&plan.source_review&&plan.compiled_source_manifest&&plan.compiled_source_graph&&plan.schema_contract,'actual artifact/source/schema bindings pending');
assert.deepEqual(plan.cases,['profile-04','profile-35']);
assert.deepEqual(plan.limits,{setupMs:15000,searchMs:60000,cleanupMs:5000,aggregateMs:180000,byteCap:4194304,aggregateCap:8388608,censusBytes:65536});
assert.equal(process.env.TMPDIR,'/home/legolas/rook2-build-tmp');
assert.equal(fs.readFileSync('/proc/self/status','utf8').match(/^Cpus_allowed_list:\s*(.*)$/m)?.[1],H);
for(const k of ['LD_PRELOAD','LD_LIBRARY_PATH','LLVM_PROFILE_FILE','NODE_OPTIONS','ROOK2_GENERATION_SAFETY_CENSUS_PATH'])assert(!process.env[k],k);
pins(plan);assert(!fs.existsSync(plan.output));fs.mkdirSync(plan.output);save(path.join(plan.output,'plan.json'),plan);
const result={complete:false,failure:null,cases:[],engine_runs:0,performance_claim:false};
const budget={bytes:0};let deadline=null;
try{
 save(path.join(plan.output,'context-before.json'),context());
 for(const id of plan.cases){
  const dir=path.join(plan.output,id);fs.mkdirSync(dir);
  const input=workloads.cases.find(c=>c.id===id),expected=oracle.cases.find(c=>c.id===id);assert(input&&expected);
  const censusPath=path.join(dir,'census.json');assert(path.isAbsolute(censusPath)&&!fs.existsSync(censusPath));
  const command=['/usr/bin/python3','/home/legolas/rook2/tools/account_native.py','--engine',plan.engine.path,'--record',path.join(dir,'native.json'),'--known-single-process'];
  save(path.join(dir,'command.json'),{command:[...command,...oracle.mode],env:{ROOK2_GENERATION_SAFETY_CENSUS_PATH:censusPath},limits:plan.limits});
  save(path.join(dir,'input.json'),input);save(path.join(dir,'expected.json'),expected);
  fs.writeFileSync(path.join(dir,'stdin-derived-from-released-api.txt'),input.protocol.recordsBeforeSearch.concat('cm_parm rnd',input.protocol.searchRecord,input.protocol.cleanupRecord).join('\n')+'\n',{flag:'wx'});
  // This is the one whole-study clock, started immediately before the first actual runReplay call.
  deadline??=Date.now()+180000;assert(Date.now()<deadline,'whole-study deadline before case');
  process.env.ROOK2_GENERATION_SAFETY_CENSUS_PATH=censusPath;
  let row;
  try{result.engine_runs++;row=await runReplay(command,input,expected,budget,{setupMs:15000,searchMs:60000,cleanupMs:5000,byteCap:4194304,aggregateCap:8388608,deadline});}
  finally{delete process.env.ROOK2_GENERATION_SAFETY_CENSUS_PATH;}
  save(path.join(dir,'replay.json'),row);
  fs.writeFileSync(path.join(dir,'stdout'),row.stdout,{flag:'wx'});fs.writeFileSync(path.join(dir,'stderr'),row.stderr,{flag:'wx'});
  save(path.join(dir,'api-child-terminal.json'),{pid:row.pid,exit:row.exit,complete:row.complete,error:row.error,cleanupUnconfirmed:row.cleanupUnconfirmed??false});
  assert.equal(row.status,'pass');checkReplay(row,input,expected);
  assert(!row.truncated&&!row.cleanupUnconfirmed&&row.discardedObservedBytes===0);
  assert(/^[\x00-\x7f]*$/.test(row.stdout+row.stderr),'non-ASCII raw cannot be certified through API decoding');
  assert.equal(Buffer.byteLength(row.stdout)+Buffer.byteLength(row.stderr),row.retainedBytes);
  const native=read(path.join(dir,'native.json'));assert.equal(native.failure,null);assert.equal(native.native_exit_code,0);assert.equal(native.native_wait_status,0);
  assert.equal(native.supervisor_pid,row.pid);assert.equal(native.native_pre_exec.pgid,row.pid);assert.equal(native.native_post_exec.pgid,row.pid);assert.deepEqual(native.argv,[plan.engine.path,...oracle.mode]);assert.equal(native.engine_sha256_before,plan.engine.sha256);assert.equal(native.engine_sha256_after,plan.engine.sha256);
  assert.deepEqual(native.native_pre_exec.affinity,[14]);assert.deepEqual(native.native_post_exec.affinity,[14]);assert.deepEqual(native.native_post_exec.tasks,[String(native.native_pid)]);
  assert.deepEqual(native.supervisor_affinity,[0,1,2,3,4,5,8,9,10,11,12,13]);
  const stat=fs.lstatSync(censusPath);assert(stat.isFile()&&!stat.isSymbolicLink()&&stat.size<=65536);
  const raw=fs.readFileSync(censusPath),c=census(raw,native.native_pid);
  result.cases.push({id,native_pid:native.native_pid,census_sha256:sha(censusPath),census_bytes:raw.length,rows:c.calls_rows});
  save(path.join(dir,'case-summary.json'),result.cases.at(-1));pins(plan);
 }
 assert.equal(result.engine_runs,2);assert.equal(new Set(result.cases.map(c=>c.native_pid)).size,2);
 assert(budget.bytes<=8388608);save(path.join(plan.output,'context-after.json'),context());pins(plan);
 result.complete=true;
}catch(e){result.failure=String(e.stack??e);process.exitCode=1;}
finally{
 try{pins(plan);result.input_closure_after=true;}catch(e){result.complete=false;result.input_closure_after=false;result.failure??=String(e.stack??e);process.exitCode=1;}
 if(!fs.existsSync(path.join(plan.output,'context-after.json')))save(path.join(plan.output,'context-after.json'),context());
 result.retained_protocol_bytes=budget.bytes;result.study_deadline_ms=deadline;save(path.join(plan.output,'result.json'),result);
}
console.log(JSON.stringify({complete:result.complete,cases:result.cases.length,engine_runs:result.engine_runs,failure:result.failure,performance_claim:false}));
