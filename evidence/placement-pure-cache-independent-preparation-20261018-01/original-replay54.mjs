// Offline only: imports the released semantic oracle, never runReplay.
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync} from 'node:fs';
import {checkReplay,workloads,oracle} from '/home/legolas/king-spec/conformance/profiling/replay-check.mjs';
const base='/home/legolas/rook2/evidence/placement-pure-cache-regression-20261018-01';
const image='/home/legolas/rook2/evidence/placement-pure-cache-generic-build-20261018-01/rook2-exact';
const report=JSON.parse(readFileSync(base+'/strict54.stdout'));
assert.equal(workloads.cases.length,54);assert.equal(oracle.cases.length,54);
assert.deepEqual(report.selectedCases,workloads.cases.map(x=>x.id));
assert.equal(report.results.length,54);assert.equal(report.status,'pass');
const checked=[],pids=new Set();
for(const [index,input] of workloads.cases.entries()){
 const row=report.results[index],expected=oracle.cases.find(x=>x.id===input.id);
 assert(expected);assert.equal(row.case,input.id);assert.equal(row.status,'pass');
 assert.deepEqual(row.command,[image,...oracle.mode]);
 assert(Number.isSafeInteger(row.pid)&&row.pid>0);assert(!pids.has(row.pid));pids.add(row.pid);
 assert.equal(row.truncated,false);assert.equal(row.discardedObservedBytes,0);assert(!row.cleanupUnconfirmed);
 assert.equal(row.retainedBytes,Buffer.byteLength(row.stdout)+Buffer.byteLength(row.stderr));
 assert([...Buffer.from(row.stdout+row.stderr)].every(x=>x<128));
 assert.equal(checkReplay(row,input,expected),true);
 checked.push({id:input.id,pid:row.pid,exit:row.exit,stdoutBytes:Buffer.byteLength(row.stdout),stderrBytes:Buffer.byteLength(row.stderr)});
}
const output={complete:true,original_checkReplay_calls:54,engine_runs:0,checked,
 scope:'Original stored54 native stdout/stderr/exit/argv records rechecked through released checkReplay; input bytes are bound runner/workloads, not a separately retained strict stdin stream.'};
writeFileSync(new URL('./original-replay54-result.json',import.meta.url),JSON.stringify(output,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({complete:true,cases:54,engine_runs:0}));
