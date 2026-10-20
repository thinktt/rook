#!/usr/bin/env node
// Focused no-search wire controls for the opt-in gate seed command.
import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import {resolve} from 'node:path';
import {fileURLToPath} from 'node:url';

export function parseControlArgs(argv) {
  const split = argv.indexOf('--');
  assert(split >= 0 && split + 1 < argv.length,
    'usage: seed-command-controls.mjs [--check-sequence-conflict] -- ENGINE [ARGS]');
  const options = argv.slice(0, split);
  assert(options.every(option => option === '--check-sequence-conflict'),
    'unknown control option');
  assert(options.length <= 1, 'duplicate control option');
  return {command: argv.slice(split + 1), checkSequenceConflict: options.length === 1};
}

function main(argv) {
const {command, checkSequenceConflict} = parseControlArgs(argv);
const run = (lines, options = ['--diagnostic-seed-command']) => {
  const child = spawnSync(command[0], [...command.slice(1), ...options], {
    input: `${lines.join('\n')}\n`, encoding: 'utf8', timeout: 5000,
    maxBuffer: 64 * 1024,
  });
  assert.equal(child.error, undefined, child.error?.message);
  assert.equal(child.signal, null);
  return child;
};

const valid = run(['xboard', 'king_seed 0', 'king_seed 4294967295',
  'king_seed 0xffffffff', 'king_seed 010', 'king_seed +7',
  'king_seed -0', '\tking_seed\t0X10  ', 'king_seed 31\r', 'quit']);
assert.equal(valid.status, 0);
assert.equal(valid.stderr, '');
assert.equal(valid.stdout,
  'king_seed 0\nking_seed 4294967295\nking_seed 4294967295\n' +
  'king_seed 8\nking_seed 7\nking_seed 0\nking_seed 16\nking_seed 31\n');

const invalid = ['08', '4294967296', '-1', '7 extra', '1.0', '+', 'abc', ''];
for (const value of invalid) {
  const child = run([`king_seed ${value}`]);
  assert.equal(child.status, 1, value);
  assert.equal(child.stdout, '', value);
  assert.equal(child.stderr, 'king-native: invalid diagnostic seed command\n', value);
}

const noValue = run(['king_seed', 'quit']);
assert.equal(noValue.status, 0);
assert.equal(noValue.stdout, 'Error (unknown command): king_seed\n');
assert.equal(noValue.stderr, '');
const ordinary = run(['king_seed 7', 'quit'], []);
assert.equal(ordinary.status, 0);
assert.equal(ordinary.stdout, 'Error (unknown command): king_seed\n');
assert.equal(ordinary.stderr, '');
if (checkSequenceConflict) {
  const conflict = run([], ['--diagnostic-seed-command', '--random-seed=7']);
  assert.equal(conflict.status, 1);
  assert.equal(conflict.stdout, '');
  assert.equal(conflict.stderr,
    'king-native: diagnostic seed commands conflict with seed sequence flags\n');
}

console.log(JSON.stringify({pass: true, acceptedAssignments: 8,
  invalidAssignments: invalid.length, noValueUnknown: true,
  normalModeUnknown: true, conflictChecked: checkSequenceConflict}));
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  main(process.argv.slice(2));
}
