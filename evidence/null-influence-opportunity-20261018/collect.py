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
ENGINE = ROOT/'evidence/null-influence-opportunity-build-20261018/rook2-exact'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    terminal = json.loads((ROOT/'evidence/production-activity-specialization-training-20261018/tool-terminal.json').read_text())
    assert terminal['exit_code'] == 0
    build_path = ENGINE.parent/'receipt.json'
    build = json.loads(build_path.read_text())
    preparation = ROOT/'evidence/null-influence-opportunity-preparation-20261018'
    prepared_path = preparation/'prepared.json'
    prepared = json.loads(prepared_path.read_text())
    archive = preparation/prepared['archive']
    assert sha(ENGINE) == build['binary_output']['sha256'] == '715b42f9cfbb1955f67dc9434404a50e684791cd7d4d3ad1c43c8e853a97b57c'
    assert build['source_sha256_before'] == build['source_sha256_after'] == prepared['variant_source_sha256']
    assert sha(archive) == prepared['archive_sha256']
    workloads = json.loads((SPEC/'workloads.json').read_text())
    files = [Path(__file__),ENGINE,build_path,prepared_path,archive,
             SPEC/'workloads.json',SPEC/'replay-oracle.json',SPEC/'replay-check.mjs']
    before = {str(p):sha(p) for p in files}
    manifest=dict(schema='rook2-null-influence-opportunity-v1', case_order=[c['id'] for c in workloads['cases']],
                  input_sha256=before, helper_affinity=sorted(os.sched_getaffinity(0)),
                  scope='D=true derivative of frozen8c; positive ordinary null map builds and null-to-quiescence entries; no cache/reuse exists',
                  performance='No production CPU or PMU interpretation; outputs and diagnostic invocation counts only',
                  limits='Released checker owns case/time/stream and cleanup bounds; one invocation per case, stop first failure')
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    rows=[]
    for case in workloads['cases']:
        directory=OUT/case['id']; directory.mkdir()
        record=directory/'counts.json'
        command=['/usr/bin/node',str(SPEC/'replay-check.mjs'),'--case',case['id'],'--','/usr/bin/taskset','-c','14',str(ENGINE)]
        env=dict(os.environ,ROOK2_NULL_PROBE=str(record))
        with (directory/'comparator.stdout').open('xb') as stdout,(directory/'comparator.stderr').open('xb') as stderr:
            child=subprocess.run(command,env=env,stdout=stdout,stderr=stderr)
        report=json.loads((directory/'comparator.stdout').read_text())
        assert child.returncode==0 and report['status']=='pass' and len(report['results'])==1
        assert not (directory/'comparator.stderr').stat().st_size
        counts=json.loads(record.read_text())
        assert set(counts)=={'null_trials','null_positive_map','null_to_quiescence','influence_builds','full','fast'}
        assert all(isinstance(v,int) and v>=0 for v in counts.values())
        assert counts['null_positive_map']+counts['null_to_quiescence']<=counts['null_trials']
        assert counts['null_positive_map']<=counts['influence_builds']
        rows.append(dict(case=case['id'],comparator_exit=child.returncode,counts=counts,counts_sha256=sha(record),oracle_sha256=sha(directory/'comparator.stdout')))
        (OUT/'partial.json').write_text(json.dumps(rows,indent=2)+'\n')
        print(json.dumps(dict(case=case['id'],null_trials=counts['null_trials'],positive_map=counts['null_positive_map'],boundary=counts['null_to_quiescence'])),flush=True)
    after={str(p):sha(p) for p in files}
    assert before==after and len(rows)==54
    totals={key:sum(row['counts'][key] for row in rows) for key in rows[0]['counts']}
    report=dict(complete=True, rows=rows, totals=totals, input_sha256_after=after,
                positive_null_build_fraction=totals['null_positive_map']/totals['influence_builds'] if totals['influence_builds'] else None,
                interpretation='Positive-ordinary null map builds are an opportunity count only, not CPU savings. Boundary entries are separate potential scope; no reuse/caching or production cost claim.')
    (OUT/'summary.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(complete=True,totals=totals,positive_null_build_fraction=report['positive_null_build_fraction'])))


if __name__ == '__main__':
    main()
