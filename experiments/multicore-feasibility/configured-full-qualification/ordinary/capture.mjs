// Outside-engine capture of original released spawn/spawnSync calls. No oracle input.
import cp from 'node:child_process';
import {syncBuiltinESMExports} from 'node:module';
import {createHash} from 'node:crypto';
import {readFileSync,writeFileSync,mkdirSync,openSync,closeSync,writeSync,existsSync} from 'node:fs';
import {join} from 'node:path';
import {fileURLToPath} from 'node:url';
const configBytes=readFileSync(process.env.ROOK2_FOCUSED_TAP_CONFIG);
const c=JSON.parse(configBytes),hash=b=>createHash('sha256').update(b).digest('hex');
let count=0;
function start(command,args){
 const index=count++;
 if(index>=c.expectedCalls.length || JSON.stringify([command,...args])!==JSON.stringify(c.expectedCalls[index]))throw Error('Unexpected launch');
 const dir=join(c.rawRoot,String(index).padStart(2,'0'));mkdirSync(dir);
 return {index,dir,argv:[command,...args],imageBefore:hash(readFileSync(c.image)),configSha256:hash(configBytes)};
}
function save(r,streams,extra){
 const raw={};
 for(const [name,data] of Object.entries(streams)){
  const path=join(r.dir,name+'.raw');writeFileSync(path,data,{flag:'wx'});raw[name]={path,bytes:data.length,sha256:hash(data)};
 }
 writeFileSync(join(r.dir,'receipt.json'),JSON.stringify({...r,...extra,raw,imageAfter:hash(readFileSync(c.image))},null,2)+'\n',{flag:'wx'});
}
const sync=cp.spawnSync;
cp.spawnSync=function(command,args,options){
 const r=start(command,args),input=Buffer.from(options.input??'');
 const result=Reflect.apply(sync,this,[command,args,options]);
 save(r,{stdin:input,stdout:Buffer.from(result.stdout??''),stderr:Buffer.from(result.stderr??'')},
  {mode:'spawnSync',pid:result.pid,status:result.status,signal:result.signal,error:result.error?String(result.error):null});
 return result;
};
function gate(child, chunk, encoding) {
 const record=join(process.env.ROOK2_FOCUSED_NATIVE_DIR,child.pid+'.json');
 const readyPath=record+'.ready', deadline=process.hrtime.bigint()+12_000_000_000n;
 const sleep=new Int32Array(new SharedArrayBuffer(4));
 while(!existsSync(readyPath)) {
  if(process.hrtime.bigint()>=deadline){child.kill('SIGTERM');throw Error('External placement ready deadline');}
  Atomics.wait(sleep,0,0,1);
 }
 const bytes=readFileSync(readyPath),ready=JSON.parse(bytes),masks=ready.native_post_exec.task_affinities;
 if(ready.schema!=='rook2-external-placement-ready-v1'||ready.supervisor_pid!==child.pid||
    ready.expected_threads!==c.threadBudget||ready.engine!==c.image||Object.keys(masks).length!==c.threadBudget||
    JSON.stringify(masks[String(ready.native_pid)])!=='[14]'||
    Object.entries(masks).some(([tid,mask])=>tid!==String(ready.native_pid)&&JSON.stringify(mask)!=='[6]'))
  throw Error('Invalid external placement ready artifact');
 const data=typeof chunk==='string'?Buffer.from(chunk,typeof encoding==='string'?encoding:'utf8'):Buffer.from(chunk);
 const release=process.hrtime.bigint();if(release<BigInt(ready.ready_monotonic_ns))throw Error('Placement chronology');
 writeFileSync(record+'.input-gate.json',JSON.stringify({schema:'rook2-placement-input-gate-v1',
  implementation:'node-focused',gate_sha256:hash(readFileSync(fileURLToPath(import.meta.url))),
  ready_path:readyPath,ready_sha256:hash(bytes),native_pid:ready.native_pid,supervisor_pid:child.pid,
  release_monotonic_ns:release.toString(),first_write_bytes:data.length,first_write_sha256:hash(data)},null,2)+'\n',{flag:'wx'});
}
const spawn=cp.spawn;
cp.spawn=function(command,args,options){
 const r=start(command,args);const names=['stdin','stdout','stderr'];
 const paths=Object.fromEntries(names.map(n=>[n,join(r.dir,n+'.raw')]));
 const fds=Object.fromEntries(names.map(n=>[n,openSync(paths[n],'wx')]));
 const sizes=Object.fromEntries(names.map(n=>[n,0]));let total=0,failure=null;
 const child=Reflect.apply(spawn,this,[command,args,options]);
 function capture(n,data){
  data=Buffer.from(data);sizes[n]+=data.length;total+=data.length;
  if(total>c.maxBytes){failure??='Capture cap';child.kill('SIGTERM');return;}
  let offset=0;while(offset<data.length)offset+=writeSync(fds[n],data,offset,data.length-offset);
 }
 const write=child.stdin.write;let capturingEnd=false,released=false;
 function release(chunk,encoding){if(!released){gate(child,chunk,encoding);released=true;}}
 child.stdin.write=function(chunk,...rest){release(chunk,rest[0]);if(!capturingEnd)capture('stdin',typeof chunk==='string'?Buffer.from(chunk,typeof rest[0]==='string'?rest[0]:'utf8'):chunk);return Reflect.apply(write,this,[chunk,...rest]);};
 const end=child.stdin.end;
 child.stdin.end=function(chunk,...rest){
  if(typeof chunk==='string'||Buffer.isBuffer(chunk)||ArrayBuffer.isView(chunk)){release(chunk,rest[0]);capture('stdin',typeof chunk==='string'?Buffer.from(chunk,typeof rest[0]==='string'?rest[0]:'utf8'):chunk);}
  capturingEnd=true;try{return Reflect.apply(end,this,[chunk,...rest]);}finally{capturingEnd=false;}
 };
 for(const n of ['stdout','stderr'])child[n].on('data',data=>capture(n,data));
 child.on('error',error=>{failure??=String(error);});
 child.on('close',(status,signal)=>{
  for(const fd of Object.values(fds))closeSync(fd);
  const raw=Object.fromEntries(names.map(n=>{const b=readFileSync(paths[n]);return [n,{path:paths[n],bytes:b.length,observedBytes:sizes[n],sha256:hash(b)}];}));
  writeFileSync(join(r.dir,'receipt.json'),JSON.stringify({...r,mode:'spawn',pid:child.pid,status,signal,error:failure,raw,imageAfter:hash(readFileSync(c.image))},null,2)+'\n',{flag:'wx'});
 });
 return child;
};
process.on('exit',()=>{
 writeFileSync(join(c.rawRoot,'launch-count.json'),JSON.stringify({expected:c.expectedCalls.length,observed:count})+'\n',{flag:'wx'});
 if(count!==c.expectedCalls.length)process.exitCode=1;
});
syncBuiltinESMExports();
