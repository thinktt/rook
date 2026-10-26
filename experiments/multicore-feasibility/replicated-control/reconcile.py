#!/usr/bin/env python3
"""Saved-raw matched-driver outcome, identity, placement and wait4 cost audit."""
import argparse
import json
from pathlib import Path
import sys

sys.dont_write_bytecode=True
from common import (CASES,NAMES,METRICS,HELPERS,LIMITS,baseline,code_paths,preparation,
    prepared_run,read,write,sha,variants,schedule,saved_lifetime,dist)

PAIRS=[('newreplica3','newpacket3'),('newreplica3','preservedpacket3'),
    ('newreplica3','newinline1'),('newreplica3','preservedinline1'),
    ('newpacket3','preservedpacket3'),('newinline1','preservedinline1')]


def housekeeping_audit(path):
    value=read(path)
    assert value['helperCpus']==sorted(HELPERS) and value['failure'] is None
    assert len(value['applies'])==60 and value['restored'] is not None
    originals={(row['pid'],row['tid'],row['starttime']):row['affinity'] for row in value['originals']}
    assert len(originals)==len(value['originals'])
    leaders={(row['pid'],row['starttime']):row['affinity'] for row in value['leaders']}
    assert len(leaders)==len(value['leaders']);seen=set()
    for event in value['applies']:
        assert event['cpus']==event['selfAffinity']==sorted(HELPERS)
        for row in event['selectedTasks']:
            key=(row['pid'],row['tid'],row['starttime'])
            assert row['after']==sorted(HELPERS) and row['before']==(sorted(HELPERS) if key in seen else originals[key])
            seen.add(key)
    assert seen==set(originals)
    for row in value['restored']:
        key=(row['pid'],row['tid'],row['starttime'])
        if key in originals:assert not row['inheritedNewThread'] and row['restored']==originals[key]
        else:
            masks=[mask for (pid,_),mask in leaders.items() if pid==row['pid']]
            assert len(masks)==1 and row['inheritedNewThread'] and row['restored']==masks[0]
    assert value['postRestoreSelfAffinity']==sorted(HELPERS)
    return dict(applyCount=60,selectedOriginalTasks=len(originals),restoredTasks=len(value['restored']),sha256=sha(path))


