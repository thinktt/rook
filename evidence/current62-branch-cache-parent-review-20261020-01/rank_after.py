from pathlib import Path
import json,sys,hashlib,os
X=Path('/home/legolas/rook2/evidence/current62-branch-cache-execution-20261020-01')
sys.path.insert(0,str(X))
from bounded_run import BoundedRunner
load=lambda p:json.loads(Path(p).read_text())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
plan=load(X/'plan.json');out=Path(plan['output']);record=load(out/'provenance.json')
assert record['complete'] and load(out/'tool-terminal.json')['exit_code']==0
assert load(out/'independent-verification.json')['complete']
assert sorted(os.sched_getaffinity(0))==plan['helper_affinity']
assert sha(plan['vector_parser'])==plan['vector_parser_sha256']
runner=BoundedRunner(out,plan,started=record['study_started_monotonic'],boot_id=record['study_boot_id'])
argv=['/usr/bin/taskset','-c','0-5,8-13','/usr/bin/python3',plan['vector_parser'],str(out/'profile-35.callgrind'),'--expected-events',','.join(plan['event_names']),'--output',str(out/'self-ranking.json')]
r=runner.run(argv,'independent-vector-SELF-ranking',plan['supervision']['annotation_command_wall_ms'])
assert r.returncode==0
rank=load(out/'self-ranking.json');expected=record['cases']['profile-35']['simulated_event_vector']['summary']
assert rank['SELF_sum']==rank['summary']==rank['totals']==expected
assert all(sum(row['SELF_events'][event] for row in rank['ranking'])==expected[event] for event in expected)
assert sha(plan['vector_parser'])==plan['vector_parser_sha256']
print(json.dumps({'complete':True,'ranking_sha256':sha(out/'self-ranking.json'),'event_totals':expected,'coalesced_NAME_groups':len(rank['ranking']),'engine_runs':0,'modeled_cost_scalar_claim':False}))
