// Untimed direct-child capture. The released comparator and engine pipes stay intact.
import childProcess from 'node:child_process';
import {syncBuiltinESMExports} from 'node:module';
import {createHash} from 'node:crypto';
import {readFileSync, writeFileSync, openSync, closeSync, writeSync,
  mkdirSync, readlinkSync, readdirSync} from 'node:fs';
import {join} from 'node:path';

const bytes = readFileSync(process.env.ROOK2_DIRECT_TAP_CONFIG);
const config = JSON.parse(bytes);
if (config.version !== 1 || !Array.isArray(config.argv) || config.argv.length < 1 ||
    !config.directory.startsWith('/') || !config.image.startsWith('/') ||
    !Number.isSafeInteger(config.maxBytes) || config.maxBytes < 1)
  throw new Error('Invalid direct capture configuration');
const hash = data => createHash('sha256').update(data).digest('hex');
const originalSpawn = childProcess.spawn;
let count = 0;
childProcess.spawn = function(command, args, options) {
  const argv = [command, ...(args ?? [])];
  if (++count !== 1 || JSON.stringify(argv) !== JSON.stringify(config.argv))
    throw new Error('Unexpected direct child');
  mkdirSync(config.directory);
  const names = ['stdin', 'stdout', 'stderr'];
  const paths = Object.fromEntries(names.map(name => [name, join(config.directory, name+'.raw')]));
  const fds = Object.fromEntries(names.map(name => [name, openSync(paths[name], 'wx')]));
  const sizes = Object.fromEntries(names.map(name => [name, 0]));
  let total = 0, failure = null, observed = null, child;
  function fail(message) {
    failure ??= message;
    child?.kill('SIGTERM');
  }
  function capture(name, chunk) {
    const data = Buffer.from(chunk);
    sizes[name] += data.length;
    total += data.length;
    if (total > config.maxBytes) { fail('Raw byte cap exceeded'); return; }
    let offset = 0;
    while (offset < data.length) {
      const written = writeSync(fds[name], data, offset, data.length-offset);
      if (written <= 0) throw new Error('Short capture write');
      offset += written;
    }
  }
  function observe() {
    if (observed || failure) return;
    try {
      const pid = child.pid;
      if (readlinkSync(`/proc/${pid}/exe`) !== config.image) throw new Error('Image mismatch');
      const tasks = readdirSync(`/proc/${pid}/task`).map(tid => {
        const status = readFileSync(`/proc/${pid}/task/${tid}/status`, 'utf8');
        const affinity = /^Cpus_allowed_list:\s*(.*)$/m.exec(status)?.[1];
        if (affinity !== '0-5,8-13') throw new Error('Unexpected affinity');
        return {tid:Number(tid), affinity};
      });
      const stat = readFileSync(`/proc/${pid}/stat`, 'utf8');
      observed = {pid, image:config.image, startTicks:stat.slice(stat.lastIndexOf(')')+2).split(/\s+/)[19], tasks};
    } catch (error) { fail(String(error.message ?? error)); }
  }
  child = Reflect.apply(originalSpawn, this, [command, args, options]);
  if (!child.stdin || !child.stdout || !child.stderr) throw new Error('Three native pipes required');
  const originalWrite = child.stdin.write;
  child.stdin.write = function(chunk, ...rest) {
    const data = typeof chunk === 'string' ? Buffer.from(chunk, typeof rest[0] === 'string' ? rest[0] : 'utf8') : Buffer.from(chunk);
    capture('stdin', data);
    return Reflect.apply(originalWrite, this, [chunk, ...rest]);
  };
  for (const name of ['stdout', 'stderr']) child[name].on('data', chunk => {
    observe(); capture(name, chunk);
  });
  child.on('error', error => { failure ??= String(error.message ?? error); });
  child.on('close', (code, signal) => {
    for (const fd of Object.values(fds)) closeSync(fd);
    const raw = Object.fromEntries(names.map(name => {
      const data = readFileSync(paths[name]);
      return [name, {path:paths[name], bytes:data.length, observedBytes:sizes[name], sha256:hash(data)}];
    }));
    writeFileSync(join(config.directory, 'receipt.json'), JSON.stringify({
      schema:'rook2-untimed-direct-wire-v1', argv, configSha256:hash(bytes),
      native:observed, exit:{code, signal}, failure, raw,
      scope:'Untimed behavioral capture; one image/affinity point observation. No CPU, wall, PMU or performance qualification.'
    }, null, 2)+'\n', {flag:'wx'});
  });
  return child;
};
syncBuiltinESMExports();
