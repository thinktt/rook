// Controller-side byte capture for an unchanged released Node comparator.
// Native pipes are retained; this adds data listeners and a stdin-write tap.
import childProcess from 'node:child_process';
import {syncBuiltinESMExports} from 'node:module';
import {createHash} from 'node:crypto';
import {readFileSync, writeFileSync, openSync, closeSync, writeSync, mkdirSync,
  readlinkSync, statSync} from 'node:fs';
import {resolve, join} from 'node:path';

const configPath = process.env.ROOK2_WIRE_TAP_CONFIG;
if (!configPath) throw new Error('wire tap requires a private configuration');
const configBytes = readFileSync(configPath);
const config = JSON.parse(configBytes);
if (config.version !== 1 || !Array.isArray(config.expectedArgv) ||
    config.expectedArgv.length < 1 || !Number.isSafeInteger(config.maxRawBytes) ||
    config.maxRawBytes < 1 || !Number.isSafeInteger(config.tickHz) || config.tickHz <= 0 ||
    !config.directory.startsWith('/') || !config.nativeExecutable.startsWith('/')) {
  throw new Error('invalid wire tap configuration');
}
const digest = bytes => createHash('sha256').update(bytes).digest('hex');
const realSpawn = childProcess.spawn;
let spawnCount = 0;

