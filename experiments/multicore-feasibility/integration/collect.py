#!/usr/bin/env python3
"""Three exact original workloads; generic control, budget1, budget2, one stream."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import selectors
import signal
import statistics
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
SPEC = Path('/home/legolas/king-spec/conformance/profiling')
sys.path.insert(0, str(ROOT/'tools'))
from compare_ordinary import stop_owned


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def write(p, d):
    temporary = p.with_suffix('.pending')
    temporary.write_text(json.dumps(d, indent=2)+'\n')
    temporary.replace(p)


def proc_ticks(pid):
    values = Path(f'/proc/{pid}/stat').read_text().rsplit(')',1)[1].split()
    return int(values[11])+int(values[12])


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--control',type=Path,required=True)
    p.add_argument('--candidate',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    out=a.output.resolve();out.mkdir()
    variants={'control':(a.control.resolve(),1,[]),
              'budget1':(a.candidate.resolve(),1,['--research-threads=1']),
              'budget2':(a.candidate.resolve(),2,['--research-threads=2'])}
    modes=json.loads((SPEC/'replay-oracle.json').read_text())['mode']
    cases=['profile-35','profile-08','profile-04']
    schedule=[]
    for case in cases:
        schedule += [dict(case=case,variant=n,warmup=True,repeat=0) for n in variants]
        for rep in range(3):
            order=list(variants);order=order[rep:]+order[:rep]
            schedule += [dict(case=case,variant=n,warmup=False,repeat=rep+1) for n in order]
    paths=[Path(__file__), HERE/'account_threads.py', ROOT/'tools/tap_wire.mjs',
           ROOT/'tools/compare_ordinary.py', SPEC/'replay-check.mjs',
           SPEC/'benchmark.mjs',SPEC/'workloads.json',SPEC/'replay-oracle.json',
           a.control.resolve(),a.candidate.resolve()]
    manifest=dict(variants={n:dict(path=str(x[0]),sha256=sha(x[0]),threads=x[1],args=x[2])
                           for n,x in variants.items()},schedule=schedule,
                  inputSha256={str(x):sha(x) for x in paths},
                  coordinatorCpu=14,workerCpu=6,helperAffinity=sorted(os.sched_getaffinity(0)),
                  idleOwnedSiblings=[7,15],
                  boundaries=dict(search='tap before original go write to move data callback',
                                  cpu='native wait4 whole lifetime, all native threads; includes pre-exec prefix',
                                  lifetime='startup/setup/search/shutdown included',rss='whole native peak RSS'))
    write(out/'plan.json',manifest)
    (out/'proc-stat-before').write_text(Path('/proc/stat').read_text())
    rows=[];deadline=time.monotonic()+1800

    def supervisor(name,directory):
        image,threads,args=variants[name]
        return [sys.executable,str(HERE/'account_threads.py'),'--engine',str(image),
                '--record',str(directory/'native.json'),'--known-single-process',
                '--thread-budget',str(threads),*args]

    for index,step in enumerate(schedule):
        d=out/f'{index:02d}-{step["case"]}-{step["variant"]}-r{step["repeat"]}';d.mkdir()
        native=supervisor(step['variant'],d)
        config=dict(version=1,expectedArgv=native+modes,directory=str(d/'wire'),
                    nativeExecutable=str(variants[step['variant']][0]),
                    maxRawBytes=8*1024*1024,tickHz=os.sysconf('SC_CLK_TCK'))
        write(d/'tap-config.json',config)
        env=dict(os.environ,ROOK2_WIRE_TAP_CONFIG=str(d/'tap-config.json'))
        command=['/usr/bin/node','--import',str(ROOT/'tools/tap_wire.mjs'),
                 str(SPEC/'replay-check.mjs'),'--case',step['case'],'--',*native]
        write(d/'launch.json',dict(argv=command,step=step))
        with (d/'stdout').open('xb') as so,(d/'stderr').open('xb') as se:
            child=subprocess.Popen(command,stdout=so,stderr=se,env=env,start_new_session=True)
            try:
                while child.poll() is None:
                    if (time.monotonic()>deadline or (d/'stdout').stat().st_size>8*1024*1024
                            or (d/'stderr').stat().st_size>1024*1024):
                        raise RuntimeError('aggregate time or stream cap')
                    if (d/'wire/failure.json').exists():raise RuntimeError('wire capture failed')
                    time.sleep(.05)
            except BaseException:
                stop_owned(child)
                write(d/'failure.json',dict(exit=child.poll(),step=step))
                raise
        assert child.returncode==0 and not (d/'stderr').stat().st_size, str(d)
        replay=json.loads((d/'stdout').read_text());n=json.loads((d/'native.json').read_text())
        tap=json.loads((d/'wire/receipt.json').read_text())
        assert replay['status']=='pass' and replay['selectedCases']==[step['case']]
        assert n['failure'] is None and n['native_exit_code']==0
        assert n['engine_sha256_before']==n['engine_sha256_after']==manifest['variants'][step['variant']]['sha256']
        assert n['expected_threads']==variants[step['variant']][1]
        assert tap['failure'] is None and len(tap['searches'])==1
        search=tap['searches'][0]
        assert search['beforeWrite']['available'] and search['afterData']['available']
        assert search['beforeWrite']['pid']==search['afterData']['pid']==n['native_pid']
        assert search['beforeWrite']['lastProcessor']==search['afterData']['lastProcessor']==14
        for name,item in tap['raw'].items():
            path=d/'wire'/f'{name}.raw';assert sha(path)==item['sha256'] and path.stat().st_size==item['bytes']
        assert not Path(f'/proc/{n["native_pid"]}').exists()
        row=dict(**step,directory=str(d),searchWallNs=search['wallNs'],
                 wholeCpuSeconds=n['total_cpu_s'],wholeWallNs=n['wall_ns'],
                 nonSearchWallNs=n['wall_ns']-search['wallNs'],rssKiB=n['maxrss_linux_kib'],
                 nativePid=n['native_pid'],taskAffinities=n['native_post_exec']['task_affinities'],
                 sha256={x:sha(d/x) for x in ['native.json','stdout','stderr','wire/receipt.json']})
        rows.append(row);write(out/'progress.json',dict(complete=False,runs=rows))

    # One explicit idle probe/configuration: budget2 remains alive and spins.
    idle=[]
    for name in variants:
        d=out/('idle-'+name);d.mkdir();command=supervisor(name,d)
        with (d/'stderr').open('xb') as se:
            start=time.monotonic_ns();child=subprocess.Popen(command,stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,stderr=se,start_new_session=True)
            try:
                child.stdin.write(b'cm_parm\n');child.stdin.flush()
                ready=selectors.DefaultSelector();ready.register(child.stdout,selectors.EVENT_READ)
                assert ready.select(10),'idle startup deadline'
                assert child.stdout.readline()==b'cm_parm\n';startup=time.monotonic_ns()-start
                kids=Path(f'/proc/{child.pid}/task/{child.pid}/children').read_text().split()
                assert len(kids)==1;pid=int(kids[0]);before=proc_ticks(pid);begin=time.monotonic_ns()
                time.sleep(.25)
                ticks=proc_ticks(pid)-before;elapsed=time.monotonic_ns()-begin
                child.stdin.write(b'quit\n');child.stdin.close();shutdown=time.monotonic_ns()
                assert child.wait(timeout=10)==0;shutdown=time.monotonic_ns()-shutdown
                ready.close();child.stdout.close()
            except BaseException:
                stop_owned(child);raise
        n=json.loads((d/'native.json').read_text());assert n['failure'] is None
        idle.append(dict(variant=name,idleNs=elapsed,idleCpuSeconds=ticks/os.sysconf('SC_CLK_TCK'),
                         startupReplyNs=startup,shutdownSupervisorNs=shutdown,
                         wholeCpuSeconds=n['total_cpu_s'],rssKiB=n['maxrss_linux_kib'],
                         nativeReceiptSha256=sha(d/'native.json')))

    assert all(sha(Path(x))==h for x,h in manifest['inputSha256'].items())
    (out/'proc-stat-after').write_text(Path('/proc/stat').read_text())
    summaries=[]
    for case in cases:
        for name in variants:
            selected=[r for r in rows if r['case']==case and r['variant']==name and not r['warmup']]
            assert len(selected)==3
            entry=dict(case=case,variant=name)
            for metric in ['searchWallNs','wholeCpuSeconds','wholeWallNs','nonSearchWallNs','rssKiB']:
                samples=[r[metric] for r in selected]
                entry[metric]=dict(samples=samples,median=statistics.median(samples),min=min(samples),max=max(samples))
            summaries.append(entry)
    result=dict(complete=True,runs=rows,summaries=summaries,idle=idle,
                qualification='three original cases only; no PGO or broad production qualification')
    write(out/'result.json',result)
    print(json.dumps(dict(complete=True,comparisons=len(rows),summaries=summaries,idle=idle),indent=2))


if __name__=='__main__':
    main()
