// Run with a locally installed Playwright; it is a test tool, not a runtime dependency.
import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { readFileSync } from 'node:fs';
import { once } from 'node:events';
import { pathToFileURL } from 'node:url';
const { chromium } = await import(process.env.PLAYWRIGHT_MODULE ? pathToFileURL(process.env.PLAYWRIGHT_MODULE).href : 'playwright');
const server = spawn('python3', [new URL('./serve.py', import.meta.url).pathname, '--port', '0']);
let browser;
const watchdog = setTimeout(() => { server.kill(); browser?.close(); throw Error('browser test deadline'); }, 120_000);
try {
  const [chunk] = await once(server.stdout, 'data');
  const url = String(chunk).match(/http:\/\/localhost:\d+\//)[0];
  browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  await page.goto(url);
  await page.waitForFunction(() => window.engine);
  const personality = JSON.parse(readFileSync(process.argv[2] || '/home/legolas/yeoldwizard/personalities.json', 'utf8')).Stanley;
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
    const result = { isolated: crossOriginIsolated, first, second, stopped, afterReset, elapsed, aborted, moves: moves.length, errors, personalityAck: lines.find(line => line.includes('opp=100 opn=33')) };
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
  console.log(JSON.stringify({ pass: true, chromium: await browser.version(), ...result }, null, 2));
} finally {
  clearTimeout(watchdog);
  await browser?.close();
  server.kill();
  await once(server, 'close');
}
