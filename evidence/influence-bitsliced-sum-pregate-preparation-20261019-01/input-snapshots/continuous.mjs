#!/usr/bin/env node
import assert from 'node:assert/strict';
import {readFileSync, writeFileSync, createReadStream} from 'node:fs';
import {createHash} from 'node:crypto';
import {resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {validateFixture, replayFamily} from './run.mjs';

const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const fixturePath = new URL('./accepted-games-v1.json', import.meta.url);
const planPath = new URL('./continuous-switching-v1.json', import.meta.url);
const canonicalPlan = JSON.parse(readFileSync(planPath));

export function continuousGames(fixture, plan = canonicalPlan) {
  validateFixture(fixture);
  assert.deepEqual(plan, canonicalPlan, 'continuous schedule is exact');
  return plan.segments.map(segment => {
    const game = fixture.games.find(game => game.id === segment.game);
    assert(game && game.plies.length >= segment.searches);
    const plies = game.plies.slice(0, segment.searches);
    assert(plies.every(row => row.expected.result === null), 'prefix must not be terminal');
    return {...game, plies};
  });
}

export function qualifyContinuousReport(fixture, independent, report) {
  assert.equal(independent.pass, true);
  assert.equal(independent.completeIndependentGames, true, 'independent coverage required');
  const games = continuousGames(fixture);
  assert.equal(report.version, 1);
  assert.equal(report.mode, 'continuous-switching');
  assert.equal(report.pass, true, 'continuity failed or incomplete');
  // Earlier native reports used a fixed 60000ms wait and omitted this field.
  const hostTimeoutMs = report.hostTimeoutMs === undefined ? 60000 : report.hostTimeoutMs;
  assert(Number.isInteger(hostTimeoutMs) && hostTimeoutMs > 0 && hostTimeoutMs <= 300000,
    'invalid continuity host timeout');
  assert.equal(report.fixtureSha256, independent.fixtureSha256);
  assert.equal(report.executableSha256, independent.executableSha256, 'different executable');
  assert.deepEqual(report.command.slice(1), independent.command.slice(1), 'different launch configuration');
  assert.equal(report.scheduleSha256, hash(readFileSync(planPath)), 'different schedule');
  assert.equal(report.comparatorSha256, independent.runnerSha256, 'different comparator');
  assert.match(report.runnerSha256, /^[a-f0-9]{64}$/);
  assert.deepEqual(report.games, games.map(game => ({id:game.id, family:game.family,
    searches:game.plies.length, pass:true})));
  assert.equal(report.processes.length, 1, 'one continuous process');
  const process = report.processes[0];
  assert.deepEqual(process.gameIds, games.map(game => game.id));
  assert.equal(process.code, 0); assert.equal(process.signal, null); assert.equal(process.forced, false);
  return {...independent, completeFocusedReplay:true,
    continuity:{segments:games.length,searches:8,processes:1,hostTimeoutMs,runnerSha256:report.runnerSha256}};
}

export function parseContinuousArgs(args) {
  const split = args.indexOf('--');
  assert(split >= 0 && split + 1 < args.length,
    'usage: continuous.mjs --report FRESH.json [--timeout-ms N] -- /absolute/ENGINE [ARGS]');
  let reportPath, hostTimeoutMs = 60000;
  const seen = new Set();
  for (let index = 0; index < split; index += 2) {
    assert(index + 1 < split, 'missing option value');
    const option = args[index];
    assert(!seen.has(option), 'duplicate option');
    seen.add(option);
    if (option === '--report') reportPath = resolve(args[index + 1]);
    else if (option === '--timeout-ms') hostTimeoutMs = Number(args[index + 1]);
    else assert.fail(`unknown option ${option}`);
  }
  assert(reportPath, 'report required');
  assert(Number.isInteger(hostTimeoutMs) && hostTimeoutMs > 0 && hostTimeoutMs <= 300000,
    'invalid continuity host timeout');
  const command = args.slice(split + 1);
  assert(command[0].startsWith('/'), 'engine executable must be an absolute path');
  return {reportPath, command, hostTimeoutMs};
}

async function executableHash(path) {
  const digest = createHash('sha256');
  for await (const bytes of createReadStream(path)) digest.update(bytes);
  return digest.digest('hex');
}

export async function main(args) {
  const {reportPath, command, hostTimeoutMs} = parseContinuousArgs(args);
  const bytes = readFileSync(fixturePath), fixture = JSON.parse(bytes);
  const games = continuousGames(fixture);
  const record = {version: 1, mode: 'continuous-switching', pass: false,
    hostTimeoutMs,
    completeFocusedReplay: false, completeGameplayQualification: false,
    fixtureSha256: hash(bytes), scheduleSha256: hash(readFileSync(planPath)),
    runnerSha256: hash(readFileSync(fileURLToPath(import.meta.url))),
    comparatorSha256: hash(readFileSync(new URL('./run.mjs', import.meta.url))),
    executableSha256: await executableHash(command[0]), command,
    startedAt: new Date().toISOString(), games: [], processes: []};
  writeFileSync(reportPath, `${JSON.stringify(record, null, 2)}\n`, {flag: 'wx'});
  try {
    // One process across all segments; existing new/setup and search comparison.
    await replayFamily(games, command, fixture.launchOption, hostTimeoutMs, 8 * 1024 * 1024, record);
    assert.equal(record.processes.length, 1);
    assert.equal(record.games.length, 4);
    assert.equal(record.games.reduce((sum, game) => sum + game.searches, 0), 8);
    assert.equal(await executableHash(command[0]), record.executableSha256);
    record.pass = true;
  } catch (error) { record.error = error.stack ?? String(error); }
  finally {
    record.finishedAt = new Date().toISOString();
    writeFileSync(reportPath, `${JSON.stringify(record, null, 2)}\n`);
  }
  console.log(JSON.stringify(record));
  if (!record.pass) process.exitCode = 1;
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url))
  await main(process.argv.slice(2));
