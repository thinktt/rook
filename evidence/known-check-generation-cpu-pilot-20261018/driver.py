"""Matched generic known-check-generation comparison; whole native wait4 with strict replay."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from measure import cgroup_snapshot

CASES=['profile-01','profile-02','profile-04','profile-05','profile-35','profile-29']
VARIANTS={'baseline': 'king-first88-build-20261018', 'known_check': 'known-check-generation-build-20261018'}
HELPERS=[0,1,2,3,4,5,8,9,10,11,12,13]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text())


def write(name,value):
    with (OUT/name).open('x') as stream:
        json.dump(value,stream,indent=2);stream.write('\n')


def native_processes():
    found=[]
    for process in Path('/proc').iterdir():
        if not process.name.isdigit():continue
        try:
            executable=os.readlink(process/'exe')
            name=Path(executable).name
            if name.startswith(('rook2','cargo','rustc','callgrind','valgrind','git','objdump','readelf','nm','llvm-profdata','c++filt')):
                found.append(dict(pid=int(process.name),executable=executable))
        except OSError:pass
    return found


def context():
    return dict(observed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        uname=list(os.uname()),helper_affinity=sorted(os.sched_getaffinity(0)),
        cgroups=cgroup_snapshot(),proc_stat=Path('/proc/stat').read_text(),
        loadavg=Path('/proc/loadavg').read_text(),native_processes=native_processes(),
        owned_background_work='All owned native jobs terminal; children restricted to cold source/text work',
        scope='Point-in-time guest observation; no assertion of exclusive host ownership',
        pmu='No PMU counters collected; retained self-open EACCES limitation remains')


def main():
    assert sorted(os.sched_getaffinity(0))==HELPERS
    assert not native_processes(),'Native build/test/engine/profiler/Git/static scan remains live'
    gate_path=OUT/'regression-gate.json';gate=load(gate_path)
    assert gate['complete'] and list(gate['variants'])==list(VARIANTS)
    assert all(sha(Path(p))==h for p,h in gate['dependencies'].items())
    paths={name:Path(item['path']) for name,item in gate['variants'].items()}
    assert all(sha(paths[name])==gate['variants'][name]['sha256'] for name in paths)
    validation={name:{**gate['dependencies'],str(gate_path):sha(gate_path)} for name in paths}
    write('validation-before.json',validation)
    write('suite.json',dict(cases=CASES,variants={n:dict(path=str(p),sha256=sha(p)) for n,p in paths.items()},
        order='One warmup/variant then four alternating forward/reverse rounds per case',
        driver_sha256=sha(Path(__file__)),
        scope='Generic88 plus validated king-first; only ordinary known-check reuse. No ordered-bit, PGO or qualification transfer.'))
    before=context();assert not before['native_processes'];write('context-before.json',before)
    result={}
    for case in CASES:
        command=[sys.executable,str(ROOT/'tools/compare_ordinary.py'),'--case',case,'--output',str(OUT/case)]
        for name,path in paths.items():command+=['--variant',name+'='+str(path)]
        with (OUT/(case+'.stdout')).open('x') as out,(OUT/(case+'.stderr')).open('x') as err:
            child=subprocess.run(command,cwd=ROOT,stdout=out,stderr=err)
        report=load(OUT/case/'summary.json')
        assert child.returncode==0 and report['complete'],(case,report['failure'])
        result[case]=report['summaries']
        print(json.dumps(dict(case=case,summaries=report['summaries'])),flush=True)
    after=context();assert not after['native_processes'];write('context-after.json',after)
    assert all(sha(Path(p))==h for files in validation.values() for p,h in files.items())
    write('suite-summary.json',dict(complete=True,summaries=result,
        artifact_hashes_after={n:sha(p) for n,p in paths.items()}))


if __name__=='__main__':main()
