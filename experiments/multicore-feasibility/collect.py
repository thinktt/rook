#!/usr/bin/env python3
"""One bounded native stream, exact-output checks, descriptive three-sample summary."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import resource
import signal
import statistics
import subprocess
import time

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def write(p, d):
    p.write_text(json.dumps(d, indent=2)+'\n')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--engine', required=True, type=Path)
    p.add_argument('--output', required=True, type=Path)
    a = p.parse_args()
    engine = a.engine.resolve()
    out = a.output.resolve()
    out.mkdir()
    source = Path('/home/legolas/king-spec/conformance/profiling/workloads.json')
    corpus = json.loads(source.read_text())['cases']
    assert len(corpus) == 54 and all(c['position']['initial'] == 'standard-start' for c in corpus)
    inputs = out/'histories.tsv'
    inputs.write_text(''.join(c['id']+'\t'+' '.join(c['position']['moves'])+'\n' for c in corpus))
    pins = {str(x):sha(x) for x in [engine, source, inputs, Path(__file__), HERE/'src/main.rs',
                                   HERE/'Cargo.toml', HERE/'Cargo.lock']}
    pins.update({str(x):sha(x) for x in (ROOT/'src').rglob('*.rs')})
    topology = {str(c):dict(core=(Path(f'/sys/devices/system/cpu/cpu{c}/topology/core_id').read_text().strip()),
                          siblings=Path(f'/sys/devices/system/cpu/cpu{c}/topology/thread_siblings_list').read_text().strip())
                for c in [6,7,14,15]}
    argv = [str(engine), str(inputs), '6']
    write(out/'plan.json', dict(argv=argv, inputSha256=pins, guestTopology=topology,
          coordinatorCpu=14, workerCpu=6, idleOwnedSiblings=[7,15],
          helperAffinity=sorted(os.sched_getaffinity(0)), timeoutSeconds=180,
          scope='standalone neutral FULL kernel, no production search or host exclusivity claim'))
    (out/'proc-stat-before').write_text(Path('/proc/stat').read_text())
    begin = resource.getrusage(resource.RUSAGE_CHILDREN)
    start = time.monotonic()
    timed_out = False
    with (out/'stdout').open('xb') as so, (out/'stderr').open('xb') as se:
        child = subprocess.Popen(argv, stdout=so, stderr=se, start_new_session=True)
        try:
            child.wait(timeout=180)
        except subprocess.TimeoutExpired:
            timed_out = True
            os.killpg(child.pid, signal.SIGKILL)
            child.wait(timeout=5)
    end = resource.getrusage(resource.RUSAGE_CHILDREN)
    receipt = dict(exit=child.returncode, timeout=timed_out, pid=child.pid,
        elapsedSeconds=time.monotonic()-start,
        wholeChildCpuSeconds=end.ru_utime+end.ru_stime-begin.ru_utime-begin.ru_stime,
        maxRssKiB=end.ru_maxrss, minorFaults=end.ru_minflt-begin.ru_minflt,
        majorFaults=end.ru_majflt-begin.ru_majflt,
        sourceUnchanged=all(sha(Path(x))==h for x,h in pins.items()))
    write(out/'receipt.json', receipt)
    (out/'proc-stat-after').write_text(Path('/proc/stat').read_text())
    assert receipt['exit'] == 0 and not timed_out and receipt['sourceUnchanged'], receipt
    assert not (out/'stderr').stat().st_size
    rows = [json.loads(line) for line in (out/'stdout').read_text().splitlines()]
    assert rows[0]['verification']=='pass' and rows[0]['full_calls']==162
    samples = rows[1:]
    assert len(samples)==30
    groups = {}
    for row in samples:
        assert row['worker_cpu']==6 and row['items']==172800
        groups.setdefault((row['kernel'], row['batch']), []).append(row)
    summaries = []
    for (kernel,batch), values in groups.items():
        assert [x['sample'] for x in values]==[0,1,2]
        assert len({x['sink'] for x in values})==1
        wall = [x['wall_ns']/x['items'] for x in values]
        cpu = [x['cpu_ns']/x['items'] for x in values]
        summaries.append(dict(kernel=kernel,batch=batch,wallNsPerItem=dict(
            min=min(wall),median=statistics.median(wall),max=max(wall)),
            cpuNsPerItem=dict(min=min(cpu),median=statistics.median(cpu),max=max(cpu))))
    for kernel in ['empty','chain','full']:
        assert len({x['sink'] for x in samples if x['kernel']==kernel})==1
        direct=next(x for x in summaries if x['kernel']==kernel and x['batch']==0)
        for x in summaries:
            if x['kernel']==kernel:
                x['elapsedSpeedupVsDirect']=direct['wallNsPerItem']['median']/x['wallNsPerItem']['median']
                x['cpuRatioVsDirect']=x['cpuNsPerItem']['median']/direct['cpuNsPerItem']['median']
    result=dict(complete=True, verificationFullCalls=162, rows=summaries,
        engineSha256=sha(engine), wholeReceipt=receipt,
        rawSha256={n:sha(out/n) for n in ['plan.json','stdout','stderr','receipt.json','proc-stat-before','proc-stat-after']},
        interpretation='No-PGO pure-kernel microexperiment; batching assumes independent available packets; no search speedup claim')
    write(out/'result.json',result)
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
