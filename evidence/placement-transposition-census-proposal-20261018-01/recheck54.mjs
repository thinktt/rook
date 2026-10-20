// Offline original oracle over retained comparator reports only; no runReplay/spawn.
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {checkReplay,workloads,oracle} from '/home/legolas/king-spec/conformance/profiling/replay-check.mjs';
const base=process.argv[2];assert(base);let count=0;
for(const input of workloads.cases){
 const r=JSON.parse(readFileSync(base+'/'+input.id+'/comparator.stdout'));
 assert.equal(r.status,'pass');assert.deepEqual(r.selectedCases,[input.id]);assert.equal(r.results.length,1);
 const row=r.results[0],answer=oracle.cases.find(x=>x.id===input.id);assert.equal(row.case,input.id);assert.equal(row.complete,true);assert.equal(row.truncated,false);assert.equal(row.discardedObservedBytes,0);assert(!row.cleanupUnconfirmed);
 assert.equal(checkReplay(row,input,answer),true);count++;
}
assert.equal(count,54);console.log(JSON.stringify({complete:true,original_oracle_calls:count,new_native_runs:0}));
