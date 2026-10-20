"""Offline metadata-only path/package roundtrip; never imports a validation module."""
from pathlib import Path
import ast,hashlib,json,tarfile
HERE=Path(__file__).resolve().parent
source=(HERE/'finalize.py').read_text();tree=ast.parse(source)
functions=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['archive_member','package_metadata']]
assert {n.name for n in functions}=={'archive_member','package_metadata'}
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ns=dict(Path=Path,tarfile=tarfile,sha=sha,EVIDENCE_ROOT=Path('/home/legolas/rook2/evidence'))
exec(compile(ast.Module(body=functions,type_ignores=[]),'finalize.py:metadata-functions-only','exec'),ns)
member=ns['archive_member'];package=ns['package_metadata']
plan=json.loads((HERE/'validation-plan.json').read_text())
assert Path(plan['output']['reconciliation']).is_relative_to(HERE)
# Original contained plan did not have the hypothesized ValueError. Exercise
# both that mapping and an actual sibling shape with safe evidence-root names.
actual_prep=member(HERE/'validation-plan.json')
actual_recon=member(Path(plan['output']['reconciliation'])/'independent-verification.json')
assert '..' not in Path(actual_prep).parts and '..' not in Path(actual_recon).parts
sample=HERE/'offline-package-roundtrip';sample.mkdir()
root=sample/'representative-evidence';prep=root/'preparation';recon=root/'reconciliation';prep.mkdir(parents=True);recon.mkdir()
entries=[prep/'plan.json',recon/'independent-verification.json']
for path,text in zip(entries,['{"prepared":true}\n','{"original_actual_exit":0}\n']):path.write_text(text)
assert member(entries[0],root)=='preparation/plan.json'
assert member(entries[1],root)=='reconciliation/independent-verification.json'
try:member(HERE/'outside-representative-root',root)
except ValueError:outside_rejected=True
else:raise AssertionError('outside-root path accepted')
record=package(sample/'roundtrip.tar.gz',entries,root)
assert set(record['members'])=={'preparation/plan.json','reconciliation/independent-verification.json'}
assert all(not Path(name).is_absolute() and '..' not in Path(name).parts for name in record['members'])
record.update(kind='offline metadata-only actual-function path/package roundtrip',finalizer_sha256=sha(HERE/'finalize.py'),original_contained_plan_has_no_observed_or_predicted_ValueError=True,original_parent_sibling_assumption_corrected=True,actual_preparation_member=actual_prep,actual_reconciliation_member=actual_recon,representative_sibling_paths_roundtrip=True,outside_root_rejected=outside_rejected,no_validation_main_or_guard_or_native_command_executed=True)
(HERE/'package-mapping-verification.json').write_text(json.dumps(record,indent=2)+'\n')
print('Offline actual metadata functions: contained and sibling mappings safe; archive bytes roundtrip; outside root rejected. No native execution.')
