// Run with a locally installed Playwright; it is a test tool, not a runtime dependency.
import assert from 'node:assert/strict';
import { readFileSync, readdirSync } from 'node:fs';
import { pathToFileURL } from 'node:url';
import { join } from 'node:path';
import { parseArgs } from 'node:util';
import { serve } from './serve.mjs';

const { values: options } = parseArgs({ options: {
  spec: { type: 'string' },
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
  await page.waitForFunction(() => window.worker);
  // The minimal worker starts accepting commands after its WASM startup.
  await page.evaluate(() => {
    window.worker.addEventListener('message', ({ data }) => {
      if (data.channel === 1 && data.text.startsWith('cm_parm rnd=')) {
        window.minimalCommandAnswered = true;
      }
      if (data.channel === 1 && data.text.startsWith('move ')) {
        window.minimalMove = data.text.trim();
      }
    });
  });
  await page.waitForFunction(() => {
    if (window.minimalCommandAnswered) return true;
    window.worker.postMessage('cm_parm rnd');
    return false;
  }, undefined, { polling: 100, timeout: 10_000 });

  await page.evaluate(() => {
    for (const line of ['cm_parm md=1 rnd=0', 'time 6637', 'go']) {
      window.worker.postMessage(line);
    }
  });
  const move = await page.waitForFunction(() => window.minimalMove);
  assert.match(await move.jsonValue(), /^move [a-h][1-8][a-h][1-8][nbrq]?$/);
  await move.dispose();

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

  await page.goto(new URL('benchmark.html', url).href);
  await page.waitForFunction(() => window.benchmark);
  const benchmark = await page.evaluate(async () => {
    await window.benchmark.ready;
    await window.benchmark.send('cm_parm rnd');
    await window.benchmark.send('quit');
    const { stdout, stderr, lastCommandStatus } = window.benchmark.state;
    return { stdout, stderr, lastCommandStatus, isolated: crossOriginIsolated };
  });
  assert.equal(benchmark.isolated, true);
  assert.match(benchmark.stdout, /^cm_parm rnd=/);
  assert.equal(benchmark.stderr, '');
  assert.equal(benchmark.lastCommandStatus, 2);
  assert.deepEqual(errors, []);
  console.log(JSON.stringify({ pass: true, chromium: await browser.version(), conformance }, null, 2));
} finally {
  clearTimeout(watchdog);
  await browser?.close();
  await new Promise(resolve => server.close(resolve));
}
