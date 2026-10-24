#!/usr/bin/env python3
"""Reconcile existing native/tap/replay receipts; never start an engine."""
import argparse
import hashlib
import json
from pathlib import Path
import statistics


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read(p):
    return json.loads(p.read_text())


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory',type=Path)
    args=parser.parse_args();b=args.directory.resolve()
    manifest=read(b/'plan.json');result=read(b/'result.json')
    assert result['complete'] and len(result['runs'])==36
    for name,h in manifest['inputSha256'].items():assert sha(Path(name))==h,name
    mode=read(Path('/home/legolas/king-spec/conformance/profiling/replay-oracle.json'))['mode']
    native_count=posts=0
    for step,row in zip(manifest['schedule'],result['runs']):
        assert all(row[k]==v for k,v in step.items())
        d=Path(row['directory']);replay=read(d/'stdout');n=read(d/'native.json');tap=read(d/'wire/receipt.json')
        variant=manifest['variants'][row['variant']]
        assert replay['status']=='pass' and replay['selectedCases']==[row['case']]
        actual=replay['results'][0]
        assert actual['status']=='pass' and actual['complete'] and not actual['truncated']
        assert actual['discardedObservedBytes']==0 and actual['exit']==dict(code=0,signal=None)
        assert n['failure'] is None and n['native_exit_code']==0 and n['supervisor_signals']==[]
        assert n['engine_sha256_before']==n['engine_sha256_after']==variant['sha256']
        assert n['argv']==[variant['path'],*variant['args'],*mode]
        tasks=n['native_post_exec']['task_affinities']
        assert len(tasks)==variant['threads'] and tasks[str(n['native_pid'])]==[14]
        assert all(cpus==[6] for tid,cpus in tasks.items() if tid!=str(n['native_pid']))
        assert n['total_cpu_s']==row['wholeCpuSeconds'] and n['wall_ns']==row['wholeWallNs']
        assert n['maxrss_linux_kib']==row['rssKiB']
        assert tap['failure'] is None and tap['pending'] is None and len(tap['searches'])==1
        search=tap['searches'][0]
        assert search['wallNs']==row['searchWallNs']
        assert n['wall_ns']-search['wallNs']==row['nonSearchWallNs']
        for boundary in ['beforeWrite','afterData']:
            assert search[boundary]['available'] and search[boundary]['pid']==n['native_pid']
            assert search[boundary]['lastProcessor']==14
        for stream,item in tap['raw'].items():
            p=d/'wire'/f'{stream}.raw'
            assert sha(p)==item['sha256'] and p.stat().st_size==item['bytes']==item['observedBytes']
            assert item['discardedObservedBytes']==0
        assert (d/'wire/stdout.raw').read_bytes()==actual['stdout'].encode()
        assert (d/'wire/stderr.raw').read_bytes()==actual['stderr'].encode()
        assert (d/'wire/stdin.raw').read_bytes().splitlines().count(b'go')==1
        for name,h in row['sha256'].items():assert sha(d/name)==h
        for pid in [n['native_pid'],n['supervisor_pid']]:assert not Path(f'/proc/{pid}').exists()
        posts+=sum(bool(line.split()) and line.split()[0].lstrip('-').isdigit()
                   for line in actual['stdout'].splitlines())
        native_count+=1
    for row in result['idle']:
        n=read(b/('idle-'+row['variant'])/'native.json')
        assert sha(b/('idle-'+row['variant'])/'native.json')==row['nativeReceiptSha256']
        assert n['failure'] is None and n['total_cpu_s']==row['wholeCpuSeconds']
        assert not Path(f'/proc/{n["native_pid"]}').exists()
        native_count+=1
    for summary in result['summaries']:
        selected=[x for x in result['runs'] if not x['warmup'] and
                  (x['case'],x['variant'])==(summary['case'],summary['variant'])]
        assert len(selected)==3
        for metric in ['searchWallNs','wholeCpuSeconds','wholeWallNs','nonSearchWallNs','rssKiB']:
            samples=[x[metric] for x in selected]
            assert summary[metric]==dict(samples=samples,median=statistics.median(samples),
                                          min=min(samples),max=max(samples))
    by={(x['case'],x['variant']):x for x in result['summaries']}
    comparisons=[]
    for case in ['profile-35','profile-08','profile-04']:
        old,one,two=[by[case,v] for v in ['control','budget1','budget2']]
        comparisons.append(dict(case=case,
            serialRefactorWallRatio=one['searchWallNs']['median']/old['searchWallNs']['median'],
            workerWallRatio=two['searchWallNs']['median']/one['searchWallNs']['median'],
            workerCpuRatio=two['wholeCpuSeconds']['median']/one['wholeCpuSeconds']['median']))
    summed={v:dict(searchWallNs=sum(by[c,v]['searchWallNs']['median'] for c in ['profile-35','profile-08','profile-04']),
                   wholeCpuSeconds=sum(by[c,v]['wholeCpuSeconds']['median'] for c in ['profile-35','profile-08','profile-04']))
            for v in ['control','budget1','budget2']}
    report=dict(complete=True,rawDirectory=str(b),nativeProcesses=native_count,
        strictSearchComparisons=36,measuredSearchComparisons=27,orderedPostsIncludingWarmups=posts,
        comparisons=comparisons,summedMedians=summed,summaries=result['summaries'],idle=result['idle'],
        rawSha256={n:sha(b/n) for n in ['plan.json','result.json','proc-stat-before','proc-stat-after']},
        limits='Three generic/no-PGO original cases; no broad conformance, production adoption or KingWCR comparison')
    (b/'reconciled.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(complete=True,nativeProcesses=native_count,posts=posts,
                         comparisons=comparisons,summedMedians=summed),indent=2))


if __name__=='__main__':
    main()
