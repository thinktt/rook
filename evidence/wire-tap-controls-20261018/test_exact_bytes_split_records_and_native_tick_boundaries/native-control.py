import sys,time
print('READY',flush=True)
for line in sys.stdin.buffer:
    if line == b'go\n':
        until=time.process_time()+0.03
        value=0
        while time.process_time()<until: value=(value+17)%65521
        sys.stdout.buffer.write(b'move a1'); sys.stdout.buffer.flush()
        time.sleep(0.01)
        sys.stdout.buffer.write(b'b2\n'); sys.stdout.buffer.flush()
        sys.stderr.buffer.write(b'synthetic-stderr\n'); sys.stderr.buffer.flush()
    elif line == b'quit\n':
        time.sleep(0.03)
        raise SystemExit(int(sys.argv[1]))
