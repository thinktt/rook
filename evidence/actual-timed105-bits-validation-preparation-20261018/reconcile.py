#!/usr/bin/env python3
"""Independent original raw/expected/exit/source reconciliation; no native jobs."""
from pathlib import Path
import collections,json,re,tarfile
import sys
sys.dont_write_bytecode=True
from guard import HERE,load,sha,write,clearance,terminal,check_sources,check_dependencies
SPEC=Path('/home/legolas/king-spec/conformance')
def same(a,b):
 if isinstance(a,bool) or isinstance(b,bool):return type(a) is type(b) and a==b
 if isinstance(a,(int,float)) and isinstance(b,(int,float)):return a==b
 if type(a) is not type(b):return False
 if isinstance(a,dict):return a.keys()==b.keys() and all(same(a[k],b[k]) for k in a)
 if isinstance(a,list):return len(a)==len(b) and all(same(x,y) for x,y in zip(a,b))
 return a==b

def archive(path):
 with tarfile.open(path,'r:gz') as t:return {m.name:__import__('hashlib').sha256(t.extractfile(m).read()).hexdigest() for m in t if m.isfile()}
def semantic(s,wire=False):
    if s.startswith('move '):return dict(type='move',move=s[5:])
    if s.startswith('stat01: '):
        m=re.fullmatch(r'stat01:\s+(-?\d+)\s+(\d+)\s+(-?\d+)\s+(\d+)\s+(\d+)(?: (.*))?',s);assert m
        a,b,c,d,e=map(int,m.groups()[:5]);return dict(type='status',engineCentiseconds=a,searchId=b,depthToken=c,remaining=d,total=e,pv=(m[6] or '').replace('0','O'))
    m=re.fullmatch(r'\s*(-?\d+)\s+([+-]?\d+)\s+(\d+)\s+(\d+)(?:\s+(.*))?',s);assert m,s
    a,b,c,d=map(int,m.groups()[:4]);pv=(m[5] or '').strip().replace('0','O')
    return dict(type='post',depthToken=a,evaluation=b,engineCentiseconds=c,searchId=d,pv=pv) if wire else dict(depth=a,score=b,workThousands=c,searchId=d,pv=pv)

