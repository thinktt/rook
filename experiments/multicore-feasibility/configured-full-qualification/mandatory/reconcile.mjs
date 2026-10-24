// Offline current-inventory, exact-source and original raw protocol audit.
// Core assertions retain the earlier mandatory-completion auditor's checks;
// historical union/count literals are replaced by this fresh released inventory.
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,readdirSync,existsSync} from 'node:fs';
import {join} from 'node:path';
import {createHash} from 'node:crypto';
const B=process.argv[2],read=p=>JSON.parse(readFileSync(p));
const hash=p=>createHash('sha256').update(readFileSync(p)).digest('hex');
const plan=read(join(B,'plan.json')),selection=read(plan.selection),artifacts=read(join(B,'artifacts.json'));
assert.equal(plan.schema,'rook2-configured-full-mandatory-v1');
assert.equal(plan.sourceCommit,'66f35e440b2180d4d22c2bcd0e5a8c99c0f1185d');
assert.equal(hash(plan.ordinaryImage),plan.ordinarySha256);
assert.equal(plan.ordinarySha256,'8f26d39fd1a69bc8a3aa6da2c364b6ddb4b065bc585a27c7420ae994566f8b1b');
assert.deepEqual(plan.helperCpus,[0,1,2,3,4,5,8,9,10,11,12,13]);
assert.deepEqual(plan.quietSiblings,[7,15]);assert.equal(plan.diagnosticCpu,14);
for(const [p,h] of Object.entries(plan.pins))assert.equal(hash(p),h,p);
for(const [p,h] of Object.entries(plan.engineSource)){
 assert.equal(hash(join(plan.worktree,p)),h,p);assert.equal(hash(join(plan.engineArchive,p)),h,p);assert.equal(hash(join(plan.repo,p)),h,p);
}
for(const [p,h] of Object.entries(plan.diagnosticSource)){
 assert.equal(hash(join(plan.worktree,p)),h,p);assert.equal(hash(join(plan.repo,p)),h,p);
}
assert(readFileSync(join(plan.worktree,'diagnostic/Cargo.toml'),'utf8').includes('rook2 = { path = ".." }'));
for(const p of Object.keys(plan.diagnosticSource).filter(p=>p.endsWith('.rs'))){
 const text=readFileSync(join(plan.worktree,p),'utf8');assert(!text.includes('set_threads('));assert(!text.includes('set_threads_with_affinity('));
}
function terminal(name){
 const t=read(join(B,name,'terminal.json')),cfg=plan.stages[name],launch=read(join(B,name,'launch.json'));
 assert.equal(t.returncode,0);assert.equal(t.expectedExit,0);assert.equal(t.cleanup,null);assert.deepEqual(t.argv,cfg.argv);
 assert.equal(launch.pid,t.pid);assert.equal(launch.pgid,t.pid);assert.deepEqual(launch.argv,cfg.argv);assert.equal(launch.cwd,cfg.cwd);
 assert.deepEqual(launch.affinity,plan.helperCpus);assert(!existsSync('/proc/'+t.pid));return t;
}
for(const name of ['library_list','library_complement','diagnostic_build','diagnostic_tests','development_tests','fixtures'])terminal(name);
function lines(name){return readFileSync(join(B,name,'stdout'),'utf8');}
function testResult(name){
 const text=lines(name),matches=[...text.matchAll(/^test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored; (\d+) measured; (\d+) filtered out;/gm)];
 assert.equal(matches.length,1);const [,passed,failed,ignored,measured,filtered]=matches[0].map((v,i)=>i?Number(v):v);
 const ok=[...text.matchAll(/^test (\S+) \.\.\. ok$/gm)].map(m=>m[1]);
 const skip=[...text.matchAll(/^test (\S+) \.\.\. ignored(?:,.*)?$/gm)].map(m=>m[1]);
 assert.equal(failed,0);assert.equal(measured,0);assert.equal(ok.length,passed);assert.equal(skip.length,ignored);
 assert.equal(new Set([...ok,...skip]).size,passed+ignored);return {passed,ignored,filtered,ok,skip};
}
const fullList=[...lines('library_list').matchAll(/^(\S+): test$/gm)].map(m=>m[1]);
assert(fullList.length>0);assert.equal(new Set(fullList).size,fullList.length);
const reusedLib=[],reusedParser=[];
for(const row of plan.reusedFocused){
 const log=readFileSync(row.stdout,'utf8'),actual=[...log.matchAll(/^test (\S+) \.\.\. ok$/gm)].map(m=>m[1]);
 assert.deepEqual(actual,row.tests);assert(actual.length>0);
 const stderr=readFileSync(row.stderr,'utf8');assert(stderr.includes('('+row.executable+')'));
 if(row.kind==='library'){assert.equal(row.executable,artifacts.libraryTests.path);reusedLib.push(...actual);}
 else{assert.equal(row.kind,'ordinary-parser');reusedParser.push(...actual);}
}
assert.deepEqual(reusedLib,plan.skippedLibraryTests);assert.equal(new Set(reusedLib).size,reusedLib.length);
assert.equal(hash(artifacts.libraryTests.path),artifacts.libraryTests.sha256);
const lib=testResult('library_complement');assert.equal(lib.filtered,reusedLib.length);
assert.deepEqual([...lib.skip].sort(),[...plan.allowedIgnoredLibraryTests].sort());
assert.deepEqual([...reusedLib,...lib.ok,...lib.skip].sort(),[...fullList].sort());
assert.equal(new Set([...reusedLib,...lib.ok,...lib.skip]).size,fullList.length);
const diagnosticTests=testResult('diagnostic_tests'),developmentTests=testResult('development_tests');
assert.equal(diagnosticTests.filtered,0);assert.equal(diagnosticTests.ignored,0);
assert.equal(developmentTests.filtered,0);assert.equal(developmentTests.ignored,0);
for(const [stage,key,name] of [['diagnostic_build','diagnostic','rook2-diag'],['diagnostic_tests','diagnosticTests','rook2-diag'],['development_tests','developmentTests','rook2-dev']]){
 const records=lines(stage).split('\n').flatMap(line=>{try{return [JSON.parse(line)];}catch{return [];}});
 const selected=records.filter(r=>r.reason==='compiler-artifact'&&r.executable&&r.target.name===name);assert.equal(selected.length,1);
 const artifact=artifacts[key];assert.deepEqual(read(join(B,stage,'artifact.json')),artifact);
 assert.equal(selected[0].executable,artifact.path);assert.equal(hash(artifact.path),artifact.sha256);
 assert(artifact.path.startsWith(B+'/'));assert.equal(selected[0].target.src_path,join(plan.worktree,stage==='development_tests'?'src/bin/rook2-dev.rs':'diagnostic/src/main.rs'));
 const libraries=records.filter(r=>r.reason==='compiler-artifact'&&r.target.name==='rook2'&&r.target.kind.includes('lib'));
 assert.equal(libraries.length,1);assert.equal(libraries[0].manifest_path,join(plan.worktree,'Cargo.toml'));assert.equal(libraries[0].target.src_path,join(plan.worktree,'src/lib.rs'));
}
assert.equal(artifacts.diagnostic.path,plan.diagnosticImage);const diagnosticSha=artifacts.diagnostic.sha256;
const fixtureDir='/home/legolas/king-spec/conformance/fixtures';
const optional=new Set(['output.analysisCandidateReport','search.analysisRootSequence']);
assert.deepEqual([...optional].sort(),selection.optionalOperations);
assert.deepEqual([...selection.files,...selection.excludedOptionalFiles].map(r=>r.path).sort(),readdirSync(fixtureDir).filter(n=>n.endsWith('.json')).map(n=>join(fixtureDir,n)).sort());
const inventory=[],ids=new Set(),operations=new Set();
for(const row of selection.files){
 assert.equal(hash(row.path),row.sha256);const f=read(row.path);assert.equal(f.version,1);assert.equal(f.cases.length,row.cases);
 assert.deepEqual([...new Set(f.cases.map(c=>c.request.operation))].sort(),row.operations);
 for(const c of f.cases){assert(!ids.has(c.id));ids.add(c.id);assert(!optional.has(c.request.operation));operations.add(c.request.operation);inventory.push(c);}
}
for(const row of selection.excludedOptionalFiles){
 assert.equal(hash(row.path),row.sha256);const f=read(row.path);assert.equal(f.cases.length,row.cases);
 assert(f.cases.every(c=>optional.has(c.request.operation)));assert.deepEqual([...new Set(f.cases.map(c=>c.request.operation))].sort(),row.operations);
}
assert.equal(inventory.length,selection.mandatoryCases);assert.deepEqual([...operations].sort(),selection.mandatoryOperations);
const d=join(B,'fixtures'),report=read(join(d,'stdout')),tap=read(join(d,'tap-config.json'));
assert(report.pass);assert.equal(report.completeEngineQualification,false);assert.deepEqual(report.command,plan.launcherCommand);
assert.deepEqual(report.files,selection.files.map(f=>({path:f.path,sha256:f.sha256,count:f.cases})));
assert.equal(report.results.length,inventory.length);assert.equal(readFileSync(join(d,'stderr')).length,0);
assert.deepEqual(read(join(d,'wire/launch-count.json')),{expected:inventory.length,observed:inventory.length});
assert.equal(readdirSync(join(d,'native')).length,2*inventory.length);
assert.equal(tap.image,plan.diagnosticImage);assert.equal(tap.rawRoot,join(d,'wire'));assert.equal(tap.maxBytes,1024*1024);
assert.deepEqual(tap.expectedCalls,inventory.map(()=>plan.launcherCommand));
const pids=new Set(),missing=[];let rawBytes=0,postExec=0;
for(const [index,test] of inventory.entries()){
 const receipt=read(join(d,'wire',String(index).padStart(2,'0'),'receipt.json')),raw={};
 assert.equal(receipt.index,index);assert.equal(receipt.configSha256,hash(join(d,'tap-config.json')));
 for(const name of ['stdin','stdout','stderr']){
  const meta=receipt.raw[name],path=join(d,'wire',String(index).padStart(2,'0'),name+'.raw'),bytes=readFileSync(path);
  assert.equal(meta.path,path);assert.equal(hash(path),meta.sha256);assert.equal(bytes.length,meta.bytes);raw[name]=bytes.toString('utf8');rawBytes+=bytes.length;
 }
 assert.equal(raw.stdin,JSON.stringify(test.request)+'\n');assert.equal(raw.stderr,'');assert(raw.stdout.endsWith('\n'));
 const response=JSON.parse(raw.stdout);assert.deepEqual(Object.keys(response).sort(),['output','version']);assert.equal(response.version,1);assert.deepEqual(response.output,test.expected);
 assert.deepEqual(receipt.argv,plan.launcherCommand);assert.equal(receipt.mode,'spawnSync');assert.equal(receipt.status,0);assert.equal(receipt.signal,null);assert.equal(receipt.error,null);
 assert.equal(receipt.imageBefore,diagnosticSha);assert.equal(receipt.imageAfter,diagnosticSha);
 const n=read(join(d,'native',receipt.pid+'.json')),owned=read(join(d,'native',receipt.pid+'.owned.json'));
 assert.equal(n.supervisor_pid,receipt.pid);assert.equal(owned.supervisor_pid,receipt.pid);assert.equal(n.native_pid,owned.native_pid);assert.equal(n.native_pid,n.pre_exec.pid);assert.equal(n.native_pid,n.waited_pid);
 assert.equal(n.pre_exec.pgid,read(join(d,'terminal.json')).pid);assert.equal(owned.pgid,n.pre_exec.pgid);
 assert.deepEqual(n.supervisor_affinity,plan.helperCpus);assert.deepEqual(n.pre_exec.affinity,[14]);
 assert.equal(n.image,plan.diagnosticImage);assert.deepEqual(n.argv,[plan.diagnosticImage]);
 assert.equal(n.image_sha256_before,diagnosticSha);assert.equal(n.image_sha256_after,diagnosticSha);
 assert.equal(n.native_exit_code,0);assert.equal(n.native_signal,null);assert.equal(n.wait_status,0);assert.equal(n.exec_error,null);assert.equal(n.failure,null);assert.deepEqual(n.signals,[]);
 if(n.post_exec){postExec++;assert.equal(n.post_exec.exe,plan.diagnosticImage);assert.deepEqual(n.post_exec.argv,n.argv);assert.deepEqual(n.post_exec.affinity,[14]);assert.deepEqual(n.post_exec.tasks,[n.native_pid]);}
 else missing.push({index,id:test.id,nativePid:n.native_pid,supervisorPid:n.supervisor_pid,reason:n.post_exec_unavailable});
 assert(!pids.has(n.native_pid));pids.add(n.native_pid);assert(!existsSync('/proc/'+n.native_pid)&&!existsSync('/proc/'+n.supervisor_pid));
 const result=report.results[index];assert.equal(result.id,test.id);assert.equal(result.contract,test.contract);assert(result.pass);assert.deepEqual(result.actual,test.expected);assert.deepEqual(result.exit,{code:0,signal:null});
}
assert.equal(pids.size,inventory.length);
for(const [p,h] of Object.entries(plan.pins))assert.equal(hash(p),h,p);
assert.equal(hash(plan.diagnosticImage),diagnosticSha);
const result={schema:'rook2-configured-full-mandatory-independent-v1',pass:true,
 sourceCommit:plan.sourceCommit,engineSourceFiles:Object.keys(plan.engineSource).length,diagnosticSourceFiles:Object.keys(plan.diagnosticSource).length,
 tests:{libraryInventory:fullList.length,freshLibraryPassed:lib.passed,reusedLibraryPassed:reusedLib.length,ignoredLibrary:lib.skip,
   reusedOrdinaryParserPassed:reusedParser.length,freshDiagnostic:diagnosticTests.passed,freshDevelopment:developmentTests.passed,failures:0},
 mandatory:{files:selection.files.length,cases:inventory.length,operations:operations.size,optionalOperationsExcluded:[...optional],allCasesPass:true,singleRunAllFixtures:true},
 rawBytes,nativeExit0:inventory.length,postExecObservations:postExec,missingPostExecObservations:missing,
 diagnostic:{path:plan.diagnosticImage,sha256:diagnosticSha,configuration:'default1; no adapter helper configuration',sameEngineSourceAsOrdinary:true,ordinaryImageRebuilt:false},
 testArtifacts:artifacts,allNativeAndSupervisorPidsAbsent:true,
 recordsSha256:Object.fromEntries(['plan.json','selection.json','artifacts.json','fixtures/stdout','fixtures/tap-config.json'].map(p=>[p,hash(join(B,p))])),
 scope:'Complete current finite mandatory adapter inventory at default1, same frozen engine source and a distinct diagnostic artifact. Worker-aware source tests are separately scoped; no mode2 mandatory, source promotion, performance qualification or external acceptance claim.'};
writeFileSync(join(B,'independent-reconciliation.json'),JSON.stringify(result,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify(result));
