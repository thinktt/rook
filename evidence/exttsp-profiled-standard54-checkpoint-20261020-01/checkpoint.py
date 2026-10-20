from pathlib import Path
import json,hashlib,tarfile,subprocess,os,io,stat
R=Path('/home/legolas/rook2');E=R/'evidence';C=E/'exttsp-profiled-standard54-checkpoint-20261020-01'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,x):
 with p.open('x') as f:json.dump(x,f,indent=2);f.write('\n')
def git(*args):return subprocess.check_output(['/usr/bin/git','-C',str(R),*args],text=True)
assert not git('diff','--cached','--name-only').strip()
source=json.loads((E/'bitplane-pin-summary-integration-20261020-01/source-promotion.json').read_text())['files_sha256']
for n,h in source.items():assert sha(R/n)==h,n
roots=['exttsp-profiled-wire-regression-20261020-01','exttsp-profiled-wire-parent-review-20261020-01','exttsp-profiled-whole-workload-parent-review-20261020-01','exttsp-profiled-standard54-preparation-20261020-01','exttsp-profiled-standard54-execution-20261020-01','exttsp-profiled-standard54-results-20261020-01','exttsp-profiled-games12-preparation-20261020-01']
files={};excluded={}
for name in roots:
 for p in sorted((E/name).rglob('*')):
  if not p.is_file():continue
  n=str(p.relative_to(R));assert not p.is_symlink()
  item={'sha256':sha(p),'bytes':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
  if p.name=='rook2-exact':excluded[n]=item
  else:files[n]=item
assert len(excluded)==0
archive=C/'closed-exttsp-profiled-standard54.tar.gz'
with tarfile.open(archive,'x:gz') as t:
 for n in files:t.add(R/n,arcname=n,recursive=False)
with tarfile.open(archive,'r:gz') as t:
 members=t.getmembers();assert len(members)==len(files)
 for m in members:
  z=files[m.name];data=t.extractfile(m).read();assert hashlib.sha256(data).hexdigest()==z['sha256'];assert len(data)==z['bytes'];assert oct(m.mode)==z['mode'];assert sha(R/m.name)==z['sha256']
put(C/'archive-manifest.json',{'roots':roots,'files':files,'excluded_preserved_images':excluded})
put(C/'archive-verification.json',{'complete':True,'archive_sha256':sha(archive),'bytes':archive.stat().st_size,'members_and_originals_reopened':len(files),'exact62_ELF_is_in_previous_closed_checkpoint':True,'production_source117_unchanged':True,'production':57,'experiment62':'whole54 PASS67.640360, regular12 pending','goal_complete':False})
selected=['STATUS.md','docs/decisions/0048-exttsp-profiled-layout.md']
for d,names in {
'exttsp-profiled-wire-regression-20261020-01':['README.md','summary.json','tool-terminal.json','independent-verification.json'],
'exttsp-profiled-wire-parent-review-20261020-01':['acceptance.json'],
'exttsp-profiled-whole-workload-parent-review-20261020-01':['admission.json','review.md'],
'exttsp-profiled-standard54-execution-20261020-01':['collector-terminal.json','activation-tool-terminal.json','verify-tool-terminal.json','offline-check-tool-terminal.json','independent-reconciliation.json','timings.csv'],
'exttsp-profiled-standard54-results-20261020-01':['README.md','report.json'],
'exttsp-profiled-pgo-checkpoint-20261020-01':['postcommit-verification.json','postcommit-tool-terminal.json','commit-selection.json'],
}.items():
 for n in names:selected.append('evidence/'+d+'/'+n)
selected += [str(p.relative_to(R)) for p in [archive,C/'archive-manifest.json',C/'archive-verification.json',C/'checkpoint.py']]
for n in selected:assert (R/n).is_file(),n
pins={n:sha(R/n) for n in sorted(selected)};parent=git('rev-parse','HEAD').strip()
put(C/'commit-selection.json',{'parent':parent,'files_sha256':pins,'source117_sha256':source})
subprocess.run(['/usr/bin/git','-C',str(R),'add','--',*pins],check=True)
assert set(git('diff','--cached','--name-only').splitlines())==set(pins)
for n,h in pins.items():
 assert hashlib.sha256(subprocess.check_output(['/usr/bin/git','-C',str(R),'show',':'+n])).hexdigest()==h
subprocess.run(['/usr/bin/git','-C',str(R),'diff','--cached','--check'],check=True)
msg='Record the profile-covered layout full54 result\n\nPreserve all216 raw lifetimes and the independent original replay checks.\nProduction57 remains current pending the62 regular12 follow-up.\n\nCo-authored-by: Codex GPT-6.1 Sol <codex@openai.com>\nCo-authored-by: Codex GPT-6 Astra <codex@openai.com>\nDirected-by: Tobias Toland <github@thinktt.e4ward.com>\n'
(C/'commit-message.txt').write_text(msg)
env={**os.environ,'GIT_AUTHOR_NAME':'Imp2 (Codex)','GIT_AUTHOR_EMAIL':'codex@openai.com','GIT_COMMITTER_NAME':'Imp2 (Codex)','GIT_COMMITTER_EMAIL':'codex@openai.com'}
subprocess.run(['/usr/bin/git','-C',str(R),'commit','-F',str(C/'commit-message.txt')],env=env,check=True)
head=git('rev-parse','HEAD').strip();assert git('rev-parse',head+'^').strip()==parent
assert git('show','-s','--format=%B',head).strip()==msg.strip()
assert git('show','-s','--format=%an <%ae>%n%cn <%ce>',head).strip()=='Imp2 (Codex) <codex@openai.com>\nImp2 (Codex) <codex@openai.com>'
for n,h in pins.items():assert hashlib.sha256(subprocess.check_output(['/usr/bin/git','-C',str(R),'show',head+':'+n])).hexdigest()==h;assert sha(R/n)==h
for n,h in source.items():assert sha(R/n)==h
assert not git('diff','--cached','--name-only').strip();assert not git('diff','--name-only').strip()
put(C/'postcommit-verification.json',{'complete':True,'head':head,'parent':parent,'HEAD_blobs_and_originals_verified':len(pins),'archive_members_and_originals_verified':len(files),'archive_sha256':sha(archive),'source117_unchanged':True,'trailers_and_author_committer_verified':True,'index_empty_tracked_clean':True,'production':57,'experiment62':'PASS whole54, regular12 pending','goal_complete':False})
print('CHECKPOINT_CLOSED',head,len(pins),len(files),sha(archive),flush=True)
