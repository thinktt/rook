#!/usr/bin/python3
"""Behavior-only native supervisor: inherited protocol descriptors, no oracle or relay."""
import hashlib, json, os, signal, sys
from pathlib import Path

def digest(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p, value):
    with Path(p).open('x') as f:
        json.dump(value, f, indent=2); f.write('\n')

image, separator, *options = sys.argv[1:]
assert separator == '--' and options in [[], ['--diagnostic-seed-command']]
assert image.startswith('/')
record_dir = Path(os.environ['ROOK2_FOCUSED_NATIVE_DIR'])
assert record_dir.is_dir()
record = {'schema':'rook2-behavior-native-wait-v1', 'supervisor_pid':os.getpid(),
          'supervisor_affinity':sorted(os.sched_getaffinity(0)), 'image':image,
          'image_sha256_before':digest(image), 'argv':[image,*options],
          'signals':[], 'failure':None, 'exec_error':None,
          'scope':'Direct native child, unchanged inherited protocol descriptors; no CPU or elapsed performance measurements.'}
assert record['supervisor_affinity'] == [0,1,2,3,4,5,8,9,10,11,12,13]
rfd,wfd = os.pipe2(os.O_CLOEXEC)
pid = os.fork()
if pid == 0:
    os.close(rfd)
    try:
        os.sched_setaffinity(0,{14})
        pre = {'pid':os.getpid(),'pgid':os.getpgrp(),'affinity':sorted(os.sched_getaffinity(0))}
        os.write(wfd, (json.dumps({'pre_exec':pre})+'\n').encode())
        os.execv(image,[image,*options])
    except BaseException as error:
        os.write(wfd,(json.dumps({'exec_error':repr(error)})+'\n').encode())
        os._exit(127)
os.close(wfd)
record['native_pid'] = pid
put(record_dir/f'{os.getpid()}.owned.json', {'supervisor_pid':os.getpid(),'native_pid':pid,'pgid':os.getpgrp()})
def forward(sig, frame):
    record['signals'].append(sig)
    try: os.kill(pid,sig)
    except ProcessLookupError: pass
for sig in [signal.SIGTERM,signal.SIGINT,signal.SIGHUP]: signal.signal(sig,forward)
with os.fdopen(rfd,'rb') as f: startup=f.read()
for line in startup.splitlines():
    row=json.loads(line)
    if 'pre_exec' in row: record['pre_exec']=row['pre_exec']
    if 'exec_error' in row: record['exec_error']=row['exec_error']
try:
    record['post_exec']={'exe':os.readlink(f'/proc/{pid}/exe'),
                        'argv':Path(f'/proc/{pid}/cmdline').read_bytes().rstrip(b'\0').decode().split('\0'),
                        'affinity':sorted(os.sched_getaffinity(pid)),
                        'tasks':sorted(int(p.name) for p in Path(f'/proc/{pid}/task').iterdir())}
except (FileNotFoundError,ProcessLookupError,PermissionError) as error:
    record['post_exec_unavailable']=type(error).__name__
waited,status=os.waitpid(pid,0)
record.update(waited_pid=waited, wait_status=status,
              native_exit_code=os.WEXITSTATUS(status) if os.WIFEXITED(status) else None,
              native_signal=os.WTERMSIG(status) if os.WIFSIGNALED(status) else None,
              image_sha256_after=digest(image))
if record['exec_error'] or record['image_sha256_before']!=record['image_sha256_after']:
    record['failure']='Native exec or image identity failure'
put(record_dir/f'{os.getpid()}.json',record)
sys.exit(record['native_exit_code'] if record['native_exit_code'] is not None else 128+record['native_signal'])
