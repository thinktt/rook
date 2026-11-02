import { commandQueue } from './queue.mjs';
import { instantiate } from './runtime.mjs';

self.onmessage = async ({ data }) => {
  const queue = commandQueue(data.queue);
  try {
    const response = await fetch(data.wasm);
    if (!response.ok) throw Error(`WASM fetch: ${response.status}`);
    const runtime = await instantiate(await response.arrayBuffer(), {
      output: (channel, text) => self.postMessage({ channel, text }),
      poll: () => queue.take(),
    });
    const engine = runtime.api.rook_create(data.flags);
    self.postMessage({ ready: true });
    try {
      for (;;) {
        const record = queue.take(true, true);
        if (record === undefined) break;
        const status = runtime.call('rook_command', record.line, engine);
        // A late search control is harmless at idle and has no request completion.
        if (!record.control) self.postMessage({ done: true, status });
        if (status) break;
      }
    } finally { runtime.api.rook_destroy(engine); }
  } catch (error) {
    self.postMessage({ error: error.message });
  }
  self.close();
};
