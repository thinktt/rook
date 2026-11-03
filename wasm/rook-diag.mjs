#!/usr/bin/env node
import { readFile } from 'node:fs/promises';
import { instantiate } from './runtime.mjs';

try {
  const wasm = process.argv[2] || new URL('./dist/rook-diag.wasm', import.meta.url);
  const chunks = [];
  for await (const chunk of process.stdin) chunks.push(chunk);
  const request = Buffer.concat(chunks).toString('utf8');
  if (!request.endsWith('\n')) throw Error('request must end in newline');
  const runtime = await instantiate(await readFile(wasm), {
    output: (channel, text) => (channel === 1 ? process.stdout : process.stderr).write(text),
  });
  process.exitCode = runtime.call('rook_diagnostic', request);
} catch (error) {
  console.error(`rook2-diag: ${error.message}`);
  process.exitCode = 1;
}
