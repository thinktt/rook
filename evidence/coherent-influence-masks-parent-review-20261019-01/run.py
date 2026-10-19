#!/usr/bin/env python3
"""Check the finished isolated source freeze, build or run declared focused tests."""
from pathlib import Path
import json,hashlib,os,subprocess,sys,datetime
R=Path('/home/legolas/rook2');E=R/'evidence'
W=Path('/home/legolas/rook2-work/imp2-coherent-influence-masks-20261019-01')
P=E/'coherent-influence-masks-parent-review-20261019-01'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
save=lambda p,v:Path(p).write_text(json.dumps(v,indent=2)+'\n')
def main():
 assert set(os.sched_getaffinity(0))=={0,1,2,3,4,5,8,9,10,11,12,13}
 assert not any(os.environ.get(k) for k in ['LD_PRELOAD','LD_LIBRARY_PATH','LLVM_PROFILE_FILE'])
 assert os.environ.get('PATH')=='/usr/bin:/bin'
 f=json.loads((P/'source-freeze.json').read_text());assert f['parent_source_review_passed']
 before={p:sha(W/p) for p in f['files_sha256']};assert before==f['files_sha256']
 mode=sys.argv[1];assert mode in ('build','focused')
 out=E/('coherent-influence-masks-'+('generic-build-execution' if mode=='build' else 'focused-native-check')+'-20261019-01')
 assert not out.exists()
 env=os.environ.copy()
 if mode=='build':
  assert f['generic_build_authorized'];out.mkdir()
  cmd=['/usr/bin/python3',str(R/'tools/build.py'),'--crate',str(W),'--mode','generic','--bin','rook2','--jobs','4','--output',str(E/'coherent-influence-masks-generic-build-20261019-01')]
 else:
  assert f['focused_authorized'];out.mkdir()
  receipt=json.loads((E/'coherent-influence-masks-generic-build-20261019-01/receipt.json').read_text())
  assert receipt['outcome']=='build-succeeded-with-stable-input-snapshot'
  env|=receipt['environment_overrides']
  cmd=['/usr/bin/cargo','test','--offline','--locked','--release','--target',receipt['target_triple'],'--jobs','4','--target-dir',receipt['target_directory'],'--manifest-path',str(W/'Cargo.toml'),'--lib','experiment37_','--','--test-threads=1']
 save(out/'command.json',{'command':cmd,'source_sha256':before,'mode':mode,'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'helper_sha256':sha(__file__)})
 with (out/'stdout').open('xb') as o,(out/'stderr').open('xb') as e:
  child=subprocess.Popen(cmd,cwd=W,env=env,stdout=o,stderr=e);code=child.wait()
 after={p:sha(W/p) for p in before}
 ok=code==0 and before==after
 if mode=='focused':
  text=(out/'stdout').read_text();n=f['new_focused_tests'];old=f['old_library_tests']
  ok=ok and f'test result: ok. {n} passed; 0 failed;' in text and f'{old} filtered out;' in text
 save(out/'result.json',{'complete':ok,'pid':child.pid,'exit_code':code,'source_unchanged':before==after,'mode':mode,'scope':'generic build only' if mode=='build' else 'declared new focused tests only; old native suite not executed','logs':{n:sha(out/n) for n in ['stdout','stderr']}})
 print(json.dumps({'complete':ok,'exit_code':code,'mode':mode,'output':str(out)}));return 0 if ok else 1
if __name__=='__main__':sys.exit(main())
