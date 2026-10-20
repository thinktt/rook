"""Untimed strict protocol check after actual prototype native job closure."""
from pathlib import Path
import hashlib,json,os,subprocess,sys
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
OUT=ROOT/'evidence/root-scheduler-native-protocol-20261018'
ENGINE=ROOT/'evidence/root-scheduler-native-build-20261018/rook2-exact'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:json.loads(p.read_text())
def main():
    assert sorted(os.sched_getaffinity(0))==[0,1,2,3,4,5,8,9,10,11,12,13]
    previous=load(ROOT/'evidence/root-scheduler-native-validation-20261018/tool-terminal.json')
    assert previous['actual_tool_terminal_observed'] and previous['exit_code']==0
    assert sha(ENGINE)==previous['artifact_sha256']
    OUT.mkdir(exist_ok=False)
    result=dict(complete=False,failure=None,artifact_sha256=sha(ENGINE),stages=[],
        scope='Parent authorized strict54/eightwire24 after passed158 and source review; untimed helpers+engines housekeeping, no codegen/performance/adoption claim')
    def run(command,stem):
        with (OUT/(stem+'.stdout')).open('xb') as a,(OUT/(stem+'.stderr')).open('xb') as b:
            child=subprocess.run(command,cwd=ROOT,stdout=a,stderr=b)
        result['stages'].append(dict(command=command,exit_code=child.returncode,actual_child_return_observed=True))
        assert child.returncode==0,stem+' failed'
    try:
        run(['/usr/bin/node','/home/legolas/king-spec/conformance/profiling/replay-check.mjs','--',str(ENGINE)],'strict54')
        report=load(OUT/'strict54.stdout')
        assert report['status']=='pass' and len(report['results'])==54 and (OUT/'strict54.stderr').stat().st_size==0
        for row in report['results']:
            assert row['status']=='pass' and row['complete'] and not row['truncated']
            assert row['exit']==dict(code=0,signal=None) and row['error'] is None and row['stderr']==''
            assert row['discardedObservedBytes']==0 and not row.get('cleanupUnconfirmed',False)
        run([sys.executable,str(ROOT/'tools/check_live.py'),'--engine',str(ENGINE),'--output',str(OUT/'wire')],'wire')
        report=load(OUT/'wire/receipt.json')
        assert report['pass'] and len(report['results'])==8 and sum(len(r['searches']) for r in report['results'])==24
        for row in report['results']:
            assert row['complete_streams'] and row['exit_code']==row['observed_exit_code']==0
        assert report['engine_sha256_before']==report['engine_sha256_after']==sha(ENGINE)==result['artifact_sha256']
        result.update(complete=True,strict_replays=54,wire_fixtures=8,wire_searches=24)
    except BaseException as error:result['failure']=f'{type(error).__name__}: {error}'
    finally:
        with (OUT/'verification.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps({k:v for k,v in result.items() if k!='stages'}),flush=True)
    return 0 if result['complete'] else 1
if __name__=='__main__':sys.exit(main())
