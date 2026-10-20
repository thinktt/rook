from pathlib import Path
import json,sys,hashlib,os
D=Path('/home/legolas/rook2/evidence/current57-callgrind-preparation-20261020-01');sys.path.insert(0,str(D));from bounded_run import BoundedRunner
load=lambda p:json.loads(Path(p).read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
plan=load(D/'plan.json');out=Path(plan['output']);p=load(out/'provenance.json');assert p['complete'] and load(out/'independent-verification.json')['complete'];rank=load(out/'self-ranking.json');assert rank['exclusive_SELF_exactly_reconciled']
for n in ['tool-terminal.json','verify-tool-terminal.json','ranking-tool-terminal.json']:
 t=load(out/n);assert t['actual_tool_terminal_observed'] and t['exit_code']==0
selected=['src/activity.rs','src/types.rs','src/ordinary.rs','src/position.rs'];record={'selected_sources':selected,'reason':'Actual current57 top SELF Activity/ordinary plus inline tag decoding and apply_unchecked endpoint discriminator. Four finite source annotations; no new target lifetime.','ranking_sha256':sha(out/'self-ranking.json'),'script_sha256':sha(__file__),'original_shared_study_deadline_retained':True}
with (out/'source-selection.json').open('x') as f:json.dump(record,f,indent=2);f.write('\n')
runner=BoundedRunner(out,plan,started=p['study_started_monotonic'],boot_id=p['study_boot_id']);rows=[]
for name in selected:
 absolute=Path(plan['compiled_source_root'])/name;assert sha(absolute)==plan['source_sha256'][name];stem='selected-'+Path(name).stem
 cmd=['/usr/bin/taskset','-c','0-5,8-13',str(Path(plan['valgrind_prefix'])/'bin/callgrind_annotate'),'--auto=no','--inclusive=no','--context=0','--threshold=0','--include='+plan['source_root'],str(out/'profile-35.callgrind'),str(absolute)]
 z=runner.run(cmd,stem,plan['supervision']['annotation_command_wall_ms'],cwd=Path(plan['source_root']),env=os.environ.copy());assert z.returncode==0
 display=(out/(stem+'.stdout')).read_text();assert '-- User-annotated source: '+str(absolute) in display;assert not (out/(stem+'.stderr')).stat().st_size;assert sha(absolute)==plan['source_sha256'][name]
 rows.append({'source':name,'absolute_source':str(absolute),'source_sha256':sha(absolute),'command':cmd,'actual_child_return_observed':True,'exit_code':z.returncode,'has_information':('No information has been collected for '+str(absolute)) not in display,'stdout_sha256':sha(out/(stem+'.stdout')),'stderr_sha256':sha(out/(stem+'.stderr'))})
_,failure=runner._files();assert failure is None,failure
with (out/'selected-annotations.json').open('x') as f:json.dump({'complete':True,'rows':rows,'original_shared_study_deadline_retained':True,'new_engine_runs':0},f,indent=2);f.write('\n')
print(json.dumps({'complete':True,'sources':selected,'new_engine_runs':0,'information':[x['has_information'] for x in rows]}))
