import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {checkReplay,workloads,oracle} from './ordinary-check/profiling/replay-check.mjs';
const report=JSON.parse(readFileSync(new URL('./ordinary-check/strict54.stdout',import.meta.url)));
assert.equal(workloads.cases.length,54);assert.equal(oracle.cases.length,54);
assert.deepEqual(report.selectedCases,workloads.cases.map(c=>c.id));assert.equal(report.results.length,54);
assert.equal(new Set(report.results.map(r=>r.case)).size,54);
for(const [i,input] of workloads.cases.entries()){
 const actual=report.results[i];assert.equal(actual.case,input.id);assert.equal(actual.truncated,false);assert.equal(actual.status,'pass');
 const expected=oracle.cases.find(e=>e.id===input.id);assert(expected);checkReplay(actual,input,expected);
 const base=new URL('./ordinary-check/strict-raw/'+input.id+'/',import.meta.url);
 assert.equal(readFileSync(new URL('stdout.raw',base),'utf8'),actual.stdout);assert.equal(readFileSync(new URL('stderr.raw',base),'utf8'),actual.stderr);
 assert.deepEqual(JSON.parse(readFileSync(new URL('exit.json',base))),actual.exit);
}
console.log(JSON.stringify({pass:true,cases:54,method:'Independent saved raw/exit against frozen original checkReplay/workload/oracle; no engine execution'}));
