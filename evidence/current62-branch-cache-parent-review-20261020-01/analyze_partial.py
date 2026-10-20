from pathlib import Path
import json,sys,hashlib
E=Path('/home/legolas/rook2/evidence');X=E/'current62-branch-cache-execution-20261020-01';P=E/'current62-branch-cache-parent-review-20261020-01'
sys.path.insert(0,str(X));from bounded_run import BoundedRunner
from vector_summary import inspect_annotator_totals
load=lambda p:json.loads(Path(p).read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
plan=load(X/'plan.json');O=Path(plan['output']);record=load(O/'provenance.json');assert not record['complete'] and load(O/'tool-terminal.json')['exit_code']==1
assert load(P/'target-and-supervision-closure.json')['target_live_and_original_offline_output_checks_pass']
runner=BoundedRunner(O,plan,started=record['study_started_monotonic'],boot_id=record['study_boot_id'])
argv=['/usr/bin/taskset','-c','0-5,8-13',str(Path(plan['valgrind_prefix'])/'bin/callgrind_annotate'),'--auto=no','--inclusive=no','--show='+','.join(plan['event_names']),'--sort=Ir','--show-percs=no','--threshold=100',str(O/'profile-35.callgrind')]
r=runner.run(argv,'postmortem-functions',60000);assert r.returncode==0
annotator=inspect_annotator_totals((O/'postmortem-functions.stdout').read_text(),plan['event_names'])
argv=['/usr/bin/taskset','-c','0-5,8-13','/usr/bin/python3',str(P/'partial_postmortem_parser.py'),str(O/'profile-35.callgrind'),'--expected-events',','.join(plan['event_names']),'--output',str(O/'partial-self-ranking.json')]
r=runner.run(argv,'postmortem-partial-SELF-ranking',60000);assert r.returncode==0
rank=load(O/'partial-self-ranking.json');assert annotator==rank['summary']
assert rank['SELF_sum']==rank['totals'] and rank['unattributed_summary_events']=={n:(2 if n=='Ir' else 0) for n in plan['event_names']}
for n in plan['event_names']:assert sum(row['SELF_events'][n] for row in rank['ranking'])+rank['unattributed_summary_events'][n]==annotator[n]
result={'partial_postmortem_checks_complete':True,'original_strict_study_complete':False,'summary':rank['summary'],'attributed_SELF_totals':rank['totals'],'unattributed_events':rank['unattributed_summary_events'],'annotator_PROGRAM_TOTALS':annotator,'ranking_sha256':sha(O/'partial-self-ranking.json'),'coalesced_NAME_groups':len(rank['ranking']),'raw_sha256':rank['raw_sha256'],'engine_or_profiler_runs':0}
(P/'partial-postmortem-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