childProcess.spawn = function(command, args, options) {
  const argv = [command, ...(args ?? [])];
  if (++spawnCount !== 1 || JSON.stringify(argv) !== JSON.stringify(config.expectedArgv)) {
    throw new Error('wire tap observed an undeclared spawn');
  }
  mkdirSync(config.directory);
  const paths = Object.fromEntries(['stdin','stdout','stderr'].map(name =>
    [name, join(config.directory, name + '.raw')]));
  const fds = Object.fromEntries(Object.entries(paths).map(([k,p]) => [k,openSync(p,'wx')]));
  const seen = {stdin:0,stdout:0,stderr:0}, kept = {...seen};
  let totalKept = 0, failure = null, child = null, native = null;
  let inputBuffer = '', outputBuffer = '', pending = null;
  const searches = [];
  const fail = message => {
    if (!failure) {
      failure = message;
      writeFileSync(join(config.directory,'failure.json'),
        JSON.stringify({failure,seen,kept})+'\n',{flag:'wx'});
      child?.kill('SIGTERM');
    }
  };
  const capture = (stream, bytes) => {
    seen[stream] += bytes.length;
    const count = Math.min(bytes.length, Math.max(0,config.maxRawBytes-totalKept));
    let offset = 0;
    while (offset < count) {
      const n = writeSync(fds[stream],bytes,offset,count-offset);
      if (n <= 0) throw new Error('short raw-file write');
      offset += n;
    }
    kept[stream] += count;
    totalKept += count;
    if (count !== bytes.length) fail('native-raw-byte-cap');
  };
  const cpu = () => {
    try {
      const children = readFileSync(`/proc/${child.pid}/task/${child.pid}/children`,'utf8')
        .trim().split(/\s+/).filter(Boolean).map(Number);
      if (children.length !== 1) throw new Error('native direct child is not unique');
      const pid = children[0];
      if (readlinkSync(`/proc/${pid}/exe`) !== config.nativeExecutable)
        throw new Error('native image mismatch');
      const raw = readFileSync(`/proc/${pid}/stat`,'utf8');
      const fields = raw.slice(raw.lastIndexOf(')')+2).trim().split(/\s+/);
      const startTicks = fields[19];
      if (native && (native.pid !== pid || native.startTicks !== startTicks))
        throw new Error('native process identity changed');
      native = {pid,startTicks,image:config.nativeExecutable};
      return {available:true,...native,userTicks:Number(fields[11]),systemTicks:Number(fields[12]),
        lastProcessor:Number(fields[36])};
    } catch (error) {
      return {available:false,reason:String(error.message ?? error)};
    }
  };
  const startSearch = stamp => {
    if (pending) { fail('overlapping-go-boundaries'); return; }
    pending = {index:searches.length,startMonotonicNs:stamp.toString(),beforeWrite:cpu()};
  };
  const endSearch = (stamp, move) => {
    if (!pending) { fail('move-without-go-boundary'); return; }
    const afterData = cpu();
    const row = {...pending,endMonotonicNs:stamp.toString(),afterData,move,
      wallNs:Number(stamp-BigInt(pending.startMonotonicNs)),cpuTicks:null,cpuSeconds:null,
      cpuUnavailableReason:null};
    if (pending.beforeWrite.available && afterData.available &&
        pending.beforeWrite.pid === afterData.pid && pending.beforeWrite.startTicks === afterData.startTicks) {
      const ticks = afterData.userTicks+afterData.systemTicks-
        pending.beforeWrite.userTicks-pending.beforeWrite.systemTicks;
      if (ticks > 0) { row.cpuTicks=ticks; row.cpuSeconds=ticks/config.tickHz; }
      else row.cpuUnavailableReason=ticks === 0 ? 'unresolved-zero-tick-delta' : 'negative-tick-delta';
    } else row.cpuUnavailableReason='native-boundary-sample-unavailable';
    searches.push(row); pending = null;
  };
  try { child = Reflect.apply(realSpawn,this,[command,args,options]); }
  catch (error) { for (const fd of Object.values(fds)) closeSync(fd); throw error; }
  if (!child.stdin || !child.stdout || !child.stderr) throw new Error('wire tap requires three pipes');
  const write = child.stdin.write;
  child.stdin.write = function(chunk,...rest) {
    const stamp = process.hrtime.bigint();
    const bytes = typeof chunk === 'string' ? Buffer.from(chunk,typeof rest[0] === 'string' ? rest[0] : 'utf8') : Buffer.from(chunk);
    inputBuffer += bytes.toString('utf8');
    const lines = inputBuffer.split('\n'); inputBuffer = lines.pop();
    for (const line of lines) if (line.replace(/\r$/,'') === 'go') startSearch(stamp);
    capture('stdin',bytes);
    return Reflect.apply(write,this,[chunk,...rest]);
  };
  // Register before the comparator's data listeners, retaining original bytes
  // before its assertions. These callbacks do not consume or rewrite its data.
  child.stdout.on('data',chunk => {
    const stamp = process.hrtime.bigint();
    const bytes = Buffer.from(chunk);
    outputBuffer += bytes.toString('utf8');
    const lines = outputBuffer.split('\n'); outputBuffer = lines.pop();
    for (const line of lines) {
      const match = /^move\s+([a-h][1-8][a-h][1-8][qrbn]?)\r?$/i.exec(line);
      if (match) endSearch(stamp,match[1]);
    }
    capture('stdout',bytes);
  });
  child.stderr.on('data',chunk => capture('stderr',Buffer.from(chunk)));
  child.on('close',(code,signal) => {
    for (const fd of Object.values(fds)) closeSync(fd);
    const raw = Object.fromEntries(Object.entries(paths).map(([name,path]) =>
      [name,{path,bytes:statSync(path).size,sha256:digest(readFileSync(path)),
        observedBytes:seen[name],discardedObservedBytes:seen[name]-kept[name]}]));
    const receipt = {schema:'rook2-controller-wire-tap-v1',configSha256:digest(configBytes),
      argv,launcherPid:child.pid,launcherExit:{code,signal},native,raw,searches,pending,
      tickHz:config.tickHz,failure,
      boundary:'Before mixed command chunk containing go; first received data chunk containing move. Not write completion or internal engine boundaries.',
      ownership:'Known single native child under the declared supervisor; point observations, not continuous descendant monitoring.',
      metrics:'Whole native CPU belongs to separate wait4 receipt. Search tick0 is unresolved. No terminal N/R, PMU or inferred work rates.'};
    writeFileSync(join(config.directory,'receipt.json'),JSON.stringify(receipt,null,2)+'\n',{flag:'wx'});
  });
  return child;
};
syncBuiltinESMExports();
