#!/usr/bin/env python3
"""Native timed-search CPU schedule, followed by external projection checks."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def save(path,data):
    with path.open('x') as f:
        json.dump(data,f,indent=2,allow_nan=False);f.write('\n')

def snapshot():
    return {s.split()[0]:[int(v) for v in s.split()[1:]]
            for s in Path('/proc/stat').read_text().splitlines()
            if s.startswith(('cpu14 ','cpu15 '))}

def main():
    os.sched_setaffinity(0,{0,1,2,3,4,5,8,9,10,11,12,13})
    data=json.loads((OUT/'workloads.json').read_text());repetitions=data['searches_per_process']
    before=snapshot();rows=[]
    for case in data['cases']:
        q=case['request']['input'];e=case['expected'];parity=[]
        for diag in ['on','off']:
            name=case['id']+'-'+diag;target=OUT/name
            command=[sys.executable,str(ROOT/'tools/measure.py'),'--output',str(target),'--label',name,
                '--fidelity','F1','--semantic-description',
                'Neutral actual work-timed recursion, explicit seed/rnd50, allowances1cs/1cs; '
                'CLI sel14/md99/ana0/TT64MiB, fixture projection has md20; separate native checker '
                'binds full vector. Fresh logical learned/pawn/TT state each repetition with allocated '
                'storage reused. Native root/poll capture; no session ingress, automatic seed, host '
                'commands or public report rendering. CPU includes startup/preparation/output; '
                'semantic N/R exclude preparation. No qualification comparison.',
                '--known-single-process','--cwd',str(ROOT),'--input-file',str(OUT/'workloads.json'),
                '--input-file',str(Path(__file__).resolve()),'--build-record',
                str(ROOT/'evidence/work-timed-build-20261017/receipt.json'),
                '--warmups','1','--repeats','3','--timeout-s','60','--aggregate-timeout-s','240',
                '--',str(OUT/'rook2-dev-exact'),'work-timed','--seed',str(q['seed']),
                '--repeat',str(repetitions),'--diagnostics',diag,'--max-nodes','8192',
                '--iteration-cap','6']
            subprocess.run(command,check=True)
            s=json.loads((target/'summary.json').read_text());assert s['complete_schedule'] and not s['failure']
            raw=[(target/r['id']/'stdout.raw').read_bytes() for r in s['records']]
            assert all(r==raw[0] for r in raw)
            v=json.loads(raw[0]);er=e['result'];es=e['stop']
            assert v['result']==dict(depth=er['depth'],rootIndex=er['rootIndex'],score=er['score'],
                pv=[m['move'] for m in er['principalVariation']],searchId=er['searchId'],elapsedCs=er['elapsedCs'])
            pending=es['pendingRoot']
            ep=None if pending is None else dict(move=pending['move']['move'],
                window=[pending['window']['lower'],pending['window']['upper']],adjustment=pending['adjustment'])
            assert v['stop']==dict(point=es['point'],reason='maximum' if es['point']=='poll' else 'root',
                depth=es['depth'],rootIndex=es['rootIndex'],nodes=es['work']['chargedSearchUnits'],
                relationQueries=es['work']['chargedRelationQueries'],elapsedCs=es['elapsedCs'],pendingRoot=ep)
            assert v['initialCandidates']==[m['move'] for m in e['initialCandidates']]
            checks=[] if diag=='off' else [dict(point=c['point'],depth=c['depth'],rootIndex=c['rootIndex'],
                nodes=c['work']['chargedSearchUnits'],relationQueries=c['work']['chargedRelationQueries'],
                elapsedCs=c['elapsedCs'],limitSeconds=c['limitSeconds'],stop=c['stop']) for c in e['timeChecks']]
            assert v['timeChecks']==checks
            witness=0
            for _ in range(repetitions):
                witness=(witness*0x100000001b3+v['result']['score']+v['stop']['nodes']+
                         v['stop']['relationQueries'])&((1<<64)-1)
            assert witness==v['consumptionWitness']
            parity.append({k:v[k] for k in ['result','stop','initialCandidates','consumptionWitness','publicationCapturesPerSearch']})
            rows.append(dict(id=name,searches_per_process=repetitions,cpu=s['summaries']['total_cpu_s'],
                wall=s['summaries']['wall_ns'],identical_output_including_warmup=True,
                reference_projection_equal=True,summary_sha256=sha(target/'summary.json'),observations=v))
        assert parity[0]==parity[1]
    after=snapshot()
    save(OUT/'cpu-observation.json',dict(before=before,after=after,
        delta={k:[b-a for a,b in zip(before[k],after[k])] for k in before},
        columns=['user','nice','system','idle','iowait','irq','softirq','steal','guest','guest_nice'],
        ticks_per_second=os.sysconf('SC_CLK_TCK')))
    save(OUT/'results.json',dict(schema='rook2-native-work-timed-cpu-v1',binary_sha256=sha(OUT/'rook2-dev-exact'),
        workloads_sha256=sha(OUT/'workloads.json'),collection_sha256=sha(Path(__file__).resolve()),
        diagnostics_parity=True,reference_projection_equal=True,records=rows,
        conformance_claim=False,performance='Development CPU only; no qualification or reference ratio.'))
    print('Validated four schedules, capture/stop/time projections and diagnostic parity.')

if __name__=='__main__':main()
