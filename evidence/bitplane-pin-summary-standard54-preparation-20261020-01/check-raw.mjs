// Offline replay of recorded streams through the unchanged released assertions.
// This program launches no engine.
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {dirname,join} from 'node:path';
import {checkReplay,workloads,oracle} from '/home/legolas/king-spec/conformance/profiling/replay-check.mjs';

const root=dirname(fileURLToPath(import.meta.url));
const read=path=>JSON.parse(readFileSync(path,'utf8'));
const manifest=read(join(root,'collection/manifest.json'));
const summary=read(join(root,'collection/summary.json'));
assert.equal(summary.complete,true);
assert.equal(summary.failure,null);
assert.equal(manifest.schedule.length,216);
const results=[];
for(const [index,step] of manifest.schedule.entries()) {
  const directory=join(root,'collection',`${String(index).padStart(3,'0')}-${step.case}-r${step.repeat}`);
  const actual=read(join(directory,'comparator.stdout')).results[0];
  const input=workloads.cases.find(c=>c.id===step.case);
  const expected=oracle.cases.find(c=>c.id===step.case);
  assert.equal(actual.status,'pass');
  assert.equal(actual.case,step.case);
  assert.equal(checkReplay(actual,input,expected),true);
  const raw={...actual,stdout:readFileSync(join(directory,'wire/stdout.raw'),'utf8'),
    stderr:readFileSync(join(directory,'wire/stderr.raw'),'utf8')};
  assert.equal(checkReplay(raw,input,expected),true);
  results.push({...step,posts:expected.posts.length,move:expected.move});
}
const result={verified:true,engineRuns:0,recordedLifetimes:results.length,
  strictChecks:results.length*2,semanticPosts:results.reduce((n,r)=>n+r.posts,0),
  results,scope:'Offline released checkReplay on each comparator record and each independently captured output stream.'};
writeFileSync(join(root,'offline-oracle-reconciliation.json'),JSON.stringify(result,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({...result,results:undefined}));
