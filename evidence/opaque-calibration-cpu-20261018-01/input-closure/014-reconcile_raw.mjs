// Pure replay reconciliation only; never spawns an engine.
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {resolve} from 'node:path';
import {createHash} from 'node:crypto';
import {checkReplay,workloads,oracle} from '/home/legolas/king-spec/conformance/profiling/replay-check.mjs';
const load=p=>JSON.parse(readFileSync(p));
const sha=p=>createHash('sha256').update(readFileSync(p)).digest('hex');
const write=(p,v)=>writeFileSync(p,JSON.stringify(v,null,2)+'\n',{flag:'wx'});
function selfTest(){
 const input=workloads.cases[0],expected=oracle.cases.find(x=>x.id===input.id);
 const acknowledgments=input.protocol.recordsBeforeSearch.filter(x=>x.startsWith('cm_parm ')).concat('cm_parm rnd=0');
 const posts=expected.posts.map(p=>[p.depth,p.score,p.workThousands,p.searchId,p.pv].join(' '));
 const actual={error:null,complete:true,exit:expected.exit,stderr:expected.stderr,
  stdout:[...acknowledgments,...posts,'move '+expected.move,...expected.resultRecords].join('\n')+'\n'};
 assert.equal(checkReplay(actual,input,expected),true);
 for(const mutate of [x=>x.stderr='unexpected',x=>x.exit={code:1,signal:null},
  x=>x.stdout=x.stdout.replace('move '+expected.move,'move a1a1'),x=>x.complete=false,
  x=>x.stdout=x.stdout.replace(posts[0],posts[0].replace(String(expected.posts[0].score),'9999'))]){
  const bad=structuredClone(actual);mutate(bad);assert.throws(()=>checkReplay(bad,input,expected));
 }
 console.log(JSON.stringify({pureOfflineControl:true,nativeExecutions:0,acceptedSynthetic:1,rejectedTampered:5}));
}
if(process.argv[2]==='--self-test'){selfTest();}
else{
 const collection=resolve(process.argv[2]),output=resolve(process.argv[3]);
 const manifest=load(collection+'/manifest.json'),summary=load(collection+'/summary.json');
 for(const [name,digest]of Object.entries(manifest.input_sha256))assert.equal(sha(name),digest,'source/input pin');
 const ids=workloads.cases.map(x=>x.id);
 assert.deepEqual(ids,manifest.profile.cases);assert.equal(summary.complete,true);assert.equal(summary.failure,null);
 const schedule=ids.flatMap(id=>[0,1,2,3].map(repeat=>({case:id,repeat,warmup:repeat===0})));
 assert.deepEqual(manifest.schedule,schedule);assert.equal(summary.runs.length,216);
 mkdirSync(output);const rows=[];let posts=0;
 for(let index=0;index<schedule.length;index++){
  const step=schedule[index],directory=collection+'/'+String(index).padStart(3,'0')+'-'+step.case+'-r'+step.repeat;
  const report=load(directory+'/comparator.stdout'),native=load(directory+'/native.json'),record=summary.runs[index];
  assert.equal(readFileSync(directory+'/comparator.stderr').length,0);
  assert.equal(report.status,'pass');assert.deepEqual(report.selectedCases,[step.case]);assert.equal(report.results.length,1);
  assert.equal(report.workloadSha256,manifest.input_sha256['/home/legolas/king-spec/conformance/profiling/workloads.json']);
  assert.equal(report.oracleSha256,manifest.input_sha256['/home/legolas/king-spec/conformance/profiling/replay-oracle.json']);
  const actual=report.results[0],input=workloads.cases.find(x=>x.id===step.case),expected=oracle.cases.find(x=>x.id===step.case);
  assert.equal(actual.case,step.case);assert.equal(actual.status,'pass');assert.equal(actual.truncated,false);
  assert.equal(actual.cleanupUnconfirmed??false,false);assert.equal(actual.discardedObservedBytes,0);
  assert.equal(checkReplay(actual,input,expected),true);
  assert.equal(native.supervisor_pid,actual.pid);assert.deepEqual(actual.command,record.command.slice(record.command.indexOf('--')+1).concat(oracle.mode));
  assert.deepEqual(native.argv,[manifest.engine,...oracle.mode]);
  assert.equal(native.native_wait_status,0);assert.equal(native.native_exit_code,0);assert.equal(native.failure,null);
  assert.equal(record.actual_comparator_return_observed,true);assert.equal(record.comparator_exit,0);assert.equal(record.failure,null);
  assert.equal(record.native_receipt_sha256,sha(directory+'/native.json'));assert.equal(record.comparator_sha256,sha(directory+'/comparator.stdout'));
  const retained=output+'/'+String(index).padStart(3,'0');mkdirSync(retained);
  write(retained+'/expected.json',expected);write(retained+'/actual-replay.json',actual);
  posts+=expected.posts.length;rows.push({...step,checkReplay:true,nativeExit:0,wrapperExit:actual.exit,comparatorExit:record.comparator_exit,
   expectedSha256:sha(retained+'/expected.json'),actualReplaySha256:sha(retained+'/actual-replay.json'),nativeReceiptSha256:sha(directory+'/native.json')});
 }
 assert.equal(posts,2496);write(output+'/verification.json',{complete:true,lifetimes:216,warmups:54,measured:162,posts,
  checkReplay:'original released function called independently for every raw actual row',engineExecutions:0,rows});
 console.log(JSON.stringify({complete:true,lifetimes:216,posts,engineExecutions:0}));
}
