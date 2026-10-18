import signal,time
signal.signal(signal.SIGTERM,signal.SIG_IGN)
print('READY',flush=True)
while True: time.sleep(1)
