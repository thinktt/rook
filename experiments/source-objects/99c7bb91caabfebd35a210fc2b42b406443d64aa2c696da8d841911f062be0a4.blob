#!/usr/bin/env node
// Independent protocol comparator. Fixture answers come from accepted records.
import assert from 'node:assert/strict';
import {spawn} from 'node:child_process';
import {createHash} from 'node:crypto';
import {readFileSync, writeFileSync, createReadStream} from 'node:fs';
import {resolve, dirname} from 'node:path';
import {fileURLToPath} from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const defaultFixture = resolve(here, 'accepted-games-v1.json');
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const MOVE = /^move\s+([a-h][1-8][a-h][1-8][qrbn]?)$/i;
const RESULT = /^(?:1-0|0-1|1\/2-1\/2) \{(?:Checkmate|Stalemate|Draw lack of wood|Draw 3 x position|Draw 50 moves|Movelist full)\}$/;
const POST = /^\s*(\d+)\s+([+-]?\d+)\s+([+-]?\d+)\s+(\d+)\s+(.+)$/;
const SEARCH_SEED = /^KING_SEARCH_SEED seed=(\d+)$/;

export function selectGames(fixture, ids = []) {
  validateFixture(fixture);
  assert(new Set(ids).size === ids.length, 'duplicate game selection');
  for (const id of ids) assert(fixture.games.some(game => game.id === id), `unknown game ${id}`);
  return ids.length ? fixture.games.filter(game => ids.includes(game.id)) : fixture.games;
}

const inventoryOf = games => ({games: games.length,
  searches: games.reduce((sum, game) => sum + game.plies.length, 0),
  families: Object.fromEntries(['main', 'openings', 'switching'].map(family =>
    [family, games.filter(game => game.family === family).length]))});

async function fileHash(path) {
  const digest = createHash('sha256');
  for await (const chunk of createReadStream(path)) digest.update(chunk);
  return digest.digest('hex');
}

// A report is a comparator receipt, not an independent attestation of its claims.
export function combineReports(fixture, fixtureSha256, reports) {
  validateFixture(fixture);
  assert(reports.length > 0, 'no reports');
  const first = reports[0];
  const completed = new Set();
  for (const report of reports) {
    assert.equal(report.version, 2);
    assert.equal(report.mode, 'independent-games');
    assert.equal(report.pass, true, 'failed or incomplete report');
    assert.equal(report.fixtureSha256, fixtureSha256);
    assert.match(report.executableSha256, /^[a-f0-9]{64}$/);
    assert.match(report.runnerSha256, /^[a-f0-9]{64}$/);
    assert.equal(report.executableSha256, first.executableSha256, 'different executable');
    assert.equal(report.runnerSha256, first.runnerSha256, 'different comparator');
    assert.deepEqual(report.command.slice(1), first.command.slice(1), 'different launch configuration');
    const selected = selectGames(fixture, report.selectedGameIds);
    assert(report.selectedGameIds.length > 0, 'missing selection');
    assert.deepEqual(report.fixtureInventory, inventoryOf(fixture.games));
    assert.deepEqual(report.inventory, inventoryOf(selected));
    assert.equal(report.games.length, selected.length);
    assert.equal(report.processes.length, selected.length);
    for (let index = 0; index < selected.length; index++) {
      const game = selected[index], result = report.games[index], process = report.processes[index];
      assert.deepEqual(result, {id: game.id, family: game.family,
        searches: game.plies.length, pass: true});
      assert.deepEqual(process.gameIds, [game.id], 'one owned process per game');
      assert.equal(process.family, game.family);
      assert.equal(process.code, 0);
      assert.equal(process.signal, null);
      assert.equal(process.forced, false);
      assert(!completed.has(game.id), `duplicate completed game ${game.id}`);
      completed.add(game.id);
    }
  }
  assert.equal(completed.size, fixture.games.length, 'incomplete game coverage');
  return {pass: true, completeIndependentGames: true,
    completeFocusedReplay: false, completeGameplayQualification: false,
    fixtureSha256, executableSha256: first.executableSha256,
    runnerSha256: first.runnerSha256, command: first.command,
    inventory: inventoryOf(fixture.games), reportCount: reports.length};
}

export function semanticPost(line) {
  const match = POST.exec(line);
  if (!match || Number(match[1]) < 1000) return null;
  const [depthToken, evaluation, engineCentiseconds, searchId] =
    match.slice(1, 5).map(Number);
  assert([depthToken, evaluation, engineCentiseconds, searchId].every(Number.isSafeInteger));
  return {depthToken, evaluation, searchId,
    pv: match[5].trim().replaceAll('0', 'O'), engineCentiseconds};
}

