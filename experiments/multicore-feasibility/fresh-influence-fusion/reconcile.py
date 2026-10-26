#!/usr/bin/env python3
"""Independent original replay/cost/placement and fresh-Influence fusion audit."""
import argparse
import json
from pathlib import Path
import sys
sys.dont_write_bytecode=True
from common import (ACCOUNT,HELPERS,LIMITS,METRICS,CASES,NAMES,admission,audit,audit_placement,
    baseline,code_paths,dist,housekeeping_audit,image_layout,native_receipt,preparation,
    prepared_run,read,readiness,readiness_summary,sha,variants)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('raw',type=Path);parser.add_argument('--output',type=Path)
    args=parser.parse_args();base=args.raw.resolve()
    plan,result=read(base/'plan.json'),read(base/'result.json')
    assert plan['schema']=='rook2-fresh-influence-fusion-generic-v1' and result['complete'] and result['failure'] is None
    expected=[]
    for case in CASES:
        expected += [dict(case=case,variant=name,warmup=True,repeat=0) for name in NAMES]
        for rotation in range(3):
            order=NAMES[rotation:]+NAMES[:rotation]
            expected += [dict(case=case,variant=name,warmup=False,repeat=rotation+1) for name in order]
    assert len(expected)==len(result['runs'])==36 and plan['schedule']==expected
    assert plan['coordinatorCpu']==14 and plan['helperCpus']==[6,4]
    assert plan['idleOwnedSiblings']==[5,7,15] and plan['helperAffinity']==sorted(HELPERS)
    assert plan['nativePreExecAffinities']=={'1':[6,14],'2':[6,14],'3':[4,6,14]}
    assert plan['limits']==LIMITS and plan['protectedArtifacts']==baseline()
    hashes=plan['inputSha256']
    assert all(str(path) in hashes for path in code_paths())
    for path,digest in hashes.items(): assert sha(path)==digest,path
    prepared_path,record_path=Path(plan['sourcePreparation']),Path(plan['preparedRun'])
    prepared=preparation(prepared_path);record=prepared_run(record_path,prepared_path,prepared)
    assert hashes[str(prepared_path)]==sha(prepared_path) and hashes[str(record_path)]==sha(record_path)
    for key in ['sourceChanges','controlSource','candidateSource','evidenceReuse','readinessSemantics']:
        assert plan[key]==prepared[key]
    modes=plan['variants'];assert list(modes)==NAMES and modes==variants(Path(record['candidate']['path']))
    assert plan['images']=={name:image_layout(Path(value['path'])) for name,value in modes.items()}
    assert plan['candidateBuild']==str(record_path.parent/'candidate-build')
    admission(record_path.parent/'candidate-build',Path(record['candidate']['path']),prepared)
    assert plan['pipelineStartMonotonicNs']==record['pipelineStartMonotonicNs']
    assert plan['pipelineDeadlineMonotonicNs']==record['pipelineDeadlineMonotonicNs']
    assert plan['pipelineDeadlineMonotonicNs']==plan['pipelineStartMonotonicNs']+3600*10**9
    start,end=result['streamStartMonotonicNs'],result['streamEndMonotonicNs']
    assert plan['streamStartMonotonicNs']==start and record['preparedMonotonicNs']<=start
    assert 0<end-start<=1800*10**9 and end<plan['pipelineDeadlineMonotonicNs']
    previous_end,pids,posts=start,set(),0
    for index,(step,row) in enumerate(zip(expected,result['runs'])):
        value=modes[step['variant']]
        directory=base/f'{index:02d}-{step["case"]}-{step["variant"]}-r{step["repeat"]}'
        native,count=audit.lifetime(directory,row,step,Path(value['path']),value['budget'],value['options'],hashes)
        assert row['orderedPosts']==count and row['placement']==audit_placement(directory,native,hashes)
        assert previous_end<=row['controllerStartMonotonicNs']<=native['start_monotonic_ns']
        assert native['reaped_monotonic_ns']<=row['controllerEndMonotonicNs']<=end and native['wall_ns']<=180*10**9
        readiness(directory,row['colors'],value['budget'],True)
        assert native['native_pid'] not in pids
        pids.add(native['native_pid']);posts+=count;previous_end=row['controllerEndMonotonicNs']
    assert len(result['idle'])==3
    for name,row in zip(NAMES,result['idle']):
        value,directory=modes[name],base/('idle-'+name)
        assert row['variant']==name and read(directory/'probe.json')==row
        native=native_receipt(directory/'native.json',Path(value['path']),value['budget'],value['options'],hashes)
        assert read(directory/'launch.json')==dict(argv=[native['python_executable'],str(ACCOUNT),
            '--engine',value['path'],'--record',str(directory/'native.json'),'--known-single-process',
            '--thread-budget',str(value['budget']),*value['options']],variant=name,kind='startup-idle-shutdown')
        assert row['nativePid']==native['native_pid'] and row['supervisorPid']==native['supervisor_pid']
        assert row['wholeCpuSeconds']==native['total_cpu_s'] and row['wholeWallNs']==native['wall_ns']
        assert row['rssKiB']==native['maxrss_linux_kib'] and row['placement']==audit_placement(directory,native,hashes)
        assert row['idleCpuTicks']==row['shutdownStartCpuTicks']-row['startupCpuTicks']>=0
        assert row['tickHz']==read(next(base.glob('*-r0'))/'tap-config.json')['tickHz']
        assert row['idleCpuSeconds']==row['idleCpuTicks']/row['tickHz']
        assert row['idleNs']==row['idleEndMonotonicNs']-row['idleStartMonotonicNs']>=250_000_000
        assert previous_end<=native['start_monotonic_ns']<row['idleStartMonotonicNs']<row['idleEndMonotonicNs']<native['reaped_monotonic_ns']<=end
        assert row['startupReplyNs']>0 and row['shutdownSupervisorNs']>0
        assert (directory/'stdin.raw').read_bytes()==b'cm_parm\nquit\n' and (directory/'stdout.raw').read_bytes()==b'cm_parm\n'
        assert (directory/'stderr').read_bytes()==b''
        for file,digest in row['sha256'].items(): assert sha(directory/file)==digest
        readiness(directory,row['colors'],value['budget'],True,idle=True)
        assert native['native_pid'] not in pids;pids.add(native['native_pid']);previous_end=native['reaped_monotonic_ns']
    assert len(pids)==39
    summaries=[dict(case=case,variant=name,**{key:dist([row[key] for row in result['runs']
        if row['case']==case and row['variant']==name and not row['warmup']]) for key in METRICS}) for case in CASES for name in NAMES]
    assert summaries==result['summaries']
    by={(row['case'],row['variant']):row for row in summaries}
    pairs=[('fused3','unfused3'),('fused3','preserved3'),('unfused3','preserved3')]
    comparisons=[dict(case=case,**{a+'Vs'+b:{key:by[case,a][key]['median']/by[case,b][key]['median']
        for key in METRICS[:3]} for a,b in pairs}) for case in CASES]
    sums={name:{key:sum(by[case,name][key]['median'] for case in CASES) for key in METRICS[:3]} for name in NAMES}
    color_readiness=[dict(case=case,variant=name,**readiness_summary([row for row in result['runs']
        if row['case']==case and row['variant']==name and not row['warmup']]))
        for case in CASES for name in ['preserved3','unfused3','fused3']]
    colors=[]
    for case in CASES:
        reports=[row['colors']['report'] for row in result['runs'] if row['case']==case and row['variant'] in ['preserved3','unfused3','fused3']]
        assert len(reports)==12 and len({value['dispatches'] for value in reports})==1
        colors.append(dict(case=case,dispatches=reports[0]['dispatches']))
    cpus={'cpu4','cpu5','cpu6','cpu7','cpu14','cpu15'}
    def ticks(path):
        return {parts[0]:[int(item) for item in parts[1:]] for line in path.read_text().splitlines()
            if (parts:=line.split()) and parts[0] in cpus}
    before,after=ticks(base/'proc-stat-before'),ticks(base/'proc-stat-after')
    assert set(before)==set(after)==cpus
    deltas={cpu:[y-x for x,y in zip(before[cpu],after[cpu])] for cpu in cpus}
    assert all(len(before[cpu])==len(after[cpu]) and all(item>=0 for item in deltas[cpu]) for cpu in cpus)
    output=dict(schema='rook2-fresh-influence-fusion-audit-v1',complete=True,replayLives=36,measured=27,warmups=9,idleProcesses=3,
        orderedPosts=posts,summaries=summaries,comparisons=comparisons,summedMedians=sums,
        colorDispatches=colors,readiness=color_readiness,idle=result['idle'],housekeeping=housekeeping_audit(base/'housekeeping.json'),
        readinessSemantics=plan['readinessSemantics'],evidenceReuse=plan['evidenceReuse'],images=plan['images'],
        sourceChanges=plan['sourceChanges'],sourceAdded=prepared['sourceAdded'],
        coldFusionWitnesses=[dict(case=r['case'],variant=r['variant'],repeat=r['repeat'],warmup=r['warmup'],fusion=r['colors']['report'].get('fusion')) for r in result['runs']],
        guestCpuTickDeltas=deltas,raw=str(base),rawSha256={name:sha(base/name) for name in ['plan.json','result.json','housekeeping.json','proc-stat-before','proc-stat-after']},
        reconcilerSha256=sha(Path(__file__)),
        scope='fixed three-case generic fresh-Influence fusion discriminator; cold native activation, not eligible-population census; complete native wall/CPU/RSS; no PGO/qualification/adoption or host-exclusivity claim')
    with (args.output or base/'reconciled.json').open('x') as stream:
        json.dump(output,stream,indent=2,allow_nan=False);stream.write('\n')
    print(json.dumps({key:output[key] for key in ['complete','replayLives','orderedPosts','summedMedians','comparisons']},indent=2))


if __name__=='__main__': main()
