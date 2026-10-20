// Original released assertions, offline on every comparator record and raw stream.
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync} from 'node:fs';
import {dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {checkReplay,workloads,oracle} from '/home/legolas/king-spec/conformance/profiling/replay-check.mjs';
const root=dirname(fileURLToPath(import.meta.url)),read=p=>JSON.parse(readFileSync(p));
const schedule=read(join(root,'schedule.json')),summary=read(join(root,'collection/summary.json'));
assert(summary.complete);assert.equal(summary.failure,null);assert.equal(summary.runs.length,432);let posts=0;
for(const [i,step] of schedule.entries()){
 const row=summary.runs[i];for(const [k,v] of Object.entries(step))assert.deepEqual(row[k],v);
 const actual=read(join(row.directory,'comparator.stdout')).results[0];const c=workloads.cases.find(x=>x.id===step.case),e=oracle.cases.find(x=>x.id===step.case);
 assert.equal(actual.case,step.case);assert.equal(actual.status,'pass');assert.equal(checkReplay(actual,c,e),true);
 assert.equal(checkReplay({...actual,stdout:readFileSync(join(row.directory,'wire/stdout.raw'),'utf8'),stderr:readFileSync(join(row.directory,'wire/stderr.raw'),'utf8')},c,e),true);posts+=e.posts.length;
}
const result={verified:true,engineRuns:0,lifetimes:432,originalChecks:864,semanticPosts:posts};
writeFileSync(join(root,'offline-oracle-reconciliation.json'),JSON.stringify(result,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify(result));
