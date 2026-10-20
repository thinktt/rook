// Offline original checker only: imports do not run replay-check's CLI.
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {checkReplay,workloads,oracle} from '/home/legolas/king-spec/conformance/profiling/replay-check.mjs';
if(process.argv.includes('--self-test')){
 const c=workloads.cases[0],e=oracle.cases.find(x=>x.id===c.id);
 const acks=c.protocol.recordsBeforeSearch.filter(x=>x.startsWith('cm_parm ')).concat('cm_parm rnd=0');
 const lines=[...acks,...e.posts.map(p=>`${p.depth} ${p.score} ${p.workThousands} ${p.searchId} ${p.pv}`),'move '+e.move,...e.resultRecords];
 const row={error:null,complete:true,exit:e.exit,stderr:e.stderr,stdout:lines.join('\n')+'\n'};
 checkReplay(row,c,e);let rejected=0;
 for(const changed of [{complete:false},{error:'host failure'},{exit:{code:1,signal:null}},{stdout:row.stdout+'extra\n'},{stderr:'unexpected'}]){
  assert.throws(()=>checkReplay({...row,...changed},c,e));rejected++;
 }
 console.log(JSON.stringify({offlineOnly:true,accepted:1,rejected}));
}else{
 let count=0;
 for(const path of process.argv.slice(2)){
  const r=JSON.parse(readFileSync(path));assert.equal(r.status,'pass');
  assert.deepEqual(r.selectedCases,workloads.cases.map(x=>x.id));assert.equal(r.results.length,54);
  for(const [i,row] of r.results.entries()){
   const c=workloads.cases[i],e=oracle.cases.find(x=>x.id===c.id);assert.equal(row.case,c.id);checkReplay(row,c,e);count++;
  }
 }
 assert.equal(count,108);console.log(JSON.stringify({offlineOnly:true,originalCheckReplayCount:count}));
}
