"""Format-semantic canaries + one accepted existingIr fixture; no recording."""
from pathlib import Path
import json,time,hashlib,subprocess,os,resource
from vector_parser import parse_text,parse_file,rank,EVENTS
P=Path(__file__).resolve().parent
started=time.monotonic();checks=[]
def save(name,data):
 with (P/name).open('x') as stream:json.dump(data,stream,indent=2);stream.write('\n')
def guard():
 assert time.monotonic()-started<90,'offline helper bound'
 assert sum(p.stat().st_size for p in P.rglob('*') if p.is_file())<=134217728,'output cap'
def okay(name,text,events,expected):
 guard();data=parse_text(text,events);assert data['SELF_sum']==expected,(name,data['SELF_sum'],expected);rank(data);checks.append(dict(name=name,passed=True));return data
def bad(name,text,events):
 guard()
 try:data=parse_text(text,events);rank(data)
 except ValueError as error:checks.append(dict(name=name,passed=True,rejected_with=str(error)));return
 raise AssertionError('accepted invalid fixture '+name)
# Local primary cl-format simple example: last omitted Flops counter iszero.
doc='events: Cycles Instructions Flops\nsummary: 110 26 2\nfl=file.f\nfn=main\n15 90 14 2\n16 20 12\ntotals: 110 26 2\n'
okay('primary-doc-three-events-short-row',doc,['Cycles','Instructions','Flops'],{'Cycles':110,'Instructions':26,'Flops':2})
# Hand-worked SELF3+5+7; inclusive100must not enter totals. File aliases shared
# across current/callee contexts; relative source positions follow lastcostrow.
assoc='events: Ir Dr\nsummary: 15 4\nob=(1) owned\nfl=(1) root.rs\nfn=(1) main\n10 3 1\ncob=(2) external\ncfl=(2) child.rs\ncfn=(2) child\ncalls=2 99\n* 100 90\nfi=(3) inline.rs\n+1 5 2\nfe=(1)\n-11 7 1\nfn=(3) next\n0 0\ncfn=(2)\ncalls=1 0x10\n* 50 20\ntotals: 15 4\n'
a=okay('compressed-inline-calls-repeated-source-zero',assoc,['Dr','Ir'],{'Ir':15,'Dr':4})
assert [r['line'] for r in a['raw_SELF_rows']]==[10,11,0,0]
assert rank(a)[0]['file_partitions']=={'root.rs':{'Ir':10,'Dr':2},'inline.rs':{'Ir':5,'Dr':2}}
assert len(a['raw_inclusive_call_arcs_NOT_ADDED'])==2
assert a['raw_inclusive_call_arcs_NOT_ADDED'][0]['explicit_calls']==2
assert a['raw_inclusive_call_arcs_NOT_ADDED'][1]['resolved_callee_object'] is None
assert a['raw_inclusive_call_arcs_NOT_ADDED'][1]['callee_object']=='external'
# Literal reverse header and independent expected dictionary. Ir iszero and its
# final counter omitted; no Ir-positive filter or positional13event assumption.
reverse='events: Bim Bi Bcm Bc DLmw DLmr ILmr D1mw D1mr I1mr Dw Dr Ir\nsummary: 0 0 1 2 0 0 0 0 0 0 0 4 0\nfl=???\nfn=unknown\n0 0 0 1 2 0 0 0 0 0 0 0 4\ntotals: 0 0 1 2 0 0 0 0 0 0 0 4 0\n'
a=okay('reordered13-Irzero-secondary-and-trailing-zero',reverse,EVENTS,{'Ir':0,'Dr':4,'Dw':0,'I1mr':0,'D1mr':0,'D1mw':0,'ILmr':0,'DLmr':0,'DLmw':0,'Bc':2,'Bcm':1,'Bi':0,'Bim':0})
assert rank(a)[0]['model_rates']=={'Bcm_div_Bc':0.5,'Bim_div_Bi':None}
assert a['raw_SELF_rows'][0]['file']=='???'
okay('repeated-SELF-hex-and-relative','events: Ir\nsummary: 9\nfl=x\nfn=f\n0x10 4\n* 3\n-0x1 2\ntotals: 9\n',['Ir'],{'Ir':9})
# Same demangled clone names across differentobjects must not merge; nor do
# distinct recursion-suffix spellings assert any physical caller relationship.
clones="events: Ir\nsummary: 6\nob=A\nfl=x\nfn=f\n0 1\nfn=f'2\n* 2\nob=B\nfn=f\n* 3\ntotals: 6\n"
a=okay('object-and-clone-identity',clones,['Ir'],{'Ir':6});assert len(rank(a))==3
# Grammar permits Costs? entirely absent; all event values are zero.
okay('all-counters-omitted','events: Ir Dr\nsummary: 0 0\nfl=x\nfn=f\n5\n*\ntotals: 0 0\n',['Ir','Dr'],{'Ir':0,'Dr':0})
# String aliases cannot prove distinct physical functions. Ranking explicitly
# coalesces this same-label pair and keeps each raw file/name token unchanged.
same='events: Ir\nsummary: 3\nob=A\nfl=a.rs\nfn=(1) helper\n0 1\nfl=b.rs\nfn=(2) helper\n0 2\ntotals: 3\n'
a=okay('same-label-coalescing-explicit',same,['Ir'],{'Ir':3})
assert len(rank(a))==1 and rank(a)[0]['attribution']=='coalesced object/function-NAME'
assert [x['file'] for x in a['raw_SELF_rows']]==['a.rs','b.rs']
assert [x['fn_name_token'] for x in a['raw_SELF_rows']]==['(1) helper','(2) helper']
badcases=[('duplicate-events',doc.replace('Cycles Instructions Flops','Cycles Cycles Flops')),('unexpected-event',doc.replace('Flops','Other')),('missing-event',doc.replace('events: Cycles Instructions Flops','events: Cycles Instructions')),('negative-counter',doc.replace('90 14 2','-90 14 2')),('extra-counter',doc.replace('90 14 2','90 14 2 0')),('summary-mismatch',doc.replace('summary: 110','summary: 111')),('missing-totals',doc.replace('totals: 110 26 2','')),('part2', 'part: 2\n'+doc),('multiple-parts','part: 1\npart: 1\n'+doc),('thread-split','thread: 1\n'+doc),('instruction-positions','positions: instr line\n'+doc),('derived-event','event: Sum = Cycles + Flops\n'+doc),('unresolved-name',doc.replace('fn=main','fn=(999)')),('overflow',doc.replace('90 14 2',str(1<<64)+' 14 2')),('jump-association',doc.replace('16 20 12','jump=1 16\n16 20 12')),('malformed-numeric',doc.replace('16 20 12','16 nope 12')),('short-summary',doc.replace('summary: 110 26 2','summary: 110 26')),('duplicate-header',doc.replace('events:','events: Cycles Instructions Flops\nevents:',1)),('cost-after-totals',doc+'17 0\n'),('negative-resulting-position',doc.replace('16 20 12','-0x20 20 12'))]
for name,text in badcases:bad(name,text,['Cycles','Instructions','Flops'])
bad('malformed-compressed-open',doc.replace('fn=main','fn=(12'),['Cycles','Instructions','Flops'])
bad('malformed-compressed-nospace',doc.replace('fn=main','fn=(1)name'),['Cycles','Instructions','Flops'])
bad('dangling-call',assoc.replace('totals: 15 4','calls=1 8\ntotals: 15 4'),['Ir','Dr'])
bad('name-redefinition',assoc.replace('fi=(3) inline.rs','fi=(1) other.rs'),['Ir','Dr'])
bad('misses-exceed-branches','events: Ir Bc Bcm\nsummary: 1 1 2\nfl=x\nfn=f\n0 1 1 2\ntotals: 1 1 2\n',['Ir','Bc','Bcm'])
bad('summed-overflow','events: Ir\nsummary: 0\nfl=x\nfn=f\n0 '+str((1<<64)-1)+'\n* 1\ntotals: 0\n',['Ir'])
save('canary-results.json',dict(complete=True,canaries=checks,checks=len(checks),scope='Hand-worked format data only, not cache or predictor simulation'))
# Existing profile only, no freshtarget. Accepted original parser result supplies
# exact row IDs/text/identity/file partitions; compare everySELF and arc row.
guard();D=Path('/home/legolas/rook2-private/current57-callgrind-20261020-01')
a=parse_file(D/'profile-35.callgrind',['Ir']);old=json.loads((D/'self-ranking.json').read_text());assert a['SELF_sum']['Ir']==old['total_simulated_Ir']==43940740008
keys=['raw_line','raw_cost_text','object','file','function','fn_name_token','line']
assert len(a['raw_SELF_rows'])==len(old['raw_SELF_rows'])
for x,y in zip(a['raw_SELF_rows'],old['raw_SELF_rows']):assert all(x[k]==y[k] for k in keys) and x['events']['Ir']==y['Ir']
assert len(a['raw_inclusive_call_arcs_NOT_ADDED'])==len(old['raw_inclusive_call_arcs_NOT_ADDED'])
for x,y in zip(a['raw_inclusive_call_arcs_NOT_ADDED'],old['raw_inclusive_call_arcs_NOT_ADDED']):assert all(x[k]==y[k] for k in keys+['explicit_calls','callee_function','callee_object']) and x['events']['Ir']==y['Ir']
r=rank(a);by={(x['object'],x['function']):x for x in r}
for y in old['ranking']:
 x=by[(y['object'],y['function'])];assert x['SELF_events']['Ir']==y['SELF_Ir'];assert {k:v['Ir'] for k,v in x['file_partitions'].items()}==y['file_partitions']