def guest_ticks(path):
    wanted={'cpu4','cpu5','cpu6','cpu7','cpu14','cpu15'}
    values={parts[0]:[int(value) for value in parts[1:]] for line in path.read_text().splitlines()
        if (parts:=line.split()) and parts[0] in wanted}
    assert set(values)==wanted
    return values


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('raw',type=Path);parser.add_argument('--output',type=Path)
    args=parser.parse_args();base=args.raw.resolve()
    plan,result=read(base/'plan.json'),read(base/'result.json')
    assert plan['schema']=='rook2-replicated-control-timing-v1' and result['complete'] and result['failure'] is None
    assert plan['depth']==8 and plan['audit'] is False and plan['seed']==0 and plan['limits']==LIMITS
    assert plan['schedule']==schedule() and len(result['runs'])==60
    assert plan['helperAffinity']==sorted(HELPERS) and plan['coordinatorCpu']==14
    assert plan['peerCpus']==[6,4] and plan['unassignedOwnedSiblings']==[5,7,15]
    hashes=plan['inputSha256'];assert all(str(path) in hashes for path in code_paths())
    for path,digest in hashes.items():assert sha(path)==digest,path
    prepared_path,record_path=Path(plan['sourcePreparation']),Path(plan['preparedRun'])
    prepared=preparation(prepared_path);record=prepared_run(record_path,prepared_path,prepared)
    assert hashes[str(prepared_path)]==sha(prepared_path) and hashes[str(record_path)]==sha(record_path)
    assert plan['inputs']==record['inputs'] and plan['protectedArtifacts']==baseline()
    modes=variants(Path(record['images']['preserved']['path']),Path(record['images']['new']['path']))
    assert plan['variants']==modes and list(modes)==NAMES
    assert plan['pipelineStartMonotonicNs']==record['pipelineStartMonotonicNs']
    assert plan['pipelineDeadlineMonotonicNs']==record['pipelineDeadlineMonotonicNs']==record['pipelineStartMonotonicNs']+3600*10**9
    start,end=result['streamStartMonotonicNs'],result['streamEndMonotonicNs']
    assert plan['streamStartMonotonicNs']==start and record['preparedMonotonicNs']<=start<end<plan['pipelineDeadlineMonotonicNs']
    assert end-start<=1800*10**9
    outcomes,pids,previous={},set(),start
    for index,(step,row) in enumerate(zip(schedule(),result['runs'])):
        value=modes[step['variant']];directory=base/f'{index:02d}-{step["case"]}-{step["variant"]}-r{step["repeat"]}'
        assert all(row[key]==item for key,item in step.items()) and row['directory']==str(directory)
        native,report=saved_lifetime(directory,step,Path(value['path']),value,hashes,Path(record['inputs'][step['case']]['path']),8)
        assert row['report']==report and row['nativePid']==native['native_pid']
        expected=dict(searchWallNs=report['searchWallNs'],joinNs=report['joinNs'],wholeCpuSeconds=native['total_cpu_s'],
            wholeWallNs=native['wall_ns'],nonSearchWallNs=native['wall_ns']-report['searchWallNs'],rssKiB=native['maxrss_linux_kib'])
        assert all(row[key]==item for key,item in expected.items())
        assert previous<=row['controllerStartMonotonicNs']<=native['start_monotonic_ns']
        assert native['reaped_monotonic_ns']<=row['controllerEndMonotonicNs']<=end
        previous=row['controllerEndMonotonicNs']
        assert native['native_pid'] not in pids;pids.add(native['native_pid'])
        for file,digest in row['sha256'].items():assert sha(directory/file)==digest,file
        canonical=outcomes.setdefault(step['case'],report['outcome'])
        assert report['outcome']==canonical,'whole structured outcome disagreement'
    assert outcomes==result['outcomes'] and len(outcomes)==3 and len(pids)==60
    summaries=[dict(case=case,variant=name,**{key:dist([row[key] for row in result['runs']
        if row['case']==case and row['variant']==name and not row['warmup']]) for key in METRICS}) for case in CASES for name in NAMES]
    assert summaries==result['summaries'];by={(row['case'],row['variant']):row for row in summaries}
    sums={name:{key:sum(by[case,name][key]['median'] for case in CASES) for key in METRICS} for name in NAMES}
    comparisons=[dict(case=case,**{a+'Vs'+b:{key:by[case,a][key]['median']/by[case,b][key]['median']
        for key in METRICS[:3]} for a,b in PAIRS}) for case in CASES]
    before,after=guest_ticks(base/'proc-stat-before'),guest_ticks(base/'proc-stat-after')
    deltas={cpu:[b-a for a,b in zip(before[cpu],after[cpu])] for cpu in before}
    assert all(len(before[cpu])==len(after[cpu]) and all(value>=0 for value in deltas[cpu]) for cpu in before)
    output=dict(schema='rook2-replicated-control-timing-audit-v1',complete=True,timingLives=60,measuredLives=45,warmups=15,
        depth=8,auditLives=3,auditDepth=2,auditTraceCap=32768,originalProtocolReplay=False,
        outcomes=outcomes,outcomeEquality='whole structured outcome equal in all20 timing lives per case, including warmups',
        summaries=summaries,summedMedians=sums,comparisons=comparisons,
        aggregateRatios={a+'Vs'+b:{key:sums[a][key]/sums[b][key] for key in METRICS[:3]} for a,b in PAIRS},
        audits=record['audits'],images=record['images'],housekeeping=housekeeping_audit(base/'housekeeping.json'),
        guestCpuTickDeltas=deltas,pipelineStartMonotonicNs=plan['pipelineStartMonotonicNs'],
        pipelineDeadlineMonotonicNs=plan['pipelineDeadlineMonotonicNs'],streamStartMonotonicNs=start,streamEndMonotonicNs=end,
        raw=str(base),rawSha256={name:sha(base/name) for name in ['plan.json','result.json','housekeeping.json','proc-stat-before','proc-stat-after']},
        reconcilerSha256=sha(Path(__file__)),
        scope='matched unwind fixed-completion NoHost depth8 actual search, original-sized independent TTs; search+whole-native all-thread CPU/RSS boundaries retained; depth2 independent serial/replica audit is finite assurance, not production replay/Host qualification or isolated kernel/cache timing')
    with (args.output or base/'reconciled.json').open('x') as stream:
        json.dump(output,stream,indent=2,allow_nan=False);stream.write('\n')
    print(json.dumps({key:output[key] for key in ['complete','timingLives','summedMedians','aggregateRatios']}))


if __name__=='__main__':main()
