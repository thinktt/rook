#!/usr/bin/env node
// Conformance test machinery: no engine behavior implementation lives here.
import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import {readFileSync, readdirSync} from 'node:fs';
import {dirname, resolve} from 'node:path';
import {fileURLToPath} from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const hash = bytes => createHash('sha256').update(bytes).digest('hex');

export function executeCase(test, command, timeout = 5000) {
  const child = spawnSync(command[0], command.slice(1), {
    input: JSON.stringify(test.request) + '\n', encoding: 'utf8',
    timeout, maxBuffer: 1024 * 1024,
  });
  const result = {id: test.id, contract: test.contract, pass: false,
    exit: {code: child.status, signal: child.signal}};
  try {
    assert(!child.error, child.error?.message);
    assert.equal(child.status, 0, 'adapter did not exit successfully');
    assert.equal(child.signal, null, 'adapter was signaled');
    const response = JSON.parse(child.stdout);
    assert.deepEqual(Object.keys(response).sort(), ['output', 'version']);
    assert.equal(response.version, 1);
    result.actual = response.output;
    assert.deepEqual(response.output, test.expected);
    result.pass = true;
  } catch (error) {
    result.error = error.message;
  }
  return result;
}

export function loadFixtures(paths) {
  const seen = new Set();
  const files = paths.map(path => {
    const bytes = readFileSync(path);
    const data = JSON.parse(bytes);
    assert.equal(data.version, 1);
    assert(Array.isArray(data.cases) && data.cases.length > 0, 'empty fixture file');
    for (const test of data.cases) {
      assert.equal(typeof test.id, 'string');
      assert(test.id.length && !seen.has(test.id), 'missing/duplicate fixture ID');
      seen.add(test.id);
      assert.equal(typeof test.contract, 'string');
      assert.equal(test.request?.version, 1);
      assert.equal(typeof test.request.operation, 'string');
      assert(test.request.input && typeof test.request.input === 'object');
      assert(test.expected && typeof test.expected === 'object');
      assert.deepEqual(Object.keys(test.request).sort(), ['input', 'operation', 'version']);
    }
    return {path, sha256: hash(bytes), cases: data.cases};
  });
  return files;
}

function main(argv) {
  const split = argv.indexOf('--');
  assert(split >= 0 && argv.length > split + 1,
    'usage: run.mjs [--fixtures FILE] [--timeout MS] -- ADAPTER [ARGS]');
  const paths = [];
  let timeout = 5000;
  for (let i = 0; i < split; i += 2) {
    assert(i + 1 < split, 'missing option value');
    if (argv[i] === '--fixtures') paths.push(resolve(argv[i + 1]));
    else if (argv[i] === '--timeout') timeout = Number(argv[i + 1]);
    else throw new Error(`unknown option ${argv[i]}`);
  }
  assert(Number.isInteger(timeout) && timeout > 0 && timeout <= 60000);
  if (!paths.length) {
    for (const name of readdirSync(resolve(here, 'fixtures')).sort()) {
      if (name.endsWith('.json')) paths.push(resolve(here, 'fixtures', name));
    }
  }
  assert(paths.length, 'no fixture files');
  const files = loadFixtures(paths);
  const command = argv.slice(split + 1);
  const results = files.flatMap(file => file.cases.map(test =>
    executeCase(test, command, timeout)));
  const report = {version: 1, completeEngineQualification: false,
    pass: results.every(r => r.pass),
    files: files.map(({path, sha256, cases}) => ({path, sha256, count: cases.length})),
    command, results};
  console.log(JSON.stringify(report, null, 2));
  if (!report.pass) process.exitCode = 1;
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try { main(process.argv.slice(2)); }
  catch (error) { console.error(error.message); process.exitCode = 1; }
}
