#!/usr/bin/env python3
"""Stream saved ID/time records and qualify both original raw replays.

Typed identity, exact key equality, call-domain completeness and numerical payload
correctness are source/control assurances. This auditor never reruns kernels.
"""
import argparse
from array import array
import json
from pathlib import Path
import re
import resource
import struct
import sys
import time
sys.dont_write_bytecode=True
from common import (HERE,ROOT,CRATE,HELPERS,SPEC,BUILD_ADAPTER,OPTIONS,TESTS,REPORT,COHORT_REPORT,
    REPORT_ENV,COUNTS,SERIALIZATION,cohort_env,step,count_audit,admit_build,audit,audit_placement,
    baseline,image_layout,preparation,read,sha)
U64=2**64-1;JMAX=262144;PMAX=16384;CAP=536870912
HEADER=struct.Struct('<8sIIIQIIII');FOOTER=struct.Struct('<11Q4BQII')
HISTORY=struct.Struct('<I6QBB5Q2Q5Q')
MAGICS=dict(capture=b'R2FCOH01',expand=b'R2FCPO01',observe=b'R2FCLE01')
COST_KINDS=['audit-prefix-lookup','prospective7-lookup','prospective6-copy-publication','audit-cohort-verification','audit-payload-comparison']
LABELS=dict(clockBasis='this-replay-root-bind-after-cold-load',demandSite='nonempty-four-plane-filter-before-typed-key',
    releaseSite='after-this-replay-parent-copy-and-descriptor-publication',mapInterval='native-coherent-build-only-after-key-lookup',
    fullInterval='post-material-post-key-lookup-through-native-join-before-audit-retained-suffix',
    selectedIds='cold-audit-knowledge-not-runtime-free-lookup',actualReady='unknown-no-producer',
    ceiling='disjoint-first-new7-map-plus-full-prefix-observed-path-costs-not-wall-saving')


def integer(value,maximum=U64):
    assert type(value) is int and 0<=value<=maximum,value
    return value


def take(stream,size):
    value=stream.read(size);assert len(value)==size,'short binary record';return value


def file_size(mode,p,j,m,c):
    return 1768+125*p+dict(capture=6,expand=14,observe=30)[mode]*j+(0 if mode=='capture' else (269*m+257*c if mode=='expand' else 150*m+191*c))


def header(stream,mode,path):
    raw=take(stream,1660);magic,version,pc,jc,bc,p,j,m,c=HEADER.unpack(raw[:HEADER.size])
    assert (magic,version,pc,jc,bc)==(MAGICS[mode],1,PMAX,JMAX,CAP)
    assert (p,j)==(COUNTS['E6'],COUNTS['S6']) and 0<=m<=j and 0<=c<=j
    assert (m==c==0) if mode=='capture' else (m>0 and c>0)
    assert path.stat().st_size==file_size(mode,p,j,m,c)<=SERIALIZATION[dict(capture='captureMaxBytes',expand='poolMaxBytes',observe='ledgerMaxBytes')[mode]]
    return dict(parents=p,jobs=j,maps=m,chains=c,rootEpoch=raw[44:])


def footer(raw):
    values=FOOTER.unpack(raw);bounds=list(values[:4]);counts=dict(zip(COUNTS,values[4:8]))
    n,r,mask=values[8:11];last,stop,selected,point=values[11:15];selected_n,pubs,flags=values[15:]
    assert 0<=bounds[0]<=bounds[1]<=bounds[2]<=bounds[3]<U64
    assert counts==COUNTS and (n,r)==(3746843,10506351) and mask==510
    assert last==stop==selected==8 and selected_n==2974350 and point in [0,1,2] and pubs==13 and flags==0
    return dict(boundariesNs=bounds,**counts,N=n,R=r,completedIterationsMask=mask,lastIterationDepth=last,
        stopDepth=stop,selectedDepth=selected,stopPoint=['root','iteration','poll'][point],selectedSearchUnits=selected_n,publications=pubs,flags=flags)


