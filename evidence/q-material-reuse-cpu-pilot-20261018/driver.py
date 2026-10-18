"""Matched generic79 source comparison; whole native wait4 with strict replay."""
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
VARIANTS={'baseline':'production-eval-observers-build-20261018',
          'reuse':'q-material-reuse-build-20261018'}
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
            if name.startswith(('rook2','cargo','rustc','callgrind','valgrind')):
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
    assert not native_processes(),'Native build/test/engine/profiler remains live'
    prep=ROOT/'evidence/q-material-reuse-proposal-20261018/prepared.json'
    prepared=load(prep)
    summaries=[]
    for name in ['q-material-reuse','q-material-reuse-inline','q-material-reuse-victim']:
        path=ROOT/'evidence'/(name+'-validation-20261018')/'validation-summary.json'
        value=load(path);assert value['all_owned_processes_terminal'] is True
        summaries.append(path)
        for filename,record in value['terminal_records'].items():
            assert record['exit_code']==0 and record['actual_tool_terminal_observed'] is True
            assert load(ROOT/filename)==record
    summary=load(summaries[0])
    assert summary['strict_replays']==54 and summary['interruption_fixtures']==8
    assert summary['native_artifact_sha256']=='21daa966ce3f74742bb75f64c0b0bd968afd5071d688a163770c463bbb6946dd'
    native_proof=ROOT/'evidence/q-material-reuse-validation-20261018/native-verification.json'
    independent=ROOT/'evidence/q-material-reuse-check-20261018/independent-verification.json'
    native=load(native_proof)
    assert native['complete'] and native['inputs_stable'] and native['failure'] is None
    assert native['units']['rook2']['passed']==136 and native['units']['rook2-dev']['passed']==2
    assert native['source_before']==native['source_after']==prepared['variant_source_sha256']
    assert sha(native_proof)==summary['native_verification_sha256']
    assert sha(independent)==summary['independent_verification_sha256']
    controls={'baseline':ROOT/'evidence/production-eval-observers-check-20261018/identity.json',
              'reuse':ROOT/'evidence/q-material-reuse-check-20261018/identity.json'}
    paths={name:ROOT/'evidence'/directory/'rook2-exact' for name,directory in VARIANTS.items()}
    validation={}
    builds={}
    for name,directory in VARIANTS.items():
        check=controls[name];identity=load(check)
        assert identity['status']=='all54-strict-replays-and-eight-interruption-fixtures-pass'
        build=ROOT/'evidence'/directory/'receipt.json';builds[name]=load(build)
        assert builds[name]['source_identity_unchanged'] and builds[name]['tool_identity_unchanged']
        assert builds[name]['pgo']['mode']=='none' and builds[name]['rust_flags']==['-C','target-cpu=x86-64']
        assert sha(build)==identity['build_receipt_sha256']
        assert sha(paths[name])==identity['native_artifact_sha256']==builds[name]['binary_output']['sha256']
        replay=check.parent/'profile-all.stdout';report=load(replay)
        assert report['status']=='pass' and len(report['results'])==54
        assert sha(replay)==identity['replay_sha256']
        wire=ROOT/'evidence'/('production-eval-observers-interruption-wire-20261018' if name=='baseline' else 'q-material-reuse-interruption-wire-20261018')/'receipt.json'
        w=load(wire);assert w['pass'] and len(w['results'])==8
        assert w['engine_sha256_before']==w['engine_sha256_after']==sha(paths[name])
        assert sha(wire)==identity['wire_receipt_sha256']
        closed=ROOT/'evidence/pgo-profile-sum-cpu-pilot-20261018/tool-terminal.json'
        assert load(closed)['exit_code']==0
        validation[name]={str(p):sha(p) for p in [check,build,replay,wire,prep,closed,native_proof,independent,*summaries]}
    assert builds['baseline']['source_sha256_before']==prepared['baseline_source_sha256']
    assert builds['reuse']['source_sha256_before']==prepared['variant_source_sha256']
    assert builds['baseline']['tool_sha256_before']==builds['reuse']['tool_sha256_before']
    changed=[p for p,h in prepared['baseline_source_sha256'].items() if h!=prepared['variant_source_sha256'][p]]
    assert changed==['src/quiescence.rs','src/quiescence_policy.rs']
    write('validation-before.json',validation)
    write('suite.json',dict(cases=CASES,variants={n:dict(path=str(p),sha256=sha(p)) for n,p in paths.items()},
        order='One warmup/variant then four alternating forward/reverse rounds per case',
        driver_sha256=sha(Path(__file__)),
        scope='Generic79 matched Q-local material endpoint trial. Later82 source and Q observer proposals are separate. No PGO or reference qualification.'))
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
