// Offline exact-source/image/fixture union and raw protocol reconciliation.
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,readdirSync,existsSync} from 'node:fs';
import {join} from 'node:path';
import {createHash} from 'node:crypto';
const B=process.argv[2],read=p=>JSON.parse(readFileSync(p));
const hash=p=>createHash('sha256').update(readFileSync(p)).digest('hex');
const plan=read(join(B,'plan.json')),selection=read(plan.selection),O=plan.priorRawRoot;
for(const [p,h] of Object.entries(plan.pins))assert.equal(hash(p),h,p);
for(const [p,h] of Object.entries(read(join(O,'plan.json')).pins))assert.equal(hash(p),h,p);
for(const [p,h] of Object.entries(read(plan.candidateSourceMap).files))assert.equal(hash(join(plan.worktree,p)),h,p);
for(const [p,h] of Object.entries(read(join(O,'retained-base-map.json')).files))assert.equal(hash(join(plan.repo,p)),h,p);
assert.equal(hash(plan.diagnosticImage),plan.diagnosticSha256);
assert.equal(hash(plan.retainedOrdinaryImage),plan.retainedOrdinarySha256);
const priorResult=read(plan.priorResult),priorRecon=read(join(O,'independent-reconciliation.json'));
assert(priorRecon.pass);assert.equal(priorRecon.candidate.fullNativeLibraryTests,196);
assert.equal(hash(join(O,'independent-reconciliation.json')),priorResult.records['independent-reconciliation.json'].sha256);
assert.equal(hash(join(O,'fixtures/stdout')),priorResult.stages.fixtures.stdout.sha256);
assert.equal(priorRecon.artifacts.diagnostic.sha256,plan.diagnosticSha256);
assert.equal(hash(priorRecon.artifacts.candidateTests.path),priorRecon.artifacts.candidateTests.sha256);
assert.equal(read(join(O,'candidate-tests/terminal.json')).returncode,0);
assert(readFileSync(join(O,'candidate-tests/stdout'),'utf8').includes('196 passed; 0 failed; 0 ignored'));
const tests=read(join(B,'test-artifacts.json'));
for(const [name,count,key] of [['diagnostic-tests',209,'diagnosticTests'],['development-tests',2,'developmentTests']]){
 assert.equal(read(join(B,name,'terminal.json')).returncode,0);
 assert(readFileSync(join(B,name,'stdout'),'utf8').includes(`${count} passed; 0 failed; 0 ignored`));
 assert.equal(hash(tests[key].path),tests[key].sha256);
}
const optional=new Set(['output.analysisCandidateReport','search.analysisRootSequence']);
const expectedFiles=new Map();let mandatoryCases=0;const mandatoryOps=new Set(),inventoryIds=new Set();
for(const row of selection.mandatoryInventory){
 assert.equal(hash(row.path),row.sha256);const f=read(row.path);assert.equal(f.cases.length,row.cases);
 assert(!expectedFiles.has(row.path));expectedFiles.set(row.path,row);
 for(const c of f.cases){assert(!inventoryIds.has(c.id));inventoryIds.add(c.id);assert(!optional.has(c.request.operation));mandatoryOps.add(c.request.operation);mandatoryCases++;}
}
assert.equal(expectedFiles.size,115);assert.equal(mandatoryCases,7673);assert.equal(mandatoryOps.size,117);
assert.deepEqual([...selection.mandatoryInventory,...selection.excludedOptionalFiles].map(r=>r.path).sort(),readdirSync('/home/legolas/king-spec/conformance/fixtures').filter(n=>n.endsWith('.json')).map(n=>'/home/legolas/king-spec/conformance/fixtures/'+n).sort());
assert.equal(selection.excludedOptionalFiles.length,2);
for(const row of selection.excludedOptionalFiles){assert.equal(hash(row.path),row.sha256);assert(row.operations.every(op=>optional.has(op)));}
const fixtureIds=new Set(),covered=new Set(),pids=new Set();let rawBytes=0,postExec=0;const groups=[],missing=[];
for(const [root,files,expectedCases,fresh] of [[O,read(selection.reuse.selection).files,1008,false],[B,selection.files,6665,true]]){
 const d=join(root,'fixtures'),report=read(join(d,'stdout'));
 assert(report.pass);assert.equal(report.completeEngineQualification,false);assert.deepEqual(report.command,plan.launcherCommand);
 assert.deepEqual(report.files,files.map(f=>({path:f.path,sha256:f.sha256,count:f.cases})));
 assert.equal(read(join(d,'terminal.json')).returncode,0);assert.equal(readFileSync(join(d,'stderr')).length,0);
 const cases=files.flatMap(file=>{
  assert.deepEqual(file,expectedFiles.get(file.path));assert(!covered.has(file.path));covered.add(file.path);
  const f=read(file.path);return f.cases;
 });assert.equal(cases.length,expectedCases);assert.equal(report.results.length,expectedCases);
 assert.deepEqual(read(join(d,'wire/launch-count.json')),{expected:expectedCases,observed:expectedCases});
 assert.equal(readdirSync(join(d,'native')).length,2*expectedCases);
 let groupBytes=0,groupPost=0;
 for(const [index,test] of cases.entries()){
  assert(!fixtureIds.has(test.id));fixtureIds.add(test.id);
  const receipt=read(join(d,'wire',String(index).padStart(2,'0'),'receipt.json')),raw={};
  for(const name of ['stdin','stdout','stderr']){const meta=receipt.raw[name],bytes=readFileSync(meta.path);assert.equal(hash(meta.path),meta.sha256);assert.equal(bytes.length,meta.bytes);raw[name]=bytes.toString('utf8');groupBytes+=bytes.length;}
  assert.equal(raw.stdin,JSON.stringify(test.request)+'\n');assert.equal(raw.stderr,'');assert(raw.stdout.endsWith('\n'));
  const response=JSON.parse(raw.stdout);assert.deepEqual(Object.keys(response).sort(),['output','version']);assert.equal(response.version,1);assert.deepEqual(response.output,test.expected);
  assert.deepEqual(receipt.argv,plan.launcherCommand);assert.equal(receipt.status,0);assert.equal(receipt.signal,null);assert.equal(receipt.error,null);
  assert.equal(receipt.imageBefore,plan.diagnosticSha256);assert.equal(receipt.imageAfter,plan.diagnosticSha256);
  const n=read(join(d,'native',receipt.pid+'.json')),owned=read(join(d,'native',receipt.pid+'.owned.json'));
  assert.equal(n.supervisor_pid,receipt.pid);assert.equal(owned.supervisor_pid,receipt.pid);assert.equal(n.native_pid,owned.native_pid);assert.equal(n.native_pid,n.pre_exec.pid);assert.equal(n.native_pid,n.waited_pid);
  assert.equal(n.pre_exec.pgid,read(join(d,'terminal.json')).pid);assert.equal(owned.pgid,n.pre_exec.pgid);
  assert.deepEqual(n.supervisor_affinity,plan.helperCpus);assert.deepEqual(n.pre_exec.affinity,[14]);
  assert.equal(n.image,plan.diagnosticImage);assert.deepEqual(n.argv,[plan.diagnosticImage]);
  assert.equal(n.image_sha256_before,plan.diagnosticSha256);assert.equal(n.image_sha256_after,plan.diagnosticSha256);
  assert.equal(n.native_exit_code,0);assert.equal(n.native_signal,null);assert.equal(n.wait_status,0);assert.equal(n.exec_error,null);assert.equal(n.failure,null);assert.deepEqual(n.signals,[]);
  if(n.post_exec){groupPost++;assert.equal(n.post_exec.exe,plan.diagnosticImage);assert.deepEqual(n.post_exec.argv,n.argv);assert.deepEqual(n.post_exec.affinity,[14]);assert.deepEqual(n.post_exec.tasks,[n.native_pid]);}
  else missing.push({fresh,index,id:test.id,nativePid:n.native_pid,supervisorPid:n.supervisor_pid,reason:n.post_exec_unavailable});
  assert(!pids.has(n.native_pid));pids.add(n.native_pid);assert(!existsSync('/proc/'+n.native_pid)&&!existsSync('/proc/'+n.supervisor_pid));
  const r=report.results[index];assert.equal(r.id,test.id);assert.equal(r.contract,test.contract);assert(r.pass);assert.deepEqual(r.actual,test.expected);assert.deepEqual(r.exit,{code:0,signal:null});
 }
 rawBytes+=groupBytes;postExec+=groupPost;groups.push({fresh,files:files.length,cases:cases.length,rawBytes:groupBytes,nativeExit0:cases.length,postExecObservations:groupPost,report:join(d,'stdout'),reportSha256:hash(join(d,'stdout'))});
}
assert.equal(covered.size,115);assert.equal(fixtureIds.size,7673);assert.equal(pids.size,7673);
for(const p of expectedFiles.keys())assert(covered.has(p));for(const id of inventoryIds)assert(fixtureIds.has(id));
for(const [p,h] of Object.entries(plan.pins))assert.equal(hash(p),h,p);
assert.equal(hash(plan.diagnosticImage),plan.diagnosticSha256);
const result={schema:'rook2-first-main-mandatory-independent-v1',pass:true,
 tests:{reusedNativeLibrary:196,freshDiagnostic:209,freshDevelopment:2,failures:0,ignored:0},
 mandatoryUnion:{files:115,cases:7673,operations:117,optionalOperationsExcluded:[...optional],allCasesPass:true,reportCount:2,singleRunAllFixtures:false},
 groups,rawBytes,nativeExit0:7673,postExecObservations:postExec,missingPostExecObservations:missing,
 diagnostic:{path:plan.diagnosticImage,sha256:plan.diagnosticSha256,unchangedSinceFirstLane:true,rebuilt:false},
 testArtifacts:tests,allNativeAndSupervisorPidsAbsent:true,canonical117FilesUnchanged:true,candidateSource118FilesUnchanged:true,
 scope:'Complete finite mandatory adapter coverage across two preserved reports on one exact isolated diagnostic image/source. No production promotion, native equality witness, gameplay/performance qualification or specification-owner acceptance.'};
writeFileSync(join(B,'independent-reconciliation.json'),JSON.stringify(result,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify(result));
