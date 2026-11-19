// Single producer / single consumer. Payload is published before the write index.
const slots = 256;
const width = 1024;
export function commandQueue(buffer = new SharedArrayBuffer(16 + slots * width)) {
  const state = new Int32Array(buffer, 0, 4);
  const bytes = new Uint8Array(buffer, 16);
  const encoder = new TextEncoder();
  const decoder = new TextDecoder('utf-8', { fatal: true });
  return {
    buffer,
    send(line, control = false) {
      if (line.length > 1022 || /[^\x01-\x09\x0b\x0c\x0e-\x7f]/.test(line)) throw Error('invalid command record');
      const read = Atomics.load(state, 0);
      const write = Atomics.load(state, 1);
      const next = (write + 1) % slots;
      if (next === read) return false;
      const data = encoder.encode(line);
      const offset = write * width;
      bytes[offset] = data.length & 255;
      bytes[offset + 1] = (data.length >> 8) | (control ? 128 : 0);
      bytes.set(data, offset + 2);
      Atomics.store(state, 1, next);
      Atomics.notify(state, 1);
      return true;
    },
    take(wait = false, metadata = false) {
      for (;;) {
        const read = Atomics.load(state, 0);
        const write = Atomics.load(state, 1);
        if (read !== write) {
          const offset = read * width;
          const length = bytes[offset] + ((bytes[offset + 1] & 127) << 8);
          const control = Boolean(bytes[offset + 1] & 128);
          const line = decoder.decode(bytes.slice(offset + 2, offset + 2 + length));
          Atomics.store(state, 0, (read + 1) % slots);
          return metadata ? { line, control } : line;
        }
        if (Atomics.load(state, 2)) return undefined; // EOF
        if (!wait) return null; // Nothing available during search.
        Atomics.wait(state, 1, write, 100);
      }
    },
    end() {
      Atomics.store(state, 2, 1);
      Atomics.notify(state, 1);
    },
  };
}
