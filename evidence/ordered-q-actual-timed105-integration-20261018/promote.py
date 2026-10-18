"""Promote only exact tested105 source; retained image identities stay explicit."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess
ROOT=Path('/home/legolas/rook2')
HERE=Path(__file__).resolve().parent
SOURCE=Path('/home/legolas/rook2-work/imp2-actual-timed105-bits-combined-20261018-19a_kn7r')
OLD=Path('/tmp/imp2-admission-combined95-20261018-n0_cyxa7')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:json.loads(p.read_text())
def write(name,value):
    with (HERE/name).open('x') as f:json.dump(value,f,indent=2);f.write('\n')
def main():
    assert sorted(os.sched_getaffinity(0))==[0,1,2,3,4,5,8,9,10,11,12,13]
    evidence=ROOT/'evidence'
    proposal=evidence/'actual-timed105-bits-combined-proposal-20261018'
    manifest=load(proposal/'source-manifest.json')
    files=manifest['files'];assert len(files)==103
    assert all(sha(SOURCE/n)==h for n,h in files.items())
    before={n:sha(ROOT/n) for n in files if (OLD/n).is_file()}
    assert len(before)==99 and all(sha(OLD/n)==h for n,h in before.items()),'Production source differs from tested95'
    assert all(not (ROOT/n).exists() for n in files if n not in before),'Unexpected new source already present'
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    assert head=='663ec6589f5c8b352866e87524a45afe573f52d5'
    summary_path=evidence/'actual-timed105-bits-validation-preparation-20261018/validation-summary.json'
    summary=load(summary_path)
    assert summary['status']=='EXACT105BITS_FRESH_DIAG_AND_NATIVE_REUSE_VALIDATION_PASS'
    assert (summary['native_units_reused'],summary['diagnostic_units_fresh'],summary['operations'],summary['cases_fresh'],summary['whole_files'])==(158,182,105,7519,102)
    assert summary['source_stable'] and summary['all_raw_expected_actual_and_child_exits_independently_reconciled']
    for key in ['diag_actual','reconciliation_actual']:
        assert summary[key]['actual_tool_terminal_observed'] and summary[key]['exit_code']==0
    native_build=evidence/'ordered-q-seeded103-combined-generic-build-20261018'
    diagnostic_build=evidence/'actual-timed105-bits-diagnostic-build-20261018'
    native=load(native_build/'receipt.json');diagnostic=load(diagnostic_build/'receipt.json')
    assert native['source_sha256_before']==native['source_sha256_after']==manifest['native43']
    assert native['tool_sha256_before']==native['tool_sha256_after']==manifest['tools23']
    cold={n.removeprefix('diagnostic/'):h for n,h in manifest['diagnostic37'].items()}
    assert diagnostic['source_sha256_before']==diagnostic['source_sha256_after']==cold
    assert diagnostic['tool_sha256_before']==diagnostic['tool_sha256_after']==manifest['tools23']
    engine=native_build/'rook2-exact';adapter=diagnostic_build/'rook2-diag-exact'
    assert sha(engine)==summary['native_generic_sha256']==native['binary_output']['sha256']
    assert sha(adapter)==summary['adapter_sha256']==diagnostic['binary_output']['sha256']
    pilot=evidence/'ordered-q-seeded103-combined-cpu-pilot-20261018'
    terminal=load(pilot/'tool-terminal.json');independent=load(pilot/'reconcile-tool-terminal.json');analysis=load(pilot/'analysis.json')
    assert all(r['actual_tool_terminal_observed'] and r['exit_code']==0 for r in [terminal,independent])
    assert sha(pilot/'analysis.json')==independent['analysis_sha256']
    assert analysis['complete'] and analysis['percent_lower']>0 and analysis['all_six_observed_ranges_disjoint']
    judgement=evidence/'ordered-q-seeded103-combined-parent-review-20261018/codegen-judgment.json'
    assert load(judgement)['parent_accepts_bounded_codegen']
    changed={n:dict(before=before.get(n),after=h) for n,h in files.items() if before.get(n)!=h}
    assert len(changed)==9,changed
    write('before.json',dict(head=head,source_sha256=before,changed=changed))
    for name in changed:
        destination=ROOT/name;destination.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(SOURCE/name,destination)
    assert all(sha(ROOT/n)==h for n,h in files.items())
    record=dict(source_promoted=True,source=str(SOURCE),source_files=103,changed=changed,
        native43=manifest['native43'],tools23=manifest['tools23'],diagnostic37=manifest['diagnostic37'],
        full_source_sha256=files,head_before=head,source_graph_sha256=summary['source_graph_sha256'],
        validation_summary_sha256=sha(summary_path),native_artifact=str(engine),native_sha256=sha(engine),
        adapter_artifact=str(adapter),adapter_sha256=sha(adapter),native_tests=158,diagnostic_tests=182,
        operations=105,cases=7519,whole_files=102,strict_replays=54,wire_fixtures=8,wire_searches=24,
        cpu_pilot_analysis_sha256=sha(pilot/'analysis.json'),cpu_pilot_percent_lower=analysis['percent_lower'],
        codegen_judgment_sha256=sha(judgement),canonical_rebuild=False,own_pgo_or_full_cost_or_gameplay_qualified=False,
        domain_audit_limit=summary['canonical_domain_limit'],root_scheduler_post_plane_transport_included=False,
        scope='Exact source promotion with named frozen artifact evidence; no canonical path binary rebuild or timing transfer')
    write('integration.json',record)
    print(json.dumps({k:v for k,v in record.items() if k not in ['native43','tools23','diagnostic37','full_source_sha256','changed']}))
if __name__=='__main__':main()