# Independent installed annotator consumes only the sameclosedIr file.
guard();cmd=['/home/legolas/.local/imp2-tools/valgrind/usr/bin/callgrind_annotate','--auto=no','--inclusive=no','--show=Ir','--sort=Ir','--show-percs=no','--threshold=100',str(D/'profile-35.callgrind')]
begin=time.monotonic();x=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=float(os.environ.get('ROOK2_OFFLINE_ANNOTATOR_SECONDS','30')),check=False);elapsed=time.monotonic()-begin
(P/'annotator.stdout').write_bytes(x.stdout);(P/'annotator.stderr').write_bytes(x.stderr)
save('annotator-command.json',dict(argv=cmd,actual_child_return_observed=True,exit_code=x.returncode,elapsed_seconds=elapsed,stdout_sha256=hashlib.sha256(x.stdout).hexdigest(),stderr_sha256=hashlib.sha256(x.stderr).hexdigest()))
assert x.returncode==0 and not x.stderr
line=next(line for line in x.stdout.decode().splitlines() if 'PROGRAM TOTALS' in line);total=int(line.split()[0].replace(',',''));assert total==a['SELF_sum']['Ir']
save('fixture-crosscheck.json',dict(complete=True,raw_path=a['raw_path'],raw_sha256=a['raw_sha256'],old_ranking_path=str(D/'self-ranking.json'),old_ranking_sha256=hashlib.sha256((D/'self-ranking.json').read_bytes()).hexdigest(),total_Ir=total,SELF_rows=len(a['raw_SELF_rows']),arcs=len(a['raw_inclusive_call_arcs_NOT_ADDED']),functions=len(r),all_original_rows_arcs_and_file_partitions_equal=True,annotator_PROGRAM_TOTALS_agree=True,native_runs=0))
a['ranking']=r;save('old-Ir-vector-result.json',a);guard()
save('run-result.json',dict(complete=True,helper_elapsed_seconds=time.monotonic()-started,annotator_elapsed_seconds=elapsed,output_bytes=sum(q.stat().st_size for q in P.rglob('*') if q.is_file()),maxrss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,model_or_engine_or_recording_runs=0))
print(json.dumps(json.loads((P/'run-result.json').read_text())))
