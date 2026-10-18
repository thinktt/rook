#!/usr/bin/env python3
from pathlib import Path
import sys,json,subprocess,hashlib,os
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
sys.path.insert(0, '/home/legolas/rook2/evidence/iterations-clock102-validation-preparation-20261018')
from guard import clearance,check_sources,check_dependencies,write,sha,terminal
plan=clearance();retry=json.loads((HERE/'retry-plan.json').read_text());out=Path(retry['output']);assert not out.exists();out.mkdir()
assert sha(HERE/'capture_codegen02.py')==retry['corrected_driver_sha256']
check_sources(plan);check_dependencies(plan)
with (out/'driver.stdout').open('xb') as a,(out/'driver.stderr').open('xb') as b:
 child=subprocess.run([sys.executable,str(HERE/'capture_codegen02.py')],stdout=a,stderr=b)
result=dict(complete=False,actual_child_return_observed=True,exit_code=child.returncode,driver_sha256=sha(HERE/'capture_codegen02.py'),retry_plan_sha256=sha(HERE/'retry-plan.json'),stdout_sha256=sha(out/'driver.stdout'),stderr_sha256=sha(out/'driver.stderr'),affinity=sorted(os.sched_getaffinity(0)),TMPDIR=os.environ.get('TMPDIR'))
if child.returncode==0:
 check_sources(plan);check_dependencies(plan);assert result['driver_sha256']==retry['corrected_driver_sha256'];result.update(complete=True,capture_sha256=sha(out/'capture.json'),source_stable=True)
write(out/'verification.json',result);print(json.dumps(result));sys.exit(0 if result['complete'] else 1)
