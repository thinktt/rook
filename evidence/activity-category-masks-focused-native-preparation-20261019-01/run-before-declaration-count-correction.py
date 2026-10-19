#!/usr/bin/env python3
"""Run only frozen experiment35 activity_batch_ native checks."""
from pathlib import Path
import hashlib,json,os,subprocess,sys,datetime
R=Path('/home/legolas/rook2')
W=Path('/home/legolas/rook2-work/imp2-activity-category-masks-20261019-01')
E=R/'evidence'
HELPERS=[0,1,2,3,4,5,8,9,10,11,12,13]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
save=lambda p,v:Path(p).write_text(json.dumps(v,indent=2)+'\n')
def main():
    assert sorted(os.sched_getaffinity(0))==HELPERS
    assert not any(os.environ.get(k) for k in ['LD_PRELOAD','LD_LIBRARY_PATH','LLVM_PROFILE_FILE'])
    source=json.loads((E/'activity-category-masks-parent-review-20261019-01/source-freeze.json').read_text())
    assert source['build_authorized']
    before={p:sha(W/p) for p in source['files_sha256']}
    assert before==source['files_sha256']
    build=E/'activity-category-masks-generic-build-20261019-01'
    receipt=json.loads((build/'receipt.json').read_text())
    assert receipt['outcome']=='build-succeeded-with-stable-input-snapshot'
    image=build/'rook2-exact'; image_hash=sha(image)
    assert image_hash==receipt['binary_output']['sha256']
    output=E/'activity-category-masks-focused-native-check-20261019-01';output.mkdir()
    env=os.environ|receipt['environment_overrides']
    command=['/usr/bin/cargo','test','--offline','--locked','--release','--target',receipt['target_triple'],'--jobs','4','--target-dir',receipt['target_directory'],'--manifest-path',str(W/'Cargo.toml'),'--lib','activity_batch_','--','--test-threads=1']
    save(output/'command.json',dict(command=command,source_sha256=before,frozen_binary_sha256=image_hash,expected_tests=8,expected_old_filtered=178,scope='focused eight new tests only; full186 not authorized',environment_overrides=receipt['environment_overrides'],helper_sha256=sha(__file__),started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat()))
    with (output/'tests.stdout').open('xb') as out,(output/'tests.stderr').open('xb') as err:
        child=subprocess.Popen(command,cwd=W,env=env,stdout=out,stderr=err);code=child.wait()
    after={p:sha(W/p) for p in before}
    text=(output/'tests.stdout').read_text()
    passed=code==0 and 'test result: ok. 8 passed; 0 failed;' in text and '178 filtered out;' in text
    result=dict(complete=passed and before==after and sha(image)==image_hash,pid=child.pid,exit_code=code,source_unchanged=before==after,frozen_binary_unchanged=sha(image)==image_hash,new_passed=8 if passed else None,old_tests_executed=0,old_filtered=178 if passed else None,full186_executed=False,logs={name:sha(output/name) for name in ['tests.stdout','tests.stderr']})
    save(output/'result.json',result);print(json.dumps(result));return 0 if result['complete'] else 1
if __name__=='__main__':sys.exit(main())
