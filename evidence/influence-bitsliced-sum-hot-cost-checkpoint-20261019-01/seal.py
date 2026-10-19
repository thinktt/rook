#!/usr/bin/env python3
"""Seal completed diagnostic evidence; never runs an engine or profiler."""
from pathlib import Path
import gzip,hashlib,json,tarfile,os
P=Path(__file__).resolve().parent;E=P.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_text())
def save(p,a):
 with Path(p).open('x') as f:json.dump(a,f,indent=2);f.write('\n')
def main():
 assert set(os.sched_getaffinity(0))=={0,1,2,3,4,5,8,9,10,11,12,13}
 roots={'raw':Path('/home/legolas/rook2-private/influence-bitsliced-sum-hot-cost-20261019-01'),'preparation':E/'influence-bitsliced-sum-hot-cost-preparation-20261019-01','canary-preparation':E/'influence-bitsliced-sum-hot-cost-supervision-check-preparation-20261019-01','canary-execution':E/'influence-bitsliced-sum-hot-cost-supervision-check-execution-20261019-01','parent-review':E/'influence-bitsliced-sum-hot-cost-parent-review-20261019-01'}
 r=roots['raw'];a=load(r/'provenance.json');v=load(r/'independent-verification.json')
 assert a['complete'] and a['failure'] is None and v['complete'] and v['original_checkReplay_cases']==2 and v['native_engine_runs']==0
 for f in ('tool-terminal.json','verify-tool-terminal.json'):
  t=load(r/f);assert t['actual_tool_terminal_observed'] and t['exit_code']==0 and t['terminal_chunk_id']
 files={}
 for prefix,root in roots.items():
  for p in sorted(root.rglob('*')):
   assert not p.is_symlink(),str(p)
   if p.is_file():files[prefix+'/'+str(p.relative_to(root))]=p
 manifest={k:{'sha256':sha(f),'bytes':f.stat().st_size,'mode':f.stat().st_mode&0o7777} for k,f in files.items()};save(P/'archive-inputs.json',manifest)
 archive=P/'closed-current43-instruction-study.tar.gz'
 with archive.open('xb') as raw:
  with gzip.GzipFile(filename='',mode='wb',fileobj=raw,mtime=0) as gz:
   with tarfile.open(fileobj=gz,mode='w|') as t:
    for k in sorted(files):
     f=files[k];q=manifest[k];assert sha(f)==q['sha256'];m=tarfile.TarInfo(k);m.size=q['bytes'];m.mode=q['mode'];m.mtime=0;m.uid=m.gid=0;m.uname=m.gname=''
     with f.open('rb') as stream:t.addfile(m,stream)
 seen=set()
 with tarfile.open(archive,'r:gz') as t:
  for m in t:
   assert m.isfile() and m.name in manifest and m.name not in seen;q=manifest[m.name];z=t.extractfile(m).read()
   assert len(z)==m.size==q['bytes'] and hashlib.sha256(z).hexdigest()==q['sha256']==sha(files[m.name]);assert m.mode==q['mode'] and m.uid==m.gid==m.mtime==0 and m.uname==m.gname=='';seen.add(m.name)
 assert seen==set(manifest)
 out={'complete':True,'archive_sha256':sha(archive),'archive_bytes':archive.stat().st_size,'members':len(manifest),'unpacked_bytes':sum(q['bytes'] for q in manifest.values()),'archive_inputs_sha256':sha(P/'archive-inputs.json'),'all_member_headers_modes_bytes_and_originals_reopened':True,'collector_actual':'6e7a77/0','independent_actual':'704fc5/0','event_scope':a['event_scope'],'native_instrumented_lifetimes':2,'new_engine_or_profiler_runs':0,'qualification':False};save(P/'archive-closure.json',out);print(json.dumps(out))
if __name__=='__main__':main()
