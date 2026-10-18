"""Matched generic85 checked bounded-reply comparison; whole native wait4 with strict replay."""
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
VARIANTS={'baseline':'quiescence-evaluation-default-build-20261018',
          'king_first':'bounded-reply-king-first-build-20261018'}
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
    prep=ROOT/'evidence/bounded-reply-king-first-preparation-20261018/prepared.json'
    prepared=load(prep)
    summary_path=ROOT/'evidence/bounded-reply-king-first-validation-20261018/validation-summary.json'
    summary=load(summary_path)
    assert summary['all_owned_processes_terminal'] is True
    assert summary['strict_replays']==54 and summary['interruption_fixtures']==8 and summary['interruption_searches']==24
    assert summary['candidate_artifact_sha256']=='61fdefb32daa9db4688f3c164ab7c94e057eef47f4459b87ad9c9a6ac5a263c1'
    assert summary['prepared_sha256']==sha(prep)
    terminal_paths=[]
    for filename,record in summary['terminal_records'].items():
        assert record['exit_code']==0 and record['actual_tool_terminal_observed'] is True
        terminal=ROOT/filename
        assert load(terminal)==record
        terminal_paths.append(terminal)
    independent=ROOT/'evidence/bounded-reply-king-first-check-20261018/independent-verification.json'
    assert sha(independent)==summary['independent_verification_sha256']
    native_proof=ROOT/'evidence/bounded-reply-king-first-validation-20261018/native-verification.json'
    native=load(native_proof)
    assert native['complete'] and native['inputs_stable'] and native['failure'] is None
    assert native['units']['rook2']['passed']==142 and native['units']['rook2-dev']['passed']==2
    assert native['source_before']==native['source_after']==prepared['variant_source_sha256']
    assert sha(native_proof)==summary['native_verification_sha256']
    control_dir=ROOT/'evidence/quiescence-evaluation-default-validation-20261018'
    controls={'baseline':control_dir/'ordinary-check-02/identity.json',
              'king_first':ROOT/'evidence/bounded-reply-king-first-check-20261018/identity.json'}
    replay_paths={'baseline':control_dir/'ordinary-check-02/strict54.stdout',
                  'king_first':controls['king_first'].parent/'profile-all.stdout'}
    wire_paths={'baseline':control_dir/'interruption-wire-02/receipt.json',
                'king_first':ROOT/'evidence/bounded-reply-king-first-interruption-wire-20261018/receipt.json'}
    control_final=load(control_dir/'identity.json')
    assert control_final['native_total_units']==142 and control_final['owned_live_processes']==0
    assert control_final['retry_all_stage_inputs_stable'] and control_final['retry_actual_exit']==0
    assert load(control_dir/'tool-terminal.json')['exit_code']==0
    pilot_closed=ROOT/'evidence/q-material-reuse-cpu-pilot-20261018/tool-terminal.json'
    assert load(pilot_closed)['exit_code']==0
    paths={name:ROOT/'evidence'/directory/'rook2-exact' for name,directory in VARIANTS.items()}
    validation={}
    builds={}
    for name,directory in VARIANTS.items():
        check=controls[name];identity=load(check)
        if name=='baseline':
            assert identity['complete'] and identity['inputs_stable'] and identity['failure'] is None
            assert all(stage['exit_code']==0 for stage in identity['stages'])
        else:
            assert identity['status']=='all54-strict-replays-and-eight-interruption-fixtures-pass'
        build=ROOT/'evidence'/directory/'receipt.json';builds[name]=load(build)
        assert builds[name]['source_identity_unchanged'] and builds[name]['tool_identity_unchanged']
        assert builds[name]['pgo']['mode']=='none' and builds[name]['rust_flags']==['-C','target-cpu=x86-64']
        if name=='king_first': assert sha(build)==identity['build_receipt_sha256']
        assert sha(paths[name])==identity['native_artifact_sha256']==builds[name]['binary_output']['sha256']
        replay=replay_paths[name];report=load(replay)
        assert report['status']=='pass' and len(report['results'])==54
        if name=='baseline': assert sha(replay)==identity['stages'][0]['stdout_sha256']
        else: assert sha(replay)==identity['replay_sha256']
        assert all(row['status']=='pass' and row['complete'] and not row['truncated']
                   and row['exit']=={'code':0,'signal':None} and row['error'] is None
                   and row['stderr']=='' and row['discardedObservedBytes']==0 for row in report['results'])
        wire=wire_paths[name];w=load(wire)
        assert w['pass'] and len(w['results'])==8 and sum(len(row['searches']) for row in w['results'])==24
        assert w['engine_sha256_before']==w['engine_sha256_after']==sha(paths[name])
        assert sha(wire)==identity['wire_receipt_sha256']
        validation[name]={str(p):sha(p) for p in [check,build,replay,wire,prep,pilot_closed,
            native_proof,summary_path,independent,*terminal_paths,control_dir/'identity.json',control_dir/'tool-terminal.json']}
    assert builds['baseline']['source_sha256_before']==prepared['baseline_source_sha256']
    assert builds['king_first']['source_sha256_before']==prepared['variant_source_sha256']
    assert builds['baseline']['tool_sha256_before']==builds['king_first']['tool_sha256_before']
    changed=[p for p,h in prepared['baseline_source_sha256'].items() if h!=prepared['variant_source_sha256'][p]]
    assert changed==['src/movegen.rs']
    write('validation-before.json',validation)
    write('suite.json',dict(cases=CASES,variants={n:dict(path=str(p),sha256=sha(p)) for n,p in paths.items()},
        order='One warmup/variant then four alternating forward/reverse rounds per case',
        driver_sha256=sha(Path(__file__)),
        scope='Generic85 matched checked-only bounded king-first trial. No PGO, final cost/gameplay or reference qualification.'))
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
