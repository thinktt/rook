// Independent offline fixture/raw/source reconciliation, no child process imports.
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,readdirSync,existsSync} from 'node:fs';
import {join} from 'node:path';
import {createHash} from 'node:crypto';
const B=process.argv[2];const read=p=>JSON.parse(readFileSync(p));
const hash=p=>createHash('sha256').update(readFileSync(p)).digest('hex');
const plan=read(join(B,'plan.json')), selection=read(plan.selection), h=plan.helperCpus;
for(const [p,sha] of Object.entries(plan.pins))assert.equal(hash(p),sha,p);
for(const variant of ['control','candidate']){
 const snapshot=read(join(B,variant+'-source-map.json'));
 for(const [name,sha] of Object.entries(snapshot.files))assert.equal(hash(join(B,variant,name)),sha);
}
for(const [name,sha] of Object.entries(read(join(B,'retained-base-map.json')).files))assert.equal(hash(join(plan.repo,name)),sha);
assert.equal(hash(plan.retainedOrdinaryImage),plan.retainedOrdinarySha256);
const negative=read(join(B,'control-tests','terminal.json')),full=read(join(B,'candidate-tests','terminal.json'));
assert.equal(negative.returncode,101);assert.equal(full.returncode,0);
const old=readFileSync(join(B,'control-tests','stdout'),'utf8'), candidate=readFileSync(join(B,'candidate-tests','stdout'),'utf8');
const names=['first_main_equal_score_stops_before_eligible_tail','first_main_below_equal_window_still_enters_tail','first_main_strict_window_upper_hit_preserves_cutoff'];
assert(old.includes('test ordinary::first_main_tests::'+names[0]+' ... FAILED'));
for(const name of names.slice(1))assert(old.includes('test ordinary::first_main_tests::'+name+' ... ok'));
assert(old.includes('Err(InternalIterativeOrdering)')&&old.includes('Ok(0)')&&old.includes('2 passed; 1 failed; 0 ignored'));
for(const name of names)assert(candidate.includes('test ordinary::first_main_tests::'+name+' ... ok'));
const summary=/test result: ok\. (\d+) passed; 0 failed; 0 ignored;/.exec(candidate);assert(summary);
const artifacts=read(join(B,'artifacts.json'));assert.equal(hash(artifacts.diagnostic.path),artifacts.diagnostic.sha256);
for(const v of ['controlTests','candidateTests'])assert.equal(hash(artifacts[v].path),artifacts[v].sha256);
const rows=selection.files.flatMap(file=>{
 assert.equal(hash(file.path),file.sha256);const f=read(file.path);assert.equal(f.cases.length,file.cases);return f.cases;
});assert.equal(rows.length,selection.caseCount);
const d=join(B,'fixtures'), report=read(join(d,'stdout'));
assert.equal(report.pass,true);assert.equal(report.completeEngineQualification,false);assert.deepEqual(report.command,plan.launcherCommand);
assert.deepEqual(report.files,selection.files.map(f=>({path:f.path,sha256:f.sha256,count:f.cases})));
assert.equal(report.results.length,rows.length);
assert.deepEqual(read(join(d,'wire','launch-count.json')),{expected:rows.length,observed:rows.length});
assert.equal(readdirSync(join(d,'native')).length,2*rows.length);
assert.equal(read(join(d,'terminal.json')).returncode,0);
assert.equal(readFileSync(join(d,'stderr')).length,0);
let totalBytes=0,postExec=0;const pids=new Set();const nativeIndex=[];
for(const [index,test] of rows.entries()){
 const rd=join(d,'wire',String(index).padStart(2,'0')), receipt=read(join(rd,'receipt.json'));
 const raw={};for(const n of ['stdin','stdout','stderr']){
  const meta=receipt.raw[n],bytes=readFileSync(meta.path);assert.equal(hash(meta.path),meta.sha256);assert.equal(bytes.length,meta.bytes);
  raw[n]=bytes.toString('utf8');totalBytes+=bytes.length;
 }
 assert.equal(raw.stdin,JSON.stringify(test.request)+'\n');assert.equal(raw.stderr,'');
 const response=JSON.parse(raw.stdout);assert(raw.stdout.endsWith('\n'));
 assert.deepEqual(Object.keys(response).sort(),['output','version']);assert.equal(response.version,1);assert.deepEqual(response.output,test.expected);
 assert.deepEqual(receipt.argv,plan.launcherCommand);assert.equal(receipt.mode,'spawnSync');
 assert.equal(receipt.status,0);assert.equal(receipt.signal,null);assert.equal(receipt.error,null);
 assert.equal(receipt.imageBefore,artifacts.diagnostic.sha256);assert.equal(receipt.imageAfter,artifacts.diagnostic.sha256);
 const native=read(join(d,'native',receipt.pid+'.json')),owned=read(join(d,'native',receipt.pid+'.owned.json'));
 assert.equal(native.supervisor_pid,receipt.pid);assert.equal(owned.supervisor_pid,receipt.pid);
 assert.equal(native.native_pid,owned.native_pid);assert.equal(native.native_pid,native.waited_pid);assert.equal(native.native_pid,native.pre_exec.pid);
 assert.equal(owned.pgid,read(join(d,'terminal.json')).pid);assert.equal(native.pre_exec.pgid,owned.pgid);
 assert.deepEqual(native.supervisor_affinity,h);assert.deepEqual(native.pre_exec.affinity,[14]);
 assert.equal(native.image,artifacts.diagnostic.path);assert.deepEqual(native.argv,[artifacts.diagnostic.path]);
 assert.equal(native.image_sha256_before,artifacts.diagnostic.sha256);assert.equal(native.image_sha256_after,artifacts.diagnostic.sha256);
 assert.equal(native.native_exit_code,0);assert.equal(native.native_signal,null);assert.equal(native.wait_status,0);
 assert.equal(native.exec_error,null);assert.equal(native.failure,null);assert.deepEqual(native.signals,[]);
 if(native.post_exec){postExec++;assert.equal(native.post_exec.exe,artifacts.diagnostic.path);assert.deepEqual(native.post_exec.argv,native.argv);assert.deepEqual(native.post_exec.affinity,[14]);assert.deepEqual(native.post_exec.tasks,[native.native_pid]);}
 assert(!pids.has(native.native_pid));pids.add(native.native_pid);
 assert(!existsSync('/proc/'+native.native_pid)&&!existsSync('/proc/'+native.supervisor_pid));
 const result=report.results[index];assert.equal(result.id,test.id);assert.equal(result.contract,test.contract);assert.equal(result.pass,true);assert.deepEqual(result.exit,{code:0,signal:null});assert.deepEqual(result.actual,test.expected);
 nativeIndex.push({index,id:test.id,operation:test.request.operation,supervisorPid:receipt.pid,nativePid:native.native_pid,postExecObserved:!!native.post_exec});
}
for(const [p,sha] of Object.entries(plan.pins))assert.equal(hash(p),sha,p);
const result={schema:'rook2-first-main-correction-independent-v1',pass:true,
 negativeControl:{unchangedProduction:true,tests:3,expectedEqualityFailure:1,discriminatingControlsPass:2,reason:'Expected Err(InternalIterativeOrdering) instead of Ok(0): old equality continuation enters disabled-IIO tail'},
 candidate:{conditionalRegressions:3,fullNativeLibraryTests:Number(summary[1]),failures:0,ignored:0},
 focusedMandatory:{files:selection.fileCount,cases:rows.length,operations:selection.operationCount,allCasesPass:true,rawBytes:totalBytes,nativeLifetimes:pids.size,nativeExit0:pids.size,postExecObservations:postExec},
 artifacts,allNativeAndSupervisorPidsAbsent:true,retainedCanonical117FilesUnchanged:true,
 scope:'Conditional internal contexts, not admitted public/native witnesses. No timing, PGO, ordinary image build, promotion, full54/full12 or artifact-wide qualification.'};
writeFileSync(join(B,'independent-reconciliation.json'),JSON.stringify(result,null,2)+'\n',{flag:'wx'});
writeFileSync(join(B,'fixture-native-index.json'),JSON.stringify(nativeIndex,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify(result));
