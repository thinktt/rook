#!/usr/bin/env python3
import hashlib,json,subprocess,sys
from pathlib import Path
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
ENGINE=ROOT/'evidence/pgo-eval-geometry-use-build-20261018/rook2-exact'
BUILD=ROOT/'evidence/pgo-eval-geometry-use-build-20261018/receipt.json'
command=[sys.executable,str(ROOT/'tools/collect_games.py'),'--engine',str(ENGINE),'--build-record',str(BUILD),'--output',str(OUT/'collection')]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
plan=dict(command=command,driver_sha256=sha(Path(__file__)),engine_sha256=sha(ENGINE),build_record_sha256=sha(BUILD),scope='Complete published12-game schedule: one excluded warmup plus three measured lifetimes each; reported-only native CPU, external quantized search observations, exact strict replay, no qualified reference acceptance')
with (OUT/'launch.json').open('x') as stream: json.dump(plan,stream,indent=2);stream.write('\n')
with (OUT/'collector.stdout').open('xb') as stdout,(OUT/'collector.stderr').open('xb') as stderr:
 result=subprocess.run(command,cwd=ROOT,stdout=stdout,stderr=stderr)
with (OUT/'terminal.json').open('x') as stream: json.dump(dict(exit_code=result.returncode,driver_sha256_after=sha(Path(__file__)),engine_sha256_after=sha(ENGINE),collector_stdout_sha256=sha(OUT/'collector.stdout'),collector_stderr_sha256=sha(OUT/'collector.stderr')),stream,indent=2);stream.write('\n')
print(json.dumps(dict(exit_code=result.returncode,output=str(OUT))))
raise SystemExit(result.returncode)
