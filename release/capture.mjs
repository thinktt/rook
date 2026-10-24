// Outside-engine capture of original released spawn/spawnSync calls. No oracle input.
import cp from 'node:child_process';
import {syncBuiltinESMExports} from 'node:module';
import {createHash} from 'node:crypto';
import {readFileSync,writeFileSync,mkdirSync,openSync,closeSync,writeSync} from 'node:fs';
import {join} from 'node:path';
const configBytes=readFileSync(process.env.ROOK_RELEASE_TAP_CONFIG);
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
 const write=child.stdin.write;let capturingEnd=false;
 child.stdin.write=function(chunk,...rest){if(!capturingEnd)capture('stdin',typeof chunk==='string'?Buffer.from(chunk,typeof rest[0]==='string'?rest[0]:'utf8'):chunk);return Reflect.apply(write,this,[chunk,...rest]);};
 const end=child.stdin.end;
 child.stdin.end=function(chunk,...rest){
  if(typeof chunk==='string'||Buffer.isBuffer(chunk)||ArrayBuffer.isView(chunk))capture('stdin',typeof chunk==='string'?Buffer.from(chunk,typeof rest[0]==='string'?rest[0]:'utf8'):chunk);
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