def cohort_summary(path,mode):
    assert path.is_file() and not path.is_symlink() and 0<path.stat().st_size<=65536
    value=read(path)
    assert value['schema']=='rook2-frontier-cohort-v1' and value['mode']==mode and value['error'] is None
    assert value['pairComplete'] is True and value['cohortVerified'] is (mode=='observe')
    assert value['caps']==dict(parents=PMAX,jobs=JMAX,observerBytes=CAP)
    assert (value['parents'],value['jobs'])==(COUNTS['E6'],COUNTS['S6'])
    for key,expected in {**COUNTS,'N':3746843,'R':10506351,'completedIterationsMask':510,'publications':13,
        'sampleStride':512,'fixedReserveBytes':524288,'captureMaxBytes':3622632,'poolMaxBytes':143607528,'ledgerMaxBytes':99305192,
        'costKinds':COST_KINDS,**LABELS}.items():assert value[key]==expected,key
    memory=integer(value['accountedMemoryBytes']);disk=integer(value['retainedAndPlannedFileBytes'])
    assert memory+disk==integer(value['accountedBytes'])<=integer(value['peakAccountedBytes'])<=CAP
    layout=value['memoryLayout'];assert set(layout)=={'stateBytes','positionBytes','jobBytes','mapRowBytes','chainRowBytes','indexSlotsPerComponent'}
    assert layout['indexSlotsPerComponent']==524288
    for key in layout:assert integer(layout[key])>0
    cohorts=2 if mode=='observe' else 1
    minimum=layout['stateBytes']+524288+cohorts*(PMAX*layout['positionBytes']+JMAX*layout['jobBytes'])
    if mode!='capture':minimum+=JMAX*(layout['mapRowBytes']+layout['chainRowBytes'])+2*524288*4
    assert memory>=minimum
    assert len(value['costs'])==5
    for cost,kind in zip(value['costs'],range(5)):
        assert set(cost)=={'kind','queries','misses','hits','comparisons','keyBytes','copyBytes','samples','sampledNs'}
        assert cost['kind']==kind
        for key in cost:integer(cost[key])
        assert cost['samples']==cost['queries']//512
        if kind<2:assert cost['hits']+cost['misses']==cost['queries']
    for key in ['payloadAuditComparisons','payloadAuditBytes']:integer(value[key])
    assert value['payloadAuditComparisons']==value['costs'][4]['comparisons']
    assert isinstance(value['costLimits'],str) and 'TLS borrow entry/exit excluded' in value['costLimits']
    if mode=='capture':assert value['map'] is value['chain'] is None
    else:
        for component in ['map','chain']:
            for number in value[component].values():integer(number,2**128-1)
    return value


def read_binary_footer(path,mode,summary,scale=None):
    assert path.is_file() and not path.is_symlink()
    with path.open('rb',buffering=65536) as stream:
        head=header(stream,mode,path);stream.seek(-108,2);raw=take(stream,108);assert not stream.read(1)
    value=footer(raw)
    for key in ['boundariesNs',*COUNTS,'N','R','completedIterationsMask','publications']:assert summary[key]==value[key],key
    if scale is not None:
        bounds=value['boundariesNs'];pair=scale['boundaries'];origin=bounds[0]
        assert [number-origin for number in bounds]==[pair[0]['startNs'],pair[0]['endNs'],pair[1]['startNs'],pair[1]['endNs']]
        for key in ['N','R','completedIterationsMask','lastIterationDepth','stopDepth','selectedDepth','stopPoint','selectedSearchUnits']:
            assert value[key]==scale['outcome'][key],key
    p,j,m,c=[head[key] for key in ['parents','jobs','maps','chains']]
    disk=file_size('capture',p,j,0,0)+65536
    if mode!='capture':disk+=file_size('expand',p,j,m,c)+65536
    if mode=='observe':disk+=file_size('observe',p,j,m,c)+65536
    assert summary['retainedAndPlannedFileBytes']==disk
    return head,value


def qualify_search(root,mode,prepared,plan):
    image=root/'rook2-candidate';directory=root/mode;row=read(directory/'result.json')
    assert plan['schema']=='rook2-frontier-cohort-observation-v1' and plan['mode']==mode and plan['step']==step(mode)
    assert plan['case']=='profile-35' and plan['options']==OPTIONS and plan['budget']==3
    assert plan['source']==prepared['candidateSource'] and plan['engine']==image_layout(image)
    for name,digest in plan['inputSha256'].items():assert sha(name)==digest,name
    native,count=audit.lifetime(directory,row,step(mode),image,3,OPTIONS,plan['inputSha256'])
    assert count==row['orderedPosts']==13 and native['wall_ns']<=180*10**9
    assert row['placement']==audit_placement(directory,native,plan['inputSha256'])
    assert row['replayRunnerExit']==0 and not Path(f'/proc/{row["replayRunnerPid"]}').exists()
    variables=cohort_env(root,mode)|{REPORT_ENV:str(directory/REPORT)}
    assert read(directory/'frontier-env.json')==dict(schema='rook2-frontier-cohort-environment-v1',variables=variables)
    for name in [REPORT,COHORT_REPORT]:assert row['reports'][name]==dict(path=str(directory/name),sha256=sha(directory/name))
    oracle=next(case for case in read(SPEC/'replay-oracle.json')['cases'] if case['id']=='profile-35')
    summary=count_audit.report_audit(read(directory/REPORT),oracle,row['searchWallNs'])
    assert summary['complete'] and not summary['censored'] and summary['counts']==COUNTS
    assert (summary['outcome']['N'],summary['outcome']['R'])==(3746843,10506351)
    return native,row,summary


