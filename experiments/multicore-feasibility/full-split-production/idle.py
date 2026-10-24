#!/usr/bin/env python3
"""One short startup-idle comparison; no search benchmark or statistical claim."""
import argparse,hashlib,json,os,selectors,subprocess,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent
ACCOUNT=HERE.parent/'integration/account_threads.py'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ticks(pid):
 x=Path(f'/proc/{pid}/stat').read_text().rsplit(')',1)[1].split();return int(x[11])+int(x[12])
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--before',type=Path,required=True);p.add_argument('--after',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.before=a.before.resolve(strict=True);a.after=a.after.resolve(strict=True);out=a.output.resolve();out.mkdir();rows=[]
 for name,image,budget in [('before-budget2',a.before,2),('after-budget1',a.after,1),('after-budget2',a.after,2)]:
  d=out/name;d.mkdir();cmd=[sys.executable,str(ACCOUNT),'--engine',str(image.resolve()),'--record',str(d/'native.json'),'--known-single-process','--thread-budget',str(budget),f'--research-threads={budget}']
  with (d/'stderr').open('xb') as se:
   start=time.monotonic_ns();c=subprocess.Popen(cmd,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=se,start_new_session=True)
   try:
    c.stdin.write(b'cm_parm\n');c.stdin.flush();sel=selectors.DefaultSelector();sel.register(c.stdout,selectors.EVENT_READ);assert sel.select(10);assert c.stdout.readline()==b'cm_parm\n';startup=time.monotonic_ns()-start
    children=Path(f'/proc/{c.pid}/task/{c.pid}/children').read_text().split();assert len(children)==1;pid=int(children[0]);before=ticks(pid);start=time.monotonic_ns();time.sleep(.25);cpu=(ticks(pid)-before)/os.sysconf('SC_CLK_TCK');wall=time.monotonic_ns()-start
    c.stdin.write(b'quit\n');c.stdin.close();start=time.monotonic_ns();assert c.wait(timeout=10)==0;shutdown=time.monotonic_ns()-start;sel.close();c.stdout.close()
   except BaseException:
    import signal
    os.killpg(c.pid,signal.SIGKILL);c.wait();raise
  n=json.loads((d/'native.json').read_text());assert n['failure'] is None and n['native_exit_code']==0;assert not (d/'stderr').stat().st_size
  rows.append(dict(variant=name,binary=str(image.resolve()),binarySha256=sha(image),idleCpuSeconds=cpu,idleWallNs=wall,startupReplyNs=startup,shutdownSupervisorNs=shutdown,wholeCpuSeconds=n['total_cpu_s'],nativeReceiptSha256=sha(d/'native.json')))
 (out/'result.json').write_text(json.dumps(dict(complete=True,runs=rows,boundary='one250ms startup idle interval per configuration; /proc tick resolution; no search'),indent=2)+'\n');print(json.dumps(rows))
if __name__=='__main__':main()
