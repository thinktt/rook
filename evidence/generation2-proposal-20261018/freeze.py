#!/usr/bin/env python3
"""Source/input freeze only, after parent's archive clearance; no native execution."""
from pathlib import Path
import collections,datetime,difflib,hashlib,json,os,platform,re,shutil,tarfile
E=Path(__file__).resolve().parent
paths=json.loads((E/'paths.json').read_text());BASE=Path(paths['base']);SOURCE=Path(paths['source'])
BASE_E=Path('/home/legolas/rook2/evidence/admission-combined95-proposal-20261018')
def sha(data):return hashlib.sha256(data).hexdigest()
def h(path):return sha(path.read_bytes())
def emit(name,obj):(E/name).write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')
base=json.loads((E/'base-source-manifest.json').read_text());assert len(base)==99
assert h(E/'base-source-manifest.json')==paths['base_manifest_sha256']
assert all(h(BASE/name)==value for name,value in base.items()),'Frozen95 source changed'
files=sorted(set(base)|{'diagnostic/src/generation.rs'});current={name:h(SOURCE/name) for name in files}
changed=[name for name in files if current[name]!=base.get(name)]
assert len(files)==100 and set(changed)=={'src/movegen.rs','diagnostic/src/admission.rs','diagnostic/src/candidate_order.rs','diagnostic/src/quiescence_evaluation.rs','diagnostic/src/main.rs','diagnostic/src/generation.rs'}
native=[name for name in files if name.startswith('src/') or name in ['Cargo.toml','Cargo.lock']]
cold=[name for name in files if name.startswith('diagnostic/')];tools=[name for name in files if name.startswith('tools/')]
assert (len(native),len(cold),len(tools))==(43,34,23)
def patch(names):
    output=''
    for name in names:
        a=(BASE/name).read_text().splitlines(True) if (BASE/name).exists() else []
        b=(SOURCE/name).read_text().splitlines(True)
        output+=''.join(difflib.unified_diff(a,b,fromfile='a/'+name if (BASE/name).exists() else '/dev/null',tofile='b/'+name))
    return output
for name,names in [('proposal.patch',changed),('native.patch',['src/movegen.rs']),('cold.patch',[name for name in changed if name.startswith('diagnostic/')])]:
    (E/name).write_text(patch(names))
# Native source proof: only insertions at the approved query and cfg-test sites.
old=(BASE/'src/movegen.rs').read_text();new=(SOURCE/'src/movegen.rs').read_text()
a=new.index('/// Semantic current-side classification, saturated at two checkers.')
b=new.index('/// Project just the fields needed',a)
stripped=new[:a]+new[b:]
a=stripped.index('    #[test]\n    fn semantic_check_classification_reports_none_single_and_saturated_double()')
b=stripped.index('    #[test]',a+len('    #[test]'))
stripped=stripped[:a]+stripped[b:]
assert stripped==old,'Native generator/default source changed beyond approved insertions'
emit('native-source-proof.json',{'base_movegen_sha256':base['src/movegen.rs'],'proposal_movegen_sha256':current['src/movegen.rs'],'stripped_query_and_cfg_test_sha256':sha(stripped.encode()),'exact_old_native_body_after_removing_two_additions':True,'existing_hot_callers_or_layouts_changed':False})
manifest={'files':current,'native43':{name:current[name] for name in native},'diagnostic34':{name:current[name] for name in cold},'tools23':{name:current[name] for name in tools}}
for name in ['files','native43','diagnostic34','tools23']:
    manifest[name+'_graph_sha256']=sha(json.dumps(manifest[name],sort_keys=True,separators=(',',':')).encode())
emit('source-manifest.json',manifest)
for name in files:
    dest=E/'proposal-source'/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(SOURCE/name,dest)
with tarfile.open(E/'prepared-source.tar.gz','w:gz') as archive:
    for name in files:archive.add(SOURCE/name,arcname=name,recursive=False)
# Reconcile every original selected fixture; preserve all original top-level headers.
base_inventory=json.loads((BASE_E/'whole-fixture-inventory.json').read_text());assert len(base_inventory)==89
new_paths=[str(Path('/home/legolas/king-spec/conformance/fixtures')/name) for name in ['search-candidate-production-v1.json','quiescence-evasion-order-v1.json','quiescence-candidates-v1.json']]
all_paths=[entry['path'] for entry in base_inventory]+new_paths;assert len(all_paths)==len(set(all_paths))==92
baseline={entry['path']:entry for entry in base_inventory}
inventory=[];mapping=[];ids=set();counts=collections.Counter();new_mapping=[]
for filename in all_paths:
    path=Path(filename);raw=path.read_bytes();fingerprint=sha(raw);doc=json.loads(raw);cases=doc['cases']
    if filename in baseline:assert fingerprint==baseline[filename]['sha256'],'Frozen selected fixture changed'
    header={k:v for k,v in doc.items() if k!='cases'};local=collections.Counter()
    for index,case in enumerate(cases):
        request=case['request'];operation=request['operation'];case_id=case['id']
        assert case_id not in ids;ids.add(case_id);counts[operation]+=1;local[operation]+=1
        entry={'ordinal':len(mapping),'fixture':filename,'fixture_sha256':fingerprint,'case_index':index,'id':case_id,'operation':operation,'request_version':request['version']}
        mapping.append(entry)
        if filename in new_paths:new_mapping.append(entry)
    inventory.append({'path':filename,'sha256':fingerprint,'header':header,'case_count':len(cases),'operation_case_counts':dict(local),'selection':'whole unmodified official file'})