def histories(stream,n,earliest,component,bounds,intervals):
    result=dict(unique=n,canonicalProduced=0,demanded7=0,new7=0,repeat7=0,no7=0,releaseBeforeFirst7=0,
        measuredFirstNew7=0,calls7=0,availableLeadNs=0,firstNewKernelNs=0)
    buckets=[0]*5;extras_count=[0]*5;extra_intervals=[0]*2
    for expected in range(n):
        values=HISTORY.unpack(take(stream,150));identity=values[0]
        release=values[1:3];production=values[3:5];first7=values[5:7]
        phase,new=values[7:9];calls=values[9:14];kernel=values[14:16];extras=values[16:21]
        assert identity==expected and release==(earliest[0][expected],earliest[1][expected])
        assert release[0]!=U64 and bounds[0]<=release[0]<=bounds[1] and release[1]>0
        for stamp in [production,first7]:
            assert (stamp[0]==U64)==(stamp[1]==U64)
            if stamp[0]!=U64:assert 0<=stamp[0]<=bounds[3] and stamp[1]>0
        produced=production[0]!=U64;demanded=first7[0]!=U64
        assert produced==(sum(calls)>0) and demanded==(calls[4]>0)
        assert new in [0,1] and bool(new)==(demanded and sum(calls[:4])==0)
        if produced:assert 0<=phase<=7
        else:assert phase==0
        if demanded:
            assert bounds[2]<=first7[0]<=bounds[3]
            if new:assert phase==7 and first7<production
            else:assert production<first7 and phase!=7
        if produced and phase==7:assert new
        if new:
            assert bounds[2]<=first7[0]<=kernel[0]<=kernel[1]==production[0]<=bounds[3]
            intervals.append((kernel[0]<<64)|kernel[1])
            result['measuredFirstNew7']+=1;result['firstNewKernelNs']+=kernel[1]-kernel[0]
        else:assert kernel==(U64,U64) and extras==(U64,)*5
        if component=='map':assert extras==(U64,)*5
        else:
            value=take(stream,40);has_value=take(stream,1)[0]
            assert has_value in [0,1] and bool(has_value)==produced
            for index,number in enumerate(extras):
                if number!=U64:
                    assert new and kernel[0]<=number<=kernel[1];extras_count[index]+=1
            for index,(left,right) in enumerate([(0,1),(3,4)]):
                assert (extras[left]==U64)==(extras[right]==U64)
                if extras[left]!=U64:
                    assert extras[left]<=extras[right];extra_intervals[index]+=extras[right]-extras[left]
            if extras[0]!=U64 and extras[2]!=U64:assert extras[1]<=extras[2]
        result['canonicalProduced']+=produced;result['demanded7']+=demanded;result['new7']+=new
        result['no7']+=not demanded;result['repeat7']+=max(calls[4]-1,0);result['calls7']+=calls[4]
        if demanded and release<first7:
            result['releaseBeforeFirst7']+=1;result['availableLeadNs']+=first7[0]-release[0]
        for index,number in enumerate(calls):buckets[index]+=number
    return result,dict(callsByPhase=buckets,optionalMarkCounts=extras_count,
        dispatchIntervalsNs=extra_intervals[0],inventoryIntervalsNs=extra_intervals[1])



