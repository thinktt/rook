#!/usr/bin/env node
// Optional Linux host benchmark; no engine behavior implementation or speed oracle.
import assert from 'node:assert/strict';
import {spawn} from 'node:child_process';
import {readFileSync,existsSync} from 'node:fs';
import {resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
export function parsePost(line){
 const m=line.match(/^\s*(-?\d+)\s+([+-]?\d+)\s+(\d+)\s+(\d+)(?:\s+(.*))?$/);
 if(!m)return null;
 return {depth:Number(m[1]),score:Number(m[2]),workThousands:Number(m[3]),searchId:Number(m[4]),pv:m[5]??''};
}
export function rates(post){
 assert(post.workThousands<2147483647,'saturated work cannot give an exact work rate');
 assert(post.wallMs>0&&post.cpuMs>0,'nonpositive timing interval');
 const virtualWorkSeconds=post.workThousands/3000000;
 return {virtualWorkSeconds,workPerWallSecond:virtualWorkSeconds/(post.wallMs/1000),
  workPerCpuSecond:virtualWorkSeconds/(post.cpuMs/1000)};
}
export function takeOutput(bytes,budget,n){
 assert(Number.isInteger(n)&&n>=0);
 assert(bytes+n<=4194304&&budget.bytes+n<=16777216,'per-run/aggregate output cap');
 budget.bytes+=n;return bytes+n;
}
export function takePost(count,budget){
 assert(count<2048&&budget.posts<8192,'per-run/aggregate post cap');budget.posts++;
}
export function streamState(){
 return {complete:false,truncated:false,retainedBytes:{stdout:0,stderr:0},discardedBytes:0,incompleteReasons:[]};
}
export function markIncomplete(state,reason,discardedBytes=0){
 state.complete=false;if(discardedBytes>0){state.truncated=true;state.discardedBytes+=discardedBytes;}
 if(!state.incompleteReasons.includes(reason))state.incompleteReasons.push(reason);
}
async function run(input,command,cpu,repeat,deadline,budget){
 const row={case:input.id,repeat,warmup:repeat===0,status:'running',posts:[],stdout:'',stderr:'',exit:null,error:null,streams:streamState(),
  measurementAvailability:{wallDeltas:'host monotonic origin immediately before go write request',cpuDeltas:'sampled engine user+system relative to pre-request sample',goWriteCompletion:null,absoluteMonotonicTimestamps:null,absoluteCpuSamples:null}};
 const child=spawn('taskset',['-c',String(cpu.index),...command,'--work-clock=kingwcr','--work-clock-post=work'],{detached:true,stdio:['pipe','pipe','pipe']});
 row.pid=child.pid;row.launchUtc=new Date().toISOString();
 const chunks=[[],[]];let bytes=0,buffer='',start=null,startCpu=null,moved=false;
 const kill=()=>{try{process.kill(-child.pid,'SIGKILL');}catch{}};
 let settle=null,closeObserved=false,cleanupTimer=null;
 const fail=e=>{row.error??=String(e);markIncomplete(row.streams,'host-failure');kill();if(!cleanupTimer)cleanupTimer=setTimeout(()=>{
  if(!closeObserved){row.cleanupUnconfirmed=true;markIncomplete(row.streams,'cleanup-collection-cutoff');settle?.({code:null,signal:null});
   child.stdin.destroy();child.stdout.destroy();child.stderr.destroy();child.unref();}
 },5000);};
 const noChildren=()=>assert.equal(readFileSync(`/proc/${child.pid}/task/${child.pid}/children`,'utf8').trim(),'','work-performing descendants need separate accounting');
 const cost=()=>{noChildren();const a=readFileSync(`/proc/${child.pid}/stat`,'utf8').split(') ').at(-1).split(' ');return(Number(a[11])+Number(a[12]))*1000/cpu.hz;};
 const expectedReplies=input.protocol.recordsBeforeSearch.filter(x=>x.startsWith('cm_parm')).concat('cm_parm rnd=0');let reply=0;
 let stage='setup';let timer=setTimeout(()=>fail('30000ms setup host deadline'),30000);
 const aggregateTimer=setTimeout(()=>fail('1800000ms aggregate host deadline'),Math.max(1,deadline-Date.now()));
 child.on('error',e=>fail(e.message));child.stdin.on('error',e=>{if(!moved)fail(e.message);});
 const finished=new Promise(done=>{settle=done;child.on('close',(code,signal)=>{closeObserved=true;done({code,signal});});});
 for(const [i,s]of [child.stdout,child.stderr].entries())s.on('data',b=>{
  try{bytes=takeOutput(bytes,budget,b.length);}catch(e){markIncomplete(row.streams,'output-limit',b.length);fail(e.message);return;}chunks[i].push(b);row.streams.retainedBytes[i===0?'stdout':'stderr']+=b.length;
  if(i!==0)return;buffer+=b.toString('utf8');
  while(buffer.includes('\n')){const n=buffer.indexOf('\n'),line=buffer.slice(0,n);buffer=buffer.slice(n+1);
   try{
    if(stage==='setup'){
     assert.equal(line,expectedReplies[reply++],'setup record differs');
     if(reply===expectedReplies.length){
      const status=readFileSync(`/proc/${child.pid}/status`,'utf8');
      row.affinity=status.match(/^Cpus_allowed_list:\s*(.+)$/m)?.[1];assert.equal(row.affinity,String(cpu.index));
      // Child work is not silently counted as main-process execution efficiency.
      const descendants=readFileSync(`/proc/${child.pid}/task/${child.pid}/children`,'utf8').trim();assert.equal(descendants,'','work-performing descendants need separate accounting');
      row.cpuResolutionMs=1000/cpu.hz;startCpu=cost();start=process.hrtime.bigint();row.goUtc=new Date().toISOString();stage='search';
      clearTimeout(timer);timer=setTimeout(()=>fail('300000ms search host deadline'),300000);child.stdin.write('go\n');
     }
    }else if(stage==='search'){
     const wallMs=Number(process.hrtime.bigint()-start)/1e6,cpuMs=cost()-startCpu;
     const post=parsePost(line);if(post){takePost(row.posts.length,budget);row.posts.push({...post,wallMs,cpuMs});continue;}
     const m=line.match(/^move ([a-h][1-8][a-h][1-8][qrbn]?)$/);assert(m,'unexpected search record');
     row.move={coordinate:m[1],wallMs,cpuMs};moved=true;stage='cleanup';clearTimeout(timer);
     timer=setTimeout(()=>fail('5000ms cleanup host deadline'),5000);child.stdin.end('quit\n');
    }else if(/^(1-0|0-1|1\/2-1\/2) \{[^\r\n]*\}$/.test(line)){
     row.resultRecords??=[];row.resultRecords.push(line);
    }else assert.fail('unexpected shutdown output');
   }catch(e){fail(e.message);}
  }
 });
 child.stdin.write(input.protocol.recordsBeforeSearch.concat('cm_parm rnd').join('\n')+'\n');
 row.exit=await finished;clearTimeout(timer);clearTimeout(aggregateTimer);clearTimeout(cleanupTimer);
 for(const [i,k]of ['stdout','stderr'].entries())row[k]=Buffer.concat(chunks[i]).toString('utf8');
 row.stopUtc=new Date().toISOString();
 try{assert.equal(row.error,null);assert.deepEqual(row.exit,{code:0,signal:null});assert(moved&&row.posts.length);assert.equal(buffer,'');assert.equal(row.stderr,'');assert(!existsSync(`/proc/${child.pid}`));
  row.lastCheckpoint=rates(row.posts.at(-1));row.status='pass';row.streams.complete=closeObserved&&!row.streams.truncated&&!row.cleanupUnconfirmed;
 }catch(e){row.error??=e.message;row.status='fail';markIncomplete(row.streams,'failed-run-collection-unqualified');}
 return row;
}
async function main(argv){
 const split=argv.indexOf('--');assert(split>0&&argv[split+1],'usage: benchmark.mjs --cpu INDEX [--case ID] -- ENGINE [ARGS]');
 let index=null,selected=null;for(let i=0;i<split;i+=2){assert(argv[i+1]);if(argv[i]==='--cpu')index=Number(argv[i+1]);else if(argv[i]==='--case')selected=argv[i+1];else assert.fail('unknown option');}
 assert(process.platform==='linux');assert(Number.isInteger(index)&&index>=0);
 const {execFileSync}=await import('node:child_process');const hz=Number(execFileSync('getconf',['CLK_TCK'],{encoding:'utf8',timeout:5000,maxBuffer:1024}).trim());assert(hz>0);
 const packet=JSON.parse(readFileSync(new URL('./workloads.json',import.meta.url))),cases=packet.cases.filter(c=>!selected||c.id===selected);assert(cases.length);
 const report={version:1,benchmarkOnly:true,completeEngineQualification:false,status:'running',cpu:index,hz,startUtc:new Date().toISOString(),runs:[],limits:{setupMs:30000,searchMs:300000,cleanupMs:5000,rawBytesPerRun:4194304,rawBytesAggregate:16777216,postsPerRun:2048,postsAggregate:8192,aggregateMs:1800000},
  metric:'virtual work seconds per CPU/wall second at the last published-post snapshot',
  limitsOfClaim:'main engine-process CPU only; sampled/quantized receipt boundaries; shared-host pinning is not exclusive isolation; no speed oracle'};
 const deadline=Date.now()+1800000,budget={bytes:0,posts:0};
 try{for(const c of cases){let shape=null;for(let r=0;r<4;r++){
  assert(Date.now()<deadline,'aggregate host deadline');const row=await run(c,argv.slice(split+1),{index,hz},r,deadline,budget);report.runs.push(row);assert.equal(row.status,'pass',row.error);
  const current={move:row.move.coordinate,resultRecords:row.resultRecords??[],posts:row.posts.map(({wallMs,cpuMs,...p})=>p)};if(shape===null)shape=current;else assert.deepEqual(current,shape,'repetitions differ behaviorally');
 }}report.status='pass';}catch(e){report.status='fail';report.error=e.message;process.exitCode=1;}
 report.stopUtc=new Date().toISOString();console.log(JSON.stringify(report,null,2));
}
if(process.argv[1]&&resolve(process.argv[1])===fileURLToPath(import.meta.url))await main(process.argv.slice(2));
