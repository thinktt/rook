#!/usr/bin/env python3
"""Direct wait4 for one multithreaded native child; no protocol relay."""
import argparse, hashlib, json, os, signal, time
from pathlib import Path

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--engine',type=Path,required=True);p.add_argument('--record',type=Path,required=True)
    a,argv=p.parse_known_args();engine=a.engine.resolve();assert not a.record.exists()
    os.sched_setaffinity(0,{13});identity=sha(engine);start=time.monotonic_ns()
    r,w=os.pipe2(os.O_CLOEXEC);pid=os.fork()
    if pid==0:
        os.close(r)
        try:
            os.sched_setaffinity(0,{14});os.write(w,json.dumps(dict(pid=os.getpid(),pgid=os.getpgrp(),affinity=sorted(os.sched_getaffinity(0)))).encode()+b'\n');os.execv(str(engine),[str(engine),*argv])
        except BaseException as e:
            os.write(w,json.dumps(dict(exec_error=repr(e))).encode()+b'\n');os._exit(127)
    os.close(w)
    def forward(sig,frame):
        try:os.kill(pid,sig)
        except ProcessLookupError:pass
    for sig in [signal.SIGTERM,signal.SIGINT,signal.SIGHUP]:signal.signal(sig,forward)
    data=b''
    while True:
        block=os.read(r,4096)
        if not block:break
        data+=block
        if len(data)>8192:os.kill(pid,signal.SIGKILL);break
    os.close(r);placement=[json.loads(s) for s in data.splitlines()];observed=None
    try:
        observed=dict(exe=os.readlink(f'/proc/{pid}/exe'),status=Path(f'/proc/{pid}/status').read_text(),tasks=sorted(x.name for x in Path(f'/proc/{pid}/task').iterdir()))
    except (FileNotFoundError,ProcessLookupError):pass
    _,status,usage=os.wait4(pid,0);end=time.monotonic_ns();code=os.waitstatus_to_exitcode(status)
    failure=None
    if len(placement)!=1 or placement[0]!=dict(pid=pid,pgid=os.getpgrp(),affinity=[14]):failure='native pre-exec/exec mismatch'
    elif sha(engine)!=identity:failure='binary changed'
    elif code!=0:failure='native exit nonzero'
    result=dict(schema='rook2-internal-native-wait4-v1',engine=str(engine),engine_sha256_before=identity,engine_sha256_after=sha(engine),argv=[str(engine),*argv],supervisor_pid=os.getpid(),native_pid=pid,supervisor_affinity=sorted(os.sched_getaffinity(0)),native_pre_exec=placement,native_post_exec=observed,native_exit_code=code,native_wait_status=status,wall_ns=end-start,total_cpu_s=usage.ru_utime+usage.ru_stime,user_cpu_s=usage.ru_utime,system_cpu_s=usage.ru_stime,maxrss_linux_kib=usage.ru_maxrss,voluntary_context_switches=usage.ru_nvcsw,involuntary_context_switches=usage.ru_nivcsw,failure=failure,scope='Whole native process wait4 includes all threads, oracle, startup/setup/drain; not executor CPU. Driver owns actual worker placement receipts.')
    with a.record.open('x') as out:json.dump(result,out,indent=2);out.write('\n')
    return code if code else (125 if failure else 0)
if __name__=='__main__':raise SystemExit(main())
