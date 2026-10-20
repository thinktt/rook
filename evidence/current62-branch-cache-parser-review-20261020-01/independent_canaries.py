from pathlib import Path
import importlib.util,json,hashlib,time,os
E=Path(__file__).resolve().parent
P=Path('/home/legolas/rook2/evidence/current62-branch-cache-parser-20261020-02/vector_parser.py')
H='d4c592666b295656e732edd7cac05b9bd4d3dc7aff619c56d010d3f24273e560'
assert hashlib.sha256(P.read_bytes()).hexdigest()==H
start=time.monotonic();spec=importlib.util.spec_from_file_location('frozen_vector_reader',P);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
rows=[]
def pos(name,text,events,expected,extra=None):
 d=m.parse_text(text,events);assert d['SELF_sum']==expected,(name,d['SELF_sum']);m.rank(d)
 if extra:extra(d)
 rows.append({'name':name,'pass':True})
def neg(name,text,events):
 try:m.parse_text(text,events)
 except ValueError as x:rows.append({'name':name,'pass':True,'rejected_with':str(x)});return
 raise AssertionError('accepted '+name)
# Ir-zero secondary accesses and entirely omitted zero vector: no positive-Ir filter.
s='version: 1\npart: 1\npositions: line\nevents: Ir Dr Dw Bc Bcm Bi Bim\nsummary: 5 7 3 4 1 0 0\nob=(1) binary\nfl=(1) outer.rs\nfn=(1) outer\n10 5\n+2 0 7 3 4 1\n*\ntotals: 5 7 3 4 1 0 0\n'
pos('Ir0-secondary-omitted-tail-and-all-zero-row',s,['Ir','Dr','Dw','Bc','Bcm','Bi','Bim'],{'Ir':5,'Dr':7,'Dw':3,'Bc':4,'Bcm':1,'Bi':0,'Bim':0},lambda d: (None if [r['line'] for r in d['raw_SELF_rows']]==[10,12,12] and d['model_rates']=={'Bcm_div_Bc':.25,'Bim_div_Bi':None} else (_ for _ in ()).throw(AssertionError('rows/rates'))))
# Shared compression dictionaries within each name class, independent across classes.
a='events: Ir Dr\nsummary: 9 6\nob=(1) binary\nfl=(1) outer.rs\nfn=(1) owner\n1 2 1\nfi=(2) inline.rs\n+1 3 2\ncob=(1)\ncfi=(1)\ncfn=(2) called\ncalls=7 40\n* 999 888\nfe=(1)\n+1 4 3\ntotals: 9 6\n'
def extra(d):
 assert [x['file'] for x in d['raw_SELF_rows']]==['outer.rs','inline.rs','outer.rs']
 assert len(d['raw_inclusive_call_arcs_NOT_ADDED'])==1
 arc=d['raw_inclusive_call_arcs_NOT_ADDED'][0];assert arc['events']=={'Ir':999,'Dr':888} and arc['explicit_calls']==7
 assert arc['callee_function']=='called' and arc['callee_file']=='outer.rs'
 assert m.rank(d)[0]['file_partitions']=={'outer.rs':{'Ir':6,'Dr':4},'inline.rs':{'Ir':3,'Dr':2}}
pos('compression-inline-arc-not-SELF',a,['Dr','Ir'],{'Ir':9,'Dr':6},extra)
z='events: Ir Bc Bcm Bi Bim\nsummary: 0 0 0 0 0\nfl=unknown\nfn=unknown\n0\ntotals: 0 0 0 0 0\n'
pos('zero-rate-denominators',z,['Ir','Bc','Bcm','Bi','Bim'],{'Ir':0,'Bc':0,'Bcm':0,'Bi':0,'Bim':0},lambda d: (None if all(x is None for x in d['model_rates'].values()) else (_ for _ in ()).throw(AssertionError('zero rate'))))
for name,text,events in [
 ('short-totals',s.replace('totals: 5 7 3 4 1 0 0','totals: 5'),['Ir','Dr','Dw','Bc','Bcm','Bi','Bim']),
 ('partial-summary-not-admitted',s.replace('summary: 5 7 3 4 1 0 0','summary: 6 7 3 4 1 0 0'),['Ir','Dr','Dw','Bc','Bcm','Bi','Bim']),
 ('duplicate-part',s.replace('part: 1','part: 1\npart: 1'),['Ir','Dr','Dw','Bc','Bcm','Bi','Bim']),
 ('second-part',s.replace('part: 1','part: 2'),['Ir','Dr','Dw','Bc','Bcm','Bi','Bim']),
 ('jump-rejected',s.replace('*\ntotals','jump=1 12\n*\ntotals'),['Ir','Dr','Dw','Bc','Bcm','Bi','Bim']),
 ('conditional-jump-rejected',s.replace('*\ntotals','jcnd=1 1 12\n*\ntotals'),['Ir','Dr','Dw','Bc','Bcm','Bi','Bim']),
 ('partial-compression',a.replace('fn=(1) owner','fn=(1'),['Ir','Dr']),
 ('alias-redefinition',a.replace('fi=(2) inline.rs','fi=(1) different.rs'),['Ir','Dr']),
 ('unresolved-alias',a.replace('fl=(1) outer.rs','fl=(98)'),['Ir','Dr']),
 ('unterminated-call',a.replace('* 999 888',''),['Ir','Dr']),
 ('missing-owner',s.replace('fn=(1) outer\n',''),['Ir','Dr','Dw','Bc','Bcm','Bi','Bim']),
 ('cost-after-totals',s+'0 0\n',['Ir','Dr','Dw','Bc','Bcm','Bi','Bim']),
 ('instruction-position-schema',s.replace('positions: line','positions: instr line'),['Ir','Dr','Dw','Bc','Bcm','Bi','Bim']),
 ('wrong-named-event-schema',s,['Ir','Dr']),
 ('prediction-count-inconsistent',z.replace('summary: 0 0 0 0 0','summary: 0 0 1 0 0').replace('0\ntotals','0 0 0 1\ntotals').replace('totals: 0 0 0 0 0','totals: 0 0 1 0 0'),['Ir','Bc','Bcm','Bi','Bim'])]:neg(name,text,events)
assert hashlib.sha256(P.read_bytes()).hexdigest()==H
result={'complete':True,'parser_sha256':H,'checks':rows,'check_count':len(rows),'elapsed_wall_s':time.monotonic()-start,'engines':0,'profilers':0,'annotator_runs':0,'parser_owner_tree_unchanged':True,'fixed_domain_only':True}
(E/'independent-canary-results.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'complete':True,'checks':len(rows),'elapsed_wall_s':result['elapsed_wall_s'],'engines':0,'profilers':0}))
