"""Future independent raw/profile/source reconciliation, no engine execution."""
from pathlib import Path
import hashlib,json,sys,os
from bounded_run import BoundedRunner
from vector_summary import inspect_profile,inspect_annotator_totals
HERE=Path(__file__).resolve().parent
load=lambda p:json.loads(Path(p).read_text())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 plan=load(HERE/'plan.json');out=Path(plan['output']);terminal=load(out/'tool-terminal.json')
 assert sorted(os.sched_getaffinity(0))==plan['helper_affinity'] and os.environ.get('TMPDIR')=='/home/legolas/rook2-build-tmp'
 assert load(HERE/'execution-clearance.json')['verify'] is True
 assert all(sha(HERE/name)==h for name,h in load(HERE/'helper-pins.json').items())
 assert terminal.get('actual_tool_terminal_observed') is True and terminal['exit_code']==0 and (terminal.get('terminal_chunk_id') or terminal.get('chunk_id'))
 record=load(out/'provenance.json');assert record['complete'] and list(record['cases'])==plan['cases'] and record['one_fixed_lifetime_per_case']
 assert sum(x['stem']=='annotate-version' for x in record['commands'])==1
 for x in record['commands']:
  expected=255 if x['stem']=='annotate-version' else 0
  assert x['actual_child_return_observed'] and x['exit_code']==x['expected_exit_code']==expected
  assert x['output_sha256']=={stream:sha(out/(x['stem']+'.'+stream)) for stream in ['stdout','stderr']}
  supervision=load(out/(x['stem']+'-supervision.json'))
  assert supervision['complete'] and supervision['actual_child_return_observed'] and supervision['returncode']==expected
  assert supervision['subreaper_enabled'] and supervision['whole_owned_tree_cleanup_confirmed'] and not supervision['remaining_owned']
  assert supervision['cleanup_elapsed_s']<=supervision['cleanup_deadline_s']==5 and not supervision['ownership_observation_errors']
  for stream,counts in supervision['stream_bytes'].items():
   assert counts['observed']==counts['retained']==(out/(x['stem']+'.'+stream)).stat().st_size and counts['discarded_observed']==0
  if x['stem']=='annotate-version':
   assert x['argv'][-2:]==[str(Path(plan['valgrind_prefix'])/'bin/callgrind_annotate'),'--version']
 assert (out/'annotate-version.stdout').read_bytes()==b'' and (out/'annotate-version.stderr').read_bytes()==b'callgrind_annotate-3.24.0\n'
 closure=load(out/'input-closure.json');assert closure==record['input_sha256'] and all(sha(path)==digest for path,digest in closure.items())
 assert sha(plan['engine'])==record['engine_sha256']==plan['engine_sha256'] and sha(plan['source_archive'])==record['source_archive_sha256']==plan['source_archive_sha256']
 reference=load(plan['strict_reference']);details={}
 for case in plan['cases']:
  row=load(out/(case+'-oracle.stdout'))['results'][0];ref=next(x for x in reference['results'] if x['case']==case)
  assert row['stdout'].encode()==ref['stdout'].encode()==(out/(case+'-stdout.raw')).read_bytes()
  assert row['stderr']==ref['stderr']=='' and row['exit']==dict(code=0,signal=None) and row['complete'] and not row['truncated'] and row['error'] is None and row['discardedObservedBytes']==0 and not row.get('cleanupUnconfirmed',False)
  owned=load(out/(case+'-oracle-supervision.json'))
  assert row['pid'] in [x['pid'] for x in owned['seen_owned_processes']], 'detached native PID not observed by supervisor'
  profile=out/(case+'.callgrind');lines=profile.read_text().splitlines()
  vector=inspect_profile(profile,plan);assert vector==record['cases'][case]['simulated_event_vector'] and vector['profile_pid']==row['pid']
  assert vector['summary']['Ir']==record['cases'][case]['total_simulated_Ir']
  assert sha(profile)==record['cases'][case]['profile_sha256'] and sha(out/(case+'.log'))==record['cases'][case]['log_sha256']
  function=next(x for x in record['commands'] if x['stem']==case+'-functions')
  assert '--threshold=100' in function['argv'] and '--inclusive=no' in function['argv']
  assert '--show='+','.join(plan['event_names']) in function['argv'] and '--sort=Ir' in function['argv'] and '--show-percs=no' in function['argv']
  annotator_totals=inspect_annotator_totals((out/(case+'-functions.stdout')).read_text(),plan['event_names'])
  assert annotator_totals==vector['summary']==record['cases'][case]['independent_named_annotator_totals']
  for name in plan['annotations']:
   stem=case+'-'+Path(name).stem+'-lines';cmd=next(x for x in record['commands'] if x['stem']==stem)
   absolute=str(Path(plan['compiled_source_root'])/name);display=(out/(stem+'.stdout')).read_text()
   assert cmd['argv'][-1]==absolute and '--threshold=0' in cmd['argv'] and '--inclusive=no' in cmd['argv']
   assert '-- User-annotated source: '+absolute in display
   expected=dict(compiled_source=absolute,source_sha256=plan['source_sha256'][name],has_information=('No information has been collected for '+absolute) not in display,threshold=0)
   assert record['cases'][case]['annotations'][name]==expected
  details[case]=dict(simulated_event_vector=vector,total_simulated_Ir=vector['summary']['Ir'],native_exit=row['exit'],raw_bytes_equal_reference=True,source_annotations=record['cases'][case]['annotations'])
 argv=['/usr/bin/taskset','-c','0-5,8-13',plan['node'],str(HERE/'recheck.mjs'),str(out)]
 runner=BoundedRunner(out,plan,started=record['study_started_monotonic'],boot_id=record['study_boot_id'])
 r=runner.run(argv,'independent-checkReplay',plan['supervision']['offline_checker_wall_ms'])
 assert r.returncode==0 and not (out/'independent-checkReplay.stderr').stat().st_size
 assert load(out/'independent-checkReplay.stdout')==dict(complete=True,originalCheckReplayCount=1,engineRuns=0)
 assert all(sha(path)==digest for path,digest in closure.items())
 result=dict(complete=True,cases=details,all_original_inputs_unchanged=True,original_checkReplay_exit_code=r.returncode,original_checkReplay_cases=1,event_scope=plan['event_scope'],native_engine_runs=0,qualification=False,outer_actual_terminal_required=True)
 with (out/'independent-verification.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
 _,storage_failure=runner._files();assert storage_failure is None,storage_failure
 print(json.dumps({k:result[k] for k in ['complete','original_checkReplay_cases','native_engine_runs','qualification']}))
if __name__=='__main__':main()
