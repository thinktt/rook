// Offline only: exactly three selected original checkReplay calls, zero engines.
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {checkReplay,workloads,oracle} from '/home/legolas/king-spec/conformance/profiling/replay-check.mjs';
const ids=['profile-01','profile-35','profile-08'];
assert.equal(process.argv.length,5);let count=0;
for(const [i,path] of process.argv.slice(2).entries()){
 const r=JSON.parse(readFileSync(path));assert.equal(r.status,'pass');
 assert.deepEqual(r.selectedCases,[ids[i]]);assert.equal(r.results.length,1);
 const row=r.results[0],c=workloads.cases.find(x=>x.id===ids[i]),e=oracle.cases.find(x=>x.id===ids[i]);
 assert.equal(row.case,ids[i]);checkReplay(row,c,e);count++;
}
assert.equal(count,3);console.log(JSON.stringify({offlineOnly:true,originalCheckReplayCount:count,selectedCases:ids}));
