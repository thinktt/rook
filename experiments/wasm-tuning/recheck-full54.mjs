// Recheck saved streams only; this does not execute an engine.
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {checkReplay,workloads,oracle} from '/home/legolas/king-spec/conformance/profiling/replay-check.mjs';
const directory=process.argv[2];
const read=name=>JSON.parse(readFileSync(directory+'/'+name,'utf8'));
const summary=read('summary.json');
assert(summary.complete && !summary.failure);
const receipts={};
for(const row of summary.runs){
  const raw=readFileSync(directory+'/'+row.file);
  const actual=JSON.parse(raw);
  checkReplay(actual,workloads.cases.find(x=>x.id===row.case),oracle.cases.find(x=>x.id===row.case));
  receipts[row.file]=createHash('sha256').update(raw).digest('hex');
}
writeFileSync(directory+'/oracle-recheck.json',JSON.stringify({
  pass:true,requests:summary.runs.length,engineExecutions:0,receipts
},null,2)+'\n');
console.log(JSON.stringify({pass:true,requests:summary.runs.length,engineExecutions:0}));