assert (len(mapping),len(counts),len(inventory),len(ids))==(7447,97,92,7447)
assert len(new_mapping)==54 and dict(collections.Counter(c['operation'] for c in new_mapping))=={'search.produceAndOrderCandidates':30,'search.quiescenceCandidates':24}
assert len({(c['fixture'],c['case_index']) for c in mapping})==7447
emit('whole-fixture-inventory.json',inventory)
emit('whole-fixture-map.json',{'cases':mapping,'unique_cases':7447,'operations':97,'whole_files':92,'partial_files':0,'duplicate_ids':0,'duplicate_fixture_indices':0})
emit('new-case-selection.json',{'new_operations':{'search.produceAndOrderCandidates':30,'search.quiescenceCandidates':24},'cases':new_mapping,'whole_files':[entry for entry in inventory if entry['path'] in new_paths]})
with tarfile.open(E/'original-fixtures.tar.gz','w:gz') as archive:
    for entry in inventory:archive.add(entry['path'],arcname='fixtures/'+Path(entry['path']).name,recursive=False)
contracts=['search-candidate-production.md','search-candidate-order.md','quiescence-candidates.md','quiescence-evasion-priority-example.md','quiescence-entry.md','quiescence-disposition.md','tactical-capture-order.md','position-setup.md','move-sequence.md','evaluation-moves.md','retained-evaluation.md']
contract_map={str(Path('/home/legolas/king-spec/spec')/name):h(Path('/home/legolas/king-spec/spec')/name) for name in contracts}
emit('contract-manifest.json',contract_map)
with tarfile.open(E/'authority-contracts.tar.gz','w:gz') as archive:
    for filename in contract_map:archive.add(filename,arcname='spec/'+Path(filename).name,recursive=False)
def tests(root,names):
    return {name:re.findall(r'#\[test\]\s*fn\s+(\w+)',(root/name).read_text()) for name in names if name.endswith('.rs') and (root/name).exists()}
base_tests=tests(BASE,list(base));after_tests=tests(SOURCE,files)
base_native=sum(len(v) for name,v in base_tests.items() if name.startswith('src/'))
base_cold=sum(len(v) for name,v in base_tests.items() if name.startswith('diagnostic/'))
after_native=sum(len(v) for name,v in after_tests.items() if name.startswith('src/'))
after_cold=sum(len(v) for name,v in after_tests.items() if name.startswith('diagnostic/'))
assert (base_native,base_cold,after_native,after_cold)==(151,149,152,156)
added={name:[test for test in names if test not in base_tests.get(name,[])] for name,names in after_tests.items()};added={name:value for name,value in added.items() if value}
emit('test-source-inventory.json',{'status':'declaration counts only; uncompiled/unexecuted','base_counts':{'native':151,'diagnostic':149},'counts':{'native':152,'diagnostic':156},'added':added,'tests':after_tests})
emit('plan.json',{'status':'SOURCE_ONLY; parent review/execution assignment required','source':str(SOURCE),'base':str(BASE),'operations':dict(counts),'operation_count':97,'unique_cases':7447,'whole_files':92,'new_cases':54,'new_whole_files':3,'partial_files':0,'duplicate_ids':0,'native_units_expected':152,'diagnostic_units_expected':156,'native_source_files':43,'diagnostic_source_files':34,'tools_files':23,'total_source_files':100,'schema_owner_map':'schema-and-owner-map.md','base_manifest_sha256':paths['base_manifest_sha256'],'base_prepared_sha256':paths['base_prepared_sha256'],'no_native_execution':True,'no_diagnostic_execution':True})
artifacts=['proposal.patch','native.patch','cold.patch','native-source-proof.json','prepared-source.tar.gz','original-fixtures.tar.gz','authority-contracts.tar.gz','base-source-manifest.json','source-manifest.json','whole-fixture-inventory.json','whole-fixture-map.json','new-case-selection.json','contract-manifest.json','test-source-inventory.json','plan.json','paths.json','review.md','schema-and-owner-map.md','freeze.py']
prepared={'status':'FROZEN SOURCE ONLY; no builds/tests/engines/codegen/profiler execution','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source':str(SOURCE),'base':str(BASE),'affinity':sorted(os.sched_getaffinity(0)),'python':platform.python_version(),'native43_graph_sha256':manifest['native43_graph_sha256'],'diagnostic34_graph_sha256':manifest['diagnostic34_graph_sha256'],'tools23_graph_sha256':manifest['tools23_graph_sha256'],'full_source_graph_sha256':manifest['files_graph_sha256'],'changed_files':changed,'expected':{'native_units':152,'diagnostic_units':156,'operations':97,'unique_cases':7447,'whole_files':92},'archives_after_parent_clearance':True,'source_stable_after':all(h(SOURCE/name)==value for name,value in current.items()),'base_stable_after':all(h(BASE/name)==value for name,value in base.items()),'artifacts':{name:h(E/name) for name in artifacts}}
assert prepared['source_stable_after'] and prepared['base_stable_after'];emit('prepared.json',prepared)
print(json.dumps({'prepared_sha256':h(E/'prepared.json'),'source':str(SOURCE),'native43':prepared['native43_graph_sha256'],'diagnostic34':prepared['diagnostic34_graph_sha256'],'tools23':prepared['tools23_graph_sha256'],'full_source_graph':prepared['full_source_graph_sha256'],'expected':prepared['expected'],'patches':{name:prepared['artifacts'][name] for name in ['proposal.patch','native.patch','cold.patch']},'base_stable':True,'source_stable':True},indent=2))
