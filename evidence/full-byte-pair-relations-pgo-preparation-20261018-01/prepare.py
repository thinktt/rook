"""Metadata/text adaptation only; never imports stage helpers or executes tools."""
from pathlib import Path
import difflib,hashlib,json
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1];E=ROOT/'evidence'
OLD=E/'activity-value-inputs-pgo-preparation-20261018-01'
BUILD=E/'full-byte-pair-relations-generic-build-20261018-01'
PRO=E/'full-byte-pair-relations-proposal-20261018-01'
REF=E/'activity-value-inputs-generic-build-20261018-01'
PGOREF=E/'activity-value-inputs-pgo-use-build-20261018-01'
DECL=E/'full-byte-pair-relations-pgo-cpu-plan-20261018-01/plan.json'
GENERIC=E/'full-byte-pair-relations-cpu-independent-preparation-20261018-01'
SOURCE=Path('/home/legolas/rook2-work/imp2-full-byte-pair-relations-20261018-oc3es5rp')
OLD_SOURCE='/home/legolas/rook2-work/imp2-activity-value-inputs-20261018-4ea01f85'
NAMES=['build_stage.py','check.py','guard.py','offline_controls.py','raw_model.py','recheck.mjs','reconcile.py','train.py','verify.py']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_text())
def write(p,v):
 with p.open('x') as f:json.dump(v,f,indent=2);f.write('\n')
