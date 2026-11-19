// Run with a locally installed Playwright; it is a test tool, not a runtime dependency.
import assert from 'node:assert/strict';
import { readFileSync, readdirSync } from 'node:fs';
import { pathToFileURL } from 'node:url';
import { join } from 'node:path';
import { parseArgs } from 'node:util';
import { serve } from './serve.mjs';

const { values: options } = parseArgs({ options: {
  spec: { type: 'string' },
  personalities: { type: 'string' },
} });

const { chromium } = await import(process.env.PLAYWRIGHT_MODULE ? pathToFileURL(process.env.PLAYWRIGHT_MODULE).href : 'playwright');
const server = await serve(0);
const url = `http://localhost:${server.address().port}/`;
let browser;
const watchdog = setTimeout(() => { server.close(); browser?.close(); throw Error('browser test deadline'); },
  options.spec ? 900_000 : 120_000);
try {
  browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  await page.goto(url);
  await page.waitForFunction(() => window.engine);
  const personality = options.personalities
    ? JSON.parse(readFileSync(options.personalities, 'utf8')).Stanley
    : { out: { opp: 100, opn: 33 } };
  assert(personality?.out, 'missing Stanley.out in personality file');
  const result = await page.evaluate(async personality => {
    const { Rook } = await import('./rook.js');
    const lines = [], moves = [], errors = [];
    const engine = await Rook.create({ onLine: line => lines.push(line), onMove: move => moves.push(move), onError: error => errors.push(error) });
    await engine.setPersonality(personality);
    await engine.setPonder('easy');
    await engine.setPonder('hard');
    await engine.setPonder('gm');
    await engine.playMove('e2e4');
    const first = await engine.go();
    const second = await engine.go(); // Retains the position after the previous engine move.
    await engine.newGame();
    await engine.setPersonality({ md: 99, rnd: 0, tts: 16777216 });
    await engine.setTimeControl({ remainingMs: 600000 });
    const started = performance.now();
    const stopped = await engine.go({ moveTimeMs: 25 });
    const elapsed = performance.now() - started;
    const unfinished = engine.go();
    await new Promise(resolve => setTimeout(resolve, 25));
    await engine.newGame(); // Aborts, waits for search completion, then resets.
    await unfinished;
    const aborted = lines.includes('aborting search ...');
    await engine.setPersonality(personality.out);
    const afterReset = await engine.go();
    // Controls that lose the race with a depth-one natural finish cannot ack
    // the next idle request. Also exercise stop immediately after go().
    for (let i = 0; i < 20; i++) {
      const move = engine.go();
      const control = engine.stop();
      await move;
      await control;
      await engine.send('cm_parm rnd');
    }
    engine.close();
    const result = { isolated: crossOriginIsolated, first, second, stopped, afterReset, elapsed, aborted, moves: moves.length, errors, personalityAck: lines.some(line => line.includes('opp=100 opn=33')) };
    window.engine.close();
    return result;
  }, personality);
  assert.equal(result.isolated, true);
  for (const name of ['first', 'second', 'stopped', 'afterReset']) assert.match(result[name], /^[a-h][1-8][a-h][1-8][nbrq]?$/);
  assert(result.elapsed < 5000, 'worker must observe deadline command during search');
  assert(result.aborted, 'reset must abort a live search');
  assert(result.personalityAck, 'actual yeoldwizard out weights acknowledged');
  assert.deepEqual(result.errors, []);
  assert.deepEqual(errors, []);
  const diagnostic = await page.evaluateHandle(async () => {
    const { instantiate, loadModule } = await import('./runtime.mjs');
    const module = await loadModule('./dist/rook-diag.wasm');
    return request => {
      const stdout = [], stderr = [];
      const runtime = instantiate(module, {
        output: (channel, line) => (channel === 1 ? stdout : stderr).push(line),
      });
      const status = runtime.call('rook_diagnostic', JSON.stringify(request));
      return { status, stdout, stderr };
    };
  });
  const assertDiagnostic = (actual, expected, id) => {
    assert.equal(actual.status, 0, `${id}: ${actual.stderr.join('\n')}`);
    assert.deepEqual(actual.stderr, [], id);
    assert.equal(actual.stdout.length, 1, id);
    assert.deepEqual(JSON.parse(actual.stdout[0]), { version: 1, output: expected }, id);
  };

  const stage = { moves: 1, baseSeconds: 1, incrementSeconds: 0 };
  const requests = Array.from({ length: 100 }, (_, moveIndex) => ({
    version: 1, operation: 'time.schedule', input: { stages: [stage], moveIndex },
  }));
  const checkSchedule = await diagnostic.evaluate((run, batch) => batch.map(run), requests);
  checkSchedule.forEach((actual, i) => assertDiagnostic(actual, { seconds: i + 1 }, 'time.schedule'));

  let conformance;
  if (options.spec) {
    const dir = join(options.spec, 'conformance', 'fixtures');
    const files = readdirSync(dir).filter(name => name.endsWith('.json')).sort();
    const optional = new Set(['output.analysisCandidateReport', 'search.analysisRootSequence']);
    conformance = { files: 0, cases: 0 };
    for (const file of files) {
      const { version, cases } = JSON.parse(readFileSync(join(dir, file), 'utf8'));
      assert.equal(version, 1, file);
      assert(cases.length, `${file}: empty fixture file`);
      const mandatory = cases.filter(test => !optional.has(test.request.operation));
      if (!mandatory.length) continue;
      for (let i = 0; i < mandatory.length; i += 32) {
        const batch = mandatory.slice(i, i + 32);
        const actual = await diagnostic.evaluate((run, requests) => requests.map(run), batch.map(test => test.request));
        batch.forEach((test, j) => assertDiagnostic(actual[j], test.expected, test.id));
      }
      conformance.files++;
      conformance.cases += mandatory.length;
    }
    assert(conformance.cases, 'no mandatory component fixtures found');
  }
  const rejected = await diagnostic.evaluate(run => run({}));
  assert.equal(rejected.status, 1);
  assert.deepEqual(rejected.stdout, []);
  assert.match(rejected.stderr.join('\n'), /^rook2-diag:/);
  await diagnostic.dispose();

  await page.goto(new URL('minimal.html', url).href);
  await page.waitForFunction(() => window.worker);
  // The minimal worker starts accepting commands after its WASM startup.
  await page.evaluate(() => {
    window.worker.addEventListener('message', ({ data }) => {
      if (data.channel === 1 && data.text.startsWith('cm_parm rnd=')) {
        window.minimalCommandAnswered = true;
      }
    });
  });
  await page.waitForFunction(() => {
    if (window.minimalCommandAnswered) return true;
    window.worker.postMessage('cm_parm rnd');
    return false;
  }, undefined, { polling: 100, timeout: 10_000 });

  await page.goto(new URL('benchmark.html', url).href);
  await page.waitForFunction(() => window.benchmark);
  const benchmark = await page.evaluate(async () => {
    await window.benchmark.ready;
    await window.benchmark.send('cm_parm rnd');
    await window.benchmark.send('quit');
    return window.benchmark.state;
  });
  assert.match(benchmark.stdout, /^cm_parm rnd=/);
  assert.equal(benchmark.stderr, '');
  assert.equal(benchmark.lastCommandStatus, 2);
  assert.deepEqual(errors, []);
  console.log(JSON.stringify({ pass: true, chromium: await browser.version(), ...result, conformance }, null, 2));

} finally {
  clearTimeout(watchdog);
  await browser?.close();
  await new Promise(resolve => server.close(resolve));
}
