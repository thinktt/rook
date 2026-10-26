#!/usr/bin/env python3
"""Independent saved replay/cost/placement audit; lean observations stay disabled."""
import argparse
import json
from pathlib import Path
import sys
sys.dont_write_bytecode=True
from common import (ACCOUNT,HELPERS,LIMITS,METRICS,CASES,NAMES,DISABLED,admission,audit,audit_placement,
    baseline,code_paths,dist,housekeeping_audit,image_layout,layout_admission,native_receipt,preparation,
    prepared_run,read,readiness,readiness_summary,sha,variants)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('raw',type=Path);parser.add_argument('--output',type=Path)
    args=parser.parse_args();base=args.raw.resolve()
    plan,result=read(base/'plan.json'),read(base/'result.json')
    assert plan['schema']=='rook2-fixed-layout-no-observations-generic-v1' and result['complete'] and result['failure'] is None
    expected=[]
    for case_index,case in enumerate(CASES):
        expected += [dict(case=case,variant=name,warmup=True,repeat=0) for name in NAMES]
        for repeat in range(3):
            rotation=(case_index*3+repeat)%6
            order=NAMES[rotation:]+NAMES[:rotation]
            expected += [dict(case=case,variant=name,warmup=False,repeat=repeat+1) for name in order]
    assert len(expected)==len(result['runs'])==72 and plan['schedule']==expected
    assert plan['coordinatorCpu']==14 and plan['helperCpus']==[6,4,2]
    assert plan['idleOwnedSiblings']==[3,5,7,15] and plan['helperAffinity']==sorted(HELPERS)
    assert plan['nativePreExecAffinities']=={'1':[6,14],'2':[6,14],'3':[4,6,14],'4':[2,4,6,14]}
    assert plan['limits']==LIMITS and plan['protectedArtifacts']==baseline()
    hashes=plan['inputSha256']
    assert all(str(path) in hashes for path in code_paths())
    for path,digest in hashes.items(): assert sha(path)==digest,path
    prepared_path,record_path=Path(plan['sourcePreparation']),Path(plan['preparedRun'])
    prepared=preparation(prepared_path);record=prepared_run(record_path,prepared_path,prepared)
    layout_path=record_path.parent/'layout-admission.json'
    layout=layout_admission(layout_path,prepared_path,prepared,record_path,record)
    assert plan['layoutAdmission']==dict(path=str(layout_path),sha256=sha(layout_path),report=layout)
    assert hashes[str(layout_path)]==sha(layout_path)
    assert all(hashes[path]==digest for path,digest in layout['inputSha256'].items())
    assert hashes[str(prepared_path)]==sha(prepared_path) and hashes[str(record_path)]==sha(record_path)
    for key in ['sourceChanges','sourceAdded','sourceRemoved','controlSource','numericalControlSource','leanSource','candidateSource','evidenceReuse','readinessSemantics']:
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
        readiness(directory,row['colors'],value['budget'],preserved=step['variant']=='retained3',disabled=step['variant'] in DISABLED)
        assert native['native_pid'] not in pids
        pids.add(native['native_pid']);posts+=count;previous_end=row['controllerEndMonotonicNs']
    assert len(result['idle'])==6
    for name,row in zip(NAMES,result['idle']):
        value,directory=modes[name],base/('idle-'+name)
        assert row['variant']==name and read(directory/'probe.json')==row
        native=native_receipt(directory/'native.json',Path(value['path']),value['budget'],value['options'],hashes)
        assert read(directory/'launch.json')==dict(argv=[native['python_executable'],str(ACCOUNT),'--account',
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
        readiness(directory,row['colors'],value['budget'],preserved=name=='retained3',idle=True,disabled=name in DISABLED)
        assert native['native_pid'] not in pids;pids.add(native['native_pid']);previous_end=native['reaped_monotonic_ns']
    assert len(pids)==78
    summaries=[dict(case=case,variant=name,**{key:dist([row[key] for row in result['runs']
        if row['case']==case and row['variant']==name and not row['warmup']]) for key in METRICS}) for case in CASES for name in NAMES]
    assert summaries==result['summaries']
    by={(row['case'],row['variant']):row for row in summaries}
    pairs=[('fixed3','observed3'),('fixed3','lean3'),('fixed3','retained3'),
        ('fixed4','fixed3'),('fixed4','retained3'),('fixed4','observed4'),
        ('observed3','retained3'),('lean3','retained3'),('lean3','observed3')]
    comparisons=[dict(case=case,**{a+'Vs'+b:{key:by[case,a][key]['median']/by[case,b][key]['median']
        for key in METRICS[:3]} for a,b in pairs}) for case in CASES]
    sums={name:{key:sum(by[case,name][key]['median'] for case in CASES) for key in METRICS} for name in NAMES}
    inventory=[dict(case=case,repeat=row['repeat'],report=row['colors']['report']['inventory'])
        for case in CASES for row in result['runs'] if row['case']==case and row['variant']=='observed4' and not row['warmup']]
    color_readiness=[dict(case=case,variant=name,**readiness_summary([row for row in result['runs']
        if row['case']==case and row['variant']==name and not row['warmup']]))
        for case in CASES for name in ['retained3','observed3','observed4']]
    colors=[]
    for case in CASES:
        reports=[row['colors']['report'] for row in result['runs'] if row['case']==case and row['variant'] in ['retained3','observed3','observed4']]
        assert len({value['dispatches'] for value in reports})==1
        colors.append(dict(case=case,dispatches=reports[0]['dispatches']))
    cpus={'cpu2','cpu3','cpu4','cpu5','cpu6','cpu7','cpu14','cpu15'}
    def ticks(path):
        return {parts[0]:[int(item) for item in parts[1:]] for line in path.read_text().splitlines()
            if (parts:=line.split()) and parts[0] in cpus}
    before,after=ticks(base/'proc-stat-before'),ticks(base/'proc-stat-after')
    assert set(before)==set(after)==cpus
    deltas={cpu:[y-x for x,y in zip(before[cpu],after[cpu])] for cpu in cpus}
    assert all(len(before[cpu])==len(after[cpu]) and all(item>=0 for item in deltas[cpu]) for cpu in cpus)
    output=dict(schema='rook2-fixed-layout-no-observations-audit-v1',complete=True,replayLives=72,measured=54,warmups=18,idleProcesses=6,
        orderedPosts=posts,summaries=summaries,comparisons=comparisons,summedMedians=sums,aggregateRatios={a+'Vs'+b:{key:sums[a][key]/sums[b][key] for key in METRICS[:3]} for a,b in pairs},inventory=inventory,
        layoutAdmission=plan['layoutAdmission'],
        colorDispatches=colors,readiness=color_readiness,idle=result['idle'],housekeeping=housekeeping_audit(base/'housekeeping.json'),
        readinessSemantics=plan['readinessSemantics'],evidenceReuse=plan['evidenceReuse'],images=plan['images'],
        sourceChanges=plan['sourceChanges'],sourceAdded=plan['sourceAdded'],sourceRemoved=plan['sourceRemoved'],
        guestCpuTickDeltas=deltas,raw=str(base),rawSha256={name:sha(base/name) for name in ['plan.json','result.json','housekeeping.json','proc-stat-before','proc-stat-after']},
        reconcilerSha256=sha(Path(__file__)),
        observations=dict(retained3='original sparse colors report validated',observed3='original colors report validated',
            observed4='original colors/inventory report validated',**{name:dict(enabled=False) for name in DISABLED}),
        scope='one fixed old-layout/unobserved counterfactual; compiled-layout admission is exact-image, not actual heap-line/cache attribution; no new work census, PGO, serial-cost, qualification/adoption or automatic follow-on')
    with (args.output or base/'reconciled.json').open('x') as stream:
        json.dump(output,stream,indent=2,allow_nan=False);stream.write('\n')
    print(json.dumps({key:output[key] for key in ['complete','replayLives','orderedPosts','summedMedians','comparisons']},indent=2))


if __name__=='__main__': main()
