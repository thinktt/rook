#!/usr/bin/env python3
"""Diagnostic-only replay parity and evaluation opportunity counts; no CPU timing."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
SPEC = Path('/home/legolas/king-spec/conformance/profiling')
ENGINE = ROOT/'evidence/evaluation-opportunity-build-20261018/rook2-exact'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    workloads = json.loads((SPEC/'workloads.json').read_text())
    files = [Path(__file__),ENGINE,SPEC/'workloads.json',SPEC/'replay-oracle.json',SPEC/'replay-check.mjs']
    before = {str(p):sha(p) for p in files}
    manifest=dict(schema='rook2-eval-opportunity-v1', case_order=[c['id'] for c in workloads['cases']],
                  input_sha256=before, helper_affinity=sorted(os.sched_getaffinity(0)),
                  scope='D=true ordinary wire derivative; full-entry retained-age0 opportunities include first root full call; no cache exists',
                  performance='No production CPU or PMU interpretation; outputs and diagnostic invocation counts only',
                  limits='Released checker owns case/time/stream and cleanup bounds; one invocation per case, stop first failure')
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    rows=[]
    for case in workloads['cases']:
        directory=OUT/case['id']; directory.mkdir()
        record=directory/'counts.json'
        command=['/usr/bin/node',str(SPEC/'replay-check.mjs'),'--case',case['id'],'--','/usr/bin/taskset','-c','14',str(ENGINE)]
        env=dict(os.environ,ROOK2_EVAL_PROBE=str(record))
        with (directory/'comparator.stdout').open('xb') as stdout,(directory/'comparator.stderr').open('xb') as stderr:
            child=subprocess.run(command,env=env,stdout=stdout,stderr=stderr)
        report=json.loads((directory/'comparator.stdout').read_text())
        assert child.returncode==0 and report['status']=='pass' and len(report['results'])==1
        assert not (directory/'comparator.stderr').stat().st_size
        counts=json.loads(record.read_text())
        assert all(isinstance(v,int) and v>=0 for v in counts.values())
        assert counts['full_entry_age_zero']<=counts['full']
        assert counts['full_relation_queries_at_age_zero']<=counts['full_relation_queries']
        rows.append(dict(case=case['id'],counts=counts,counts_sha256=sha(record),oracle_sha256=sha(directory/'comparator.stdout')))
        (OUT/'partial.json').write_text(json.dumps(rows,indent=2)+'\n')
        print(json.dumps(dict(case=case['id'],full=counts['full'],age_zero=counts['full_entry_age_zero'])),flush=True)
    after={str(p):sha(p) for p in files}
    assert before==after and len(rows)==54
    totals={key:sum(row['counts'][key] for row in rows) for key in rows[0]['counts']}
    report=dict(complete=True, rows=rows, totals=totals, input_sha256_after=after,
                full_age_zero_fraction=totals['full_entry_age_zero']/totals['full'] if totals['full'] else None,
                interpretation='Opportunity upper estimate including first root call; age0 alone is not a complete cache validity key or a speedup')
    (OUT/'summary.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(complete=True,totals=totals,full_age_zero_fraction=report['full_age_zero_fraction'])))


if __name__ == '__main__':
    main()
