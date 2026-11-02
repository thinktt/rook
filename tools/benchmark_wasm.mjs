#!/usr/bin/env node
// Matched released54 search windows; no engine implementation or timing oracle.
import assert from 'node:assert/strict';
import { spawn, execFileSync } from 'node:child_process';
import { readFileSync, writeFileSync, mkdirSync, readdirSync, createWriteStream, statSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { createInterface } from 'node:readline';
import { once } from 'node:events';
import { resolve, dirname } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { performance } from 'node:perf_hooks';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const args = process.argv.slice(2), options = {};
for (let i = 0; i < args.length; i += 2) { assert(args[i].startsWith('--') && args[i+1]); options[args[i].slice(2)] = args[i+1]; }
for (const key of ['output','native','clock','playwright','chromium']) assert(options[key], `--${key} required`);
const output = resolve(options.output), cpu = Number(options.cpu ?? 14), repeats = Number(options.repeats ?? 3);
assert(Number.isInteger(cpu) && cpu >= 0 && Number.isInteger(repeats) && repeats > 0);
mkdirSync(output);
const spec = resolve(options.spec ?? '/home/legolas/king-spec/conformance/profiling');
const { workloads, oracle, checkReplay } = await import(pathToFileURL(spec+'/replay-check.mjs'));
const { chromium } = await import(pathToFileURL(resolve(options.playwright)));
const cases = workloads.cases.filter(c => !options.case || c.id === options.case);
assert(cases.length);
const sha = path => createHash('sha256').update(readFileSync(path)).digest('hex');
const save = (path, value) => writeFileSync(path, JSON.stringify(value, null, 2)+'\n');
const snapshots = pid => readdirSync(`/proc/${pid}/task`).map(tid => {
  const status = readFileSync(`/proc/${pid}/task/${tid}/status`, 'utf8');
  return { tid: Number(tid), name: readFileSync(`/proc/${pid}/task/${tid}/comm`, 'utf8').trim(), cpus: status.match(/^Cpus_allowed_list:\s*(.*)$/m)[1] };
});
const placement = pid => { const tasks = snapshots(pid); assert(tasks.length && tasks.every(t => t.cpus === String(cpu)), 'engine thread escaped CPU'); return tasks; };
const owned = new Set();
function launch(command, argv, extra = {}) {
  const child = spawn(command, argv, { detached: true, stdio: ['pipe','pipe','pipe'], ...extra });
  owned.add(child);
  child.on('close', () => owned.delete(child));
  return child;
}
const kill = child => { try { process.kill(-child.pid, 'SIGKILL'); } catch {} };
const clock = launch(resolve(options.clock), []);
const clockWaiters = [];
createInterface({ input: clock.stdout }).on('line', line => clockWaiters.shift().resolve(JSON.parse(line)));
clock.on('exit', () => { for (const waiter of clockWaiters.splice(0)) waiter.reject(Error('CPU clock helper exited')); });
async function sample(pid) {
  const promise = new Promise((resolve,reject) => clockWaiters.push({resolve,reject}));
  clock.stdin.write(`${pid}\n`);
  const value = await timeout(promise,5000);
  assert.equal(value.pid, pid); assert.equal(value.error, undefined, 'process CPU clock unavailable');
  return value;
}
const delta = (a,b) => Number(BigInt(b.cpuNs)-BigInt(a.cpuNs))/1e9;
const timeout = (promise, ms) => {
  let timer;
  return Promise.race([promise, new Promise((_, reject) => { timer=setTimeout(() => reject(Error('host deadline')), ms); })]).finally(() => clearTimeout(timer));
};
let browser, server;
const summary = { startedAt: new Date().toISOString(), complete: false, cpu, repeats, caseCount: cases.length, runs: [], caseSummaries: {} };
const globalTimer = setTimeout(() => { for (const child of owned) kill(child); browser?.close(); }, 7_200_000);

async function wire(variant, input) {
  const command = variant === 'native' ? [resolve(options.native)] : [process.execPath, root+'/wasm/rook.mjs'];
  const child = launch('taskset', ['-c', String(cpu), ...command, ...oracle.mode]);
  let stdout='', stderr='', buffer='', stage='setup', acknowledgments=0, start, before, measured;
  const expectedReplies = input.protocol.recordsBeforeSearch.filter(x => x.startsWith('cm_parm ')).concat('cm_parm rnd=0');
  let resolveMove, rejectMove;
  const move = new Promise((resolve,reject) => { resolveMove=resolve; rejectMove=reject; });
  const exited = new Promise(resolve => child.on('close', (code,signal) => resolve({code,signal})));
  child.on('error', rejectMove); child.stdin.on('error', rejectMove);
  child.stderr.on('data', chunk => { stderr += chunk; if (stderr.length>4*1024**2) rejectMove(Error('stderr cap')); });
  child.stdout.on('data', chunk => {
    stdout += chunk; buffer += chunk;
    if (stdout.length>4*1024**2) return rejectMove(Error('stdout cap'));
    while (buffer.includes('\n')) {
      const n=buffer.indexOf('\n'), line=buffer.slice(0,n); buffer=buffer.slice(n+1);
      if (stage==='setup') {
        if (line!==expectedReplies[acknowledgments++]) return rejectMove(Error('setup acknowledgment mismatch'));
        if (acknowledgments===expectedReplies.length) {
          stage='arming';
          (async () => {
            try {
              const tasks=placement(child.pid);
              before=await sample(child.pid); start=performance.now(); stage='search';
              measured={pid:child.pid,tasksBefore:tasks,before};
              child.stdin.write(input.protocol.searchRecord+'\n');
            } catch (error) { rejectMove(error); }
          })();
        }
      } else if (stage==='search' && /^move [a-h][1-8][a-h][1-8][qrbn]?$/.test(line)) {
        stage='measured'; const end=performance.now();
        sample(child.pid).then(after => { Object.assign(measured,{after,wallSeconds:(end-start)/1000,cpuSeconds:delta(before,after),tasksAfter:placement(child.pid)}); resolveMove(); }).catch(rejectMove);
      }
    }
  });
  child.on('exit', () => { if (stage!=='measured') rejectMove(Error('engine exited before selected move')); });
  try {
    child.stdin.write(input.protocol.recordsBeforeSearch.concat('cm_parm rnd').join('\n')+'\n');
    await timeout(move, 330_000);
    child.stdin.end(input.protocol.cleanupRecord+'\n');
    const exit=await timeout(exited,5000);
    const actual={stdout,stderr,exit,error:null,complete:true};
    checkReplay(actual,input,oracle.cases.find(c=>c.id===input.id));
    return {...measured,...actual};
  } finally { if (child.exitCode===null) kill(child); }
}

async function chrome(input) {
  const context=await browser.newContext();
  const page=await context.newPage();
  const problems=[];page.on('pageerror',error=>problems.push(error.message));
  try {
    await page.goto(summary.browserUrl+'benchmark.html');
    await page.waitForFunction(()=>window.benchmark);
    await timeout(page.evaluate(()=>window.benchmark.ready),30_000);
    const candidates=[];
    for (const p of (await summary.cdp.send('SystemInfo.getProcessInfo')).processInfo.filter(p=>p.type==='renderer')) {
      const tasks=snapshots(p.id);
      if (tasks.some(t=>/DedicatedWorker/.test(t.name))) candidates.push({pid:p.id,tasks});
    }
    assert.equal(candidates.length,1,'cannot identify a unique owned renderer/worker');
    const pid=candidates[0].pid;
    execFileSync('taskset',['-apc',String(cpu),String(pid)],{stdio:'pipe'});
    const tasksBefore=placement(pid);
    await timeout(page.evaluate(async lines=>{ for(const line of lines) await window.benchmark.send(line); },input.protocol.recordsBeforeSearch.concat('cm_parm rnd')),30_000);
    const before=await sample(pid), start=performance.now();
    const local=await timeout(page.evaluate(()=>window.benchmark.go()),330_000);
    const end=performance.now(), after=await sample(pid), tasksAfter=placement(pid);
    await page.evaluate(line=>window.benchmark.send(line),input.protocol.cleanupRecord);
    const streams=await page.evaluate(()=>({stdout:window.benchmark.state.stdout,stderr:window.benchmark.state.stderr}));
    const quitStatus=await page.evaluate(()=>window.benchmark.state.lastCommandStatus);
    assert.equal(quitStatus,2,'browser worker did not return quit');
    assert.deepEqual(problems,[]);
    const actual={...streams,exit:{code:0,signal:null},error:null,complete:true};
    // Browser worker termination is context/worker lifecycle, not a POSIX engine exit.
    checkReplay(actual,input,oracle.cases.find(c=>c.id===input.id));
    return {pid,quitCommandStatus:quitStatus,exitObservation:'Worker quit status2 observed; exit0 below is the comparator projection, not a POSIX process-exit receipt',workerTasks:tasksBefore.filter(t=>/DedicatedWorker/.test(t.name)),tasksBefore,tasksAfter,before,after,
      cpuSeconds:delta(before,after),wallSeconds:(end-start)/1000,browserWallSeconds:local.wallMs/1000,...actual};
  } finally { await context.close(); }
}

try {
  // An independently observable worker burn proves the remote process clock includes worker CPU.
  const control=launch(process.execPath,['-e',`const{Worker}=require('node:worker_threads');console.log('ready');process.stdin.once('data',()=>{new Worker("const{parentPort}=require('node:worker_threads');let s=process.cpuUsage();while(process.cpuUsage(s).user+process.cpuUsage(s).system<200000){}parentPort.postMessage('done')",{eval:true}).on('message',()=>console.log('done'));});setInterval(()=>{},1000);`]);
  const controlLines=createInterface({input:control.stdout});
  await timeout(once(controlLines,'line'),5000);const a=await sample(control.pid);
  const finished=once(controlLines,'line');control.stdin.write('go\n');await timeout(finished,5000);const b=await sample(control.pid);
  const burned=delta(a,b);assert(burned>0.18&&burned<0.8,'worker CPU accounting control failed');kill(control);
  save(output+'/clock-control.json',{before:a,after:b,cpuSeconds:burned});
  // Regression control: drain more stderr than the old blocked socket could hold.
  const logger=launch('python3',['-c','import sys;sys.stderr.write("x"*1048576);sys.stderr.flush();print("done",flush=True)']);
  const logStream=createWriteStream(output+'/logging-control.raw');
  const logFinished=once(logStream,'finish');logger.stderr.pipe(logStream);
  await timeout(Promise.all([once(logger.stdout,'data'),once(logger,'close'),logFinished]),5000);
  assert.equal(statSync(output+'/logging-control.raw').size,1048576);
  save(output+'/logging-control.json',{pass:true,drainedBytes:1048576});
  server=launch('python3',[root+'/wasm/serve.py','--port','0']);
  server.stderr.pipe(createWriteStream(output+'/server.stderr'));
  const [urlChunk]=await timeout(once(server.stdout,'data'),10_000);summary.browserUrl=String(urlChunk).match(/http:\/\/localhost:\d+\//)[0];
  browser=await chromium.launch({headless:true,executablePath:resolve(options.chromium)});summary.chromium=await browser.version();summary.node=process.version;
  summary.cdp=await browser.newBrowserCDPSession();
  const files=[options.native,options.clock,process.execPath,resolve(options.chromium),root+'/wasm/dist/rook.wasm',
    ...['rook.mjs','node-worker.mjs','worker.mjs','runtime.mjs','queue.mjs','benchmark.html','serve.py'].map(x=>root+'/wasm/'+x),
    root+'/tools/benchmark_wasm.mjs',root+'/tools/process_clock.c',spec+'/workloads.json',spec+'/replay-oracle.json',spec+'/replay-check.mjs'];
  const pins=Object.fromEntries(files.map(p=>[resolve(p),sha(p)]));
  const base=['native','node','chromium'];
  const schedule=cases.flatMap((c,i)=>Array.from({length:repeats+1},(_,r)=>base.map((_,v)=>({case:c.id,repeat:r,warmup:r===0,variant:base[(v+i+r)%3]}))).flat());
  const plan={schema:'rook-wasm-search-performance-v1',cpu,repeats,schedule,pins,
    boundary:'High-resolution live process CPU before go dispatch to selected-move receipt; monotonic host wall around same request. Startup/setup/shutdown excluded.',
    chromiumBoundary:'Owned unique renderer CPU includes worker, renderer main thread and its compilation threads; browser/GPU/utility processes and external controller remain on housekeeping and are excluded. Extra in-page wall recorded.',
    lifecycle:'Native/Node fresh processes. Chromium fresh browser context/page/worker per run; shared browser parent. No full-browser lifetime cost or hard exit equivalence claim.',
    comparison:'Current PGO native release versus non-PGO WASM; this does not isolate the cost of WASM alone.',
    limits:{runSeconds:390,searchSeconds:330,browserReadySeconds:30,aggregateSeconds:7200,streamBytesPerRun:4194304,retainedBytes:268435456},
    pmu:'No cycles/instructions/IPC collected',environment:{before:readFileSync('/proc/stat','utf8')}};
  save(output+'/plan.json',plan);
  writeFileSync(output+'/collector.mjs',readFileSync(fileURLToPath(import.meta.url)));
  let retained=0;
  for(const [i,step] of schedule.entries()){
    const input=cases.find(c=>c.id===step.case);
    const data=await timeout(step.variant==='chromium'?chrome(input):wire(step.variant,input),390_000);
    assert(data.cpuSeconds>0&&data.wallSeconds>0);
    const filename=`${String(i).padStart(3,'0')}-${step.case}-${step.variant}-r${step.repeat}.json`;
    const row={...step,...data};save(output+'/'+filename,row);retained+=Buffer.byteLength(JSON.stringify(row));assert(retained<268435456);
    summary.runs.push({...step,file:filename,cpuSeconds:data.cpuSeconds,wallSeconds:data.wallSeconds,pid:data.pid});
    for(const variant of base){
      const samples=summary.runs.filter(x=>x.case===step.case&&x.variant===variant&&!x.warmup);
      if(samples.length===repeats){
        const stats=key=>{const values=samples.map(x=>x[key]).sort((a,b)=>a-b);return{minimum:values[0],median:values[Math.floor(values.length/2)],maximum:values.at(-1)};};
        summary.caseSummaries[step.case]??={};summary.caseSummaries[step.case][variant]={cpu:stats('cpuSeconds'),wall:stats('wallSeconds')};
      }
    }
    const {cdp,...serializable}=summary;save(output+'/summary.json',serializable);
  }
  assert(Object.entries(pins).every(([p,h])=>sha(p)===h),'input changed');
  summary.totals=Object.fromEntries(base.map(v=>[v,{cpu:cases.reduce((n,c)=>n+summary.caseSummaries[c.id][v].cpu.median,0),wall:cases.reduce((n,c)=>n+summary.caseSummaries[c.id][v].wall.median,0)}]));
  summary.complete=true;
} catch(error){ summary.failure=error.stack;process.exitCode=1; }
finally{
  summary.finishedAt=new Date().toISOString();
  summary.ownedPidsAtCleanup=[...owned].map(child=>child.pid);
  try { summary.chromePidsAtCleanup=(await summary.cdp?.send('SystemInfo.getProcessInfo'))?.processInfo.map(p=>p.id)??[]; } catch {}
  save(output+'/context-after.json',{procStat:readFileSync('/proc/stat','utf8')});
  clearTimeout(globalTimer);await browser?.close();
  for(const child of owned)kill(child);
  const {cdp,...serializable}=summary;save(output+'/summary.json',serializable);
  console.log(JSON.stringify({complete:summary.complete,failure:summary.failure,totals:summary.totals}));
}
