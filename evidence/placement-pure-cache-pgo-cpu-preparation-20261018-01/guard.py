#!/usr/bin/env python3
"""No launch/merge: actual own-profile proof admission for a future matched pilot."""
from pathlib import Path
import hashlib,json
P=Path(__file__).resolve().parent;E=P.parent;ROOT=E.parent
FUNCTIONAL=E/'placement-pure-cache-pgo-reconciliation-20261018-01/independent-verification.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_text())
def terminal(value):
 assert value['actual_tool_terminal_observed'] is True and value['exit_code']==0
 assert isinstance(value.get('terminal_chunk_id') or value.get('chunk_id'),str)
 assert (value.get('terminal_chunk_id') or value.get('chunk_id')).strip()
def validate_gate():
 plan=load(P/'plan.json');clear=load(P/'launch-clearance.json')
 assert clear['parent_review_complete'] is True and clear['all_owned_jobs_closed'] is True
 assert clear['approved_functional_proof']==str(FUNCTIONAL)
 assert clear['plan_sha256']==sha(P/'plan.json') and clear['driver_sha256']==sha(P/'run_pilot.py') and clear['guard_sha256']==sha(P/'guard.py')
 for name in ['functional','backend']:
  approval=clear['approved_'+name];assert approval['parent_approved'] is True
  path=Path(approval['path']);assert str(path) in clear['dependencies']
  assert clear['dependencies'][str(path)]==approval['sha256']==sha(path)
  terminal(approval['actual_terminal'])
 assert clear['approved_functional']['path']==str(FUNCTIONAL)
 assert clear['approved_functional']['actual_terminal']==load(FUNCTIONAL.parent/'tool-terminal.json')
 assert set(plan['dependencies'])<=set(clear['dependencies'])
 for path,h in plan['dependencies'].items():assert clear['dependencies'][path]==h
 for path,h in clear['dependencies'].items():assert sha(path)==h,path
 def pinned(path,h=None):
  path=Path(path);assert str(path) in clear['dependencies'],path
  assert clear['dependencies'][str(path)]==sha(path),path
  if h is not None:assert sha(path)==h,path
 # New source schema/native184 proof supplements, never replaces, both
 # actual own-PGO54/profile/use54/wire24 proof rows below.
 declaration=plan['predeclaration'];pinned(declaration['path'],declaration['sha256'])
 assert load(declaration['path'])['advance_rule']==plan['advance_rule']
 source=plan['source_manifest'];pinned(source['path'],source['sha256'])
 manifest=load(source['path']);assert manifest['schema']=='relative-path-sha256-v1'
 assert manifest['counts']=={'native_and_manifests':46,'tools':23,'total':69}
 files=manifest['files']
 assert manifest['graph_sha256']==plan['source_graph_sha256']==hashlib.sha256(json.dumps(files,sort_keys=True,separators=(',',':')).encode()).hexdigest()
 assert {k:v for k,v in files.items() if not k.startswith('tools/')}==plan['pgo_trials']['candidate']['source46']
 assert {k:v for k,v in files.items() if k.startswith('tools/')}==plan['tools23']
 generic=plan['generic_functional_proof'];pinned(generic['path'],generic['sha256'])
 proof=load(generic['path'])
 assert proof['complete'] and proof['native_tests']==plan['expected_native_tests']==184
 assert proof['engine_sha256']==plan['generic_candidate_sha256']
 assert proof['source46_tools23_archive69_equal'] and proof['only_declared_placement_cache_sources_changed_vs_fullbyte_baseline']
 assert proof['influence_relation_pawn_and_remembered_unchanged'] and proof['independent_influence_test_module_unchanged']
 assert proof['strict54_original_checkReplay'] and proof['compiler_cargo_generic_bound'] and proof['all_dependencies_stable']
 assert len(proof['wire8_searches24_raw_protocol'])==8 and sum(x['searches'] for x in proof['wire8_searches24_raw_protocol'])==24
 for path,h in proof['dependencies'].items():pinned(path,h)
 for variant,trial in plan['pgo_trials'].items():
  proof_path=Path(trial['reconciliation'])/'independent-verification.json';pinned(proof_path)
  proof=load(proof_path)
  assert proof['complete'] and proof['own_profile_only'] and proof['strict_training54'] and proof['fresh_strict54'] and proof['wire8_searches24']
  assert set(proof['variants'])=={trial['label']}
  row=proof['variants'][trial['label']]
  assert row['artifact_sha256']==plan['variants'][variant]['sha256']
  assert row['source_sha256']==trial['source46']
  assert row['training_strict_replays']==row['post_use_strict_replays']==row['raw_profiles']==54
  assert row['wire_fixtures']==8 and row['wire_searches']==24
  assert row['profile_independently_remerged'] and row['profile_remerge_exit_code']==0
  build=Path(trial['use_build']);train=Path(trial['training']);check=Path(trial['use_check']);wire=Path(trial['wire'])
  pinned(build/'receipt.json',row['build_receipt_sha256']);pinned(build/'rook2-exact',row['artifact_sha256'])
  pinned(train/'training.json',row['training_record_sha256']);pinned(train/'merged.profdata',row['profile_sha256'])
  pinned(train/'verification.json',row['training_verification_sha256']);pinned(train/'replay.json',row['training_replay_sha256'])
  pinned(check/'identity.json',row['strict_identity_sha256']);pinned(check/'profile-all.stdout',row['post_use_replay_sha256']);pinned(wire/'receipt.json',row['wire_receipt_sha256'])
  receipt=load(build/'receipt.json');training=load(train/'training.json')
  assert receipt['mode']=='generic' and receipt['pgo']['mode']=='profile-use' and receipt['pgo']['inputs_unchanged']
  assert receipt['source_sha256_before']==receipt['source_sha256_after']==row['source_sha256']
  assert receipt['tool_sha256_before']==receipt['tool_sha256_after']==plan['tools23']
  assert receipt['toolchain']==plan['toolchain'] and receipt['target_cpu']=='x86-64' and receipt['target_triple']=='x86_64-unknown-linux-gnu'
  assert receipt['pgo']['input_sha256_before']==receipt['pgo']['input_sha256_after']=={str(train/'merged.profdata'):row['profile_sha256'],str(train/'training.json'):row['training_record_sha256']}
  assert receipt['rust_flags']==['-C','target-cpu=x86-64','-C',f"profile-use={train/'merged.profdata'}",'-C','llvm-args=-pgo-warn-missing-function']
  assert training['engine_source_sha256']==row['source_sha256'] and training['profile_sha256']==row['profile_sha256']
  assert len(training['raw_profiles_sha256'])==54
  for path,h in training['raw_profiles_sha256'].items():pinned(path,h)
  # Complete existing stage evidence, including raw outputs, archives and observed outer terminals.
  for key in ['instrumented_build','training','use_build','use_check','wire','reconciliation']:
   directory=Path(trial[key]);assert directory.is_dir()
   for path in directory.rglob('*'):
    if path.is_file():pinned(path)
  for key in ['instrumented_build','training','use_build','use_check','reconciliation']:terminal(load(Path(trial[key])/'tool-terminal.json'))
  terminal(load(train/'verify-tool-terminal.json'))
 for v in plan['variants'].values():pinned(v['path'],v['sha256'])
 assert plan['prepared_only'] is True
 return plan,clear,load(FUNCTIONAL)
if __name__=='__main__':
 plan,clear,proof=validate_gate()
 print(json.dumps({'gate_passed':True,'native_runs':0,'profile_merges':0,'candidate':plan['variants']['candidate']['sha256']}))
