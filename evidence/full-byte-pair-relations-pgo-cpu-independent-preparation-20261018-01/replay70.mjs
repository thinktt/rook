// Original oracle over existing records only; never calls runReplay/spawn.
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync} from 'node:fs';
import {checkReplay,workloads,oracle} from '/home/legolas/king-spec/conformance/profiling/replay-check.mjs';
const base='/home/legolas/rook2/evidence/full-byte-pair-relations-pgo-cpu-pilot-20261018-01';
const plan=JSON.parse(readFileSync(base+'/plan.json'));
assert.deepEqual(plan.cases,['profile-01','profile-02','profile-04','profile-05','profile-29','profile-35','profile-08']);
const checks=[];
for(const caseId of plan.cases){
 const summary=JSON.parse(readFileSync(base+'/'+caseId+'/summary.json'));
 const input=workloads.cases.find(x=>x.id===caseId),expected=oracle.cases.find(x=>x.id===caseId);
 assert(input&&expected);assert.equal(summary.runs.length,10);
 for(const [index,step] of summary.runs.entries()){
  const dir=base+'/'+caseId+'/'+String(index).padStart(2,'0')+'-'+step.variant;
  const report=JSON.parse(readFileSync(dir+'/comparator.stdout'));
  assert.deepEqual(report.selectedCases,[caseId]);assert.equal(report.results.length,1);assert.equal(report.status,'pass');
  const row=report.results[0];assert.equal(row.case,caseId);assert.equal(row.status,'pass');
  assert.deepEqual(row.command,[...step.command.slice(step.command.indexOf('--')+1),...oracle.mode]);
  assert.equal(row.truncated,false);assert.equal(row.discardedObservedBytes,0);assert(!row.cleanupUnconfirmed);
  assert.equal(row.retainedBytes,Buffer.byteLength(row.stdout)+Buffer.byteLength(row.stderr));
  assert(Buffer.from(row.stdout+row.stderr).every(x=>x<128));
  assert.equal(checkReplay(row,input,expected),true);
  checks.push({case:caseId,index,variant:step.variant,warmup:step.warmup,pid:row.pid,exit:row.exit,stdoutBytes:Buffer.byteLength(row.stdout),stderrBytes:Buffer.byteLength(row.stderr)});
 }
}
assert.equal(checks.length,70);assert.equal(checks.filter(x=>x.warmup).length,14);assert.equal(checks.filter(x=>!x.warmup).length,56);
writeFileSync(new URL('./original-checkReplay70-result.json',import.meta.url),JSON.stringify({complete:true,original_oracle_calls:70,new_engine_runs:0,checks},null,2)+String.fromCharCode(10),{flag:'wx'});
console.log(JSON.stringify({complete:true,original_oracle_calls:70,new_engine_runs:0}));
