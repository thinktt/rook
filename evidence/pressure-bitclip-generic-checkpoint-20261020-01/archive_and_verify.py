from pathlib import Path
import json,hashlib,tarfile,stat
R=Path('/home/legolas/rook2');E=R/'evidence';C=E/'pressure-bitclip-generic-checkpoint-20261020-01'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,x):
 with p.open('x') as f:json.dump(x,f,indent=2);f.write('\n')
names=['pressure-bitclip-selection-20261020-01', 'pressure-bitclip-design-20261020-01', 'pressure-bitclip-source-20261020-01', 'pressure-bitclip-parent-review-20261020-01', 'pressure-bitclip-generic-build-20261020-01', 'pressure-bitclip-native-20261020-01', 'pressure-bitclip-backend-review-20261020-01', 'pressure-bitclip-generic-screen-preparation-20261020-01', 'pressure-bitclip-generic-screen-execution-20261020-01', 'pressure-bitclip-generic-screen-20261020-01', 'pressure-bitclip-generic-decision-20261020-01', 'current57-pressure-bitclip-review-20261020-01', 'current57-root-collapse-reachability-review-20261020-01', 'current57-empty-hint-witness-design-20261020-01', 'current57-domain-delivery-checkpoint-20261020-01']
files=[];excluded={}
for name in names:
 d=E/name;assert d.is_dir()
 for p in sorted(d.rglob('*')):
  if not p.is_file():continue
  assert not p.is_symlink(),p
  with p.open('rb') as f:magic=f.read(4)
  if magic==b'\x7fELF':excluded[str(p.relative_to(R))]={'sha256':sha(p),'bytes':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))};continue
  files.append(p)
assert len(excluded)==1 and next(iter(excluded)).endswith('/rook2-exact'),excluded
members={str(p.relative_to(R)):{'sha256':sha(p),'bytes':p.stat().st_size,'mode':stat.S_IMODE(p.stat().st_mode)} for p in files}
put(C/'member-manifest.json',members);put(C/'excluded-members.json',excluded)
a=C/'closed-pressure-bitclip-generic.tar.gz'
with tarfile.open(a,'w:gz') as t:
 for p in files:t.add(p,arcname=str(p.relative_to(R)),recursive=False)
with tarfile.open(a,'r:gz') as t:
 rows=t.getmembers();assert len(rows)==len(members) and {m.name for m in rows}==set(members)
 for m in rows:
  v=members[m.name];data=t.extractfile(m).read();assert hashlib.sha256(data).hexdigest()==v['sha256'] and len(data)==v['bytes'] and m.mode==v['mode'];assert sha(R/m.name)==v['sha256']
for n,v in excluded.items():assert sha(R/n)==v['sha256']
source=json.loads((E/'bitplane-pin-summary-integration-20261020-01/source-promotion.json').read_text())['files_sha256']
for n,h in source.items():assert sha(R/n)==h,n
put(C/'verification.json',{'complete':True,'archive':a.name,'sha256':sha(a),'bytes':a.stat().st_size,'members':len(members),'original_bytes':sum(v['bytes'] for v in members.values()),'all_original_and_archive_member_bytes_modes_match':True,'all_excluded_ELF_bytes_preserved_at_named_paths':True,'canonical_source117_unchanged':source,'production':57,'experiment61':'PARK','new_native_runs_by_archiver':0})
(C/'README.md').write_text("# Closed experiment61 and bounded source-investigation checkpoint\n\nThe archive preserves selected source/build/native/backend/fixed70 evidence,\nunchanged methods, every original raw run and independent replay checks. One\nfrozen generic ELF is excluded by exact path/hash/size/mode and preserved at its\noriginal location. All archived bytes, modes and original files were reopened.\nNo source or raw artifact is normalized. Initial parent/author metadata guards\nand failures are preserved without candidate-source repair or an extra build.\n\nExperiment61 passes198 library tests and70 original replay checks. Its single\ngeneric screen improves0.259022%,6/7lower,worst1.006301279, missing the fixed0.5%\naggregate gate. Park without retry, PGO or adoption. Production57 remains exact\nover117 source files; best whole54/whole12 remain69.051049/689.783349s on Vic.\nNo qualification claim or new external execution authority follows.\n\nBounded source investigations reject the positive-saturation root-collapse\nshortcut, retain the negative chain's missing actual restricted-entry/return\npremises, and decline an uncontrolled tiny-TT hint search. These are not runtime\ncounterexamples or new admission rules. Prior domain/delivery commit receipts\nretain the exact raw-readelf whitespace failure and disposition. Candidate57's\nseparate opaque bundle remains frozen locally with authorization pending.\n")
print('CLOSED61_ARCHIVE',len(members),sha(a),a.stat().st_size)
