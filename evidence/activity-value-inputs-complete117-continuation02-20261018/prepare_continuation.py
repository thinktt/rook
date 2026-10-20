"""Offline partial-proof and inert continuation preparation; no subprocess/native jobs."""
from pathlib import Path
import ast,difflib,hashlib,json,sys,tarfile
sys.dont_write_bytecode=True
from guard import check_sources,check_dependencies,check_partial
HERE=Path(__file__).resolve().parent
OLD=Path('/home/legolas/rook2/evidence/activity-value-inputs-complete117-preparation-20261018-01')
sha=lambda path:hashlib.sha256(Path(path).read_bytes()).hexdigest()
def write(name,value):
 with (HERE/name).open('x') as f:json.dump(value,f,indent=2);f.write('\n')
def main():
 assert not (HERE/'validation-plan.json').exists()
 original=json.loads((OLD/'validation-plan.json').read_text());plan=json.loads(json.dumps(original))
 plan.update(status='CONTINUATION02_PREPARED_HOLD_CORPUS',execution_authorized=False,prepared01=str(OLD),diagnostic_crate_tools_sha256={},metadata_revision='continuation02')
 plan['partial01']=dict(diagnostic=str(OLD/'diagnostic'),build=str(OLD/'diagnostic-build'),adapter_sha256='0e5eb3e074e81835ae791f00b0f98c838cbd9c5cdf01ef7f5b74965a355a9e80',unit_sha256='e9a720a631c572d327bca9df95f07a0aac90757cecc8685fa316d89d66296aae',failed_outer=dict(session_id=20878,initial_chunk_id='e7032c',terminal_chunk_id='588af9',exit_code=1))
 plan['output']['diagnostic']=str(HERE/'corpus');plan['output']['reconciliation']=str(HERE/'reconciliation')
 plan['harness_sha256']={name:sha(HERE/name) for name in ['guard.py','run_corpus.py','record_case.py','reconcile.py','finalize.py']}
 pins=dict(plan['immutable_dependencies'])
 # Pin originals, failed outer, green children and exact archive/image. Never
 # import original guard or reuse its original permission as continuation authority.
 for name in ['validation-plan.json','execution-clearance.json','prepared.json','source-proof.json','archive-verification.json','source-112.tar.gz','official-inputs-115.tar.gz','guard.py','stage.py','record_case.py','reconcile.py','finalize.py','execution-freeze/verification.json','execution-freeze/tool-terminal.json','execution-freeze/source-frozen.tar.gz','diagnostic/verification.json','diagnostic/tool-terminal.json','diagnostic/unit-bin/rook2-diag/unit-exact','diagnostic-build/receipt.json','diagnostic-build/archive-receipt.json','diagnostic-build/verified-source-before.tar.gz','diagnostic-build/rook2-diag-exact','diagnostic-build/child-build-terminal.json']:
  pins[str(OLD/name)]=sha(OLD/name)
 for path in (OLD/'diagnostic').iterdir():
  if path.is_file():pins[str(path)]=sha(path)
 for path in (OLD/'diagnostic-build').iterdir():
  if path.is_file() and path.suffix in ['.json','.stdout','.stderr']:pins[str(path)]=sha(path)
 plan['immutable_dependencies']=pins
 check_sources(plan);check_dependencies(plan);check_partial(plan)
 assert len(plan['tools_sha256'])==23 and plan['diagnostic_crate_tools_sha256']=={}
 assert not Path(plan['output']['diagnostic']).exists() and not Path(plan['output']['reconciliation']).exists()
 assert (HERE/'record_case.py').read_bytes()==(OLD/'record_case.py').read_bytes()
 for name in plan['harness_sha256']:ast.parse((HERE/name).read_text(),filename=name)
 # The reused43-file diagnostic archive is exact; root native/tools remain in
 # separately checked112-source snapshots and original freeze archive.
 with tarfile.open(OLD/'execution-freeze/source-frozen.tar.gz','r:gz') as t:
  members={m.name:hashlib.sha256(t.extractfile(m).read()).hexdigest() for m in t if m.isfile()}
 assert members==plan['source_sha256'] and len(members)==112
 partial=dict(failed01_outer_preserved=plan['partial01']['failed_outer'],failed01_complete=False,green_unit_count=209,green_unit_sha256=plan['partial01']['unit_sha256'],green_build_and_archive_children_exit0=True,adapter_sha256=plan['partial01']['adapter_sha256'],old_corpus_never_started=True,diagnostic_crate_tools_count=0,root_tools_separately_pinned_count=23,root_native_count=46,cold_count=43,source112_exact=True,source_graph_sha256=plan['source_graph_sha256'],compiler_flags_equal_verified_generic=True,original_native178_strict54_eightwire_reuse_unchanged=True,no_source_or_fixture_changes=True,no_new_native_or_compiler_jobs=True)
 write('partial-proof.json',partial);write('validation-plan.json',plan)
 c=json.loads((OLD/'execution-clearance.json').read_text());c.update(authorized=False,scope='activity-value-inputs-complete117-corpus-continuation02',plan_sha256=sha(HERE/'validation-plan.json'),metadata_revision='continuation02',note='HOLD for parent review/new continuation clearance; old01 authorization does not authorize this corpus attempt')
 write('execution-clearance.json',c)
 # Minimal correction shown independently of removal of compilation/replay paths.
 patch=[]
 for name in ['stage.py','reconcile.py']:
  before=(OLD/name).read_text();after=before.replace("br['tool_sha256_before']==br['tool_sha256_after']==plan['tools_sha256']", "br['tool_sha256_before']==br['tool_sha256_after']=={} #diagnostic crate-local tools; root23 separately pinned")
  assert before!=after
  patch.append(''.join(difflib.unified_diff(before.splitlines(keepends=True),after.splitlines(keepends=True),fromfile='attempt01/'+name,tofile='scope-corrected-reference/'+name)))
 (HERE/'crate-tool-scope-correction.patch').write_text(''.join(patch))
 patch=[]
 for before,after in [('guard.py','guard.py'),('stage.py','run_corpus.py'),('record_case.py','record_case.py'),('reconcile.py','reconcile.py'),('finalize.py','finalize.py')]:
  patch.append(''.join(difflib.unified_diff((OLD/before).read_text().splitlines(keepends=True),(HERE/after).read_text().splitlines(keepends=True),fromfile='attempt01/'+before,tofile='continuation02/'+after)))
 (HERE/'continuation-adaptation.patch').write_text(''.join(patch))
 prefix=['/usr/bin/taskset','-c','0-5,8-13','/usr/bin/env','TMPDIR=/home/legolas/rook2-build-tmp','PYTHONDONTWRITEBYTECODE=1','/usr/bin/python3']
 write('commands.json',dict(authorized=False,sequence=[prefix+[str(HERE/name)] for name in ['run_corpus.py','reconcile.py','finalize.py']],actual_outer_terminal_required_between_each=True,build_unit_or_replay_commands_present=False))
 write('prepared.json',dict(status='CONTINUATION02_SOURCE_PREPARED_NATIVE_HOLD',source_graph_sha256=plan['source_graph_sha256'],plan_sha256=sha(HERE/'validation-plan.json'),partial_proof_sha256=sha(HERE/'partial-proof.json'),same_adapter_sha256=plan['partial01']['adapter_sha256'],unit209_reused=True,no_build_or_unit_or_native178_or_strict_wire_repetition=True,whole_files=115,operations=117,unique_cases=7673,execution_authorized=False,harness_sha256=plan['harness_sha256']))
 check_sources(plan);check_dependencies(plan)
 print(json.dumps(dict(prepared=True,failed01_outer_exit=1,green209_reused=True,same_adapter=plan['partial01']['adapter_sha256'],source112_graph=plan['source_graph_sha256'],corpus_unstarted=True,execution_authorized=False)))
if __name__=='__main__':main()