def main():
 plan=clearance();check_sources(plan);check_dependencies(plan);out=Path(plan['output']['reconciliation']);assert not out.exists();out.mkdir()
 terminal(Path(plan['output']['diagnostic'])/'tool-terminal.json');V=Path(plan['native_validation']);B=Path(plan['native_generic_build'])
 paths={'strict-check':V/'ordinary-check','interruption-wire':V/'interruption-wire','generic-build':B,'diagnostic':Path(plan['output']['diagnostic']),'diagnostic-build':Path(plan['output']['diagnostic-build'])}
 source=Path(plan['home_source']);proposal=Path(plan['proposal']);ref=Path(plan['native_reference']);proof=load(ref/'reuse-proof.json')
 for name in ['native-actual-terminal.json','generic-actual-terminal.json','strict-wire-actual-terminal.json']:terminal(V/name)
 vr=load(V/'native-verification.json');assert vr['complete'] and vr['inputs_stable'] and vr['source_before']==vr['source_after']==plan['native_sha256']
 assert vr['units']['rook2']['passed']==156 and vr['units']['rook2-dev']['passed']==2
 for name,item in vr['units'].items():
  assert sha(V/'unit-bin'/name/'rook2-exact')==item['binary_sha256'];assert len(re.findall(r'^test .* \.\.\. ok$',(V/(name+'-tests.stdout')).read_text(),re.M))==item['passed']
 assert archive(proposal/'source-103.tar.gz')==plan['source_sha256']
 assert archive(proposal/'official-inputs-102.tar.gz')=={name.lstrip('/'):h for name,h in plan['fixtures'].items()}
 br=load(paths['diagnostic-build']/'receipt.json');expected={k.removeprefix('diagnostic/'):v for k,v in plan['diagnostic_sha256'].items()};assert br['source_sha256_before']==br['source_sha256_after']==expected and br['source_identity_unchanged']
 native=load(B/'receipt.json');assert native['source_sha256_before']==native['source_sha256_after']==plan['native_sha256'] and native['tool_sha256_before']==native['tool_sha256_after']==plan['tools_sha256']
 assert br['toolchain']==native['toolchain'] and br['rust_flags']==native['rust_flags']==['-C','target-cpu=x86-64'] and br['pgo']['mode']==native['pgo']['mode']=='none'
 ar=load(paths['diagnostic-build']/'archive-receipt.json');assert ar['verified_against_build_before_hashes'] and sha(paths['diagnostic-build']/ar['archive'])==ar['sha256'] and archive(paths['diagnostic-build']/ar['archive'])==expected|br['tool_sha256_before']
 diagvr=load(paths['diagnostic']/'verification.json');assert diagvr['complete'] and diagvr['failure'] is None and diagvr['units']['rook2-diag']['passed']==182
 assert sha(paths['diagnostic']/'unit-bin/rook2-diag/unit-exact')==diagvr['units']['rook2-diag']['binary_sha256']
 assert len(re.findall(r'^test .* \.\.\. ok$',(paths['diagnostic']/'rook2-diag-tests.stdout').read_text(),re.M))==182
 # Strict54 original checker stdout contains the exact retained native streams.
 strict=paths['strict-check'];report=load(strict/'strict54.stdout');work=load(SPEC/'profiling/workloads.json');oracle=load(SPEC/'profiling/replay-oracle.json');raw=out/'strict-raw'
 assert report['status']=='pass' and len(report['results'])==len(work['cases'])==len(oracle['cases'])==54 and report['selectedCases']==[c['id'] for c in work['cases']]
 engine=paths['generic-build']/'rook2-exact'
 for row,c in zip(report['results'],work['cases']):
  answer=next(a for a in oracle['cases'] if a['id']==c['id']);assert row['case']==c['id'] and row['status']=='pass' and row['command']==[str(engine),'--work-clock=kingwcr','--work-clock-post=work'] and row['exit']==answer['exit']==dict(code=0,signal=None)
  assert row['complete'] and not row['truncated'] and not row.get('cleanupUnconfirmed',False) and row['discardedObservedBytes']==0 and row['error'] is None and row['stderr']==answer['stderr']=='' and row['stdout'].endswith('\n')
  lines=row['stdout'].splitlines();acks=[x for x in c['protocol']['recordsBeforeSearch'] if x.startswith('cm_parm ')]+['cm_parm rnd=0'];assert lines[:len(acks)]==acks;lines=lines[len(acks):]
  assert [semantic(x) for x in lines[:len(answer['posts'])]]==answer['posts'] and lines[len(answer['posts']):]==['move '+answer['move']]+answer['resultRecords']
  d=raw/c['id'];d.mkdir(parents=True);(d/'stdout.raw').write_text(row['stdout']);(d/'stderr.raw').write_text(row['stderr']);(d/'stdin.reconstructed').write_text('\n'.join(c['protocol']['recordsBeforeSearch']+['cm_parm rnd',c['protocol']['searchRecord'],c['protocol']['cleanupRecord']])+'\n')
 assert not (strict/'strict54.stderr').stat().st_size
 wire=paths['interruption-wire'];wr=load(wire/'receipt.json');fixtures=load(SPEC/'fixtures/interrupted-sessions-v1.json')['cases'];assert wr['pass'] and len(wr['results'])==len(fixtures)==8 and wr['engine_sha256_before']==wr['engine_sha256_after']==sha(engine)
 searches=0
 for row,c in zip(wr['results'],fixtures):
  assert row['id']==c['id'] and row['status']=='pass' and row['complete_streams'] and row['exit_code']==row['observed_exit_code']==0
  for key,item in row['raw'].items():
   f=wire/c['id']/(key+'.raw');assert sha(f)==item['sha256'] and f.stat().st_size==item['bytes']
  assert (wire/c['id']/'stderr.raw').read_bytes()==b'';text=(wire/c['id']/'stdout.raw').read_text();assert text.endswith('\n');lines=iter(text.splitlines());stdin=[]
  for request,answer in zip(c['request']['input']['searches'],c['expected']['results']):
   commands=request['commands'];stdin+=commands+[f"time {request['allowanceCs']}",'cm_parm','go']+request['queued']
   for command in commands:
    if command.startswith('cm_parm '):assert next(lines)==' '.join(command.split())
   assert next(lines)=='cm_parm';assert [semantic(next(lines),True) for _ in answer['events']]==answer['events']
   if request['queued'] and request['queued'][-1]=='force':assert next(lines)=='aborting search ...'
   searches+=1
  assert list(lines)==[] and (wire/c['id']/'stdin.raw').read_text()=='\n'.join(stdin+['quit'])+'\n'
 assert searches==24
 # All102 original files, each complete and byte-bound; no supplied expected data in runtime.
 diag=paths['diagnostic'];official=load(diag/'conformance.stdout');assert official['pass'] and official['completeEngineQualification'] is False and len(official['results'])==7519
 expected=[];files=[];ids=set();ops=collections.Counter()
 for name,h in plan['fixtures'].items():
  f=Path(name);assert sha(f)==h;doc=load(f);assert doc['version']==1 and len(doc['cases'])==plan['fixture_counts'][name];files.append(dict(path=name,sha256=h,count=len(doc['cases'])))
  for index,c in enumerate(doc['cases']):
   assert c['id'] not in ids;ids.add(c['id']);expected.append((name,index,c));ops[c['request']['operation']]+=1
 assert len(files)==102 and len(expected)==len(ids)==7519 and len(ops)==105 and dict(ops)==plan['operation_case_counts'] and official['files']==files
 raw=diag/'raw-cases';assert int((raw/'cursor').read_text())==7519 and len(list(raw.glob('*.json')))==7519
 hashes={};rows=[];adapter=paths['diagnostic-build']/'rook2-diag-exact'
 for ordinal,((name,index,c),row) in enumerate(zip(expected,official['results'])):
  assert row['id']==c['id'] and row['contract']==c['contract'] and row['pass'] and row['exit']==dict(code=0,signal=None)
  stem=raw/f'{ordinal:06d}';record=load(stem.with_suffix('.json'));assert record['ordinal']==ordinal and record['child_returncode']==0 and record['failure'] is None and record['adapter']==str(adapter) and record['child_pid']>0 and record['affinity']==plan['affinity']
  request=load(stem.with_suffix('.stdin'));response=load(stem.with_suffix('.stdout'));assert same(request,c['request']) and set(response)=={'version','output'} and response['version']==1 and same(response['output'],c['expected']) and same(row['actual'],response['output']) and stem.with_suffix('.stderr').stat().st_size==0
  for ext in ['.stdin','.stdout','.stderr','.json']:
   f=stem.with_suffix(ext);hashes[str(f.relative_to(diag))]=sha(f)
  rows.append(dict(ordinal=ordinal,fixture=name,case_index=index,id=c['id'],operation=c['request']['operation'],raw_output_sha256=sha(stem.with_suffix('.stdout')),actual_child_exit_code=0))
 check_sources(plan);check_dependencies(plan)
 write(out/'raw-case-sha256.json',hashes);write(out/'case-reconciliation.json',dict(cases=7519,whole_files=102,partial_files=0,duplicate_ids=0,all_original_expected_raw_and_official_actual_equal=True,rows=rows))
 result=dict(status='pass',native_units_reused=158,diagnostic_units=182,strict_replays_reused=54,wire_fixtures_reused=8,wire_searches_reused=24,cases=7519,operations=105,whole_files=102,source_stable=True,native_sha256=sha(B/'rook2-exact'),adapter_sha256=sha(adapter),all_raw_expected_actual_and_exits_equal=True,raw_case_manifest_sha256=sha(out/'raw-case-sha256.json'),case_reconciliation_sha256=sha(out/'case-reconciliation.json'),native_reuse_proof_sha256=sha(ref/'reuse-proof.json'))
 write(out/'independent-verification.json',result);print(json.dumps(result))
if __name__=='__main__':main()
