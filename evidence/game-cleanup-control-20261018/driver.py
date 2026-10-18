import os,sys,json,subprocess,time,hashlib
from pathlib import Path
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from collect_games import stop_within_five_seconds
native=OUT/'ignores-term.py';native.write_text("import signal,time\nsignal.signal(signal.SIGTERM,signal.SIG_IGN)\nprint('READY',flush=True)\nwhile True: time.sleep(1)\n")
controller=OUT/'controller.py';controller.write_text("import subprocess,sys\nraise SystemExit(subprocess.call(sys.argv[1:]))\n")
command=[sys.executable,str(controller),sys.executable,str(ROOT/'tools/account_native.py'),'--engine',str(Path(sys.executable).resolve()),'--record',str(OUT/'native.json'),'--known-single-process',str(native)]
inputs=[Path(__file__),ROOT/'tools/collect_games.py',ROOT/'tools/account_native.py',ROOT/'tools/compare_ordinary.py',native,controller]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();before={str(p):sha(p) for p in inputs}
process=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
ready=process.stdout.readline();assert ready==b'READY\n',ready
cleanup=stop_within_five_seconds(process)
stdout,stderr=process.communicate(timeout=1)
(OUT/'controller.stdout').write_bytes(ready+stdout);(OUT/'controller.stderr').write_bytes(stderr)
after={str(p):sha(p) for p in inputs}
report=dict(command=command,comparator_exit=process.returncode,cleanup=cleanup,input_sha256_before=before,input_sha256_after=after,
 expected='Synthetic native deliberately ignores SIGTERM; forced exit is expected, all owned PIDs must reconcile within fixed5s cleanup')
(OUT/'control.json').write_text(json.dumps(report,indent=2)+'\n')
assert cleanup['reconciled'] and cleanup['elapsed_s']<5 and before==after,report
print(json.dumps(report))
