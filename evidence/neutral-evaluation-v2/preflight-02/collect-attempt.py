#!/usr/bin/env python3
"""Frozen development schedule; external expected-data comparison follows timing."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
SHA = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def save(path, data):
    with path.open('x') as f:
        json.dump(data, f, indent=2, allow_nan=False)
        f.write('\n')

def cpu_snapshot():
    return {s.split()[0]: [int(v) for v in s.split()[1:]]
            for s in Path('/proc/stat').read_text().splitlines()
            if s.startswith(('cpu14 ', 'cpu15 '))}

def strings(moves):
    return [m['move'] for m in moves]

def work(w):
    assert w['searchCounterDelta'] == w['chargedSearchUnits']
    return dict(nodes=w['chargedSearchUnits'], relationQueries=w['chargedRelationQueries'])

def expected_projection(e):
    iterations = []
    for i in e['iterations']:
        steps = []
        for s in i['steps']:
            steps.append(dict(move=s['move']['move'],
                window=[s['window']['lower'], s['window']['upper']], score=s['score'],
                bestScore=s['bestScore'], secondScore=s['secondScore'],
                childPv=strings(s['childPrincipalVariation']),
                pv=strings(s['principalVariation']), **work(s['work'])))
        iterations.append(dict(depth=i['depth'], candidates=strings(i['candidates']),
            steps=steps, score=i['score'], pv=strings(i['principalVariation']), **work(i['work'])))
    r=e['result']
    return dict(initialCandidates=strings(e['initialCandidates']), iterations=iterations,
        score=r['score'], pv=strings(r['principalVariation']),
        nodesPerSearch=r['work']['chargedSearchUnits'],
        chargedRelationQueriesPerSearch=r['work']['chargedRelationQueries'])

def main():
    os.sched_setaffinity(0, {0,1,2,3,4,5,8,9,10,11,12,13})
    dataset=json.loads((OUT/'workloads.json').read_text())
    before=cpu_snapshot()
    rows=[]
    description=('Neutral fixed completed iterations; fresh logical learned/pawn/TT state per search; '
        'allocated storage reused within process; deterministic rnd=0; max4095 charged visits errors '
        'on interruption; semantic counters exclude root preparation; CPU includes initialization, '
        'root preparation, all repetitions, allocation, process startup/output; no host polling, '
        'timed root controller, production personality/session/protocol, or full diagnostic adapter. '
        'F1 development collection with selected exact native fixture anchors; no qualification claim.')
    for c in dataset['cases']:
        parity=[]
        for diag in ['on','off']:
            label=c['id']+'-'+diag
            target=OUT/label
            inp=c['input']
            cmd=[sys.executable,str(ROOT/'tools/measure.py'),'--output',str(target),'--label',label,
                '--fidelity','F1','--semantic-description',description,'--known-single-process',
                '--cwd',str(ROOT),'--input-file',str(OUT/'workloads.json'),
                '--input-file',str(Path(__file__).resolve()),'--build-record',
                str(ROOT/'evidence/evaluation-v2-build-20261017/receipt.json'),
                '--warmups','1','--repeats','3','--timeout-s','60','--aggregate-timeout-s','240',
                '--',str(OUT/'rook2-dev-exact'),'ordinary','--fen',inp['fen'],
                '--moves',' '.join(inp['moves']),'--depth',str(inp['completedIterations']),
                '--repeat',str(c['searches_per_process']),'--max-nodes','4095',
                '--diagnostics',diag,'--tts-bytes',str(inp['personalityParameters']['tts'])]
            subprocess.run(cmd,check=True)
            s=json.loads((target/'summary.json').read_text())
            assert s['complete_schedule'] and not s['failure']
            outputs=[(target/f"{r['id']}"/'stdout.raw').read_bytes() for r in s['records']]
            assert all(x==outputs[0] for x in outputs)
            value=json.loads(outputs[0]);exp=expected_projection(c['expected'])
            assert {k:value[k] for k in exp}==exp,label
            assert value['repeat']==c['searches_per_process']
            witness=0
            for _ in range(value['repeat']):
                witness=(witness*0x100000001b3+value['score']+value['nodesPerSearch']+
                         value['chargedRelationQueriesPerSearch']) & ((1<<64)-1)
            assert witness==value['consumptionWitness']
            parity.append({k:value[k] for k in [*exp,'consumptionWitness']})
            rows.append(dict(id=label,searches_per_process=value['repeat'],
                cpu=s['summaries']['total_cpu_s'],wall=s['summaries']['wall_ns'],
                identical_output_including_warmup=True,expected_projection_equal=True,
                summary_sha256=SHA(target/'summary.json'),observations=value))
        assert parity[0]==parity[1],c['id']
    after=cpu_snapshot()
    save(OUT/'cpu-observation.json',dict(before=before,after=after,
        delta={k:[b-a for a,b in zip(before[k],after[k])] for k in before},
        columns=['user','nice','system','idle','iowait','irq','softirq','steal','guest','guest_nice'],
        ticks_per_second=os.sysconf('SC_CLK_TCK'),
        scope='Collection interval only; CPU15 observations cannot prove absolute exclusion.'))
    save(OUT/'results.json',dict(schema='rook2-neutral-evaluation-fixed-root-summary-v2',
        binary_sha256=SHA(OUT/'rook2-dev-exact'),workloads_sha256=SHA(OUT/'workloads.json'),
        collection_sha256=SHA(Path(__file__).resolve()),diagnostic_parity=True,
        expected_root_projection_equal=True,conformance_claim=False,
        performance='Development CPU only; no reference ratio or qualification.',records=rows))
    print('Validated',len(rows),'schedules and every root-step projection.')

if __name__=='__main__':
    main()
