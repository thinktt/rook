// Original two retained-output checks only; never launches an engine.
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {join} from 'node:path';
import {checkReplay,workloads,oracle} from '/home/legolas/king-spec/conformance/profiling/replay-check.mjs';
const read=p=>JSON.parse(readFileSync(p,'utf8')),plan=read(process.argv[2]);
assert.deepEqual(plan.cases,['profile-35','profile-08']);let count=0;
for(const id of plan.cases){const report=read(join(plan.output,id,'checker.stdout'));assert.equal(report.status,'pass');assert.deepEqual(report.selectedCases,[id]);assert.equal(report.results.length,1);assert.equal(checkReplay(report.results[0],workloads.cases.find(c=>c.id===id),oracle.cases.find(c=>c.id===id)),true);count++;}
console.log(JSON.stringify({complete:true,originalCheckReplayCount:count,engineRuns:0}));
