from pathlib import Path
import json,hashlib,tarfile,stat
R=Path('/home/legolas/rook2');E=R/'evidence';C=E/'activity-kind-return-generic-checkpoint-20261020-01'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,x):
 with p.open('x') as f:json.dump(x,f,indent=2);f.write('\n')
names=['activity-kind-return-selection-20261020-01','activity-kind-return-source-20261020-01','activity-kind-return-parent-review-20261020-01','activity-kind-return-generic-build-20261020-01','activity-kind-return-native-20261020-01','activity-kind-return-backend-review-20261020-01','activity-kind-return-generic-screen-preparation-20261020-01','activity-kind-return-generic-screen-execution-20261020-01','activity-kind-return-generic-screen-20261020-01','activity-kind-return-generic-decision-20261020-01','current57-retained-origin-review-20261020-01','current57-retained-origin-independent-review-20261020-01','current57-activity-tag-review-20261020-01','current57-activity-ray-gather-review-20261020-01','current57-activity-kind-boundary-review-20261020-01','current57-activity-boundary-discriminator-20261020-01']
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
a=C/'closed-activity-kind-return-generic.tar.gz'
with tarfile.open(a,'w:gz') as t:
 for p in files:t.add(p,arcname=str(p.relative_to(R)),recursive=False)
with tarfile.open(a,'r:gz') as t:
 rows=t.getmembers();assert len(rows)==len(members) and {m.name for m in rows}==set(members)
 for m in rows:
  v=members[m.name];data=t.extractfile(m).read();assert hashlib.sha256(data).hexdigest()==v['sha256'] and len(data)==v['bytes'] and m.mode==v['mode'];assert sha(R/m.name)==v['sha256']
for n,v in excluded.items():assert sha(R/n)==v['sha256']
source=json.loads((E/'bitplane-pin-summary-integration-20261020-01/source-promotion.json').read_text())['files_sha256']
for n,h in source.items():assert sha(R/n)==h,n
put(C/'verification.json',{'complete':True,'archive':a.name,'sha256':sha(a),'bytes':a.stat().st_size,'members':len(members),'original_bytes':sum(v['bytes'] for v in members.values()),'all_original_and_archive_member_bytes_modes_match':True,'all_excluded_ELF_bytes_preserved_at_named_paths':True,'canonical_source117_unchanged':source,'production':57,'experiment60':'PARK','new_native_runs_by_archiver':0})
(C/'README.md').write_text('# Closed experiment60 and retained-origin checkpoint\n\nThe archive preserves the complete selected source/build/native/backend/fixed70\nrecords, unchanged methods, all original raw runs and independent oracle checks.\nOne frozen generic ELF is excluded by exact path/hash/size/mode and preserved at\nits original location. All archived member bytes, modes and original files were\nreopened and verified. No source or raw artifact is normalized.\n\nExperiment60 passes195 library tests and70 original replay checks but costs\n1.036641% more CPU,0/7 lower,worst1.023642. It is parked without retry, PGO or\nsource adoption. Production57 remains exact across117 source members; best\nwhole54/whole12 remain69.051049/689.783349s on Vic. No qualification is claimed.\n\nThe archive also preserves bounded negative Activity opportunity reviews,\nthe conditional kind-boundary review and independent native retained-origin\nproof/acceptance, including the exact reviewed production map before its new\nscoped conclusion was appended. These do not close all production obligations.\n')
print('CLOSED60_ARCHIVE',len(members),sha(a),a.stat().st_size)
