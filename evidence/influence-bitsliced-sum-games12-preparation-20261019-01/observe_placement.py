#!/usr/bin/env python3
"""One read-only point observation of the explicitly named collector tree."""
import argparse,json,os
from pathlib import Path
H={0,1,2,3,4,5,8,9,10,11,12,13}
a=argparse.ArgumentParser();a.add_argument('--pid',type=int,required=True);a.add_argument('--output',type=Path,required=True);x=a.parse_args()
assert set(os.sched_getaffinity(0))==H
plan=json.loads((Path(__file__).parent/'plan.json').read_text());pending=[x.pid];rows=[]
while pending:
 pid=pending.pop(0);proc=Path('/proc')/str(pid)
 tids=sorted((proc/'task').iterdir(),key=lambda q:int(q.name))
 children=[int(q) for q in (proc/'task'/str(pid)/'children').read_text().split()]
 exe=os.readlink(proc/'exe');is_native=exe==plan['engine'];expected={14} if is_native else H
 tasks=[dict(tid=int(t.name),mask=sorted(os.sched_getaffinity(int(t.name)))) for t in tids]
 rows.append(dict(pid=pid,exe=exe,cmdline=(proc/'cmdline').read_bytes().replace(b'\0',b' ').decode(),tasks=tasks,children=children,native=is_native))
 assert all(set(t['mask'])==expected for t in tasks),(pid,tasks,sorted(expected))
 pending+=children
assert sum(q['native'] for q in rows)==1,'snapshot requires one actual live native child'
with x.output.open('x') as f:json.dump(dict(collector_pid=x.pid,processes=rows,helper_mask=sorted(H),scope='single external point observation of all current owned tasks, not continuous monitoring'),f,indent=2);f.write('\n')
print(json.dumps(dict(complete=True,processes=len(rows),tasks=sum(len(q['tasks']) for q in rows))))
