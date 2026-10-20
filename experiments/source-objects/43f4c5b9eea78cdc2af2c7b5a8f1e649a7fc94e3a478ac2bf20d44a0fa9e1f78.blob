#!/usr/bin/env python3
from pathlib import Path
import sys
sys.dont_write_bytecode=True
from guard import HERE,load,sha,write,clearance,terminal,check_sources,check_dependencies

def main():
 plan=clearance();paths={k:Path(v) for k,v in plan['output'].items()};records=[paths[k]/'tool-terminal.json' for k in ['freeze','generic-build','native-validation','strict-check','diagnostic','reconciliation']]
 for path in records:terminal(path)
 check_sources(plan);check_dependencies(plan);result=load(paths['reconciliation']/'independent-verification.json');assert result['status']=='pass' and result['native_units']==152 and result['diagnostic_units']==156 and result['diagnostic_cases']==7447 and result['diagnostic_operations']==97 and result['whole_fixture_files']==92
 summary=dict(status='Exact generation2 fresh validation passed; stopped before measurement/integration',home_source=plan['home_source'],frozen_source=plan['frozen_source'],native_artifact_sha256=result['native_artifact_sha256'],diagnostic_artifact_sha256=result['diagnostic_artifact_sha256'],native_units=152,diagnostic_units=156,strict_replays=54,interruption_fixtures=8,interruption_searches=24,diagnostic_cases=7447,diagnostic_operations=97,whole_fixture_files=92,source_file_count=100,source_stable=True,all_raw_expected_actual_and_exits_independently_reconciled=True,terminal_records={str(q):load(q) for q in records},independent_verification_sha256=sha(paths['reconciliation']/'independent-verification.json'),source_sha256=plan['source_sha256'],all_owned_processes_terminal=True,closure_basis='All actual outer exits observed; successful stage drivers synchronously awaited every Cargo/build/unit/original-replay/wire/DIAG child; no detached work launched.',environment=dict(TMPDIR=plan['TMPDIR'],helper_and_engine_affinity=plan['affinity'],other_work='Fresh phase2 build/strict/codegen may overlap untimed housekeeping; no measuredCPU or profiler live during authorized work; no owned14/15tasks'),native_source_improvements=False,scope=plan['scope'])
 write(HERE/'validation-summary.json',summary)
 dirs=[HERE]+list(paths.values());files={str(q):sha(q) for d in dirs if d.exists() for q in sorted(d.rglob('*')) if q.is_file() and q.name!='validation-file-manifest.json'}
 write(HERE/'validation-file-manifest.json',files);print(__import__('json').dumps(dict(summary=str(HERE/'validation-summary.json'),summary_sha256=sha(HERE/'validation-summary.json'),manifest_sha256=sha(HERE/'validation-file-manifest.json'),native_artifact_sha256=result['native_artifact_sha256'],diagnostic_artifact_sha256=result['diagnostic_artifact_sha256'],all_owned_processes_terminal=True)))
if __name__=='__main__':main()
