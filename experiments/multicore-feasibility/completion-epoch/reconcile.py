#!/usr/bin/env python3
"""Independent original replay/cost/placement and completion epoch audit."""
import argparse
import json
from pathlib import Path
import sys
sys.dont_write_bytecode=True
from common import (ACCOUNT,HELPERS,LIMITS,METRICS,CASES,NAMES,SPEC,admission,audit,audit_placement,
    baseline,code_paths,dist,housekeeping_audit,image_layout,native_receipt,preparation,
    prepared_run,read,readiness,readiness_summary,sha,variants)


def audit_run(base):
    base=Path(base).resolve()
    plan,result=read(base/'plan.json'),read(base/'result.json')
    assert plan['schema']=='rook2-completion-epoch-generic-v1' and result['complete'] and result['failure'] is None
    assert CASES==['profile-35','profile-08','profile-43']
    assert NAMES==['preserved1','preserved3','inline1','owner3']
    expected=[]
    for case in CASES:
        expected += [dict(case=case,variant=name,warmup=True,repeat=0) for name in NAMES]
        for rotation in range(3):
            order=NAMES[rotation:]+NAMES[:rotation]
            expected += [dict(case=case,variant=name,warmup=False,repeat=rotation+1) for name in order]
    assert len(expected)==len(result['runs'])==48 and plan['schedule']==expected
    assert plan['coordinatorCpu']==14 and plan['helperCpus']==[6,4]
    assert plan['idleOwnedSiblings']==[5,7,15] and plan['helperAffinity']==sorted(HELPERS)
    assert plan['nativePreExecAffinities']=={'1':[6,14],'2':[6,14],'3':[4,6,14]}
    assert plan['limits']==LIMITS and plan['protectedArtifacts']==baseline()
    hashes=plan['inputSha256']
    assert all(str(path) in hashes for path in code_paths())
    for path,digest in hashes.items(): assert sha(path)==digest,path
    prepared_path,record_path=Path(plan['sourcePreparation']),Path(plan['preparedRun'])
    prepared=preparation(prepared_path);record=prepared_run(record_path,prepared_path,prepared)
    assert isinstance(record,dict)
    assert plan['layoutAdmission']==record['layout']
    assert plan['loweringAdmission']==record['lowering']
    assert hashes[str(prepared_path)]==sha(prepared_path) and hashes[str(record_path)]==sha(record_path)
    for key in ['sourceChanges','sourceAdded','sourceRemoved','controlSource','candidateSource','evidenceReuse','readinessSemantics','sourceChallenge']:
        assert plan[key]==prepared[key]
    assert len(plan['controlSource'])==len(plan['candidateSource'])==69
    assert plan['sourceChanges']==['src/colors_worker.rs']
    assert plan['sourceAdded']==plan['sourceRemoved']==[]
    modes=plan['variants'];assert list(modes)==NAMES and modes==variants(Path(record['candidate']['path']))
    for name,budget in zip(NAMES,[1,3,1,3]):
        assert modes[name]['budget']==budget and modes[name]['report'] is True
        assert modes[name]['options']==['--threads='+str(budget),'--owner-local-inventory','--q-owner-local-inventory']
    assert modes['preserved1']['path']==modes['preserved3']['path']==record['control']['path']
    assert modes['inline1']['path']==modes['owner3']['path']==record['candidate']['path']
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
    bindings=[]
    for index,(step,row) in enumerate(zip(expected,result['runs'])):
        value=modes[step['variant']]
        directory=base/f'{index:02d}-{step["case"]}-{step["variant"]}-r{step["repeat"]}'
        native,count=audit.lifetime(directory,row,step,Path(value['path']),value['budget'],value['options'],hashes)
        assert len(native['native_post_exec']['task_affinities'])==value['budget']
        assert row['orderedPosts']==count and row['placement']==audit_placement(directory,native,hashes)
        assert previous_end<=row['controllerStartMonotonicNs']<=native['start_monotonic_ns']
        assert native['reaped_monotonic_ns']<=row['controllerEndMonotonicNs']<=end and native['wall_ns']<=180*10**9
        readiness(directory,row['colors'],value['budget'],True)
        bindings.append(dict(kind='replay',**step,engine=native['engine'],
            engineSha256=native['engine_sha256_before'],argv=native['argv'],
            threadBudget=native['expected_threads'],nativePid=native['native_pid'],
            nativeReceiptSha256=sha(directory/'native.json')))
        assert native['native_pid'] not in pids
        pids.add(native['native_pid']);posts+=count;previous_end=row['controllerEndMonotonicNs']
    assert len(result['idle'])==4
    for name,row in zip(NAMES,result['idle']):
        value,directory=modes[name],base/('idle-'+name)
        assert row['variant']==name and read(directory/'probe.json')==row
        native=native_receipt(directory/'native.json',Path(value['path']),value['budget'],value['options'],hashes)
        assert len(native['native_post_exec']['task_affinities'])==value['budget']
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
        bindings.append(dict(kind='idle',variant=name,engine=native['engine'],
            engineSha256=native['engine_sha256_before'],argv=native['argv'],
            threadBudget=native['expected_threads'],nativePid=native['native_pid'],
            nativeReceiptSha256=sha(directory/'native.json')))
        assert native['native_pid'] not in pids;pids.add(native['native_pid']);previous_end=native['reaped_monotonic_ns']
    assert len(pids)==len(bindings)==52 and result['rowBindings']==bindings
    assert result['terminalNativeReceipts']==52
    assert sum(not row['warmup'] for row in result['runs'])==36
    assert sum(row['warmup'] for row in result['runs'])==12
    oracle={row['id']:row for row in read(SPEC/'replay-oracle.json')['cases']}
    expected_posts=sum(len(oracle[step['case']]['posts']) for step in expected)
    assert posts==expected_posts==560
    work=[dict(case=case,orderedPosts=len(oracle[case]['posts']),
        finalPostWorkThousands=oracle[case]['posts'][-1]['workThousands'] if oracle[case]['posts'] else None)
        for case in CASES]
    summaries=[dict(case=case,variant=name,**{key:dist([row[key] for row in result['runs']
        if row['case']==case and row['variant']==name and not row['warmup']]) for key in METRICS}) for case in CASES for name in NAMES]
    assert summaries==result['summaries']
    by={(row['case'],row['variant']):row for row in summaries}
    pairs=[('owner3','preserved3'),('inline1','preserved1'),('owner3','inline1'),('preserved3','preserved1')]
    comparisons=[dict(case=case,**{a+'Vs'+b:{key:by[case,a][key]['median']/by[case,b][key]['median']
        for key in METRICS} for a,b in pairs}) for case in CASES]
    sums={name:{key:sum(by[case,name][key]['median'] for case in CASES) for key in METRICS} for name in NAMES}
    ratios={a+'Vs'+b:{key:sums[a][key]/sums[b][key] for key in METRICS} for a,b in pairs}
    color_readiness=[dict(case=case,variant=name,**readiness_summary([row for row in result['runs']
        if row['case']==case and row['variant']==name and not row['warmup']]))
        for case in CASES for name in ['preserved3','owner3']]
    colors=[]
    for case in CASES:
        reports=[row['colors']['report'] for row in result['runs'] if row['case']==case and row['variant'] in ['preserved3','owner3']]
        assert len(reports)==8
        for field in ['dispatches','sampled_dispatches','completed_samples','paired_samples']:
            assert len({value[field] for value in reports})==1,(case,field)
        colors.append(dict(case=case,**{field:reports[0][field] for field in
            ['dispatches','sampled_dispatches','completed_samples','paired_samples']}))
    cpus={'cpu4','cpu5','cpu6','cpu7','cpu14','cpu15'}
    def ticks(path):
        return {parts[0]:[int(item) for item in parts[1:]] for line in path.read_text().splitlines()
            if (parts:=line.split()) and parts[0] in cpus}
    before,after=ticks(base/'proc-stat-before'),ticks(base/'proc-stat-after')
    assert set(before)==set(after)==cpus
    deltas={cpu:[y-x for x,y in zip(before[cpu],after[cpu])] for cpu in cpus}
    assert all(len(before[cpu])==len(after[cpu]) and all(item>=0 for item in deltas[cpu]) for cpu in cpus)
    output=dict(schema='rook2-completion-epoch-audit-v1',complete=True,replayLives=48,measured=36,warmups=12,idleProcesses=4,
        nativeProcesses=len(pids),terminalNativeReceipts=len(pids),rowBindingsVerified=len(bindings),rowBindings=bindings,orderedPosts=posts,expectedOrderedPosts=expected_posts,
        summaries=summaries,comparisons=comparisons,summedMedians=sums,ratios=ratios,variants=modes,work=work,
        colorDispatches=colors,readiness=color_readiness,idle=result['idle'],housekeeping=housekeeping_audit(base/'housekeeping.json'),
        readinessSemantics=plan['readinessSemantics'],evidenceReuse=plan['evidenceReuse'],sourceChallenge=plan['sourceChallenge'],images=plan['images'],layoutAdmission=plan['layoutAdmission'],
        loweringAdmission=plan['loweringAdmission'],
        sourceChanges=plan['sourceChanges'],sourceAdded=prepared['sourceAdded'],sourceRemoved=prepared['sourceRemoved'],
        controlSource=plan['controlSource'],candidateSource=plan['candidateSource'],protectedArtifacts=plan['protectedArtifacts'],
        guestCpuTickDeltas=deltas,raw=str(base),rawSha256={name:sha(base/name) for name in ['plan.json','result.json','housekeeping.json','proc-stat-before','proc-stat-after']},
        reconcilerSha256=sha(Path(__file__)),
        scope='fixed three-case generic completion epoch discriminator; unchanged sparse512 observations; owner-ready precedes ordinary/Q hooks; sampled residual join excludes eager generation and cannot measure saved work; no hot census or measured-life layout queries; cold actual-production layout admission bound separately; complete native wall/CPU/RSS; no PGO/qualification/adoption or host-exclusivity claim')
    return output


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('raw',type=Path);parser.add_argument('--output',type=Path)
    args=parser.parse_args();base=args.raw.resolve()
    output=audit_run(base)
    with (args.output or base/'reconciled.json').open('x') as stream:
        json.dump(output,stream,indent=2,allow_nan=False);stream.write('\n')
    print(json.dumps({key:output[key] for key in ['complete','replayLives','orderedPosts','summedMedians','comparisons']},indent=2))


if __name__=='__main__': main()
