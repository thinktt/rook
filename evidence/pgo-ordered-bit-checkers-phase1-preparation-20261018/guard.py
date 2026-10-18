from pathlib import Path
import hashlib,json,os
HERE=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:json.loads(p.read_text())
def require_clearance():
 c=load(HERE/'execution-clearance.json')
 assert c.get('authorized') is True and c.get('all_conflicting_native_work_terminal') is True
 assert c.get('scope')=='phase1-own-pgo-validation-no-cpu'
 t=c['parent_second_pilot_actual_terminal'];assert t['session_id']==59875 and t['actual_tool_terminal_observed'] and t['exit_code']==0 and t['terminal_chunk_id']=='5193f7'
 assert sorted(os.sched_getaffinity(0))==[0,1,2,3,4,5,8,9,10,11,12,13]
 return c
def terminal(path):
 t=load(path);assert t.get('actual_tool_terminal_observed') is True and t['exit_code']==0
 return t
