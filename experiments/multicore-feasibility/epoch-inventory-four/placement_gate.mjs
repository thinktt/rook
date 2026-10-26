// Load before the unchanged tap; no first protocol byte precedes TID placement.
import childProcess from 'node:child_process';
import {syncBuiltinESMExports} from 'node:module';
import {readFileSync, writeFileSync, existsSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';

const sha = bytes => createHash('sha256').update(bytes).digest('hex');
const config = JSON.parse(readFileSync(process.env.ROOK2_WIRE_TAP_CONFIG));
const expected = config.expectedArgv;
const record = expected[expected.indexOf('--record')+1];
const budget = Number(expected[expected.indexOf('--thread-budget')+1]);
if (!record?.startsWith('/') || ![1,2,3,4].includes(budget)) throw new Error('invalid placement declaration');
const realSpawn = childProcess.spawn;
let spawns = 0;
childProcess.spawn = function(command, args, options) {
  if (++spawns !== 1 || JSON.stringify([command,...(args ?? [])]) !== JSON.stringify(expected))
    throw new Error('placement gate observed undeclared spawn');
  const child = Reflect.apply(realSpawn,this,[command,args,options]);
  if (!child.stdin) throw new Error('placement gate requires stdin pipe');
  const write = child.stdin.write;
  let released = false;
  child.stdin.write = function(chunk,...rest) {
    if (!released) {
      const readyPath = record+'.ready';
      const deadline = process.hrtime.bigint()+12_000_000_000n;
      const pause = new Int32Array(new SharedArrayBuffer(4));
      while (!existsSync(readyPath)) {
        if (process.hrtime.bigint() >= deadline) {
          child.kill('SIGTERM');
          throw new Error('external placement ready deadline');
        }
        Atomics.wait(pause,0,0,1);
      }
      const readyBytes = readFileSync(readyPath);
      const ready = JSON.parse(readyBytes);
      const affinities = ready.native_post_exec.task_affinities;
      const helpers = Object.entries(affinities).filter(([tid]) => tid !== String(ready.native_pid))
        .map(([,mask]) => mask).sort((a,b) => a[0]-b[0]);
      if (ready.schema !== 'rook2-external-placement-ready-v1' ||
          ready.supervisor_pid !== child.pid || ready.expected_threads !== budget ||
          ready.engine !== config.nativeExecutable || Object.keys(affinities).length !== budget ||
          JSON.stringify(affinities[String(ready.native_pid)]) !== '[14]' ||
          JSON.stringify(helpers) !== JSON.stringify({1:[],2:[[6]],3:[[4],[6]],4:[[2],[4],[6]]}[budget]))
        throw new Error('invalid external placement ready artifact');
      const bytes = typeof chunk === 'string' ? Buffer.from(chunk,typeof rest[0] === 'string' ? rest[0] : 'utf8') : Buffer.from(chunk);
      const release = process.hrtime.bigint();
      if (release < BigInt(ready.ready_monotonic_ns)) throw new Error('placement chronology');
      writeFileSync(record+'.input-gate.json', JSON.stringify({
        schema:'rook2-placement-input-gate-v1', implementation:'node-sync',
        gate_sha256:sha(readFileSync(fileURLToPath(import.meta.url))),
        ready_path:readyPath, ready_sha256:sha(readyBytes),
        native_pid:ready.native_pid, supervisor_pid:child.pid,
        release_monotonic_ns:release.toString(), first_write_bytes:bytes.length,
        first_write_sha256:sha(bytes)
      },null,2)+'\n',{flag:'wx'});
      released = true;
    }
    return Reflect.apply(write,this,[chunk,...rest]);
  };
  return child;
};
syncBuiltinESMExports();

// The released raw tap is unchanged and loads after this experiment's gate.
await import('../../../tools/tap_wire.mjs');
