import { parentPort, workerData } from 'node:worker_threads';
import { readFile } from 'node:fs/promises';
import { commandQueue } from './queue.mjs';
import { instantiate } from './runtime.mjs';

const queue = commandQueue(workerData.queue);
function take(wait) {
  const line = queue.take(wait);
  if (line != null) parentPort.postMessage({ drain: true });
  return line;
}
try {
  const runtime = await instantiate(await readFile(workerData.wasm), {
    output: (channel, text) => parentPort.postMessage({ channel, text }),
    poll: () => take(false),
  });
  const handle = runtime.api.rook_create(workerData.flags);
  let status = 0;
  try {
    for (;;) {
      const line = take(true);
      if (line === undefined) break;
      status = runtime.call('rook_command', line, handle);
      if (status) break;
    }
  } finally { runtime.api.rook_destroy(handle); }
  parentPort.postMessage({ exit: status === 1 ? 1 : 0 });
} catch (error) {
  parentPort.postMessage({ channel: 2, text: `rook-wasm: ${error.message}\n` });
  parentPort.postMessage({ exit: 1 });
}
