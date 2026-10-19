// Future offline checker only; never invokes runReplay or spawns an engine.
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {checkReplay,workloads,oracle} from '/home/legolas/king-spec/conformance/profiling/replay-check.mjs';
const out=process.argv[2];let count=0;
for(const id of ['profile-35','profile-08']){
 const r=JSON.parse(readFileSync(`${out}/${id}-oracle.stdout`));assert.equal(r.status,'pass');assert.deepEqual(r.selectedCases,[id]);assert.equal(r.results.length,1);
 const row=r.results[0],input=workloads.cases.find(x=>x.id===id),expected=oracle.cases.find(x=>x.id===id);assert(input&&expected);checkReplay(row,input,expected);
 assert.deepEqual(readFileSync(`${out}/${id}-stdout.raw`),Buffer.from(row.stdout));assert.deepEqual(readFileSync(`${out}/${id}-stderr.raw`),Buffer.from(row.stderr));count++;
}
console.log(JSON.stringify({complete:true,originalCheckReplayCount:count,engineRuns:0}));
