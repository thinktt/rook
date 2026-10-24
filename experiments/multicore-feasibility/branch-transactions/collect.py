#!/usr/bin/env python3
"""Preselected serial queue pilot; no parallel speedup or qualification claim."""
import argparse, hashlib, json, os, signal, subprocess, time
from pathlib import Path

HERE=Path(__file__).resolve().parent

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):
    q=p.with_suffix('.pending');q.write_text(json.dumps(x,indent=2)+'\n');q.replace(p)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--binary',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();out=a.output.resolve();out.mkdir();binary=a.binary.resolve()
    schedule=[dict(case=c,queue_depth=q) for c in ['profile-35','profile-08','profile-04'] for q in [2,4]]
    files=[binary,Path(__file__),*(HERE/'inputs').glob('*.txt')]
    write(out/'plan.json',dict(schedule=schedule,max_depth=8,max_tail=8,log_events=16384,
          native_cpu=14,helper_affinity=sorted(os.sched_getaffinity(0)),per_process_seconds=180,
          total_seconds=900,scope='serial fixed-completion NoHost timing=None rnd=0 inline evaluator',
          inputs={str(f):sha(f) for f in files}))
    (out/'proc-stat-before').write_text(Path('/proc/stat').read_text())
    rows=[];deadline=time.monotonic()+900
    for i,item in enumerate(schedule):
        stem=f'{i:02d}-{item["case"]}-q{item["queue_depth"]}';start=time.monotonic()
        cmd=['taskset','-c','14',str(binary),'--input',str(HERE/'inputs'/(item['case']+'.txt')),
             '--queue-depth',str(item['queue_depth']),'--max-depth','8','--max-tail','8','--log-events','16384']
        with (out/(stem+'.stdout')).open('wb') as stdout,(out/(stem+'.stderr')).open('wb') as stderr:
            proc=subprocess.Popen(cmd,stdout=stdout,stderr=stderr,start_new_session=True)
            timed_out=False
            try:proc.wait(timeout=max(0.01,min(180,deadline-time.monotonic())))
            except subprocess.TimeoutExpired:
                timed_out=True;os.killpg(proc.pid,signal.SIGKILL);proc.wait()
        row=dict(**item,argv=cmd,pid=proc.pid,exit=proc.returncode,timed_out=timed_out,wall_seconds=time.monotonic()-start,
                 stdout_sha256=sha(out/(stem+'.stdout')),stderr_sha256=sha(out/(stem+'.stderr')))
        rows.append(row);write(out/'progress.json',rows)
        if proc.returncode or timed_out:raise RuntimeError(f'pilot stopped: {stem}: {row}')
        report=json.loads((out/(stem+'.stdout')).read_text())
        if report['unsafe_validation'] or not all(c['passed'] for c in report['controls']):
            raise RuntimeError('validator/control failure; no further samples')
        print(stem,report['stopped_reason'],len(report['candidates']),report['accepted_nodes'],flush=True)
    (out/'proc-stat-after').write_text(Path('/proc/stat').read_text())
    write(out/'closure.json',dict(complete=True,rows=rows))

if __name__=='__main__':main()
