#!/usr/bin/env python3
# Independent whole-fixture/raw-response/exits/closure reconciliation.
import argparse,collections,hashlib,json,re,tarfile,sys
from pathlib import Path
P=Path(__file__).resolve().parent;E=P.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:json.loads(p.read_text())
def same(a,b):
 if isinstance(a,bool) or isinstance(b,bool):return type(a) is type(b) and a==b
 if isinstance(a,(int,float)) and isinstance(b,(int,float)):return a==b
 if type(a) is not type(b):return False
 if isinstance(a,dict):return a.keys()==b.keys() and all(same(a[k],b[k]) for k in a)
 if isinstance(a,list):return len(a)==len(b) and all(same(x,y) for x,y in zip(a,b))
 return a==b

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--label',default='20261018');args=parser.parse_args();assert re.fullmatch(r'[A-Za-z0-9_-]+',args.label)
 out=E/('diagnostic-admission-combined95-'+args.label);build=E/('diagnostic-admission-combined95-build-'+args.label)
 plan=load(P/'plan.json');prep=load(P/'source-preparation.json');v=load(out/'verification.json');report=load(out/'conformance.stdout');before=load(out/'inputs-before.json');after=load(out/'inputs-after.json');br=load(build/'receipt.json')
 assert v['complete'] and v['inputs_stable'] and v['failure'] is None and all(s['exit_code']==0 for s in v['stages'])
 assert report['pass'] and report['completeEngineQualification'] is False and len(report['results'])==7393
 expected=[];files=[];ops=collections.Counter();all_ids=set();new_records=collections.Counter()
 for name,h in plan['fixtures'].items():
  path=Path(name);assert sha(path)==h;doc=load(path);assert doc['version']==1;files.append({'path':name,'sha256':h,'count':len(doc['cases'])})
  for index,case in enumerate(doc['cases']):
   assert case['id'] not in all_ids;all_ids.add(case['id']);ops[case['request']['operation']]+=1;expected.append((name,index,case))
   if case['request']['operation']=='search.quiescenceTree':
    new_records['visited_nodes']+=case['expected']['nodes'];new_records['trace_events']+=len(case['expected']['trace']);new_records['evaluation_records']+=len(case['expected']['evaluations'])
    for node in case['expected']['evaluations']:
     for stage in node['stages']:new_records[stage['kind']+'_stages']+=1
 assert len(files)==89 and len(expected)==len(all_ids)==7393 and len(ops)==95 and dict(ops)==plan['operation_case_counts']
 assert report['files']==files
 raw=out/'raw-cases';assert int((raw/'cursor').read_text())==7393;assert len(list(raw.glob('*.json')))==7393
 raw_hashes={};case_rows=[]
 for ordinal,((fixture,index,case),result) in enumerate(zip(expected,report['results'])):
  assert result['id']==case['id'] and result['contract']==case['contract'] and result['pass'] and result['exit']=={'code':0,'signal':None}
  stem=raw/f'{ordinal:06d}';record=load(stem.with_suffix('.json'));assert record['ordinal']==ordinal and record['child_returncode']==0 and record['failure'] is None
  assert record['adapter']==str(build/'rook2-diag-exact') and set(record['affinity'])=={0,1,2,3,4,5,8,9,10,11,12,13}
  request=load(stem.with_suffix('.stdin'));response=load(stem.with_suffix('.stdout'))
  assert same(request,case['request']) and set(response)=={'version','output'} and response['version']==1
  assert same(response['output'],case['expected']) and same(result['actual'],response['output'])
  assert stem.with_suffix('.stderr').stat().st_size==0
  names=[stem.with_suffix(ext) for ext in ['.stdin','.stdout','.stderr','.json']]
  for p in names:raw_hashes[str(p.relative_to(out))]=sha(p)
  case_rows.append({'ordinal':ordinal,'fixture':fixture,'case_index':index,'id':case['id'],'operation':case['request']['operation'],'raw_stem':str(stem.relative_to(out)),'raw_output_sha256':sha(stem.with_suffix('.stdout')),'child_exit_code':0})
 assert dict(new_records)=={'visited_nodes':46,'trace_events':92,'evaluation_records':46,'fast_stages':16,'full_stages':33}
 assert all(before[k]==after[k] for k in after) and all(sha(Path(p))==h for p,h in before['dependencies'].items())
 reference=load(Path(plan['native_build_reference']));assert before['native']==prep['native_source_sha256']==reference['source_sha256_before']==reference['source_sha256_after']
 assert before['native_tools']==prep['tool_source_sha256']==reference['tool_sha256_before']==reference['tool_sha256_after']
 assert before['adapter']==prep['adapter_source_sha256']==br['source_sha256_before']==br['source_sha256_after']
 assert len(before['native'])==43 and len(before['adapter'])==33 and len(before['native_tools'])==23
 source=Path(plan['source_root'])
 for group in ['native','native_tools']:
  for name,h in before[group].items():assert sha(source/name)==h
 for name,h in before['adapter'].items():assert sha(source/'diagnostic'/name)==h
 assert sha(build/'rook2-diag-exact')==br['binary_output']['sha256']==v['adapter_sha256'];assert sha(out/'unit-bin/rook2-diag-exact')==v['unit_binary_sha256']
 assert re.search(r'test result: ok\. 149 passed; 0 failed;',(out/'unit-tests.stdout').read_text())
 for archive_name,manifest in [('prepared-source-closure.tar.gz',prep['full_source_sha256']),('prepared-adapter.tar.gz',prep['adapter_source_sha256'])]:
  with tarfile.open(P/archive_name,'r:gz') as t:actual={m.name:hashlib.sha256(t.extractfile(m).read()).hexdigest() for m in t if m.isfile()}
  assert actual==manifest
 ar=load(build/'archive-receipt.json');assert ar['verified_against_build_before_hashes'] and sha(build/ar['archive'])==ar['sha256'] and ar['binary_sha256']==v['adapter_sha256']
 (out/'raw-case-sha256.json').write_text(json.dumps(raw_hashes,indent=2)+'\n');(out/'case-reconciliation.json').write_text(json.dumps({'case_count':7393,'partial_files':0,'duplicate_ids':0,'all_original_expected_and_raw_outputs_equal':True,'cases':case_rows},indent=2)+'\n')
 identity={'status':'95 native-backed diagnostic operations pass','adapter_sha256':v['adapter_sha256'],'cases':7393,'units':149,'operations':sorted(ops),'whole_fixture_files':89,'partial_files':0,'duplicate_case_ids':0,'independent_raw_response_equal':7393,'new_case_count':1232,'inherited_quiescence_tree_observation_counts':dict(new_records),'source_identity_stable':True,'build_receipt_sha256':sha(build/'receipt.json'),'verification_sha256':sha(out/'verification.json'),'official_report_sha256':sha(out/'conformance.stdout'),'raw_manifest_sha256':sha(out/'raw-case-sha256.json'),'case_reconciliation_sha256':sha(out/'case-reconciliation.json'),'native_binary_sha256':plan['inherited_native_binary_sha256'],'native_build_reference_sha256':sha(Path(plan['native_build_reference'])),'native_reuse_evidence_sha256':plan['native_reuse_evidence_sha256'],'reconciler_sha256':sha(Path(__file__)),'cpu_measurements':0,'profilers':0,'pgo':0,'ordinary_native_rebuilds':0,'ordinary_native_replays':0,'complete_mandatory_qualification':False}
 with (out/'identity.json').open('x') as f:json.dump(identity,f,indent=2);f.write('\n')
 print(json.dumps({'cases':7393,'units':149,'adapter_sha256':v['adapter_sha256'],'all_original_raw_outputs_reconciled':True}))
if __name__=='__main__':main()
