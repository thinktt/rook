#!/usr/bin/env node
// Production-wire replay only: no search implementation or performance oracle.
import assert from 'node:assert/strict';
import {spawn} from 'node:child_process';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {parsePost} from './benchmark.mjs';
export const workloads=JSON.parse(readFileSync(new URL('./workloads.json',import.meta.url)));
export const oracle=JSON.parse(readFileSync(new URL('./replay-oracle.json',import.meta.url)));
const replies=input=>input.protocol.recordsBeforeSearch.filter(x=>x.startsWith('cm_parm ')).concat('cm_parm rnd=0');
export function checkReplay(actual,input,expected){
 assert.equal(actual.error,null,'host failure');assert.equal(actual.complete,true,'incomplete collection');
 assert.deepEqual(actual.exit,expected.exit);assert.equal(actual.stderr,expected.stderr);
 assert(actual.stdout.endsWith('\n'),'partial stdout');
 const lines=actual.stdout.split('\n');lines.pop();const acks=replies(input);
 assert.deepEqual(lines.splice(0,acks.length),acks,'ordered setup acknowledgments');
 const posts=[];for(let i=0;i<expected.posts.length;i++){
  const p=parsePost(lines.shift()??'');assert(p,'missing/invalid post');p.pv=p.pv.trim().replaceAll('0','O');posts.push(p);
 }
 assert.deepEqual(posts,expected.posts,'ordered semantic posts/work');
 assert.equal(lines.shift(),'move '+expected.move,'selected move');
 assert.deepEqual(lines,expected.resultRecords,'complete shutdown records');return true;
}
export async function runReplay(command,input,expected,budget={bytes:0},options={}){
 const setupMs=options.setupMs??30000,searchMs=options.searchMs??900000,cleanupMs=options.cleanupMs??5000;
 const byteCap=options.byteCap??4194304,aggregateCap=options.aggregateCap??134217728,deadline=options.deadline??Date.now()+21600000;
 const row={case:input.id,status:'running',startUtc:new Date().toISOString(),command:[...command,...oracle.mode],stdout:'',stderr:'',exit:null,error:null,complete:false,truncated:false,retainedBytes:0,discardedObservedBytes:0};
 const child=spawn(command[0],[...command.slice(1),...oracle.mode],{detached:true,stdio:['pipe','pipe','pipe']});row.pid=child.pid;
 const chunks=[[],[]];let stage='setup',buffer='',count=0,closed=false,settle,cleanupTimer=null;
 const kill=()=>{try{process.kill(-child.pid,'SIGKILL');}catch{}};
 const fail=reason=>{row.error??=reason;kill();if(!cleanupTimer)cleanupTimer=setTimeout(()=>{
  if(!closed){row.cleanupUnconfirmed=true;child.stdin.destroy();child.stdout.destroy();child.stderr.destroy();child.unref();settle({code:null,signal:null});}
 },cleanupMs);};
 let timer=setTimeout(()=>fail('setup host deadline'),setupMs);
 const aggregateTimer=setTimeout(()=>fail('aggregate host deadline'),Math.max(1,deadline-Date.now()));
 const done=new Promise(r=>{settle=r;child.on('close',(code,signal)=>{closed=true;r({code,signal});});});
 child.on('error',e=>fail(e.message));child.stdin.on('error',e=>{if(stage!=='cleanup')fail(e.message);});
 for(const [i,s]of [child.stdout,child.stderr].entries())s.on('data',b=>{
  if(row.retainedBytes+b.length>byteCap||budget.bytes+b.length>aggregateCap){row.truncated=true;row.discardedObservedBytes+=b.length;fail('output cap');return;}
  row.retainedBytes+=b.length;budget.bytes+=b.length;chunks[i].push(b);if(i)return;
  buffer+=b.toString('utf8');while(buffer.includes('\n')){
   const n=buffer.indexOf('\n'),line=buffer.slice(0,n);buffer=buffer.slice(n+1);
   if(row.error)continue;
   if(stage==='setup'){
    const acks=replies(input);if(line!==acks[count++]){fail('setup acknowledgment mismatch');continue;}
    if(count===acks.length){stage='search';clearTimeout(timer);timer=setTimeout(()=>fail('search host deadline'),searchMs);child.stdin.write(input.protocol.searchRecord+'\n');}
   }else if(stage==='search'&&/^move [a-h][1-8][a-h][1-8][qrbn]?$/.test(line)){
    stage='cleanup';clearTimeout(timer);timer=setTimeout(()=>fail('cleanup host deadline'),cleanupMs);child.stdin.end(input.protocol.cleanupRecord+'\n');
   }
  }
 });
 child.stdin.write(input.protocol.recordsBeforeSearch.concat('cm_parm rnd').join('\n')+'\n');
 row.exit=await done;clearTimeout(timer);clearTimeout(aggregateTimer);clearTimeout(cleanupTimer);
 for(const[i,k]of ['stdout','stderr'].entries())row[k]=Buffer.concat(chunks[i]).toString('utf8');
 row.stopUtc=new Date().toISOString();row.complete=closed&&!row.error&&!row.truncated&&!row.cleanupUnconfirmed;
 try{assert.equal(stage,'cleanup','missing move/cleanup');checkReplay(row,input,expected);row.status='pass';}
 catch(e){row.status='fail';row.failure=e.message;}return row;
}
export function selectCases(argv){
 const split=argv.indexOf('--');assert(split>=0&&argv[split+1],'usage: replay-check.mjs [--case ID] -- ENGINE [ARGS]');
 let id=null;assert(split===0||split===2,'unknown options');if(split){assert.equal(argv[0],'--case');id=argv[1];}
 const cases=workloads.cases.filter(c=>!id||c.id===id);assert(cases.length,'unknown case');return{cases,command:argv.slice(split+1)};
}
async function main(argv){
 const{cases,command}=selectCases(argv),budget={bytes:0},deadline=Date.now()+21600000;
 const sha=url=>createHash('sha256').update(readFileSync(url)).digest('hex');
 const report={version:1,fixture:oracle.id,completeEngineQualification:false,selectedCases:cases.map(c=>c.id),startUtc:new Date().toISOString(),status:'running',
  workloadSha256:sha(new URL('./workloads.json',import.meta.url)),oracleSha256:sha(new URL('./replay-oracle.json',import.meta.url)),
  limits:{setupMs:30000,searchMs:900000,cleanupMs:5000,aggregateMs:21600000,rawBytesPerRun:4194304,rawBytesAggregate:134217728},results:[]};
 for(const input of cases){const expected=oracle.cases.find(c=>c.id===input.id);assert(expected);const row=await runReplay(command,input,expected,budget,{deadline});report.results.push(row);if(row.status!=='pass')break;}
 report.status=report.results.length===cases.length&&report.results.every(r=>r.status==='pass')?'pass':'fail';report.stopUtc=new Date().toISOString();
 console.log(JSON.stringify(report,null,2));if(report.status!=='pass')process.exitCode=1;
}
if(process.argv[1]&&resolve(process.argv[1])===fileURLToPath(import.meta.url))await main(process.argv.slice(2));
