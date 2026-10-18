#!/usr/bin/env python3
# Record exactly one original-runner request and native-backed adapter response.
import argparse,fcntl,json,os,signal,subprocess,sys
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--adapter',required=True);p.add_argument('--records',type=Path,required=True);a=p.parse_args()
assert set(os.sched_getaffinity(0)) <= {0,1,2,3,4,5,8,9,10,11,12,13}
a.records.mkdir(exist_ok=True)
with (a.records/'cursor').open('a+') as cursor:
 fcntl.flock(cursor,fcntl.LOCK_EX);cursor.seek(0);index=int(cursor.read() or '0');cursor.seek(0);cursor.truncate();cursor.write(str(index+1));cursor.flush()
stem=a.records/f'{index:06d}';request=sys.stdin.buffer.read();stem.with_suffix('.stdin').write_bytes(request)
child=None
# Original runner owns its timeout. If it stops this proxy, close its child too.
def stop(signum,frame):
 if child is not None and child.poll() is None:
  child.terminate()
 raise InterruptedError(f'proxy stopped by signal {signum}')
signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
out=b'';err=b'';code=125;failure=None
try:
 child=subprocess.Popen([a.adapter],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 out,err=child.communicate(request);code=child.returncode
except BaseException as error:
 failure=f'{type(error).__name__}: {error}'
 if child is not None and child.poll() is None:
  child.kill();out,err=child.communicate()
finally:
 stem.with_suffix('.stdout').write_bytes(out);stem.with_suffix('.stderr').write_bytes(err)
 stem.with_suffix('.json').write_text(json.dumps({'ordinal':index,'adapter':a.adapter,'child_pid':None if child is None else child.pid,'child_returncode':code,'failure':failure,'affinity':sorted(os.sched_getaffinity(0))},indent=2)+'\n')
sys.stdout.buffer.write(out);sys.stdout.buffer.flush();sys.stderr.buffer.write(err);sys.stderr.buffer.flush()
if code<0:
 signal.signal(-code,signal.SIG_DFL);os.kill(os.getpid(),-code)
sys.exit(code)