def audit_storage(root):
    # The native observer has exited. Charge this auditor's actual allocator
    # high-water RSS, retained local raw files and planned bounded outputs to
    # the SAME total cap; native RAM is not simultaneously allocated here.
    excluded={'rook2-candidate'}
    retained=sum(path.stat().st_size for path in root.rglob('*') if path.is_file()
        and not {'candidate-build','test-target'}.intersection(path.relative_to(root).parts)
        and path.name not in excluded)
    planned=2*SERIALIZATION['auditJsonMaxBytes']+SERIALIZATION['auditFinalMetadataReserveBytes']
    peak=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024
    working=SERIALIZATION['auditWorkingStorageMaxBytes']
    assert peak<=working and retained+planned+working<=CAP
    assert peak+retained+planned<=CAP
    return dict(phase='native-exited-streaming-audit',peakSelfRssBytes=peak,retainedLocalRawBytes=retained,
        plannedBoundedOutputBytes=planned,declaredWorkingStorageMaxBytes=working,
        actualCombinedBytes=peak+retained+planned,declaredCombinedMaxBytes=working+retained+planned,
        capBytes=CAP,excluded='engine binary and build/test targets; native engine RAM no longer allocated')

def stream_cohort(root,summaries,scales):
    paths=[root/'capture.bin',root/'pool.bin',root/'ledger.bin'];modes=['capture','expand','observe']
    heads=[];feet=[]
    for path,mode in zip(paths,modes):
        h,f=read_binary_footer(path,mode,summaries[mode],scales.get(mode));heads.append(h);feet.append(f)
    cap,pool,ledger=heads
    assert cap['rootEpoch']==pool['rootEpoch']==ledger['rootEpoch']
    assert {key:pool[key] for key in ['parents','jobs','maps','chains']}=={key:ledger[key] for key in ['parents','jobs','maps','chains']}
    assert feet[0]==feet[1]
    p,j,m,c=[pool[key] for key in ['parents','jobs','maps','chains']]
    earliest=[(array('Q',[U64])*n,array('Q',[U64])*n) for n in [m,c]]
    assert earliest[0][0].itemsize==8
    intervals=[];last_release=(-1,-1);created=0
    with paths[0].open('rb',buffering=65536) as a,paths[1].open('rb',buffering=65536) as b,paths[2].open('rb',buffering=65536) as d:
        for stream in [a,b,d]:stream.seek(1660)
        for _ in range(p):assert take(a,125)==take(b,125)==take(d,125)
        for _ in range(j):
            captured=take(a,6);expanded=take(b,14);observed=take(d,30)
            assert captured==expanded[:6] and expanded==observed[:14]
            parent,movement,map_id,chain_id,ns,ordinal=struct.unpack('<IHIIQQ',observed)
            assert parent<=created and parent<p
            if parent==created:created+=1
            assert map_id<m and chain_id<c
            release=(ns,ordinal);assert feet[2]['boundariesNs'][0]<=ns<=feet[2]['boundariesNs'][1]
            assert last_release<release and ordinal>last_release[1];last_release=release
            for values,identity in zip(earliest,[map_id,chain_id]):
                if values[0][identity]==U64:values[0][identity]=ns;values[1][identity]=ordinal
        assert created==p
        # Pool keys and expected outputs remain opaque. Native exact-key controls
        # establish dedup/equality; every serialized ID is independently used.
        for n,values in zip([m,c],earliest):assert all(value!=U64 for value in values[0]) and len(values[0])==n
        b.seek(269*m+257*c,1)
        assert footer(take(a,108))==feet[0] and not a.read(1)
        assert footer(take(b,108))==feet[1] and not b.read(1)
        result={};metadata={}
        for component,n,values in zip(['map','chain'],[m,c],earliest):
            result[component],metadata[component]=histories(d,n,values,component,feet[2]['boundariesNs'],intervals)
            assert result[component]==summaries['observe'][component],component
        assert footer(take(d,108))==feet[2] and not d.read(1)
    assert len(intervals)<=2*JMAX
    intervals.sort();previous=0;ceiling=0
    for value in intervals:
        start,end=value>>64,value&U64;assert previous<=start<=end;previous=end;ceiling+=end-start
    bounds=feet[2]['boundariesNs'];assert ceiling==sum(value['firstNewKernelNs'] for value in result.values())<=bounds[3]-bounds[2]
    costs=summaries['observe']['costs']
    assert costs[1]['queries']==COUNTS['M7']+COUNTS['F7']
    assert costs[1]['hits']==sum(value['calls7'] for value in result.values())
    assert costs[0]['hits']==sum(sum(value['callsByPhase'][:4]) for value in metadata.values())
    for mode in ['capture','observe']:
        costs_mode=summaries[mode]['costs'];layout=summaries[mode]['memoryLayout']
        assert costs_mode[2]['queries']==costs_mode[3]['queries']==j
        assert costs_mode[2]['copyBytes']==j*layout['jobBytes']+p*layout['positionBytes']
        assert costs_mode[3]['comparisons']==j and costs_mode[3]['keyBytes']==j*(layout['jobBytes']+layout['positionBytes'])
    for component,n in [('map',m),('chain',c)]:
        assert summaries['expand'][component]==dict(unique=n,canonicalProduced=0,demanded7=0,new7=0,repeat7=0,
            no7=n,releaseBeforeFirst7=0,measuredFirstNew7=0,calls7=0,availableLeadNs=0,firstNewKernelNs=0)
    return dict(**result,metadata=metadata,generousCeilingNs=ceiling,iteration7SpanNs=bounds[3]-bounds[2],
        intervalCount=len(intervals),globallyDisjoint=True,actualReady='unknown-no-producer',
        sourceAssurance='Exact typed-key equality, complete domains, canonical payloads and no-kernel-change rely on frozen source and six new plus six reused controls; this audit streams IDs, times and counts without typed-key or kernel re-execution.',
        auditorStorage='At most4*262144 u64 release cells plus524288 packed interval integers;128MiB declared working limit including sort/runtime, actual self RSS plus retained/planned raw files checked under the SAME512MiB cap. No JSON key catalogue.',
        ceilingScope='Native map plus post-material post-lookup FULL prefix through join, including pawn/local work; generous all-ready observed-path ceiling, not readiness, hardware saving or speed.',
        rawFiles={str(path):dict(sha256=sha(path),bytes=path.stat().st_size) for path in paths})


