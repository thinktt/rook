// Experiment host: preserve compiled WASM while constructing fresh Rust sessions.
import { readFileSync } from 'node:fs';
import { createInterface } from 'node:readline';
import { instantiate } from '../../wasm/runtime.mjs';
let stdout = '', stderr = '', handle;
const send = data => process.stdout.write(JSON.stringify(data)+'\n');
const runtime = instantiate(readFileSync(process.argv[2]), {
  output(channel, text) {
    if (channel === 1) {
      stdout += text;
      if (/^move [a-h]/.test(text)) send({ event: 'move' });
    } else stderr += text;
  },
});
const command = line => runtime.call('rook_command', line, handle);
const input = createInterface({ input: process.stdin });
input.on('line', line => {
  try {
    const request = JSON.parse(line);
    if (request.op === 'prepare') {
      if (handle !== undefined) runtime.api.rook_destroy(handle);
      handle = runtime.api.rook_create(2);
      stdout = ''; stderr = '';
      for (const line of request.lines) if (command(line) !== 0) throw Error('setup failed');
      send({ ready: true });
    } else if (request.op === 'go') {
      if (command('go') !== 0) throw Error('search failed');
      if (command('quit') !== 2) throw Error('logical session quit failed');
      send({ complete: true, stdout, stderr, quitStatus: 2 });
    } else if (request.op === 'close') {
      if (handle !== undefined) runtime.api.rook_destroy(handle);
      handle = undefined; input.close(); process.stdin.destroy(); send({ closed: true });
    } else throw Error('unknown experiment request');
  } catch (error) { send({ error: error.stack }); process.exitCode = 1; input.close(); process.stdin.destroy(); }
});
send({ started: true });