export function validateFixture(data) {
  assert.deepEqual(Object.keys(data).sort(), ['contract', 'games', 'launchOption', 'version']);
  assert.equal(data.version, 1);
  assert.equal(data.contract, 'GATE-REPLAY-FOCUSED');
  assert.equal(data.launchOption, '--diagnostic-seed-command');
  assert(Array.isArray(data.games) && data.games.length >= 12 && data.games.length <= 24);
  const counts = {main: 0, openings: 0, switching: 0};
  const ids = new Set();
  for (const game of data.games) {
    assert.deepEqual(Object.keys(game).sort(),
      ['family', 'id', 'initialMoves', 'personalityCommands', 'plies']);
    assert(Object.hasOwn(counts, game.family));
    counts[game.family]++;
    assert(typeof game.id === 'string' && game.id && !ids.has(game.id));
    ids.add(game.id);
    assert(Array.isArray(game.initialMoves));
    assert(game.initialMoves.every(move => /^[a-h][1-8][a-h][1-8][qrbn]?$/.test(move)));
    assert(game.personalityCommands && typeof game.personalityCommands === 'object');
    assert(Object.keys(game.personalityCommands).every(id => {
      const match = /^P(\d{3})$/.exec(id);
      return match !== null && Number(match[1]) >= 1 && Number(match[1]) <= 188;
    }));
    assert(Array.isArray(game.plies) && game.plies.length > 0 && game.plies.length <= 200);
    for (const row of game.plies) {
      assert.deepEqual(Object.keys(row).sort(), ['clockCentiseconds', 'expected', 'personality', 'seed']);
      assert(Number.isInteger(row.clockCentiseconds) && row.clockCentiseconds > 0);
      assert(Number.isInteger(row.seed) && row.seed >= 0 && row.seed <= 0xffffffff);
      const commands = game.personalityCommands[row.personality];
      assert(Array.isArray(commands) && commands.length >= 6);
      assert.equal(commands[0], 'cm_parm default');
      assert(commands.every(command => /^cm_parm [a-z0-9_ =-]+$/.test(command)));
      assert.deepEqual(Object.keys(row.expected).sort(), ['move', 'posts', 'result']);
      assert(MOVE.test(`move ${row.expected.move}`));
      assert(row.expected.result === null ||
        (typeof row.expected.result === 'string' && RESULT.test(row.expected.result)));
      assert(Array.isArray(row.expected.posts) && row.expected.posts.length > 0);
      for (const post of row.expected.posts) {
        assert.deepEqual(Object.keys(post).sort(),
          ['depthToken', 'engineCentiseconds', 'evaluation', 'pv', 'searchId']);
        assert([post.depthToken, post.engineCentiseconds, post.evaluation,
          post.searchId].every(Number.isSafeInteger));
        assert.equal(typeof post.pv, 'string');
      }
      if (row.expected.result !== null) assert.equal(row, game.plies.at(-1),
        'terminal result belongs only to the final search');
    }
  }
  assert(Object.values(counts).every(count => count > 0));
  return {games: data.games.length,
    searches: data.games.reduce((sum, game) => sum + game.plies.length, 0),
    families: counts};
}

