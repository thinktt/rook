#!/usr/bin/env node
// A normal stdin/stdout executable: node wasm/rook.mjs [ordinary engine flags].
import { Worker } from 'node:worker_threads';
import { fileURLToPath } from 'node:url';
import { commandQueue } from './queue.mjs';

let flags = 0;
let wasm = new URL('./dist/rook.wasm', import.meta.url);
const options = process.argv.slice(2);
for (let i = 0; i < options.length; i++) {
  const option = options[i];
  if (option === '--wasm') wasm = options[++i];
  else if (option === '--diagnostic-seed-command') flags |= 1;
  else if (option === '--work-clock-post=work') flags |= 2;
  else if (option !== '--work-clock=kingwcr') {
    console.error(`rook2: unsupported option: ${option}`);
    process.exit(1);
  }
}
const queue = commandQueue();
const pending = [];
let ended = false;
let reportedExit = false;
let partial = '';
const worker = new Worker(new URL('./node-worker.mjs', import.meta.url), {
  workerData: { queue: queue.buffer, wasm: wasm instanceof URL ? fileURLToPath(wasm) : wasm, flags },
});
function flush() {
  while (pending.length && queue.send(pending[0])) pending.shift();
  if (ended && !pending.length) queue.end();
}
function fail(error) {
  console.error(`rook-wasm: ${error.message}`);
  process.exitCode = 1;
  process.stdin.destroy();
  worker.terminate();
}
process.stdin.setEncoding('utf8');
process.stdin.on('data', chunk => {
  try {
    partial += chunk;
    for (;;) {
      const newline = partial.indexOf('\n');
      if (newline < 0) break;
      if (newline + 1 > 1023) throw Error('overlength command record');
      let line = partial.slice(0, newline);
      partial = partial.slice(newline + 1);
      if (line.endsWith('\r')) line = line.slice(0, -1);
      pending.push(line);
    }
    flush();
  } catch (error) { fail(error); }
});
process.stdin.on('end', () => {
  if (partial) return fail(Error('unterminated command record'));
  ended = true;
  flush();
});
worker.on('message', message => {
  if (message.channel) (message.channel === 1 ? process.stdout : process.stderr).write(message.text);
  if (message.drain) { try { flush(); } catch (error) { fail(error); } }
  if (message.exit !== undefined) {
    reportedExit = true;
    process.exitCode = message.exit;
    process.stdin.destroy();
  }
});
worker.on('error', fail);

worker.on('exit', code => {
  if (!reportedExit) fail(Error(`Worker exited before reporting completion (${code})`));
});
