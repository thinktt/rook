// Offline assertions on all70 retained native outputs; never launches an engine.
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {join} from 'node:path';
import {checkReplay,workloads,oracle} from '/home/legolas/king-spec/conformance/profiling/replay-check.mjs';
const read=path=>JSON.parse(readFileSync(path,'utf8'));
const plan=read(process.argv[2]);
let count=0;
for(const id of plan.cases) {
  const directory=join(plan.output,id);
  const manifest=read(join(directory,'manifest.json'));
  for(const [index,step] of manifest.schedule.entries()) {
    const report=read(join(directory,`${String(index).padStart(2,'0')}-${step.variant}`,'comparator.stdout'));
    assert.equal(report.status,'pass');
    assert.deepEqual(report.selectedCases,[id]);
    assert.equal(report.results.length,1);
    assert.equal(checkReplay(report.results[0],workloads.cases.find(c=>c.id===id),oracle.cases.find(c=>c.id===id)),true);
    count++;
  }
}
assert.equal(count,70);
console.log(JSON.stringify({complete:true,originalCheckReplayCount:count,engineRuns:0}));
