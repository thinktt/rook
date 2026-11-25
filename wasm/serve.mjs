import { once } from 'node:events';
import { readFile } from 'node:fs/promises';
import { createServer } from 'node:http';
import { extname, resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';
import { parseArgs } from 'node:util';

const root = fileURLToPath(new URL('.', import.meta.url));
const contentTypes = new Map([
  ['.html', 'text/html; charset=utf-8'],
  ['.js', 'text/javascript; charset=utf-8'],
  ['.mjs', 'text/javascript; charset=utf-8'],
  ['.json', 'application/json'],
  ['.wasm', 'application/wasm'],
]);

export async function serve(port = 8080) {
  const server = createServer(async (request, response) => {
    const end = (status, headers) => {
      response.writeHead(status, headers).end();
    };
    response.setHeader('Cross-Origin-Opener-Policy', 'same-origin');
    response.setHeader('Cross-Origin-Embedder-Policy', 'require-corp');
    response.setHeader('Cache-Control', 'no-store');

    if (request.method !== 'GET' && request.method !== 'HEAD') {
      return end(405, { Allow: 'GET, HEAD' });
    }
    let pathname;
    try {
      pathname = decodeURIComponent(new URL(request.url, 'http://localhost').pathname);
    } catch {
      return end(400);
    }
    const file = resolve(root, pathname === '/' ? 'rook-test.html' : '.' + pathname);
    const contentType = contentTypes.get(extname(file));
    if (!file.startsWith(root.endsWith(sep) ? root : root + sep) || !contentType) {
      return end(404);
    }

    try {
      const body = await readFile(file);
      response.writeHead(200, { 'Content-Type': contentType, 'Content-Length': body.length });
      response.end(request.method === 'HEAD' ? undefined : body);
    } catch (error) {
      end(['ENOENT', 'ENOTDIR', 'EISDIR'].includes(error.code) ? 404 : 500);
    }
  });
  server.listen(port, '127.0.0.1');
  await once(server, 'listening');
  return server;
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const { values } = parseArgs({ options: { port: { type: 'string', default: '8080' } } });
  const server = await serve(Number(values.port));
  console.log(`Open http://localhost:${server.address().port}/`);
}
