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
function workerMain() {
  // JavaScript strings must become UTF-8 bytes before Rust can read them.
  // Output from Rust makes the reverse trip: UTF-8 bytes to JavaScript strings.
  const encoder = new TextEncoder();
  const decoder = new TextDecoder();

  // wasm holds the functions and memory exported by the WASM module.
  // engine is a handle identifying the Rust engine we create inside that memory.
  let wasm, engine;

  // self refers to the worker. Messages arrive here from the page.
  // There are two message shapes: { wasm: URL } and { command: 'text' }.
  self.onmessage = async ({ data }) => {
    if (data.wasm) {
      // The first message supplies the URL. Download the binary as raw bytes.
      const bytes = await fetch(data.wasm).then(r => r.arrayBuffer());

      // Instantiate means create a runnable copy of the WASM module.
      // Rook requires three JavaScript callbacks, grouped under the name "rook".
      const { instance } = await WebAssembly.instantiate(bytes, {
        rook: {
          output(channel, pointer, length) {
            // WASM passes numbers rather than a JavaScript string:
            // pointer is the starting byte address; length is the byte count.
            // Uint8Array gives us a view of those bytes in WASM's memory.
            const text = decoder.decode(
              new Uint8Array(wasm.memory.buffer, pointer, length)
            );
            // Send the decoded text back to the page. Channel 1 is ordinary
            // output; channel 2 is error/diagnostic output.
            self.postMessage({ channel, text });
          },
          // Date.now() returns milliseconds; Rook requests whole seconds.
          epoch_seconds: () => Math.floor(Date.now() / 1000),
          // Rook calls this during search to check for incoming controls.
          // -1 means none available. This minimal example has no stop queue.
          poll_command: () => -1,
        },
      });
      wasm = instance.exports;
      // Initialize the module, then create one engine with default flags (0).
      wasm.rook_init();
      engine = wasm.rook_create(0);
      // Tell the page it can now send commands.
      self.postMessage({ ready: true });
    } else {
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
    }
  };
}

// This function runs in your page. Await it to get a ready-to-use engine.
export async function createRook(
  // import.meta.url is this JS file's URL. Resolve the binary relative to it.
  wasmURL = new URL('./dist/rook.wasm', import.meta.url),
  // Supply your own callback to display output somewhere other than the console.
  onOutput = console.log,
) {
  // Workers normally load a separate JS file. To keep this example in one file,
  // turn workerMain into source text followed by a call that starts it.
  const source = `(${workerMain.toString()})();`;
  // A Blob holds that source text. Its temporary URL lets Worker load it.
  const workerURL = URL.createObjectURL(new Blob([source], { type: 'text/javascript' }));
  const worker = new Worker(workerURL);

  // Wait for the worker's ready message before returning to the caller.
  // The same handler forwards subsequent engine output to onOutput.
  await new Promise((resolve, reject) => {
    worker.onmessage = ({ data }) => {
      if (data.ready) resolve();
      else onOutput(data.text);
    };
    worker.onerror = event => reject(Error(event.message));
    // Give the worker an absolute URL so it can fetch the WASM binary.
    worker.postMessage({ wasm: new URL(wasmURL, import.meta.url).href });
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
