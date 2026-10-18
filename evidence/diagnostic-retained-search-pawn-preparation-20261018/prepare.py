#!/usr/bin/env python3
# Source/text/archive preparation only; never compile or execute an adapter.
from pathlib import Path
import collections,hashlib,io,json,tarfile,sys
P=Path(__file__).parent;E=P.parent;paths=json.loads((P/'paths.json').read_text());S=Path(paths['source_root']);F=Path(paths['frozen_proposal']);Q=Path(paths['proposal_evidence']);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sys.dont_write_bytecode=True;sys.path.insert(0,str(S/'tools'))
from build import source_snapshot,tool_snapshot

def write(path,value):
 with path.open('x') as f:json.dump(value,f,indent=2);f.write('\n')
def archive(path,files):
 with tarfile.open(path,'x:gz') as t:
  for name,data in files.items():
   m=tarfile.TarInfo(name);m.size=len(data);m.mode=0o644;t.addfile(m,io.BytesIO(data))
 with tarfile.open(path,'r:gz') as t:actual={m.name:hashlib.sha256(t.extractfile(m).read()).hexdigest() for m in t if m.isfile()}
 assert actual=={k:hashlib.sha256(v).hexdigest() for k,v in files.items()}
m=json.loads((Q/'proposal-source-sha256.json').read_text());assert {k:sha(S/k) for k in m}=={k:sha(F/k) for k in m}==m
native=source_snapshot(S);tools=tool_snapshot(S);adapter=source_snapshot(S/'diagnostic');reference=Path(paths['native_build_reference']);r=json.loads(reference.read_text());assert native==r['source_sha256_before']==r['source_sha256_after'] and tools==r['tool_sha256_before']==r['tool_sha256_after']
assert len(native)==43 and len(tools)==23 and len(adapter)==30
archive(P/'prepared-source-closure.tar.gz',{k:(S/k).read_bytes() for k in m});archive(P/'prepared-adapter.tar.gz',{k:(S/'diagnostic'/k).read_bytes() for k in adapter})
inventory=json.loads((Q/'fixture-inventory.json').read_text());fixtures={x['path']:x['sha256'] for x in inventory};assert len(fixtures)==82
ops=collections.Counter();ids=[]
for name,h in fixtures.items():
 path=Path(name);assert sha(path)==h;doc=json.loads(path.read_text());assert doc['version']==1
 for case in doc['cases']:ids.append(case['id']);ops[case['request']['operation']]+=1
assert len(ids)==len(set(ids))==6151 and len(ops)==87
archive(P/'exact-inputs.tar.gz',{Path(k).name:Path(k).read_bytes() for k in fixtures})
(P/'fixture-inventory.json').write_bytes((Q/'fixture-inventory.json').read_bytes());(P/'whole-fixture-case-map.json').write_bytes((Q/'whole-fixture-case-map.json').read_bytes())
V=E/'quiescence-evaluation-default-validation-20261018';evidence=[reference,reference.parent/'tool-terminal.json',V/'native-verification.json',V/'native-tool-terminal.json',V/'native-actual-terminal.json',V/'identity.json',V/'tool-terminal.json',V/'finalizer-actual-terminal.json',V/'ordinary-check-02/identity.json',V/'ordinary-check-02/tool-terminal.json',V/'strict-wire-retry-actual-terminal.json',V/'interruption-wire-02/receipt.json']
plan={'status':'frozen87 adapter plan; parent pilot clearance recorded; untimed execution next','source_root':str(S),'frozen_proposal':str(F),'proposal_manifest_sha256':sha(Q/'proposal-source-sha256.json'),'expected_unit_tests':126,'expected_native_unit_tests':142,'expected_case_count':6151,'expected_operation_count':87,'fixture_file_count':82,'partial_files':0,'duplicate_case_ids':0,'operations':sorted(ops),'operation_case_counts':dict(ops),'fixtures':fixtures,'new_operations':['evaluation.retainedPawnSubtotal','evaluation.searchPawnSequence'],'new_cases':862,'new_result_records':25992,'fixture_selection':'Every case from82 whole original official files; metadata headers unchanged; no partial files or duplicate IDs','native_build_reference':str(reference),'inherited_native_binary_sha256':r['binary_output']['sha256'],'native_unit_evidence':str(V/'native-verification.json'),'ordinary_identity':str(V/'ordinary-check-02/identity.json'),'native_reuse_evidence_sha256':{str(p):sha(p) for p in evidence},'adapter_preparation':'source-preparation.json','mutable_root_tool_dependency':False,'authorization':'Parent explicit pilot92704 actualterminal0/d687c2, independent35b97e passes60; untimed DIAG only; no ordinary native rebuild/replays/CPU timing/PGO/profilers','raw_recording':'Original run.mjs invokes record_case.py; one adapter child per original case. Recorder preserves literal stdin/stdout/stderr and child exit/affinity. Independent reconciliation compares full original expected JSON to both raw output and official runner actual.'}
write(P/'plan.json',plan)
write(P/'source-preparation.json',{'full_source_sha256':m,'native_source_sha256':native,'tool_source_sha256':tools,'adapter_source_sha256':adapter,'archive':'prepared-adapter.tar.gz','archive_sha256':sha(P/'prepared-adapter.tar.gz'),'source_closure_archive':'prepared-source-closure.tar.gz','source_closure_archive_sha256':sha(P/'prepared-source-closure.tar.gz'),'exact_inputs_archive_sha256':sha(P/'exact-inputs.tar.gz'),'planned_verifier_sha256':sha(P/'run.py'),'planned_reconciler_sha256':sha(P/'reconcile.py'),'raw_recorder_sha256':sha(P/'record_case.py'),'native_reference':str(reference),'native_reference_sha256':sha(reference),'proposal_manifest_sha256':sha(Q/'proposal-source-sha256.json')})
print(json.dumps({'source_root':str(S),'native':len(native),'tools':len(tools),'adapter':len(adapter),'units':126,'cases':6151,'operations':87,'whole_files':82}))
