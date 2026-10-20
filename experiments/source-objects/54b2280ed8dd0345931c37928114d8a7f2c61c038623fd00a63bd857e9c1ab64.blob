#!/usr/bin/env node
// Offline collection only: never launches an engine.
import assert from 'node:assert/strict';
import {readFileSync, statSync, writeFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {dirname, resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {combineReports} from './run.mjs';
import {qualifyContinuousReport} from './continuous.mjs';

const args = process.argv.slice(2);
assert(args.length >= 3 && args[0] === '--report',
  'usage: combine.mjs --report FRESH.json [--fixture FILE] [--continuous REPORT] REPORT.json ...');
const output = resolve(args[1]);
let fixture = resolve(dirname(fileURLToPath(import.meta.url)), 'accepted-games-v1.json');
let start = 2;
let continuous;
const options=new Set();
while (args[start]?.startsWith('--')) {
  const option=args[start]; assert(!options.has(option),'duplicate option'); options.add(option);
  assert(args[start+1]&&!args[start+1].startsWith('--'),'missing option value');
  if(option==='--fixture')fixture=resolve(args[start+1]);
  else if(option==='--continuous')continuous=resolve(args[start+1]);
  else assert.fail('unknown option '+option);
  start+=2;
}
const paths = args.slice(start);
assert(paths.length > 0 && paths.length <= 24, 'report count');
assert(new Set(paths.map(path => resolve(path))).size === paths.length, 'duplicate report path');
const bytes = readFileSync(fixture);
const reports = paths.map(path => {
  assert(statSync(path).size <= 1024 * 1024, 'individual report exceeds 1MiB');
  return JSON.parse(readFileSync(path, 'utf8'));
});
let result = combineReports(JSON.parse(bytes),
  createHash('sha256').update(bytes).digest('hex'), reports);
if(continuous){
  assert(statSync(continuous).size<=1024*1024,'continuity report exceeds 1MiB');
  result=qualifyContinuousReport(JSON.parse(bytes),result,JSON.parse(readFileSync(continuous,'utf8')));
  result.continuity.report={path:continuous,sha256:createHash('sha256').update(readFileSync(continuous)).digest('hex')};
}
result.reports = paths.map(path => ({path: resolve(path),
  sha256: createHash('sha256').update(readFileSync(path)).digest('hex')}));
writeFileSync(output, `${JSON.stringify(result, null, 2)}\n`, {flag: 'wx'});
console.log(JSON.stringify(result));