class Session {
  constructor(command, option, maxBytes) {
    this.lines = {stdout: [], stderr: []};
    this.consumed = {stdout: 0, stderr: 0};
    this.buffer = {stdout: '', stderr: ''};
    this.bytes = 0;
    this.waiters = new Set();
    this.child = spawn(command[0], [...command.slice(1), option],
      {stdio: ['pipe', 'pipe', 'pipe']});
    for (const stream of ['stdout', 'stderr']) {
      this.child[stream].on('data', chunk => {
        this.bytes += chunk.length;
        if (this.bytes > maxBytes) {
          this.failure = new Error('process output cap exceeded');
          this.rejectWaiters(this.failure);
          return;
        }
        this.buffer[stream] += chunk.toString('utf8');
        const parts = this.buffer[stream].split('\n');
        this.buffer[stream] = parts.pop();
        for (const line of parts) {
          this.lines[stream].push(line);
          for (const waiter of [...this.waiters]) {
            if (waiter.stream === stream &&
                this.lines[stream].length - 1 >= waiter.from &&
                waiter.pattern.test(line)) {
              clearTimeout(waiter.timer);
              this.waiters.delete(waiter);
              waiter.resolve(this.lines[stream].length - 1);
            }
          }
        }
      });
    }
    this.child.on('error', error => { this.failure = error; this.rejectWaiters(error); });
    this.closed = new Promise(resolveClosed => {
      this.child.on('close', (code, signal) => {
        this.exit = {code, signal, forced: !!this.forced};
        this.rejectWaiters(new Error(`engine closed: ${code}/${signal}`));
        resolveClosed(this.exit);
      });
    });
  }
  rejectWaiters(error) {
    for (const waiter of this.waiters) {
      clearTimeout(waiter.timer);
      waiter.reject(error);
    }
    this.waiters.clear();
  }
  send(commands) {
    assert(!this.failure && !this.exit, 'engine unavailable');
    this.child.stdin.write(`${commands.join('\n')}\n`);
  }
  wait(stream, pattern, from, timeoutMs) {
    assert(!this.failure && !this.exit, 'engine unavailable');
    const found = this.lines[stream].findIndex((line, index) => index >= from && pattern.test(line));
    if (found >= 0) return Promise.resolve(found);
    return new Promise((resolveWait, rejectWait) => {
      const waiter = {stream, pattern, from, resolve: resolveWait, reject: rejectWait};
      waiter.timer = setTimeout(() => {
        this.waiters.delete(waiter);
        rejectWait(new Error(`timeout waiting for ${stream} ${pattern}`));
      }, timeoutMs);
      this.waiters.add(waiter);
    });
  }
  async sendAndWait(commands, stream, pattern, timeoutMs) {
    const from = this.consumed[stream];
    const wait = this.wait(stream, pattern, from, timeoutMs);
    this.send(commands);
    const through = await wait;
    return this.consumeThrough(stream, through);
  }
  consumeThrough(stream, through) {
    const from = this.consumed[stream];
    assert(through >= from, `already consumed ${stream} record`);
    this.consumed[stream] = through + 1;
    return this.lines[stream].slice(from, through + 1);
  }
  assertComplete() {
    assert.ifError(this.failure);
    for (const stream of ['stdout', 'stderr']) {
      assert.equal(this.consumed[stream], this.lines[stream].length,
        `unconsumed ${stream}: ${this.lines[stream].slice(this.consumed[stream]).join(' | ')}`);
      assert.equal(this.buffer[stream], '', `trailing partial ${stream} output`);
    }
  }
  async stop() {
    if (!this.exit) {
      try { this.send(['quit']); } catch { /* already closing */ }
      const deadline = new Promise(resolveDeadline => setTimeout(() => resolveDeadline(false), 5000));
      if (await Promise.race([this.closed.then(() => true), deadline]) === false && !this.exit) {
        this.forced = true;
        this.child.kill('SIGKILL');
      }
    }
    return this.closed;
  }
}

export async function replayFamily(games, command, option, timeoutMs, maxBytes, record) {
  const session = new Session(command, option, maxBytes);
  try {
    for (const game of games) {
      const setup = await session.sendAndWait(
        ['xboard', 'new', 'force', 'post', 'easy', 'level 0 5 0',
          ...game.initialMoves, 'cm_parm default'],
        'stdout', /^cm_parm default$/, timeoutMs);
      assert.deepEqual(setup, ['cm_parm default'], 'setup acknowledgment/output');
      let completed = 0;
      for (const row of game.plies) {
        const commands = game.personalityCommands[row.personality];
        const settings = await session.sendAndWait(['force', ...commands],
          'stdout', new RegExp(`^${commands.at(-1)}$`), timeoutMs);
        assert.deepEqual(settings, commands, 'each personality acknowledgment/output');
        const ack = await session.sendAndWait([`king_seed ${row.seed}`],
          'stdout', new RegExp(`^king_seed ${row.seed}$`), timeoutMs);
        assert.deepEqual(ack, [`king_seed ${row.seed}`]);
        const search = await session.sendAndWait(
          [`time ${row.clockCentiseconds}`, `otim ${row.clockCentiseconds}`, 'go'],
          'stdout', MOVE, timeoutMs);
        const stderrThrough = await session.wait('stderr', SEARCH_SEED,
          session.consumed.stderr, timeoutMs);
        const trace = session.consumeThrough('stderr', stderrThrough);
        assert.deepEqual(trace, [`KING_SEARCH_SEED seed=${row.seed}`], 'consumed seed/stderr');
        const moveLine = search.at(-1);
        const posts = search.slice(0, -1).map(semanticPost);
        assert(posts.length > 0 && posts.every(post => post !== null),
          `unexpected search output: ${search.join(' | ')}`);
        assert.deepEqual(posts, row.expected.posts, 'semantic posts');
        assert.equal(MOVE.exec(moveLine)[1].toLowerCase(), row.expected.move, 'selected move');
        if (row.expected.result !== null) {
          const escaped = row.expected.result.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
          const through = await session.wait('stdout', new RegExp(`^${escaped}$`),
            session.consumed.stdout, timeoutMs);
          const result = session.consumeThrough('stdout', through);
          assert.deepEqual(result, [row.expected.result], 'terminal result/output');
        }
        completed++;
      }
      record.games.push({id: game.id, family: game.family, searches: completed, pass: true});
    }
  } finally {
    const exit = await session.stop();
    record.processes.push({family: games[0].family, gameIds: games.map(game => game.id), ...exit,
      stdoutRecords: session.lines.stdout.length,
      stderrRecords: session.lines.stderr.length, outputBytes: session.bytes});
    session.assertComplete();
    assert.equal(exit.code, 0, 'engine exit');
    assert.equal(exit.signal, null, 'engine signal');
    assert.equal(exit.forced, false, 'forced cleanup');
  }
}

