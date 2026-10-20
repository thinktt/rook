#!/usr/bin/env python3
"""No native launch: bind pending actual functional/backend approval to this pilot."""
from pathlib import Path
import hashlib,json
P=Path(__file__).resolve().parent
E=P.parent;ROOT=E.parent
FUNCTIONAL=E/'fullbyte-remembered-reciprocal-independent-preparation-20261018-01/independent-verification.json'
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
 assert clear['plan_sha256']==sha(P/'plan.json') and clear['driver_sha256']==sha(P/'run_pilot.py')
 assert clear['guard_sha256']==sha(P/'guard.py')
 # Parent supplies these real records after closure; no inherited/guessed success IDs.
 for name in ['functional','backend']:
  approval=clear['approved_'+name]
  assert approval['parent_approved'] is True
  path=Path(approval['path']);assert str(path) in clear['dependencies']
  assert clear['dependencies'][str(path)]==approval['sha256']==sha(path)
  terminal(approval['actual_terminal'])
 assert clear['approved_functional']['path']==str(FUNCTIONAL)
 assert clear['approved_functional']['actual_terminal']==load(FUNCTIONAL.parent/'tool-terminal.json')
 assert set(plan['dependencies'])<=set(clear['dependencies'])
 for path,h in plan['dependencies'].items():assert clear['dependencies'][path]==h
 for path,h in clear['dependencies'].items():assert sha(path)==h,path
 for v in plan['variants'].values():assert sha(v['path'])==v['sha256']
 functional=load(FUNCTIONAL)
 assert functional['complete'] and functional['engine_sha256']==plan['variants']['candidate']['sha256']
 assert functional['source46_tools23_archive69_equal'] and functional['only_remembered_changed_vs_fullbyte_baseline']
 assert functional['fullbyte_activity_retained_pawn_unchanged'] and functional['independent_influence_test_module_unchanged']
 assert functional['native_tests']==179 and functional['strict54_original_checkReplay']
 assert functional['compiler_cargo_generic_bound'] and functional['all_dependencies_stable'] and functional['new_native_engine_runs']==0
 assert len(functional['wire8_searches24_raw_protocol'])==8
 assert sum(x['searches'] for x in functional['wire8_searches24_raw_protocol'])==24
 assert set(functional['stage_terminals'])=={'build','native','regression'}
 for value in functional['stage_terminals'].values():terminal(value)
 # Include the full independent proof closure, not only a top-level success flag.
 for path,h in functional['dependencies'].items():
  assert path in clear['dependencies'] and clear['dependencies'][path]==h==sha(path),path
 assert plan['prepared_only'] is True # frozen preparation remains declarative
 return plan,clear,functional
if __name__=='__main__':
 plan,clear,functional=validate_gate()
 print(json.dumps({'gate_passed':True,'candidate':plan['variants']['candidate']['sha256'],'native_runs':0}))
