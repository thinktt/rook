import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {join} from 'node:path';
import {checkReplay,workloads,oracle} from '/home/legolas/king-spec/conformance/profiling/replay-check.mjs';
const read=p=>JSON.parse(readFileSync(p,'utf8'));
let count=0;
for(const id of ['profile-35','profile-08']) {
  const report=read(join(process.argv[2],id,'comparator.stdout'));
  assert.equal(report.status,'pass');
  assert.deepEqual(report.selectedCases,[id]);
  assert.equal(report.results.length,1);
  assert.equal(checkReplay(report.results[0],workloads.cases.find(c=>c.id===id),oracle.cases.find(c=>c.id===id)),true);
  count++;
}
console.log(JSON.stringify({originalCheckReplayCount:count,engineRuns:0}));
