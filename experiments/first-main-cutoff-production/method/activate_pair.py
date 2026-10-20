#!/usr/bin/python3
"""Bind the one completed own-PGO image to the pre-frozen432 schedule; no engine."""
import hashlib,json,sys
from pathlib import Path
B=Path(__file__).resolve().parent;sys.dont_write_bytecode=True;sys.path.insert(0,str(B/'pgo'))
from guard import require_clearance,check_thin_build,terminal,PLAN,sha
require_clearance();terminal(B/'use-build/tool-terminal.json');terminal(B/'training/verify-tool-terminal.json')
r=json.loads((B/'use-build/receipt.json').read_text());v=json.loads((B/'training/verification.json').read_text());check_thin_build(B/'use-build','profile-use')
assert v['complete'] and v['independent_remerge_byte_identical']
candidate=B/'use-build/rook2-exact';control=Path(PLAN['baseline_own_pgo']['path']);assert sha(candidate)==r['binary_output']['sha256'];assert sha(control)==PLAN['baseline_own_pgo']['sha256']
schedule=json.loads((B/'pair/schedule.json').read_text());assert len(schedule)==432 and sum(x['warmup'] for x in schedule)==108
inputs=dict(PLAN['input_sha256'])
for p in [B/'pgo/plan.json',B/'pgo/execution-clearance.json',B/'pgo/script-pins.json',B/'training/training.json',B/'training/verification.json',B/'training/merged.profdata',B/'use-build/receipt.json',B/'use-build/tool-terminal.json',B/'training/verify-tool-terminal.json',B/'source-freeze.json']:
 inputs[str(p)]=sha(p)
plan={'schema':'rook2-first-main-paired54-v1','variants':{'control':{'path':str(control),'sha256':sha(control)},'candidate':{'path':str(candidate),'sha256':sha(candidate)}},'input_sha256':inputs,'schedule':str(B/'pair/schedule.json'),'schedule_sha256':sha(B/'pair/schedule.json'),'lifetimes':432,'warmups':108,'measured':324,'nativeCpu':14,'primaryMetric':'whole native wait4 user+system CPU lifetime plus same small child pre-exec prefix','trainingExcluded':True,'numericalGainGate':None,'promotion':False}
with (B/'pair/plan.json').open('x') as f:json.dump(plan,f,indent=2);f.write('\n')
print(json.dumps({'candidateSha256':sha(candidate),'controlSha256':sha(control),'planSha256':sha(B/'pair/plan.json'),'lifetimes':432,'numericalGainGate':None}))
