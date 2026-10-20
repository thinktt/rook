from guard import *
import re
SPEC=Path("/home/legolas/king-spec/conformance")
def semantic(s,wire=False):
 if s.startswith('move '):return dict(type='move',move=s[5:])
 if s.startswith('stat01: '):
  m=re.fullmatch(r'stat01:\s+(-?\d+)\s+(\d+)\s+(-?\d+)\s+(\d+)\s+(\d+)(?: (.*))?',s);assert m
  a,b,c,d,e=map(int,m.groups()[:5]);return dict(type='status',engineCentiseconds=a,searchId=b,depthToken=c,remaining=d,total=e,pv=(m[6] or '').replace('0','O'))
 m=re.fullmatch(r'\s*(-?\d+)\s+([+-]?\d+)\s+(\d+)\s+(\d+)(?:\s+(.*))?',s);assert m,s
 a,b,c,d=map(int,m.groups()[:4]);pv=(m[5] or '').strip().replace('0','O')
 return dict(type='post',depthToken=a,evaluation=b,engineCentiseconds=c,searchId=d,pv=pv) if wire else dict(depth=a,score=b,workThousands=c,searchId=d,pv=pv)

def replay(report_path,engine,training,raw_out):
 report=load(report_path);work=load(SPEC/'profiling/workloads.json');oracle=load(SPEC/'profiling/replay-oracle.json')
 assert report['status']=='pass' and len(report['results'])==len(work['cases'])==len(oracle['cases'])==54
 assert report['selectedCases']==[c['id'] for c in work['cases']]
 expected_command=(['/usr/bin/taskset','-c','14'] if training else [])+[str(engine),'--work-clock=kingwcr','--work-clock-post=work']
 for row,c in zip(report['results'],work['cases']):
  answer=next(x for x in oracle['cases'] if x['id']==c['id'])
  assert row['case']==c['id'] and row['command']==expected_command and row['status']=='pass' and row['exit']==answer['exit']==dict(code=0,signal=None)
  assert row['error'] is None and row['complete'] and not row['truncated'] and not row.get('cleanupUnconfirmed',False) and row['discardedObservedBytes']==0
  assert row['stderr']==answer['stderr']=='' and row['stdout'].endswith('\n')
  lines=row['stdout'].splitlines();acks=[x for x in c['protocol']['recordsBeforeSearch'] if x.startswith('cm_parm ')]+['cm_parm rnd=0'];assert lines[:len(acks)]==acks;lines=lines[len(acks):]
  assert [semantic(x) for x in lines[:len(answer['posts'])]]==answer['posts']
  assert lines[len(answer['posts']):]==['move '+answer['move']]+answer['resultRecords']
  d=raw_out/c['id'];d.mkdir(parents=True);(d/'stdout.raw').write_text(row['stdout']);(d/'stderr.raw').write_text(row['stderr'])
  (d/'stdin.reconstructed').write_text('\n'.join(c['protocol']['recordsBeforeSearch']+['cm_parm rnd',c['protocol']['searchRecord'],c['protocol']['cleanupRecord']])+'\n')
 return report

