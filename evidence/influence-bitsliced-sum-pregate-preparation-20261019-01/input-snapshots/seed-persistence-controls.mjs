#!/usr/bin/env node
// Small live control of override retention, replacement and new-game lifetime.
import assert from 'node:assert/strict';
import {spawn} from 'node:child_process';
import {EventEmitter} from 'node:events';

const split = process.argv.indexOf('--');
assert(split >= 0 && split + 1 < process.argv.length,
  'usage: seed-persistence-controls.mjs -- ENGINE [ARGS]');
const command = process.argv.slice(split + 1);
const child = spawn(command[0], [...command.slice(1), '--diagnostic-seed-command'],
  {stdio: ['pipe', 'pipe', 'pipe']});
const events = new EventEmitter();
const lines = {stdout: [], stderr: []};
const consumed = {stdout: 0, stderr: 0};
const buffers = {stdout: '', stderr: ''};
let failure;
let outputBytes = 0;
let exitReceipt;
const outputCap = 64 * 1024;
const closed = new Promise(resolveClosed => child.once('close', (code, signal) => {
  exitReceipt = {code, signal};
  events.emit('stdout');
  events.emit('stderr');
  resolveClosed(exitReceipt);
}));
function fail(error) {
  if (!failure) failure = error;
  events.emit('stdout');
  events.emit('stderr');
}
for (const stream of ['stdout', 'stderr']) {
  child[stream].on('data', chunk => {
    outputBytes += chunk.length;
    if (outputBytes > outputCap) {
      fail(new Error('persistence control output cap exceeded'));
      return;
    }
    buffers[stream] += chunk.toString('utf8');
    const parts = buffers[stream].split('\n');
    buffers[stream] = parts.pop();
    for (const line of parts) {
      lines[stream].push(line);
      events.emit(stream);
    }
  });
}
child.on('error', fail);
child.stdin.on('error', fail);
function send(commands) {
  assert.ifError(failure);
  assert(!exitReceipt, 'engine unavailable');
  child.stdin.write(`${commands.join('\n')}\n`);
}
function wait(stream, pattern, from, timeoutMs = 30000) {
  return new Promise((resolveWait, rejectWait) => {
    const finish = (error, index) => {
      clearTimeout(timer);
      events.off(stream, check);
      if (error) rejectWait(error); else resolveWait(index);
    };
    const check = () => {
      if (failure) return finish(failure);
      const index = lines[stream].findIndex((line, at) => at >= from && pattern.test(line));
      if (index >= 0) return finish(null, index);
      if (exitReceipt) return finish(new Error('engine exited before expected line'));
    };
    const timer = setTimeout(() => finish(new Error(`timeout ${stream} ${pattern}`)), timeoutMs);
    events.on(stream, check);
    check();
  });
}
function consumeThrough(stream, through) {
  const from = consumed[stream];
  assert(through >= from, `already consumed ${stream} record`);
  consumed[stream] = through + 1;
  return lines[stream].slice(from, through + 1);
}
async function exchange(commands, stream, pattern) {
  const pending = wait(stream, pattern, consumed[stream]);
  send(commands);
  return consumeThrough(stream, await pending);
}
async function setup() {
  const output = await exchange(['xboard', 'new', 'force', 'nopost', 'easy',
    'level 0 5 0', 'cm_parm default md=1 rnd=0'],
  'stdout', /^cm_parm default md=1 rnd=0$/);
  assert.deepEqual(output, ['cm_parm default md=1 rnd=0'], 'setup output');
}
async function search(expectedSeed) {
  const move = exchange(['time 18100', 'otim 18100', 'go'],
    'stdout', /^move [a-h][1-8][a-h][1-8][qrbn]?$/i);
  const trace = wait('stderr', /^KING_SEARCH_SEED seed=\d+$/,
    consumed.stderr).then(index => consumeThrough('stderr', index));
  const [moveLines, traceLines] = await Promise.all([move, trace]);
  assert.equal(moveLines.length, 1, `unexpected search stdout: ${moveLines.join(' | ')}`);
  assert.deepEqual(traceLines, [`KING_SEARCH_SEED seed=${expectedSeed}`],
    'unexpected search stderr or consumed seed');
}
async function closeWithin(ms) {
  if (exitReceipt) return true;
  let timer;
  const onTime = await Promise.race([closed.then(() => true),
    new Promise(resolveTimeout => { timer = setTimeout(() => resolveTimeout(false), ms); })]);
  clearTimeout(timer);
  return onTime;
}
function assertComplete() {
  assert.ifError(failure);
  for (const stream of ['stdout', 'stderr']) {
    assert.equal(consumed[stream], lines[stream].length,
      `unconsumed ${stream}: ${lines[stream].slice(consumed[stream]).join(' | ')}`);
    assert.equal(buffers[stream], '', `trailing partial ${stream} output`);
  }
}
try {
  await setup();
  assert.deepEqual(await exchange(['king_seed 3735928559'], 'stdout',
    /^king_seed 3735928559$/), ['king_seed 3735928559']);
  await search(3735928559);
  await setup();
  await search(3735928559); // no new assignment after `new`
  await setup();
  assert.deepEqual(await exchange(['king_seed 17'], 'stdout', /^king_seed 17$/),
    ['king_seed 17']);
  await search(17);
  send(['quit']);
  if (!await closeWithin(5000)) {
    child.kill('SIGKILL');
    await closeWithin(5000);
    throw new Error('quit deadline exceeded');
  }
  assert.deepEqual(exitReceipt, {code: 0, signal: null});
  assertComplete();
  console.log(JSON.stringify({pass: true, searches: 3,
    consumedSeeds: [3735928559, 3735928559, 17], cleanExit: true}));
} catch (error) {
  if (!exitReceipt) {
    child.stdin.end();
    if (!await closeWithin(5000)) {
      child.kill('SIGKILL');
      await closeWithin(5000);
    }
  }
  console.error(JSON.stringify({pass: false, error: error.message,
    exit: exitReceipt, stdout: lines.stdout, stderr: lines.stderr,
    partial: buffers, outputBytes}));
  process.exitCode = 1;
}
