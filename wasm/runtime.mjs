// The same WASM host imports in Node and the browser. No WASI or bindings package.
export function instantiate(bytes, { output, poll = () => null }) {
  let api;
  const encoder = new TextEncoder();
  const decoder = new TextDecoder();
  const imports = { rook: {
    output(channel, pointer, length) {
      output(channel, decoder.decode(new Uint8Array(api.memory.buffer, pointer, length)));
    },
    epoch_seconds: () => Math.floor(Date.now() / 1000) >>> 0,
    poll_command(pointer, capacity) {
      const line = poll();
      if (line == null) return -1;
      const data = encoder.encode(line);
      if (data.length > capacity) return -2;
      new Uint8Array(api.memory.buffer, pointer, data.length).set(data);
      return data.length;
    },
  } };
  const instance = new WebAssembly.Instance(new WebAssembly.Module(bytes), imports);
  api = instance.exports;
  api.rook_init();
  return {
    api,
    call(name, text, ...prefix) {
      const data = encoder.encode(text);
      const pointer = api.rook_alloc(data.length);
      try {
        new Uint8Array(api.memory.buffer, pointer, data.length).set(data);
        return api[name](...prefix, pointer, data.length);
      } finally {
        api.rook_free(pointer, data.length);
      }
    },
  };
}
