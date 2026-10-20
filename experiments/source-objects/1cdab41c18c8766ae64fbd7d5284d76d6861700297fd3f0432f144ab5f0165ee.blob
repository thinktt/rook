// Capture original spawnSync controls without changing their execution or oracle.
import childProcess from 'node:child_process';
import {syncBuiltinESMExports} from 'node:module';
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {join} from 'node:path';
import {createHash} from 'node:crypto';
const config=JSON.parse(readFileSync(process.env.ROOK2_SYNC_TAP_CONFIG));
if(config.version!==1||!config.image.startsWith('/')||!config.directory.startsWith('/'))throw Error('config');
mkdirSync(config.directory);let count=0;
const original=childProcess.spawnSync;
const hash=x=>createHash('sha256').update(x).digest('hex');
childProcess.spawnSync=function(command,args,options){
 if(command!==config.image||![JSON.stringify([]),JSON.stringify(['--diagnostic-seed-command'])].includes(JSON.stringify(args)))throw Error('unexpected child');
 const index=count++,dir=join(config.directory,String(index).padStart(2,'0'));mkdirSync(dir);
 const before=hash(readFileSync(command));
 const input=Buffer.from(options.input??'');
 const result=Reflect.apply(original,this,[command,args,options]);
 const streams={stdin:input,stdout:Buffer.from(result.stdout??''),stderr:Buffer.from(result.stderr??'')};
 const raw={};for(const [name,data] of Object.entries(streams)){
  const path=join(dir,name+'.raw');writeFileSync(path,data,{flag:'wx'});raw[name]={path,bytes:data.length,sha256:hash(data)};
 }
 const after=hash(readFileSync(command));
 writeFileSync(join(dir,'receipt.json'),JSON.stringify({index,argv:[command,...args],pid:result.pid,status:result.status,signal:result.signal,error:result.error?String(result.error):null,imageBefore:before,imageAfter:after,raw,scope:'Direct original spawnSync result and all raw bytes; inherited parent affinity, no live /proc observation for these short controls.'},null,2)+'\n',{flag:'wx'});
 return result;
};syncBuiltinESMExports();
