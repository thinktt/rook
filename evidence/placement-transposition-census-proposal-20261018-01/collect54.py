#!/usr/bin/env python3
"""One original54 strict serial collection; every native encounter preserved, untimed."""
from common import *
import shutil

def main():
    plan=guard('collect');build=Path(plan['build']);terminal(build/'tool-terminal.json')
    receipt=load(build/'receipt.json');image=build/'rook2-exact';identity=sha(image)
    assert receipt['binary_output']['sha256']==identity
    assert receipt['source_sha256_before']==receipt['source_sha256_after']==plan['native48'] and receipt['tool_sha256_before']==receipt['tool_sha256_after']==plan['tools23']
    out=Path(plan['collection']);assert not out.exists();assert shutil.disk_usage(out.parent).free>=plan['maximum_private_bytes']+plan['free_disk_margin_bytes'];out.mkdir()
    write(out/'manifest.json',{'plan_sha256':sha(P/'plan.json'),'image_sha256':identity,'case_order':plan['case_order'],'helper_affinity':H,'scope':'D=true diagnostic counts only; native inherits housekeeping, no separate per-native affinity observation; unrelated untimed full117 may overlap','maximum_private_bytes':plan['maximum_private_bytes']})
    rows=[];used=0
    try:
        for case in plan['case_order']:
            guard('collect');assert sha(image)==identity
            d=out/case;d.mkdir();raw=d/'encounters.bin';report=d/'native-counts.jsonl'
            allowance=plan['maximum_private_bytes']-used;assert allowance>=4244
            assert shutil.disk_usage(out).free>=allowance+plan['free_disk_margin_bytes']
            env=dict(os.environ,ROOK2_CENSUS_RAW=str(raw),ROOK2_CENSUS_REPORT=str(report),ROOK2_CENSUS_MAX_BYTES=str(allowance))
            argv=['/usr/bin/node',plan['replay_checker'],'--case',case,'--',str(image)]
            child(argv,d/'comparator',env=env)
            comparator=load(d/'comparator.stdout');assert comparator['status']=='pass' and comparator['selectedCases']==[case] and len(comparator['results'])==1
            result=comparator['results'][0]
            assert result['command']==[str(image),*plan['runtime_modes']] and result['error'] is None
            assert result['status']=='pass' and result['exit']=={'code':0,'signal':None} and result['complete'] and not result['truncated'] and result['discardedObservedBytes']==0 and not result.get('cleanupUnconfirmed',False)
            assert result['stderr']=='' and (d/'comparator.stderr').read_bytes()==b''
            with report.open('rb') as f:header=json.loads(f.readline())
            assert header['type']=='header' and header['pid']==result['pid'] and header['byte_limit']==allowance
            size=raw.stat().st_size+report.stat().st_size;assert size<=allowance;used+=size
            rows.append({'case':case,'native_pid':result['pid'],'normal_exit':result['exit'],'raw_sha256':sha(raw),'report_sha256':sha(report),'private_bytes':size,'comparator_sha256':sha(d/'comparator.stdout'),'allowance':allowance})
            write(d/'receipt.json',rows[-1]);print(json.dumps({'case':case,'private_bytes':size,'total_private_bytes':used}),flush=True)
        assert len(rows)==54 and len({x['native_pid'] for x in rows})==54 and used<=plan['maximum_private_bytes'];guard('collect')
        write(out/'result.json',{'complete':True,'cases':rows,'total_private_bytes':used,'image_sha256':identity,'plan_sha256':sha(P/'plan.json'),'native_runs':54,'cpu_interpretation':False})
    except BaseException as error:
        write(out/'failure.json',{'error':repr(error),'completed_cases':rows,'private_bytes_completed':used,'all_outputs_preserved':True});raise
if __name__=='__main__':main()
