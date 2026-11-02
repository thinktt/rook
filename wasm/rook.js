import { commandQueue } from './queue.mjs';

// Keep the engine in one worker for the lifetime of this object.
export class Rook {
  static async create(options = {}) {
    if (!globalThis.crossOriginIsolated) {
      throw Error('Rook needs cross-origin isolation; see wasm/README.md.');
    }
    const engine = new Rook(options);
    await engine.ready;
    await engine.newGame();
    return engine;
  }

  constructor({ wasm = new URL('./dist/rook.wasm', import.meta.url),
    onLine = () => {}, onPost = () => {}, onMove = () => {}, onError = console.error } = {}) {
    this.queue = commandQueue();
    this.worker = new Worker(new URL('./worker.mjs', import.meta.url), { type: 'module' });
    this.tail = Promise.resolve();
    this.search = null;
    this.closed = false;
    this.pending = null;
    this.ready = new Promise((resolve, reject) => {
      this.worker.onerror = event => { reject(Error(event.message)); this.fail(Error(event.message)); };
      this.worker.onmessage = ({ data }) => {
        if (data.ready) resolve();
        if (data.error) { const error = Error(data.error); reject(error); this.fail(error); }
        if (data.channel === 2) onError(data.text.trimEnd());
        if (data.channel === 1) {
          for (const line of data.text.trimEnd().split('\n')) {
            onLine(line);
            if (line.startsWith('move ')) { this.lastMove = line.slice(5); onMove(this.lastMove); }
            else if (/^\s*\d+\s/.test(line)) onPost(line);
          }
        }
        if (data.done) {
          const pending = this.pending;
          this.pending = null;
          if (data.status === 1) { pending?.reject(Error('Engine command failed')); this.close(); }
          else pending?.resolve(this.lastMove);
        }
      };
    });
    this.worker.postMessage({ queue: this.queue.buffer, wasm: String(wasm), flags: 0 });
  }

  fail(error) {
    this.pending?.reject(error);
    this.pending = null;
    this.close();
  }

  // Raw ordinary-protocol commands, serialized at idle boundaries.
  send(line, beforeSend = () => {}) {
    const task = this.tail.then(() => {
      if (this.closed) throw Error('Engine is closed');
      return new Promise((resolve, reject) => {
        this.pending = { resolve, reject };
        try { beforeSend(); if (!this.queue.send(line)) throw Error('Command queue is full'); }
        catch (error) { this.pending = null; reject(error); }
      });
    });
    this.tail = task.catch(() => {});
    return task;
  }

  async newGame() {
    await this.abort();
    for (const command of ['new', 'force', 'easy', 'post']) await this.send(command);
  }

  async setPersonality(personality) {
    await this.abort();
    const weights = personality.out ?? personality;
    const assignments = Object.entries(weights).map(([key, value]) => {
      if (!/^[a-z][a-z0-9_]*$/i.test(key) || !/^[+-]?\d+$/.test(String(value))) {
        throw Error(`Invalid personality weight: ${key}`);
      }
      return `${key}=${value}`;
    });
    await this.send('cm_parm default');
    await this.send(`cm_parm ${assignments.join(' ')}`);
  }

  async setTimeControl({ remainingMs, baseMs = remainingMs, incrementMs = 0, moves = 0 }) {
    if (![remainingMs, baseMs, incrementMs, moves].every(Number.isFinite) ||
        remainingMs < 0 || baseMs < 1000 || incrementMs < 0 || moves < 0 ||
        incrementMs % 1000 || moves % 1) throw Error('Invalid time control (increment uses whole seconds)');
    const seconds = Math.floor(baseMs / 1000);
    await this.send(`level ${moves} ${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, '0')} ${incrementMs / 1000}`);
    await this.send(`time ${Math.floor(remainingMs / 10)}`);
  }

  setPonder(mode = 'easy') {
    const remainingMs = { easy: 66_370, hard: 94_830, gm: 181_000 }[mode.toLowerCase()];
    if (remainingMs === undefined) throw Error('Expected easy, hard or gm');
    return this.setTimeControl({ remainingMs, baseMs: 300_000 });
  }

  async playMove(move) {
    if (!/^[a-h][1-8][a-h][1-8][nbrq]?$/.test(move)) throw Error('Expected a coordinate move');
    await this.send('force');
    await this.send(move);
  }

  go({ moveTimeMs } = {}) {
    if (this.search) throw Error('Engine is already searching');
    if (moveTimeMs !== undefined && (!Number.isFinite(moveTimeMs) || moveTimeMs <= 0)) throw Error('Invalid moveTimeMs');
    this.lastMove = undefined;
    // The deadline starts when go reaches the worker, after preceding commands.
    let timer;
    this.searchReady = new Promise(resolve => { this.markSearchReady = resolve; });
    const task = this.send('go', () => {
      this.markSearchReady();
      if (moveTimeMs !== undefined) timer = setTimeout(() => this.stop(), moveTimeMs);
    });
    this.search = task.finally(() => { this.markSearchReady(); clearTimeout(timer); this.search = null; });
    return this.search;
  }

  // These bypass idle serialization: WASM reads them at its existing search polls.
  async stop() {
    if (this.search) { await this.searchReady; if (this.search) this.queue.send('?', true); }
  }
  async abort() {
    if (this.search) {
      const search = this.search;
      await this.searchReady;
      if (this.search) this.queue.send('force', true);
      await search;
    }
  }

  close() {
    if (this.closed) return;
    this.closed = true;
    this.pending?.reject(Error('Engine is closed'));
    this.pending = null;
    this.queue.end();
    this.worker.terminate();
  }
}
export default Rook;
