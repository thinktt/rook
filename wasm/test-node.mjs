import assert from 'node:assert/strict';
import { test } from 'node:test';
import { spawn, spawnSync } from 'node:child_process';
import { readFileSync } from 'node:fs';
import { commandQueue } from './queue.mjs';
import { instantiate } from './runtime.mjs';
import { Rook } from './rook.js';

const runner = new URL('./rook.mjs', import.meta.url).pathname;
const diagnostic = new URL('./rook-diag.mjs', import.meta.url).pathname;

test('command queue wraps, preserves order, distinguishes empty and EOF', () => {
  const q = commandQueue();
  assert.equal(q.take(), null);
  for (let batch = 0; batch < 4; batch++) {
    for (let i = 0; i < 255; i++) assert(q.send(`time ${i}`));
    assert.equal(q.send('force'), false);
    for (let i = 0; i < 255; i++) assert.equal(q.take(), `time ${i}`);
  }
  assert(q.send(''));
  assert.equal(q.take(), '');
  assert(q.send('?', true));
  assert.deepEqual(q.take(false, true), { line: '?', control: true });
  q.end();
  assert.equal(q.take(), undefined);
  assert.throws(() => q.send('x\ny'));
  assert.throws(() => q.send('x'.repeat(1023)));
});

test('ABI repeatedly allocates, executes and frees diagnostic requests', () => {
  const lines = [];
  const r = instantiate(readFileSync(new URL('./dist/rook-diag.wasm', import.meta.url)), { output: (channel, text) => lines.push([channel, text]) });
  for (let i = 0; i < 100; i++) {
    const request = { version: 1, operation: 'time.schedule', input: { stages: [{ moves: 1, baseSeconds: 1, incrementSeconds: 0 }], moveIndex: i } };
    assert.equal(r.call('rook_diagnostic', JSON.stringify(request)), 0);
    assert.deepEqual(JSON.parse(lines.at(-1)[1]).output, { seconds: i + 1 });
  }
});

test('ordinary CLI accepts split CRLF records and more than one queue capacity', async () => {
  const child = spawn(process.execPath, [runner]);
  let stdout = '', stderr = '';
  child.stdout.on('data', chunk => { stdout += chunk; });
  child.stderr.on('data', chunk => { stderr += chunk; });
  const done = new Promise(resolve => child.on('close', code => resolve(code)));
  child.stdin.write('cm_pa');
  child.stdin.end('rm\r\n' + 'cm_parm\n'.repeat(600) + 'quit\n');
  assert.equal(await done, 0);
  assert.equal(stderr, '');
  assert.equal(stdout, 'cm_parm\n'.repeat(601));
});

test('diagnostic and ordinary CLI propagate failure exits', () => {
  const bad = spawnSync(process.execPath, [diagnostic], { input: '{}\n', encoding: 'utf8' });
  assert.equal(bad.status, 1);
  assert.match(bad.stderr, /rook2-diag:/);
  const option = spawnSync(process.execPath, [runner, '--unsupported'], { encoding: 'utf8' });
  assert.equal(option.status, 1);
});

// No worker is needed to exercise the preset-to-time-control boundary.
test('ponder presets forward the released work-clock inputs with the standard schedule', async () => {
  const calls = [];
  const receiver = { setTimeControl: async value => calls.push(value) };
  for (const mode of ['easy', 'Hard', 'GM']) await Rook.prototype.setPonder.call(receiver, mode);
  assert.deepEqual(calls, [66_370, 94_830, 181_000].map(remainingMs => ({ remainingMs, baseMs: 300_000 })));
  assert.throws(() => Rook.prototype.setPonder.call(receiver, 'unknown'), /easy, hard or gm/);
});
