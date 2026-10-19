// Thin transport around the ORIGINAL public runner and oracle, not a replay implementation.
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync} from 'node:fs';
import {runReplay,checkReplay,workloads,oracle} from '/home/legolas/king-spec/conformance/profiling/replay-check.mjs';
const [mode,planPath,name,out]=process.argv.slice(2),plan=JSON.parse(readFileSync(planPath));
const input=workloads.cases.find(x=>x.id==='profile-08'),expected=oracle.cases.find(x=>x.id==='profile-08');
assert(input&&expected);
if(mode==='live'){
 const v=plan.variants[name],prefix=plan.valgrind_prefix;
 const command=['/usr/bin/taskset','-c','14','/usr/bin/env',`VALGRIND_LIB=${prefix}/libexec/valgrind`,`${prefix}/bin/valgrind`,'--tool=callgrind','--cache-sim=no','--branch-sim=no',`--callgrind-out-file=${out}/profile.callgrind`,`--log-file=${out}/valgrind.log`,v.engine];
 const options={...plan.timeout_ms,deadline:Date.now()+plan.timeout_ms.aggregateMs};
 delete options.aggregateMs;
 const row=await runReplay(command,input,expected,{bytes:0},options);
 writeFileSync(`${out}/replay.json`,JSON.stringify(row,null,2)+'\n',{flag:'wx'});
 writeFileSync(`${out}/stdout.raw`,row.stdout,{flag:'wx'});writeFileSync(`${out}/stderr.raw`,row.stderr,{flag:'wx'});
 assert.equal(row.status,'pass');checkReplay(row,input,expected);
 assert.deepEqual(row.command,[...command,...oracle.mode]);
 assert.equal(row.discardedObservedBytes,0);assert(!row.truncated&&!row.cleanupUnconfirmed);
 console.log(JSON.stringify({complete:true,pid:row.pid,engineRuns:1,originalCheckReplay:1}));
}else{
 assert.equal(mode,'offline');const row=JSON.parse(readFileSync(`${out}/replay.json`));
 assert.equal(row.case,'profile-08');assert.equal(row.status,'pass');checkReplay(row,input,expected);
 assert.deepEqual(readFileSync(`${out}/stdout.raw`),Buffer.from(row.stdout));
 assert.deepEqual(readFileSync(`${out}/stderr.raw`),Buffer.from(row.stderr));
 assert.equal(row.discardedObservedBytes,0);assert(!row.truncated&&!row.cleanupUnconfirmed);
 console.log(JSON.stringify({complete:true,engineRuns:0,originalCheckReplay:1}));
}