def main():
 before=load(OLD/'script-pins.json');assert set(before)==set(NAMES)
 assert all(sha(OLD/n)==before[n] for n in NAMES)
 assert sha(DECL)=='571b4cf361023fd791b363d484d9c7ff9fc7722da9a39297b863365e86a874df'
 assert sha(GENERIC/'independent-reconciliation.json')=='9209fdd94bb4e82c61b431d7c2f2615211e2f0659b49528a5b5c4628716334a8'
 gp=load(GENERIC/'independent-reconciliation.json');gt=load(GENERIC/'tool-terminal.json')
 assert gp['complete'] and gp['advance_rule_satisfied'] and gp['original_checkReplay']==70 and gp['normal_lifetimes']==70
 assert gt['actual_tool_terminal_observed'] and gt['exit_code']==0 and gt['terminal_chunk_id']=='6cc934'
 r=load(BUILD/'receipt.json');ref=load(REF/'receipt.json');pr=load(PGOREF/'receipt.json');m=load(PRO/'source-manifest.json')
 assert sha(BUILD/'rook2-exact')==r['binary_output']['sha256']=='948c336c70b8e803b982cc88ea1f0cf3791c172c2c6f3fd090bb69bce1a98219'
 assert sha(REF/'rook2-exact')==ref['binary_output']['sha256']=='7cf3980014506970ba8aaf885bcc1c983823307005aaae7efc5d0fdc7a43cd16'
 assert sha(PGOREF/'rook2-exact')==pr['binary_output']['sha256']=='d5ee1f3f7258f152c0a9c50664855c46f6b631e611a85bdfdae07f509654decc'
 assert r['crate']==str(SOURCE)==m['path']
 assert r['source_sha256_before']==r['source_sha256_after']==m['native46']
 assert r['tool_sha256_before']==r['tool_sha256_after']==m['tools23']
 assert ref['source_sha256_before']==ref['source_sha256_after']==pr['source_sha256_before']==pr['source_sha256_after']
 assert ref['tool_sha256_before']==ref['tool_sha256_after']==pr['tool_sha256_before']==pr['tool_sha256_after']==m['tools23']
 assert [n for n,h in m['native46'].items() if ref['source_sha256_before'][n]!=h]==['src/influence.rs','src/relation_table.rs']
 assert m['source_graph_sha256']=='6aa2f8a1f81bc9c6b6f4ba26b987a259bca648a61a7b052f7d1166fcb1ea9b50'
 assert len(m['native46'])==46 and len(m['tools23'])==23
 for name,h in m['source69'].items():
  assert sha(SOURCE/name)==h==sha(BUILD/'source-before'/name)
 oldplan=load(OLD/'plan.json')
 assert r['toolchain']==ref['toolchain']==pr['toolchain']==oldplan['toolchain']
 assert r['rust_flags']==ref['rust_flags']==oldplan['base_flags']==['-C','target-cpu=x86-64']
 assert r['target_triple']==oldplan['target_triple'] and r['target_cpu']==oldplan['target_cpu']
 assert r['cargo_config_sha256_before']==r['cargo_config_sha256_after']==oldplan['cargo_config_sha256']=={}
 assert sha(Path(oldplan['merge_tool']).resolve())==oldplan['merge_tool_sha256']
 def adapt(text):return text.replace('activity-value-inputs-pgo-','full-byte-pair-relations-pgo-').replace(OLD_SOURCE,str(SOURCE)).replace('activity-value-inputs-own-pgo-validation-no-cpu','full-byte-pair-relations-own-pgo-validation-no-cpu').replace('Independent activity-value source/profile/artifact/raw reconciliation','Independent full-byte-pair source/profile/artifact/raw reconciliation').replace("[('activity-value-inputs',PLAN['source_root'])]","[('full-byte-pair-relations',PLAN['source_root'])]").replace('Own exact activity-value candidate compiler training','Own exact full-byte-pair candidate compiler training')
 delta=[]
 for name in NAMES:
  original=(OLD/name).read_text();text=adapt(original)
  assert OLD_SOURCE not in text and 'activity-value-inputs' not in text,(name,'stale active trial binding')
  with (HERE/name).open('x') as f:f.write(text)
  delta.extend(difflib.unified_diff(original.splitlines(True),text.splitlines(True),fromfile='activity-audited/'+name,tofile='full-byte-pair-proposed/'+name))
 plan=load(OLD/'plan.json')
 plan.update(schema='rook2-full-byte-pair-relations-own-pgo-plan-v1',status='PREPARATION ONLY; stages unrun; parent review and explicit execution clearance required',source_root=str(SOURCE),engine_source_sha256=m['native46'],tool_source_sha256=m['tools23'],generic_candidate_sha256=r['binary_output']['sha256'],generic_build_receipt=str(BUILD/'receipt.json'),generic_build_receipt_sha256=sha(BUILD/'receipt.json'),source_manifest_path=str(PRO/'source-manifest.json'),source_manifest_sha256=sha(PRO/'source-manifest.json'),source_graph_sha256=m['source_graph_sha256'])
 for key in ['instrumented_build','training','use_build','use_check','wire','reconciliation']:
  plan[key]=adapt(plan[key]);assert not Path(plan[key]).exists() and not Path(plan[key]).is_symlink()
 for suffix in ['dev-generic-pgo-generate','dev-generic-pgo-use']:assert not (SOURCE/'target'/suffix).exists()
 pins_to_add=[BUILD/'receipt.json',BUILD/'rook2-exact',BUILD/'archive-receipt.json',BUILD/'verified-source-before.tar.gz',REF/'archive-receipt.json',REF/'verified-source-before.tar.gz',PGOREF/'receipt.json',PGOREF/'rook2-exact',PGOREF/'archive-receipt.json',PRO/'source-manifest.json',PRO/'source-proof.json',PRO/'review.md',PRO/'proposal.patch',DECL,GENERIC/'independent-reconciliation.json',GENERIC/'tool-terminal.json',E/'full-byte-pair-relations-independent-preparation-20261018-01/independent-verification.json',E/'full-byte-pair-relations-independent-preparation-20261018-01/tool-terminal.json',E/'full-byte-pair-relations-codegen-review-20261018-01/review-summary.json',E/'full-byte-pair-relations-codegen-review-20261018-01/review.md',E/'full-byte-pair-relations-codegen-review-20261018-01/tool-terminal.json',Path('/usr/bin/node'),Path('/usr/bin/python3')]
 plan['input_sha256'].update({str(p):sha(p) for p in pins_to_add})
 plan['method_provenance']={str(OLD/n):before[n] for n in NAMES}
 plan['scope']='Exact full-byte-pair own profile only; activity retained and pawn fusion excluded; no activity/control/117 profile transfer; no CPU comparison/timing/qualification/promotion'
 plan['future_cpu_predeclaration']={'path':str(DECL),'sha256':sha(DECL),'rule':load(DECL)['advance_rule'],'scope':'Later separate matched own-PGO70 only; this pipeline has no timing launch authority'}
 plan['baseline_generic']={'path':str(REF/'rook2-exact'),'sha256':sha(REF/'rook2-exact')}
 plan['baseline_own_pgo']={'path':str(PGOREF/'rook2-exact'),'sha256':sha(PGOREF/'rook2-exact'),'source_equals_baseline_generic':True,'profile_reused':False}
 write(HERE/'plan.json',plan)
 delta.extend(difflib.unified_diff((OLD/'plan.json').read_text().splitlines(True),(HERE/'plan.json').read_text().splitlines(True),fromfile='activity-audited/plan.json',tofile='full-byte-pair-proposed/plan.json'))
 commands=adapt((OLD/'commands.md').read_text());(HERE/'commands.md').write_text(commands)
 delta.extend(difflib.unified_diff((OLD/'commands.md').read_text().splitlines(True),commands.splitlines(True),fromfile='activity-audited/commands.md',tofile='full-byte-pair-proposed/commands.md'))
 delta.extend(difflib.unified_diff((OLD/'prepare.py').read_text().splitlines(True),Path(__file__).read_text().splitlines(True),fromfile='activity-audited/prepare.py',tofile='full-byte-pair-proposed/prepare.py'))
 (HERE/'helper-adaptation.patch').write_text(''.join(delta))
 pins={n:sha(HERE/n) for n in NAMES};write(HERE/'script-pins.json',pins)
 template=dict(authorized=False,all_conflicting_native_work_terminal=False,scope='full-byte-pair-relations-own-pgo-validation-no-cpu',plan_sha256=sha(HERE/'plan.json'),source_root=str(SOURCE),prepared_scripts_sha256=pins,functional_candidate_accepted=False,generic_pilot_advance_accepted=False,generic_candidate_sha256=plan['generic_candidate_sha256'],generic_pilot_evidence={},generic_pilot_actual_terminals={},functional_evidence={},actual_terminals={},training_cpu=14,sibling15_no_owned_task=False,quiet_window_and_interference_review=None,notes='Inert template, not clearance. Parent binds actual functional/backend/generic70 evidence and terminals; no CPU timing authority.')
 write(HERE/'execution-clearance.template.json',template)
 write(HERE/'tool-terminal.template.json',load(OLD/'tool-terminal.template.json'))
 assert not (HERE/'execution-clearance.json').exists()
 assert all(sha(OLD/n)==before[n] for n in NAMES)
 assert all(sha(SOURCE/n)==h for n,h in m['source69'].items())
 assert all(sha(p)==h for p,h in plan['input_sha256'].items())
 unchanged=[n for n in NAMES if sha(OLD/n)==sha(HERE/n)]
 result=dict(complete=True,preparation_only=True,source_files=46,tool_files=23,source69_graph_sha256=m['source_graph_sha256'],source_copies=0,source_mutations=0,stage_executions=0,native_engine_runs=0,builds=0,profile_merges=0,tool_version_runs=0,script_imports=0,ast_parses=0,offline_controls_run=False,plan_sha256=sha(HERE/'plan.json'),script_pins_sha256=sha(HERE/'script-pins.json'),authority_template_sha256=sha(HERE/'execution-clearance.template.json'),helper_delta_sha256=sha(HERE/'helper-adaptation.patch'),prepare_sha256=sha(Path(__file__)),new_helper_hashes=pins,unchanged_helpers=unchanged,original_helpers_unchanged=True,all_future_outputs_and_pgo_targets_absent=True,actual_terminal_reported_separately=True)
 write(HERE/'preparation-status.json',result);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
