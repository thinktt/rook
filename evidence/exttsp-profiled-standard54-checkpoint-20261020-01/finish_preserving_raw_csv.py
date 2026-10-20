from pathlib import Path
import json,hashlib,tarfile,subprocess,os
R=Path('/home/legolas/rook2');E=R/'evidence';C=E/'exttsp-profiled-standard54-checkpoint-20261020-01'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,x):
 with p.open('x') as f:json.dump(x,f,indent=2);f.write('\n')
def git(*args):return subprocess.check_output(['/usr/bin/git','-C',str(R),*args],text=True)
x=json.loads((C/'commit-selection.json').read_text());pins=x['files_sha256'];parent=x['parent'];source=x['source117_sha256'];archive=C/'closed-exttsp-profiled-standard54.tar.gz';files=json.loads((C/'archive-manifest.json').read_text())['files']
assert git('rev-parse','HEAD').strip()==parent
assert set(git('diff','--cached','--name-only').splitlines())==set(pins)
for n,h in pins.items():
 assert sha(R/n)==h
 assert hashlib.sha256(subprocess.check_output(['/usr/bin/git','-C',str(R),'show',':'+n])).hexdigest()==h
raw='evidence/exttsp-profiled-standard54-execution-20261020-01/timings.csv'
assert raw in pins and sha(R/raw)==files[raw]['sha256']
b=(R/raw).read_bytes();assert len(b.splitlines())==55 and b.count(b'\r\n')==55
assert all(line==line.rstrip() for line in b.replace(b'\r\n',b'\n').splitlines())
z=subprocess.run(['/usr/bin/git','-C',str(R),'diff','--cached','--check'],capture_output=True)
(C/'initial-whitespace.stdout').write_bytes(z.stdout);(C/'initial-whitespace.stderr').write_bytes(z.stderr)
assert z.returncode==2 and not z.stderr
# Every reported whitespace error names only the byte-exact original CSV.
assert all(line.startswith(raw.encode()+b':') for line in z.stdout.splitlines() if b': trailing whitespace.' in line)
subprocess.run(['/usr/bin/git','-C',str(R),'diff','--cached','--check','--',*[n for n in pins if n!=raw]],check=True)
with tarfile.open(archive,'r:gz') as t:
 members=t.getmembers();assert len(members)==len(files)
 for m in members:
  assert hashlib.sha256(t.extractfile(m).read()).hexdigest()==files[m.name]['sha256'];assert sha(R/m.name)==files[m.name]['sha256']
for n,h in source.items():assert sha(R/n)==h
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
