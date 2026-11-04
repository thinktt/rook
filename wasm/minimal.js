// Minimal browser interface to rook.wasm.
//
// Usage from another JavaScript module:
//   import { createRook } from './minimal.js';
//   const rook = await createRook();
//   rook.reset();
//   rook.setPonder('easy');
//   rook.playMove('e2e4');
//   rook.go();
// Output appears in the console by default. Call rook.close() when finished.

// A worker runs JavaScript on a separate thread, keeping the page responsive
// while Rook searches. This function contains all the code for that worker.
async function workerMain() {
  // Commands cross into Rust as UTF-8 bytes; output comes back as UTF-8 bytes.
  const encoder = new TextEncoder();
  const decoder = new TextDecoder();
  let wasm;

  // These are the JavaScript hooks that WASM imports under the name "rook".
  const rook = {
    output(channel, pointer, length) {
      // Read the requested bytes from WASM memory and turn them into text.
      const text = decoder.decode(
        new Uint8Array(wasm.memory.buffer, pointer, length)
      );
      // Channel 1 is ordinary output; channel 2 is error/diagnostic output.
      self.postMessage({ channel, text });
    },

    // Calendar time supplies the default random seed.
    epoch_seconds: () => Math.floor(Date.now() / 1000),

    // -1 means no incoming search control. We haven't added a stop queue yet.
    poll_command: () => -1,
  };

  // The worker loads WASM itself from this fixed URL on the same server.
  const bytes = await fetch(`${self.location.origin}/dist/rook.wasm`).then(r => r.arrayBuffer());
  const { instance } = await WebAssembly.instantiate(bytes, { rook });
  wasm = instance.exports;
  wasm.rook_init();
  const engine = wasm.rook_create(0);

  // self is the worker's global object. Handle settings and text commands here.
  self.onmessage = ({ data }) => {
    if (data.setSeed !== undefined) {
      wasm.rook_set_seed(engine, data.setSeed);
      return;
    }

    if (data.setWorkClockPost !== undefined) {
      wasm.rook_set_work_clock_post(engine, data.setWorkClockPost);
      return;
    }

    // Rust cannot read a JavaScript string directly. Reserve space in WASM's
    // memory, then copy the encoded command into that space.
    const command = encoder.encode(data.command);
    const pointer = wasm.rook_alloc(command.length);
    try {
      new Uint8Array(wasm.memory.buffer, pointer, command.length).set(command);
      // Pass the engine handle and the command's address/length to Rust.
      // A 'go' command stays in this call until the search finishes.
      wasm.rook_command(engine, pointer, command.length);
    } finally {
      // Free the temporary command buffer, even if the call throws an error.
      wasm.rook_free(pointer, command.length);
    }
  };

  // The page can send commands once the engine and handler are ready.
  self.postMessage({ ready: true });
}

// This function runs in your page. Await it to get a ready-to-use engine.
// Supply a callback to display output somewhere other than the console.
export async function createRook(onOutput = console.log) {
  // Workers normally load a separate JS file. To keep this example in one file,
  // turn workerMain into source text followed by a call that starts it.
  const source = `await (${workerMain.toString()})();`;
  // A Blob holds that source text. Its temporary URL lets Worker load it.
  const workerURL = URL.createObjectURL(new Blob([source], { type: 'text/javascript' }));
  // A module worker allows top-level await while workerMain loads WASM.
  const worker = new Worker(workerURL, { type: 'module' });

  // Wait for the worker's ready message before returning to the caller.
  // The same handler forwards subsequent engine output to onOutput.
  await new Promise((resolve, reject) => {
    worker.onmessage = ({ data }) => {
      if (data.ready) resolve();
      else onOutput(data.text);
    };
    worker.onerror = event => reject(Error(event.message));
  });
  // The worker has loaded its source; release the temporary source URL.
  URL.revokeObjectURL(workerURL);

  const rook = {
    send(command) {
      worker.postMessage({ command });
    },

    reset() {
      rook.send('new');
      rook.send('force');
    },

    // Settings take effect between searches; messages wait if WASM is busy.
    setSeed(seed) {
      worker.postMessage({ setSeed: seed });
    },

    setWorkClockPost(enabled) {
      worker.postMessage({ setWorkClockPost: enabled });
    },

    // Accept a complete personality (with an "out" property), or just its weights.
    setPersonality(personality) {
      const weights = personality.out ?? personality;
      const assignments = Object.entries(weights)
        .map(([key, value]) => `${key}=${value}`).join(' ');
      rook.send('cm_parm default');
      rook.send(`cm_parm ${assignments}`);
    },

    // Apply a coordinate move, such as e2e4, without triggering an automatic reply.
    playMove(move) {
      rook.send('force');
      rook.send(move);
    },

    // Ask the engine to choose and play the next move. Output goes to onOutput.
    go() {
      rook.send('go');
    },

    // Times here are work-clock milliseconds, not a real-time search deadline.
    // The protocol uses minutes:seconds for the base and centiseconds for time.
    // Increments must be whole seconds (1000, 2000, etc.). moves=0 means sudden death.
    setTimeControl({ remainingMs, baseMs = remainingMs, incrementMs = 0, moves = 0 }) {
      const seconds = Math.floor(baseMs / 1000);
      const minutes = Math.floor(seconds / 60);
      const remainder = String(seconds % 60).padStart(2, '0');
      rook.send(`level ${moves} ${minutes}:${remainder} ${incrementMs / 1000}`);
      rook.send(`time ${Math.floor(remainingMs / 10)}`);
    },

    // These difficulty presets use the same time-control method above.
    setPonder(mode = 'easy') {
      const remainingMs = { easy: 66_370, hard: 94_830, gm: 181_000 }[mode.toLowerCase()];
      if (remainingMs === undefined) throw Error('Expected easy, hard or gm');
      rook.setTimeControl({ remainingMs, baseMs: 300_000 });
    },

    close() {
      worker.terminate();
    },
  };

  return rook;
}