def audit_run(root,during=False):
    root=Path(root).resolve();state=read(root/'pipeline.json');prepared_path=Path(state['preparation']);prepared=preparation(prepared_path)
    assert state['schema']=='rook2-frontier-cohort-pipeline-v1' and state['sourcePreparation']==prepared
    assert state['preparationSha256']==sha(prepared_path) and state['protectedArtifacts']==baseline()
    start,deadline=state['pipelineStartMonotonicNs'],state['pipelineDeadlineMonotonicNs'];assert deadline==start+1800*10**9
    names=['unit-tests','candidate-build','capture','expand','observe']+([] if during else ['audit'])
    assert [row['stage'] for row in state['stages']]==names
    assert (state['active']=='audit' and not state['complete']) if during else (state['complete'] and state['active'] is None)
    assert state['failure'] is None
    expected=[['/usr/bin/cargo','test','--offline','--locked','--lib','--target','x86_64-unknown-linux-gnu','--jobs','4',
        '--target-dir',str(root/'test-target'),'--manifest-path',str(CRATE/'Cargo.toml'),'frontier_cohort::tests','--','--test-threads=1'],
        ['/usr/bin/python3',str(BUILD_ADAPTER),'--crate',str(CRATE),'--mode','generic','--bin','rook2','--jobs','4','--output',str(root/'candidate-build')],
        ['/usr/bin/python3',str(HERE/'pipeline.py'),'--preparation',str(prepared_path),'--output',str(root),'--search-mode','capture'],
        [str(root/'rook2-candidate')],
        ['/usr/bin/python3',str(HERE/'pipeline.py'),'--preparation',str(prepared_path),'--output',str(root),'--search-mode','observe'],
        ['/usr/bin/python3',str(HERE/'reconcile.py'),str(root),'--during-pipeline']]
    previous=start
    for row,argv,cap in zip(state['stages'],expected,[300,300,200,300,200,300]):
        assert row['argv']==argv and row['cwd']==str(ROOT) and row['exit']==0
        assert previous<=row['startedMonotonicNs']<row['endedMonotonicNs']<row['deadlineMonotonicNs']==min(deadline,row['startedMonotonicNs']+cap*10**9)
        previous=row['endedMonotonicNs'];assert not Path(f'/proc/{row["pid"]}').exists()
        assert row['extraEnvironment']==(cohort_env(root,'expand') if row['stage']=='expand' else {})
        for suffix in ['stdout','stderr']:assert sha(root/(row['stage']+'.'+suffix))==row[suffix+'Sha256']
    text=(root/'unit-tests.stdout').read_text();passed=re.findall(r'^test (\S+) \.\.\. ok$',text,re.M)
    assert sorted(passed)==TESTS and state['stages'][0]['passedTests']==passed
    assert re.findall(r'^test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored;',text,re.M)==[('6','0','0')]
    assert (root/'expand.stdout').stat().st_size==0 and (root/'expand.stderr').stat().st_size==0
    image=root/'rook2-candidate';admit_build(root/'candidate-build',image,CRATE,prepared['candidateSource'])
    summaries={mode:cohort_summary(root/mode/COHORT_REPORT,mode) for mode in ['capture','expand','observe']}
    searches={};scales={}
    for mode,index in [('capture',2),('observe',4)]:
        plan=read(root/(mode+'-plan.json'))
        assert plan['pipelineStartMonotonicNs']==start and plan['pipelineDeadlineMonotonicNs']==deadline
        assert plan['sourcePreparation']==str(prepared_path) and plan['preparationSha256']==sha(prepared_path)
        assert plan['protectedArtifacts']==baseline()
        native,row,scale=qualify_search(root,mode,prepared,plan);scales[mode]=scale
        assert summaries[mode]['boundariesNs'][3]<=row['searchWallNs']
        stage=state['stages'][index]
        assert stage['startedMonotonicNs']<=row['controllerStartMonotonicNs']<row['controllerEndMonotonicNs']<=stage['endedMonotonicNs']
        searches[mode]=dict(nativePid=native['native_pid'],supervisorPid=native['supervisor_pid'],
            replayRunnerPid=row['replayRunnerPid'],observedTaskAffinities=native['native_post_exec']['task_affinities'],
            orderedPosts=13,wholeCpuSeconds=row['wholeCpuSeconds'],wholeWallNs=row['wholeWallNs'],rssKiB=row['rssKiB'],
            searchWallNs=row['searchWallNs'],counter=scale,cohortSummary=summaries[mode])
    for role in ['nativePid','supervisorPid','replayRunnerPid']:assert searches['capture'][role]!=searches['observe'][role]
    assert scales['capture']['outcome']==scales['observe']['outcome']
    audit_storage(root)
    cohort=stream_cohort(root,summaries,scales)
    if not during:
        house=read(root/'housekeeping.json')
        assert house['failure'] is None and house['helperCpus']==house['postRestoreSelfAffinity']==sorted(HELPERS)
        assert len(house['applies'])==6 and house['restored'] is not None
        assert all(event['cpus']==event['selfAffinity']==sorted(HELPERS) for event in house['applies'])
        assert state['endedMonotonicNs']<deadline
    mutable={'pipeline.json','audit.stdout','audit.stderr','housekeeping.json'} if during else set()
    pins={str(path):sha(path) for path in root.rglob('*') if path.is_file() and path.name not in mutable and 'test-target' not in path.parts and 'candidate-build' not in path.parts}
    assert time.monotonic_ns()<deadline
    result=dict(schema='rook2-frontier-cohort-audit-v1',complete=True,censored=False,raw=str(root),duringPipeline=during,
        focusedPassed=6,reusedAggregateControls=6,replayLives=2,terminalNativeReceipts=2,orderedPostsPerReplay=13,
        counts=COUNTS,searches=searches,cohort=cohort,coldExpansion=summaries['expand'],
        source=prepared['candidateSource'],image=image_layout(image),protectedArtifacts=state['protectedArtifacts'],
        stageExits={item['stage']:item['exit'] for item in state['stages']},pipelineStartMonotonicNs=start,pipelineDeadlineMonotonicNs=deadline,
        terminalAuditMonotonicNs=time.monotonic_ns(),rawSha256=pins,auditorStorage=audit_storage(root),
        scope='Full original35 cohort capture, cold expansion and same-source observation; no producer/consumer, service, readiness, speed or qualification claim')
    assert len(json.dumps(result,indent=2,allow_nan=False).encode())+1<=SERIALIZATION['auditJsonMaxBytes']
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('root',type=Path);parser.add_argument('--during-pipeline',action='store_true')
    args=parser.parse_args();root=args.root.resolve();output=root/('audit-before-restore.json' if args.during_pipeline else 'reconciled.json')
    assert not output.exists()
    try:
        value=audit_run(root,args.during_pipeline)
        with output.open('x') as stream:json.dump(value,stream,indent=2,allow_nan=False);stream.write('\n')
    except BaseException as error:
        with (root/'audit-failure.json').open('x') as stream:json.dump(dict(complete=False,failure=repr(error)),stream);stream.write('\n')
        raise
    print(json.dumps(dict(complete=value['complete'],counts=value['counts'],cohort=value['cohort']),indent=2))

if __name__=='__main__':main()
