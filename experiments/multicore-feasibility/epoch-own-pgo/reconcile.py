#!/usr/bin/env python3
"""Independent saved-record audit and54-row sums; no helper or native execution."""
import argparse
import json
from pathlib import Path
import sys

sys.dont_write_bytecode=True
from common import (ACCOUNT, HELPERS, LIMITS, METRICS, NAMES, PIPELINE_SECONDS,
    SPEC, audit, audit_placement, baseline, cases, code_paths, drift, generic_evidence,
    housekeeping_audit, image_layout, native_receipt, preparation, prepared_run,
    read, readiness, readiness_summary, sha, variants)

PAIRS=[('epoch3','practical2'),('epoch3','current2'),('epoch3','serial1'),
       ('inline1','serial1'),('current2','practical2'),('epoch3','inline1')]


def guest_ticks(path):
    wanted={'cpu4','cpu5','cpu6','cpu7','cpu14','cpu15'}
    result={parts[0]:[int(item) for item in parts[1:]] for line in path.read_text().splitlines()
            if (parts:=line.split()) and parts[0] in wanted}
    assert set(result)==wanted
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('raw',type=Path)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    base=args.raw.resolve()
    plan,result=read(base/'plan.json'),read(base/'result.json')
    assert plan['schema']=='rook2-epoch-own-pgo-full54-v1' and plan['study']=='descriptive-original54'
    assert result['complete'] and result['failure'] is None
    expected=[]
    for index,case in enumerate(cases()):
        order=NAMES[index%5:]+NAMES[:index%5]
        expected += [dict(case=case,variant=name,warmup=False,repeat=1) for name in order]
    assert len(expected)==len(result['runs'])==270
    assert plan['cases']==cases() and plan['schedule']==expected
    assert plan['coordinatorCpu']==14 and plan['helperCpus']==[6,4]
    assert plan['idleOwnedSiblings']==[5,7,15] and plan['helperAffinity']==sorted(HELPERS)
    assert plan['nativePreExecAffinities']=={'1':[6,14],'2':[6,14],'3':[4,6,14]}
    assert plan['limits']==LIMITS and plan['protectedArtifacts']==baseline()
    hashes=plan['inputSha256']
    assert all(str(path) in hashes for path in code_paths())
    for path,digest in hashes.items():
        assert sha(path)==digest,path
    prepared_path,record_path=Path(plan['sourcePreparation']),Path(plan['preparedRun'])
    prepared=preparation(prepared_path)
    record,receipt,effective=prepared_run(record_path,prepared_path,prepared)
    assert hashes[str(prepared_path)]==sha(prepared_path) and hashes[str(record_path)]==sha(record_path)
    assert plan['source']==prepared['candidateSource'] and plan['evidenceReuse']==generic_evidence(prepared)
    assert plan['readinessSemantics']==prepared['readinessSemantics']
    assert plan['profileSha256']==record['profileSha256'] and plan['effectiveRustcOptions']==effective
    assert plan['drift']==drift(prepared,record_path.parent/'training/merged.profdata')
    assert plan['candidateBuild']==str(record_path.parent/'use-build')
    modes=plan['variants']
    assert list(modes)==NAMES and modes==variants(Path(record['candidate']['path']))
    assert plan['images']=={name:image_layout(Path(value['path'])) for name,value in modes.items()}
    assert plan['pipelineStartMonotonicNs']==record['pipelineStartMonotonicNs']
    assert plan['pipelineDeadlineMonotonicNs']==record['pipelineDeadlineMonotonicNs']
    assert plan['pipelineDeadlineMonotonicNs']==plan['pipelineStartMonotonicNs']+PIPELINE_SECONDS*10**9
    start,end=result['streamStartMonotonicNs'],result['streamEndMonotonicNs']
    assert plan['streamStartMonotonicNs']==start and record['preparedMonotonicNs']<=start
    assert 0<end-start<=LIMITS['totalSeconds']*10**9 and end<plan['pipelineDeadlineMonotonicNs']
    previous_end,pids,posts=start,set(),0
    posts_by_variant={name:0 for name in NAMES}
    for index,(step,row) in enumerate(zip(expected,result['runs'])):
        value=modes[step['variant']]
        directory=base/f'{index:03d}-{step["case"]}-{step["variant"]}-r1'
        native,count=audit.lifetime(directory,row,step,Path(value['path']),value['budget'],value['options'],hashes)
        assert row['placement']==audit_placement(directory,native,hashes)
        assert row['orderedPosts']==count
        assert previous_end<=row['controllerStartMonotonicNs']<=native['start_monotonic_ns']
        assert native['reaped_monotonic_ns']<=row['controllerEndMonotonicNs']<=end
        assert native['wall_ns']<=LIMITS['perLifeSeconds']*10**9
        readiness(directory,row['colors'],value['budget'],value['report'])
        assert bool(native['colors_report_path'])==value['report']
        assert native['native_pid'] not in pids
        pids.add(native['native_pid']);posts+=count;posts_by_variant[step['variant']]+=count
        previous_end=row['controllerEndMonotonicNs']
    assert len(result['idle'])==5
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
        assert row['tickHz']==read(next(base.glob('*-r1'))/'tap-config.json')['tickHz']
        assert row['idleCpuSeconds']==row['idleCpuTicks']/row['tickHz']
        assert row['idleNs']==row['idleEndMonotonicNs']-row['idleStartMonotonicNs']>=250_000_000
        assert previous_end<=native['start_monotonic_ns']<row['idleStartMonotonicNs']<row['idleEndMonotonicNs']<native['reaped_monotonic_ns']<=end
        assert row['startupReplyNs']>0 and row['shutdownSupervisorNs']>0
        assert (directory/'stdin.raw').read_bytes()==b'cm_parm\nquit\n'
        assert (directory/'stdout.raw').read_bytes()==b'cm_parm\n' and (directory/'stderr').read_bytes()==b''
        assert set(row['sha256'])=={'launch.json','native.json','stdin.raw','stdout.raw','stderr'}
        for file,digest in row['sha256'].items():
            assert sha(directory/file)==digest
        readiness(directory,row['colors'],value['budget'],value['report'],idle=True)
        assert native['native_pid'] not in pids
        pids.add(native['native_pid']);previous_end=native['reaped_monotonic_ns']
    assert len(pids)==275 and len(set(posts_by_variant.values()))==1
    by={(row['case'],row['variant']):row for row in result['runs']}
    assert len(by)==270
    table=[dict(case=case,**{name:{key:by[case,name][key] for key in METRICS} for name in NAMES}) for case in cases()]
    totals={name:{key:sum(by[case,name][key] for case in cases()) for key in METRICS[:-1]} for name in NAMES}
    assert table==result['table'] and totals==result['totals']
    ratios={a+'Vs'+b:{key:totals[a][key]/totals[b][key] for key in METRICS[:3]} for a,b in PAIRS}
    case_ratios=[dict(case=case,**{a+'Vs'+b:{key:by[case,a][key]/by[case,b][key]
        for key in METRICS[:3]} for a,b in PAIRS}) for case in cases()]
    gains={}
    for a,b in PAIRS:
        label=a+'Vs'+b
        rows=[dict(case=case,searchWallRatio=by[case,a]['searchWallNs']/by[case,b]['searchWallNs'],
            searchWallDeltaNs=by[case,a]['searchWallNs']-by[case,b]['searchWallNs'],
            wholeCpuDeltaSeconds=by[case,a]['wholeCpuSeconds']-by[case,b]['wholeCpuSeconds']) for case in cases()]
        gains[label]=dict(faster=sum(row['searchWallDeltaNs']<0 for row in rows),
            slower=sum(row['searchWallDeltaNs']>0 for row in rows), tied=sum(row['searchWallDeltaNs']==0 for row in rows),
            byWallRatio=sorted(rows,key=lambda row:row['searchWallRatio']),
            byWallDelta=sorted(rows,key=lambda row:row['searchWallDeltaNs']))
    memory={name:dict(sumLifetimePeakRssKiB=sum(by[case,name]['rssKiB'] for case in cases()),minRssKiB=min(by[case,name]['rssKiB'] for case in cases()),
        maxRssKiB=max(by[case,name]['rssKiB'] for case in cases()),
        meanRssKiB=sum(by[case,name]['rssKiB'] for case in cases())/54) for name in NAMES}
    oracle={row['id']:row for row in read(SPEC/'replay-oracle.json')['cases']}
    work=[dict(case=case,orderedPosts=len(oracle[case]['posts']),
        finalPostWorkThousands=oracle[case]['posts'][-1]['workThousands'] if oracle[case]['posts'] else None)
        for case in cases()]
    readiness_rows=[dict(case=case,**readiness_summary([by[case,'epoch3']])) for case in cases()]
    before,after=guest_ticks(base/'proc-stat-before'),guest_ticks(base/'proc-stat-after')
    deltas={cpu:[y-x for x,y in zip(before[cpu],after[cpu])] for cpu in before}
    assert all(len(before[cpu])==len(after[cpu]) and all(x>=0 for x in deltas[cpu]) for cpu in before)
    output=dict(schema='rook2-epoch-own-pgo-full54-audit-v1',complete=True,replayLives=270,
        originalCases=54,observationsPerCell=1,warmups=0,idleProcesses=5,orderedPosts=posts,
        orderedPostsByVariant=posts_by_variant,work=work,table=table,totals=totals,ratios=ratios,
        caseRatios=case_ratios,gainsLosses=gains,memory=memory,idle=result['idle'],readiness=readiness_rows,
        readinessSemantics=plan['readinessSemantics'],evidenceReuse=plan['evidenceReuse'],
        images=plan['images'],source=plan['source'],profileSha256=plan['profileSha256'],drift=plan['drift'],
        trainingAudit=record['trainingAudit'],housekeeping=housekeeping_audit(base/'housekeeping.json',275),
        preparationHousekeeping=housekeeping_audit(record_path.parent/'housekeeping-prepare.json',5),
        guestCpuTickDeltas=deltas,guestCpuTickFieldOrder='user nice system idle iowait irq softirq steal guest guest_nice',
        raw=str(base),rawSha256={name:sha(base/name) for name in ['plan.json','result.json',
            'proc-stat-before','proc-stat-after','housekeeping.json']},reconcilerSha256=sha(Path(__file__)),
        uncertainty='one observation per cell; descriptive complete sums, not medians, repeatability, qualification, promotion or matched KingWCR evidence')
    with (args.output or base/'reconciled.json').open('x') as stream:
        json.dump(output,stream,indent=2,allow_nan=False);stream.write('\n')
    print(json.dumps({key:output[key] for key in ['complete','replayLives','orderedPosts','totals','ratios']},indent=2))


if __name__=='__main__':
    main()
