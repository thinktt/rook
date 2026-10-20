#!/usr/bin/env python3
"""Close already-terminal and independently reconciled current51 game12 evidence."""
import csv,gzip,hashlib,json,os,tarfile,datetime
from pathlib import Path
P=Path(__file__).resolve().parent
D=P.parent/'tactical-check-mask-games12-preparation-20261020-01'
H={0,1,2,3,4,5,8,9,10,11,12,13}
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_text())
def save(p,v):
 with p.open('x') as f:json.dump(v,f,indent=2,allow_nan=False);f.write('\n')
def main():
 assert set(os.sched_getaffinity(0))==H
 assert os.environ['PATH']=='/usr/bin:/bin'
 # Refuse closure until both real collector and independent terminals exist.
 actual_collector=load(D/'collector-tool-terminal.json')
 actual_independent=load(D/'independent-tool-terminal.json')
 for terminal in (actual_collector,actual_independent):
  assert terminal['actual_tool_terminal_observed'] is True
  assert terminal['exit_code']==0 and terminal['terminal_chunk_id']
 assert actual_collector['initial_chunk_id']=='0a76e2' and actual_collector['session_id']==27581
 assert actual_independent['proof_sha256']==sha(D/'reconciliation/result.json')
 terminals=load(D/'collector-terminals.json')
 assert terminals['games12']['actual_terminal_chunk']==actual_collector['terminal_chunk_id']
 assert terminals['games12']['exit_code']==0 and terminals['games12']['actual_terminal_chunk']
 r=load(D/'reconciliation/result.json')
 assert r['complete'] and not r['failures'] and r['descriptive_only'] and not r['qualified_performance_pass']
 after=load(D/'input-after.json');assert after['complete'] and not after['failures']
 sm=load(D/'games12/summary.json');assert sm['complete'] and sm['complete12'] and sm['failure'] is None
 assert len(sm['runs'])==48 and len(sm['game_summaries'])==12
 g=r['games12'];assert (g['lifetimes'],g['warmups'],g['measured'],g['searches'])==(48,12,36,2528)
 plan=load(D/'plan.json')
 assert sha(D/'plan.json')=='18077f9cf5924b4fdfc375cd26f17608faf7a6e27578ce121afa2d070015737f'
 assert plan['engine_sha256']=='48ee57b14e436338037e21f0f01f0f340959d7b05771f5cd759a3eab38d655b4'
 for f,h in plan['dependency_sha256'].items():assert sha(f)==h,('changed authority input',f)
 rows=[]
 for game in plan['ordered_games']:
  u=g['units'][game];a,b=u['local'],u['reference']
  rows.append(dict(game=game,local_cpu_median_s=a['median'],local_cpu_minimum_s=a['minimum'],local_cpu_maximum_s=a['maximum'],reference_cpu_median_s=b['median'],reference_cpu_minimum_s=b['minimum'],reference_cpu_maximum_s=b['maximum'],reported_ratio=u['median_ratio']))
 with (P/'unit-medians.csv').open('x',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 report=dict(scope='Reported-only current51 whole-native game12 CPU; no qualification',engine_sha256=plan['engine_sha256'],lifetimes=48,warmups=12,measured=36,searches=2528,semantic_posts=g['semantic_posts'],local_sum_unit_medians_s=g['sum_unit_medians_s'],reference_sum_unit_medians_s=g['reference_sum_unit_medians_s'],ratio_of_sums=g['ratio_of_sums'],cpu_context=g['cpu_context'],unresolved_measured_search_cpu=g['unresolved_measured_search_cpu'],units=g['units'],independent_reconciliation_sha256=sha(D/'reconciliation/result.json'),actual_collector_terminals=terminals,qualified_performance_pass=False)
 save(P/'reference-comparison.json',report)
 paths=sorted(x for x in D.rglob('*') if x.is_file())
 assert all(not x.is_symlink() for x in D.rglob('*'))
 manifest={str(x.relative_to(D)):dict(sha256=sha(x),bytes=x.stat().st_size,mode=x.stat().st_mode&0o7777) for x in paths}
 save(P/'archive-inputs.json',manifest)
 archive=P/'closed-games12.tar.gz'
 with archive.open('xb') as raw:
  with gzip.GzipFile(filename='',mode='wb',fileobj=raw,mtime=0) as gz:
   with tarfile.open(fileobj=gz,mode='w|') as tar:
    for x in paths:
     k=str(x.relative_to(D));a=manifest[k];assert sha(x)==a['sha256']
     ti=tarfile.TarInfo(k);ti.size=a['bytes'];ti.mode=a['mode'];ti.mtime=0;ti.uid=ti.gid=0;ti.uname=ti.gname=''
     with x.open('rb') as f:tar.addfile(ti,f)
 seen=[]
 with tarfile.open(archive,'r:gz') as tar:
  for m in tar:
   assert m.isfile() and m.name in manifest and m.name not in seen
   a=manifest[m.name];f=tar.extractfile(m);h=hashlib.sha256();count=0
   while True:
    b=f.read(1048576)
    if not b:break
    h.update(b);count+=len(b)
   assert m.size==count==a['bytes'] and m.mode==a['mode'] and h.hexdigest()==a['sha256']
   assert m.uid==m.gid==m.mtime==0 and m.uname==m.gname==''
   assert sha(D/m.name)==a['sha256'];seen.append(m.name)
 assert set(seen)==set(manifest)
 save(P/'archive-closure.json',dict(complete=True,archive_sha256=sha(archive),archive_bytes=archive.stat().st_size,members=len(seen),unpacked_bytes=sum(v['bytes'] for v in manifest.values()),all_member_headers_modes_bytes_and_originals_reopened=True,archive_inputs_sha256=sha(P/'archive-inputs.json'),independent_reconciliation_sha256=sha(D/'reconciliation/result.json'),created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat()))
 readme=f"""# Current51 complete game12 CPU

Exact own-PGO image `{plan['engine_sha256']}`. All48 fresh native lifetimes passed:12 warmups and36 measured repetitions,2528 exact searches total. All raw streams and native exits were independently reconciled before this report.

The sum of12 per-game median whole-native CPU times is **{g['sum_unit_medians_s']:.6f}s**. The historical supplied Rust-PGO reference is **{g['reference_sum_unit_medians_s']:.6f}s**; reported ratio **{g['ratio_of_sums']:.9f}**. This is a cross-machine/window reported comparison, not a qualification pass or universal conversion factor.

`unit-medians.csv` contains all12 medians and ranges. `reference-comparison.json` retains all three CPU samples per unit and descriptive ratio envelopes. Whole-native wait4 user+system includes the disclosed small pre-exec prefix; this is not internal prepared-loop CPU. Per-search quantized CPU remains unresolved where unavailable. No PMU measurements or external full-game gate are implied. CPU14/15 field deltas are retained with iowait separate.

`closed-games12.tar.gz` preserves every file in the closed preparation/raw directory; `archive-inputs.json` names every member and its exact bytes/mode. The archiver reopened every member and compared each original. `archive-closure.json` binds the archive. Source/tool/spec authority identities and original comparator streams remain inside that closure.
"""
 with (P/'README.md').open('x') as f:f.write(readme)
 print(json.dumps(dict(complete=True,local_sum_unit_medians_s=g['sum_unit_medians_s'],ratio_of_sums=g['ratio_of_sums'],archive_sha256=sha(archive))))
if __name__=='__main__':main()
