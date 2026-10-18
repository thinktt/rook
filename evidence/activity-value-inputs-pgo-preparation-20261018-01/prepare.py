"""Metadata/text adaptation only: never imports stage helpers or executes tools."""
from pathlib import Path
import difflib
import hashlib
import json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
OLD=ROOT/'evidence/complete117-pgo-preparation-20261018'
BUILD=ROOT/'evidence/activity-value-inputs-generic-build-20261018-01'
SOURCE=Path('/home/legolas/rook2-work/imp2-activity-value-inputs-20261018-4ea01f85')
OLD_SOURCE='/home/legolas/rook2-work/imp2-complete117-ledger-test-proposal-20261018-9a56f133'
NAMES=['build_stage.py','check.py','guard.py','offline_controls.py','raw_model.py',
       'recheck.mjs','reconcile.py','train.py','verify.py']

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def load(path):return json.loads(Path(path).read_text())
def write(path,value):
    with path.open('x') as stream:
        json.dump(value,stream,indent=2);stream.write('\n')

def main():
    before=load(OLD/'script-pins.json')
    assert set(before)==set(NAMES)
    assert all(sha(OLD/name)==before[name] for name in NAMES)
    receipt=load(BUILD/'receipt.json')
    assert sha(BUILD/'receipt.json')=='18585bc825ae3049fd7ffd3953bade1c8a78df0650d021364a5443d6c8eaf88b'
    assert sha(BUILD/'rook2-exact')==receipt['binary_output']['sha256']=='7cf3980014506970ba8aaf885bcc1c983823307005aaae7efc5d0fdc7a43cd16'
    assert receipt['crate']==str(SOURCE)
    assert receipt['source_sha256_before']==receipt['source_sha256_after']
    assert receipt['tool_sha256_before']==receipt['tool_sha256_after']
    source_map=receipt['source_sha256_before'];tools=receipt['tool_sha256_before']
    assert len(source_map)==46 and len(tools)==23
    for relative,digest in (source_map|tools).items():
        assert sha(SOURCE/relative)==digest
        assert sha(BUILD/'source-before'/relative)==digest
    old_plan=load(OLD/'plan.json')
    assert receipt['toolchain']==old_plan['toolchain']
    assert receipt['rust_flags']==old_plan['base_flags']
    assert receipt['target_triple']==old_plan['target_triple']
    assert receipt['target_cpu']==old_plan['target_cpu']
    assert receipt['cargo_config_sha256_before']==receipt['cargo_config_sha256_after']==old_plan['cargo_config_sha256']
    assert sha(Path(old_plan['merge_tool']).resolve())==old_plan['merge_tool_sha256']
    renames={
        'complete117-pgo-preparation-20261018':HERE.name,
        'complete117-pgo-instrumented-build-20261018':'activity-value-inputs-pgo-instrumented-build-20261018-01',
        'complete117-pgo-training-20261018':'activity-value-inputs-pgo-training-20261018-01',
        'complete117-pgo-use-build-20261018':'activity-value-inputs-pgo-use-build-20261018-01',
        'complete117-pgo-use-check-20261018':'activity-value-inputs-pgo-use-check-20261018-01',
        'complete117-pgo-interruption-wire-20261018':'activity-value-inputs-pgo-interruption-wire-20261018-01',
        'complete117-pgo-reconciliation-20261018':'activity-value-inputs-pgo-reconciliation-20261018-01',
        OLD_SOURCE:str(SOURCE),
        'complete117-own-pgo-validation-no-cpu':'activity-value-inputs-own-pgo-validation-no-cpu',
        'functional_117_accepted':'functional_candidate_accepted',
    }
    def adapt(text):
        for old,new in renames.items():text=text.replace(old,new)
        return text
    delta=[]
    for name in NAMES:
        original=(OLD/name).read_text()
        text=adapt(original)
        if name=='guard.py':
            needle=" assert c['functional_candidate_accepted'] is True\n"
            assert text.count(needle)==1
            text=text.replace(needle,needle+
                " assert c['generic_pilot_advance_accepted'] is True\n"
                " assert c['generic_candidate_sha256']==PLAN['generic_candidate_sha256']\n"
                " assert c['generic_pilot_evidence'] and c['generic_pilot_actual_terminals']\n"
                " for path,digest in c['generic_pilot_evidence'].items():assert sha(path)==digest\n"
                " for path,digest in c['generic_pilot_actual_terminals'].items():assert sha(path)==digest;terminal(path)\n")
        if name=='offline_controls.py':
            needle='functional_candidate_accepted=True,'
            assert text.count(needle)==1
            text=text.replace(needle,needle+
                "generic_pilot_advance_accepted=True,generic_candidate_sha256=g.PLAN['generic_candidate_sha256'],"
                "generic_pilot_evidence={str(g.HERE/'plan.json'):g.sha(g.HERE/'plan.json')},"
                "generic_pilot_actual_terminals={str(terminal):g.sha(terminal)},")
            needle="('functional_candidate_accepted',False),"
            assert text.count(needle)==1
            text=text.replace(needle,needle+
                "('generic_pilot_advance_accepted',False),('generic_candidate_sha256','0'*64),"
                "('generic_pilot_evidence',{}),('generic_pilot_actual_terminals',{}),")
        if name=='reconcile.py':
            text=text.replace('Independent single117 source/profile/artifact/raw reconciliation',
                              'Independent activity-value source/profile/artifact/raw reconciliation')
            text=text.replace("[('complete117',PLAN['source_root'])]",
                              "[('activity-value-inputs',PLAN['source_root'])]")
            needle="  prefix='complete117-pgo'\n  tr=ROOT/f'evidence/{prefix}-training-20261018';ib=ROOT/f'evidence/{prefix}-instrumented-build-20261018';build=ROOT/f'evidence/{prefix}-use-build-20261018';check=ROOT/f'evidence/{prefix}-use-check-20261018';wire=ROOT/f'evidence/{prefix}-interruption-wire-20261018'\n"
            assert text.count(needle)==1
            text=text.replace(needle,"  tr=Path(PLAN['training']);ib=Path(PLAN['instrumented_build']);build=Path(PLAN['use_build']);check=Path(PLAN['use_check']);wire=Path(PLAN['wire'])\n")
            assert 'profile_remerge_command=merge_argv' in text
        if name=='verify.py':text=text.replace('Own exact117 compiler training','Own exact activity-value candidate compiler training')
        assert 'complete117' not in text,(name,'stale complete117 stage binding')
        assert OLD_SOURCE not in text
        (HERE/name).write_text(text)
        delta.extend(difflib.unified_diff(original.splitlines(True),text.splitlines(True),
            fromfile='complete117-audited/'+name,tofile='activity-value-proposed/'+name))
    plan=load(HERE/'plan.json')
    plan['schema']='rook2-activity-value-inputs-own-pgo-plan-v1'
    plan['status']='PREPARATION ONLY; unparsed/unrun; parent review and independent generic advancement required'
    plan['source_root']=str(SOURCE)
    plan['engine_source_sha256']=source_map
    plan['tool_source_sha256']=tools
    plan['generic_candidate_sha256']=receipt['binary_output']['sha256']
    plan['generic_build_receipt']=str(BUILD/'receipt.json')
    plan['generic_build_receipt_sha256']=sha(BUILD/'receipt.json')
    for key in ['instrumented_build','training','use_build','use_check','wire','reconciliation']:
        plan[key]=adapt(plan[key])
        path=Path(plan[key]);assert not path.exists() and not path.is_symlink(),str(path)
    for suffix in ['dev-generic-pgo-generate','dev-generic-pgo-use']:
        assert not (SOURCE/'target'/suffix).exists()
    plan['input_sha256'].update({str(BUILD/'receipt.json'):sha(BUILD/'receipt.json'),
                                 str(BUILD/'rook2-exact'):sha(BUILD/'rook2-exact')})
    plan['method_provenance']={str(OLD/name):before[name] for name in NAMES}
    plan['scope']='Exact activity-value-inputs candidate own profile only; no merged control profile reuse; no CPU comparison, timing, qualification or promotion'
    original=(OLD/'plan.json').read_text()
    text=json.dumps(plan,indent=2)+'\n';(HERE/'plan.json').write_text(text)
    delta.extend(difflib.unified_diff(original.splitlines(True),text.splitlines(True),
        fromfile='complete117-audited/plan.json',tofile='activity-value-proposed/plan.json'))
    commands=adapt((OLD/'commands.md').read_text())
    commands=commands.replace('Parent authorization is absent.',
        'Parent authorization is absent; reviewed generic-pilot advancement is a separate required admission.')
    (HERE/'commands.md').write_text(commands)
    delta.extend(difflib.unified_diff((OLD/'commands.md').read_text().splitlines(True),commands.splitlines(True),
        fromfile='complete117-audited/commands.md',tofile='activity-value-proposed/commands.md'))
    (HERE/'helper-adaptation.patch').write_text(''.join(delta))
    pins={name:sha(HERE/name) for name in NAMES}
    write(HERE/'script-pins.json',pins)
    template=dict(authorized=False,all_conflicting_native_work_terminal=False,
        scope='activity-value-inputs-own-pgo-validation-no-cpu',
        plan_sha256=sha(HERE/'plan.json'),source_root=str(SOURCE),
        prepared_scripts_sha256=pins,functional_candidate_accepted=False,
        generic_pilot_advance_accepted=False,generic_candidate_sha256=plan['generic_candidate_sha256'],
        generic_pilot_evidence={},generic_pilot_actual_terminals={},
        functional_evidence={},actual_terminals={},training_cpu=14,
        sibling15_no_owned_task=False,quiet_window_and_interference_review=None,
        notes='Inert template, not clearance. Parent must bind exact functional receipts plus original generic-pilot result/independent reconciliation and observed terminals before any stage. No timing authority.')
    write(HERE/'execution-clearance.template.json',template)
    assert not (HERE/'execution-clearance.json').exists()
    assert all(sha(OLD/name)==before[name] for name in NAMES)
    assert all(sha(SOURCE/path)==digest for path,digest in (source_map|tools).items())
    result=dict(complete=True,preparation_only=True,script_imports=0,ast_parses=0,
        stage_executions=0,native_engine_runs=0,builds=0,merges=0,tool_version_runs=0,
        source_copies=0,native_source_mutations=0,source_files=46,tool_files=23,
        plan_sha256=sha(HERE/'plan.json'),script_pins_sha256=sha(HERE/'script-pins.json'),
        authority_template_sha256=sha(HERE/'execution-clearance.template.json'),
        helper_delta_sha256=sha(HERE/'helper-adaptation.patch'),
        original_script_pins_sha256=sha(OLD/'script-pins.json'),
        exact_candidate_receipt_sha256=sha(BUILD/'receipt.json'),
        referenced_inputs_unchanged=True,original_helpers_unchanged=True,
        all_future_outputs_and_pgo_targets_absent=True,
        new_helper_hashes=pins,actual_terminal_reported_separately=True)
    write(HERE/'preparation-status.json',result)
    print(json.dumps(result))

if __name__=='__main__':main()
