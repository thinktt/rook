#!/usr/bin/env python3
"""Source-only freeze; never invokes a compiler, adapter, engine or profiler."""
from pathlib import Path
import collections,datetime,difflib,hashlib,json,os,platform,re,shutil,tarfile
E=Path(__file__).resolve().parent
paths=json.loads((E/'paths.json').read_text())
BASE=Path(paths['base']);SOURCE=Path(paths['source'])
def sha(data):return hashlib.sha256(data).hexdigest()
def identity(path):return sha(path.read_bytes())
def emit(name,value):(E/name).write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
base=json.loads((E/'base-source-sha256.json').read_text())
assert all(identity(BASE/name)==value for name,value in base.items()),'Frozen88 source changed'
files=sorted(set(base)|{'diagnostic/src/boundary_admission.rs'})
current={name:identity(SOURCE/name) for name in files}
changed=[name for name in files if current[name]!=base.get(name)]
native=sorted(name for name in files if name.startswith('src/') or name in ['Cargo.toml','Cargo.lock'])
adapter=sorted(name for name in files if name.startswith('diagnostic/'))
tools=sorted(name for name in files if name.startswith('tools/'))
assert (len(native),len(adapter),len(tools),len(files))==(43,32,23,98)
assert len(changed)==6
native_changed=[name for name in changed if name in native]
adapter_changed=[name for name in changed if name in adapter]
assert len(native_changed)==3 and len(adapter_changed)==3
shared=json.loads((E/'shared-native-seams-v2-manifest.json').read_text())
assert identity(E/'shared-native-seams-v2.patch')==shared['sha256']
for name,entry in shared['files'].items():assert identity(E/'shared-prerequisite'/name)==entry['proposal']
def diff(names,older):
    result=''
    for name in names:
        before=older/name;after=SOURCE/name
        a=before.read_text().splitlines(True) if before.exists() else []
        b=after.read_text().splitlines(True)
        result+=''.join(difflib.unified_diff(a,b,fromfile='a/'+name if before.exists() else '/dev/null',tofile='b/'+name))
    return result
for filename,names,older in [('proposal.patch',changed,BASE),('adapter.patch',adapter_changed,BASE),('native-full.patch',native_changed,BASE),('native-dependent.patch',native_changed,E/'shared-prerequisite')]:
    (E/filename).write_text(diff(names,older))
for name in files:
    dest=E/'proposal-source'/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(SOURCE/name,dest)
with tarfile.open(E/'prepared-source.tar.gz','w:gz') as archive:
    for name in files:archive.add(SOURCE/name,arcname=name,recursive=False)
manifest={'files':current,'native43':{name:current[name] for name in native},'diagnostic32':{name:current[name] for name in adapter},'tools23':{name:current[name] for name in tools}}
for group in ['files','native43','diagnostic32','tools23']:
    manifest[group+'_graph_sha256']=sha(json.dumps(manifest[group],sort_keys=True,separators=(',',':')).encode())
emit('source-manifest.json',manifest)
contracts=['draw-boundary.md','move-reversal.md','mate-leaf.md','repetition-admission.md','cutoff-memory.md','search-candidate-order.md','position-setup.md','ordinary-iterations.md']
emit('contract-manifest.json',{str(Path('/home/legolas/king-spec/spec')/name):identity(Path('/home/legolas/king-spec/spec')/name) for name in contracts})
selection=json.loads((E/'selection.json').read_text());whole=json.loads((E/'whole-fixture-case-map.json').read_text())
assert (whole['case_count'],whole['operation_count'],whole['whole_files'])==(6978,92,86)
new_tests={name:re.findall(r'#\[test\]\s*fn\s+(\w+)',(SOURCE/name).read_text()) for name in changed if name.endswith('.rs')}
base_tests={name:re.findall(r'#\[test\]\s*fn\s+(\w+)',(BASE/name).read_text()) if (BASE/name).exists() else [] for name in new_tests}
added_tests={name:[test for test in names if test not in base_tests[name]] for name,names in new_tests.items()}
added_tests={name:tests for name,tests in added_tests.items() if tests}
assert sum(len(tests) for name,tests in added_tests.items() if name.startswith('diagnostic/'))==6
assert sum(len(tests) for name,tests in added_tests.items() if name.startswith('src/'))==4
emit('test-source-plan.json',{'executed':False,'compiled':False,'new_tests':added_tests,'shared_native_tests':2,'own_native_tests':2,'own_diagnostic_tests':6,'expected_native_total':149,'expected_diagnostic_total':139,'accepted_native_baseline_total':145,'accepted_diagnostic_baseline_total':133})
artifacts=['proposal.patch','adapter.patch','native-full.patch','native-dependent.patch','shared-native-seams-v2.patch','shared-native-seams-v2-manifest.json','prepared-source.tar.gz','source-manifest.json','base-source-sha256.json','fixture-inventory.json','selection.json','whole-fixture-case-map.json','contract-manifest.json','test-source-plan.json','schema-design.md','native-owner-map.md','review.md','freeze.py','bookkeeping-failures.json','static-review-correction.json']
prepared={'status':'frozen source-only; no compiler/test/engine/profiler or binary inspection',
 'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'base':str(BASE),'source':str(SOURCE),'evidence':str(E),
 'affinity':sorted(os.sched_getaffinity(0)),'python':platform.python_version(),
 'source_counts':{'native':43,'diagnostic':32,'tools':23,'whole':98},'changed_files':changed,
 'full_source_graph_sha256':manifest['files_graph_sha256'],'native43_graph_sha256':manifest['native43_graph_sha256'],
 'diagnostic32_graph_sha256':manifest['diagnostic32_graph_sha256'],'tools23_graph_sha256':manifest['tools23_graph_sha256'],
 'shared_prerequisite_sha256':shared['sha256'],'fixture_plan':{'operations':92,'cases':6978,'whole_files':86,'new_operations':selection['new_operations'],'new_cases':817,'partial_files':0,'duplicate_ids':0,'duplicate_fixture_indices':0,'original_metadata_headers_preserved':True},
 'later_validation_plan':{'native_total_expected':149,'diagnostic_total_expected':139,'case_count':6978,'operation_count':92,'requires_parent_execution_assignment':True,'native_baseline_not_reusable_after_changes':True},
 'artifacts':{name:identity(E/name) for name in artifacts},'base_stable_after':all(identity(BASE/name)==value for name,value in base.items()),'source_stable_after':all(identity(SOURCE/name)==value for name,value in current.items())}
emit('prepared.json',prepared)
print(json.dumps({'source':str(SOURCE),'source_graph':prepared['full_source_graph_sha256'],'native43':prepared['native43_graph_sha256'],'adapter32':prepared['diagnostic32_graph_sha256'],'tools23':prepared['tools23_graph_sha256'],'prepared_sha256':identity(E/'prepared.json'),'patches':{name:prepared['artifacts'][name] for name in ['proposal.patch','adapter.patch','native-dependent.patch']},'tests_unrun':added_tests,'source_stable':prepared['source_stable_after'],'base_stable':prepared['base_stable_after']},indent=2))
