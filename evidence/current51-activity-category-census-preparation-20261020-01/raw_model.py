"""Selected-case raw replay and fixed activity-counter reconciliation; no PGO guard."""
from pathlib import Path
import hashlib,json,re
SPEC=Path('/home/legolas/king-spec/conformance')
CASES=['profile-01','profile-35','profile-08']
def load(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):
 with Path(p).open('x') as f:json.dump(v,f,indent=2);f.write('\n')
def semantic(s,wire=False):
 if s.startswith('move '):return dict(type='move',move=s[5:])
 if s.startswith('stat01: '):
  m=re.fullmatch(r'stat01:\s+(-?\d+)\s+(\d+)\s+(-?\d+)\s+(\d+)\s+(\d+)(?: (.*))?',s);assert m
  a,b,c,d,e=map(int,m.groups()[:5]);return dict(type='status',engineCentiseconds=a,searchId=b,depthToken=c,remaining=d,total=e,pv=(m[6] or '').replace('0','O'))
 m=re.fullmatch(r'\s*(-?\d+)\s+([+-]?\d+)\s+(\d+)\s+(\d+)(?:\s+(.*))?',s);assert m,s
 a,b,c,d=map(int,m.groups()[:4]);pv=(m[5] or '').strip().replace('0','O')
 return dict(type='post',depthToken=a,evaluation=b,engineCentiseconds=c,searchId=d,pv=pv) if wire else dict(depth=a,score=b,workThousands=c,searchId=d,pv=pv)
def replay(report_path,engine,case,raw_out=None):
 report=load(report_path);work=load(SPEC/'profiling/workloads.json');oracle=load(SPEC/'profiling/replay-oracle.json')
 assert case in CASES and report['status']=='pass' and report['selectedCases']==[case] and len(report['results'])==1
 assert report['workloadSha256']==sha(SPEC/'profiling/workloads.json') and report['oracleSha256']==sha(SPEC/'profiling/replay-oracle.json')
 c=next(x for x in work['cases'] if x['id']==case);answer=next(x for x in oracle['cases'] if x['id']==case);row=report['results'][0]
 expected_command=['/usr/bin/taskset','-c','14',str(engine),'--work-clock=kingwcr','--work-clock-post=work']
 assert row['case']==case and row['command']==expected_command and row['status']=='pass' and row['exit']==answer['exit']==dict(code=0,signal=None)
 assert type(row['pid']) is int and row['pid']>0
 assert row['error'] is None and row['complete'] and not row['truncated'] and not row.get('cleanupUnconfirmed',False) and row['discardedObservedBytes']==0
 assert row['stderr']==answer['stderr']=='' and row['stdout'].endswith('\n')
 assert row['retainedBytes']==len(row['stdout'].encode())+len(row['stderr'].encode())
 lines=row['stdout'].splitlines();acks=[x for x in c['protocol']['recordsBeforeSearch'] if x.startswith('cm_parm ')]+['cm_parm rnd=0'];assert lines[:len(acks)]==acks;lines=lines[len(acks):]
 assert [semantic(x) for x in lines[:len(answer['posts'])]]==answer['posts']
 assert lines[len(answer['posts']):]==['move '+answer['move']]+answer['resultRecords']
 payloads={'stdout.raw':row['stdout'].encode(),'stderr.raw':row['stderr'].encode(),'stdin.reconstructed': ('\n'.join(c['protocol']['recordsBeforeSearch']+['cm_parm rnd',c['protocol']['searchRecord'],c['protocol']['cleanupRecord']])+'\n').encode()}
 if raw_out is not None:
  raw_out=Path(raw_out)
  for n,b in payloads.items():
   with (raw_out/n).open('xb') as f:f.write(b)
 return row,payloads
COUNTERS=['groups','sources','encounters','unique','repeats','shortcut_encounters','adjusted_encounters','shortcut_unique','adjusted_unique','shortcut_repeats','adjusted_repeats']
def counters(probe,native_pid):
 assert probe['schema']=='rook2-activity-category-census-v1' and probe['pid']==native_pid and type(probe['pid']) is int
 assert probe['complete'] is True and probe['overflow'] is False and len(probe['rows'])==32
 bins={};totals={k:0 for k in COUNTERS};groups={}
 for row in probe['rows']:
  for k in ['color','kind','source_bin']+COUNTERS:assert type(row[k]) is int and row[k]>=0,(k,row)
  c,k,b=row['color'],row['kind'],row['source_bin'];assert c in range(2) and k in range(1,5) and b in range(4) and (c,k,b) not in bins
  bins[c,k,b]=row
  for name in ['categories','repeat_categories']:assert len(row[name])==4 and all(type(x) is int and x>=0 for x in row[name])
  assert row['encounters']==row['unique']+row['repeats'] and row['repeats']<=row['encounters']
  for a in ['encounters','unique','repeats']:assert row['shortcut_'+a]+row['adjusted_'+a]==row[a]
  assert row['shortcut_encounters']==row['shortcut_unique']+row['shortcut_repeats']
  assert row['adjusted_encounters']==row['adjusted_unique']+row['adjusted_repeats']
  assert sum(row['categories'])==row['encounters'] and sum(row['repeat_categories'])==row['repeats']
  assert all(h<=e for h,e in zip(row['repeat_categories'],row['categories'])) and row['unique']<=64*row['groups']
  if b==0:assert row['sources']==0 and all(row[x]==0 for x in COUNTERS if x not in ['groups','sources'])
  elif b==1:assert row['sources']==row['groups'] and row['repeats']==0
  elif b==2:assert row['sources']==2*row['groups']
  else:assert row['sources']>=3*row['groups']
  if row['groups']==0:assert all(row[x]==0 for x in COUNTERS) and not any(row['categories']+row['repeat_categories'])
  for x in COUNTERS:totals[x]+=row[x]
  groups[c,k]=groups.get((c,k),0)+row['groups']
 assert set(bins)=={(c,k,b) for c in range(2) for k in range(1,5) for b in range(4)} and len(set(groups.values()))==1
 return dict(rows=32,totals=totals,compute_groups_per_color_kind=next(iter(groups.values())),source_bin3_means='at least three sources',counts_only=True)
