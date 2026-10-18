"""Matched own-PGO85 checked bounded-reply comparison; whole native wait4 with strict replay."""
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
VARIANTS={'baseline':'pgo-bounded-reply-baseline-use-build-20261018',
          'king_first':'pgo-bounded-reply-king-first-use-build-20261018'}
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
    assert not native_processes(),'Native build/test/engine/profiler remains live'
    prep=ROOT/'evidence/bounded-reply-king-first-preparation-20261018/prepared.json'
    prepared=load(prep)
    summary_path=ROOT/'evidence/pgo-bounded-reply-matched-validation-20261018/validation-summary.json'
    summary=load(summary_path)
    assert summary['all_owned_processes_terminal'] and not summary['source_fix_during_task']
    assert summary['compiler_training_replays']==summary['raw_profiles']==summary['post_use_strict_replays']==108
    assert summary['interruption_fixtures']==16 and summary['interruption_searches']==48 and summary['profile_remerges']==2
    terminals=[]
    for filename,record in summary['actual_terminals'].items():
        assert record['exit_code']==0
        terminal=ROOT/filename
        assert load(terminal)==record
        terminals.append(terminal)
    independent=summary_path.parent/'independent-verification.json'
    assert sha(independent)==summary['independent_verification_sha256']
    generic=ROOT/'evidence/bounded-reply-king-first-cpu-pilot-20261018'
    assert load(generic/'tool-terminal.json')['exit_code']==0 and load(generic/'analysis.json')['complete']
    paths={name:ROOT/'evidence'/directory/'rook2-exact' for name,directory in VARIANTS.items()}
    validation={}
    builds={}
    for name,directory in VARIANTS.items():
        slug=name.replace('_','-')
        variant=summary['variants'][slug]
        build_path=ROOT/'evidence'/directory/'receipt.json';build=load(build_path);builds[name]=build
        check=ROOT/'evidence'/('pgo-bounded-reply-'+slug+'-use-check-20261018')/'identity.json'
        identity=load(check)
        training_dir=ROOT/'evidence'/('pgo-bounded-reply-'+slug+'-training-20261018')
        training_path=training_dir/'training.json';training=load(training_path)
        verification_path=training_dir/'verification.json';verification=load(verification_path)
        profile=training_dir/'merged.profdata'
        replay=check.parent/'profile-all.stdout';report=load(replay)
        wire=ROOT/'evidence'/('pgo-bounded-reply-'+slug+'-interruption-wire-20261018')/'receipt.json';w=load(wire)
        assert identity['status']=='pass' and identity['strict_replays']==54
        assert identity['interruption_fixtures']==8 and identity['interruption_searches']==24 and identity['missing_function_warnings']==0
        assert build['pgo']['mode']=='profile-use' and build['rust_flags'][:2]==['-C','target-cpu=x86-64']
        assert build['source_identity_unchanged'] and build['tool_identity_unchanged']
        assert sha(build_path)==identity['build_receipt_sha256']==variant['use_build_receipt_sha256']
        assert sha(paths[name])==identity['native_artifact_sha256']==build['binary_output']['sha256']==variant['use_artifact_sha256']
        assert training['complete'] and verification['complete'] and verification['strict_replays']==54
        assert sha(training_path)==identity['training_record_sha256']==variant['training_record_sha256']
        assert sha(verification_path)==identity['training_verification_sha256']==variant['training_verification_sha256']
        assert sha(profile)==training['profile_sha256']==identity['profile_sha256']==variant['profile_sha256']
        assert training['engine_source_sha256']==build['source_sha256_before']==build['source_sha256_after']==variant['source_sha256']
        assert variant['raw_profiles']==54 and variant['raw_profiles_PID_linked'] and variant['profile_independent_remerge_byte_identical']
        assert variant['missing_function_warnings']==variant['stale_or_malformed_profile_warnings']==0
        assert report['status']=='pass' and len(report['results'])==54 and sha(replay)==identity['replay_sha256']==variant['strict_raw_report_sha256']
        assert all(row['status']=='pass' and row['complete'] and not row['truncated']
            and row['exit']=={'code':0,'signal':None} and row['error'] is None and row['stderr']==''
            and row['discardedObservedBytes']==0 for row in report['results'])
        assert w['pass'] and len(w['results'])==8 and sum(len(row['searches']) for row in w['results'])==24
        assert sha(wire)==identity['wire_receipt_sha256']==variant['wire_receipt_sha256']
        assert w['engine_sha256_before']==w['engine_sha256_after']==sha(paths[name])
        validation[name]={str(p):sha(p) for p in [prep,summary_path,independent,build_path,check,
            training_path,verification_path,profile,training_dir/'merged.profdata.gz',replay,wire,
            generic/'analysis.json',generic/'tool-terminal.json',*terminals]}
    assert builds['baseline']['source_sha256_before']==prepared['baseline_source_sha256']
    assert builds['king_first']['source_sha256_before']==prepared['variant_source_sha256']
    assert builds['baseline']['tool_sha256_before']==builds['king_first']['tool_sha256_before']
    assert builds['baseline']['target_triple']==builds['king_first']['target_triple']=='x86_64-unknown-linux-gnu'
    changed=[p for p,h in prepared['baseline_source_sha256'].items() if h!=prepared['variant_source_sha256'][p]]
    assert changed==['src/movegen.rs']
    write('validation-before.json',validation)
    write('suite.json',dict(cases=CASES,variants={n:dict(path=str(p),sha256=sha(p)) for n,p in paths.items()},
        order='One warmup/variant then four alternating forward/reverse rounds per case',
        driver_sha256=sha(Path(__file__)),
        scope='Matched own-source PGO85 checked-only bounded king-first trial. No new observer/ordered-bit source, old8d profile, final cost/gameplay or reference qualification transfer.'))
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