export async function main(argv) {
  const split = argv.indexOf('--');
  assert(split >= 0 && split + 1 < argv.length,
    'usage: run.mjs --report FRESH.json [--fixture FILE] [--game ID ...] [--timeout-ms N] -- /absolute/ENGINE [ARGS]');
  let reportPath, fixturePath = defaultFixture, timeoutMs = 300000;
  const ids = [], options = new Set();
  for (let index = 0; index < split; index += 2) {
    assert(index + 1 < split);
    assert(argv[index] === '--game' || !options.has(argv[index]), 'duplicate option');
    options.add(argv[index]);
    if (argv[index] === '--report') reportPath = resolve(argv[index + 1]);
    else if (argv[index] === '--fixture') fixturePath = resolve(argv[index + 1]);
    else if (argv[index] === '--timeout-ms') timeoutMs = Number(argv[index + 1]);
    else if (argv[index] === '--game') ids.push(argv[index + 1]);
    else assert.fail(`unknown option ${argv[index]}`);
  }
  assert(reportPath && Number.isInteger(timeoutMs) && timeoutMs > 0 && timeoutMs <= 300000);
  const fixtureBytes = readFileSync(fixturePath);
  const fixture = JSON.parse(fixtureBytes);
  const fixtureInventory = validateFixture(fixture);
  const selected = selectGames(fixture, ids);
  const inventory = inventoryOf(selected);
  const command = argv.slice(split + 1);
  assert(command[0].startsWith('/'), 'engine executable must be an absolute path');
  const record = {version: 2, mode: 'independent-games',
    selectedGameIds: selected.map(game => game.id), fixtureInventory,
    executableSha256: await fileHash(command[0]),
    runnerSha256: hash(readFileSync(fileURLToPath(import.meta.url))),
    fixtureSha256: hash(fixtureBytes), inventory,
    command, startedAt: new Date().toISOString(), pass: false, games: [], processes: []};
  writeFileSync(reportPath, `${JSON.stringify(record, null, 2)}\n`, {flag: 'wx'});
  try {
    for (const game of selected) {
      await replayFamily([game],
        command, fixture.launchOption, timeoutMs, 32 * 1024 * 1024, record);
      writeFileSync(reportPath, `${JSON.stringify(record, null, 2)}\n`);
    }
    record.pass = record.games.length === inventory.games &&
      record.processes.every(process => process.code === 0 &&
        process.signal === null && !process.forced);
    assert.equal(await fileHash(command[0]), record.executableSha256, 'executable changed during replay');
    record.completeIndependentGames = record.pass && selected.length === fixtureInventory.games;
    record.completeFocusedReplay = false;
    record.completeGameplayQualification = false;
  } catch (error) {
    record.pass = false;
    record.completeFocusedReplay = false;
    record.error = error.stack ?? error.message;
  } finally {
    record.finishedAt = new Date().toISOString();
    writeFileSync(reportPath, `${JSON.stringify(record, null, 2)}\n`);
  }
  console.log(JSON.stringify({pass: record.pass, games: record.games.length,
    searches: record.games.reduce((n, game) => n + game.searches, 0),
    processes: record.processes, error: record.error, reportPath}));
  if (!record.pass) process.exitCode = 1;
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  await main(process.argv.slice(2));
}
