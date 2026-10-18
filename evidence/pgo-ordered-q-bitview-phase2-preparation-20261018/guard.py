import hashlib,json,os
from pathlib import Path
HERE=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:json.loads(p.read_text())
def require_clearance():
 c=load(HERE/'execution-clearance.json');assert c['authorized'] and c['scope']=='phase2-own-pgo-validation-no-cpu';t=c['parent_generic_pilot_actual_terminal'];assert t['session_id']==65283 and t['terminal_chunk_id']=='7a45d0' and t['exit_code']==0 and t['actual_tool_terminal_observed'];assert sorted(os.sched_getaffinity(0))==[0,1,2,3,4,5,8,9,10,11,12,13];assert os.environ['TMPDIR']=='/home/legolas/rook2-build-tmp';return c
def terminal(path):
 t=load(path);assert t.get('actual_tool_terminal_observed') is True and t['exit_code']==0;return t
