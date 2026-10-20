from pathlib import Path
import hashlib,json,subprocess,os,stat
R=Path('/home/legolas/rook2');E=R/'evidence';C=E/'current57-domain-delivery-checkpoint-20261020-01'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,v):
 with p.open('x') as f:json.dump(v,f,indent=2);f.write('\n')
def git(a):
 z=subprocess.run(['/usr/bin/git']+a,cwd=R,capture_output=True);assert z.returncode==0,(a,z.stderr);return z.stdout
parent=git(['rev-parse','HEAD']).decode().strip();assert parent=='a278e9d8104fdcd4fac9ea4577542953f27462c5';assert not git(['diff','--cached','--name-only'])
roots=['current57-placement-admission-review-20261020-01','current57-placement-admission-independent-review-20261020-01','current57-evaluation-window-review-20261020-01','current57-remembered-lifecycle-review-20261020-01','current57-ordinary-opportunity-review-20261020-01','current57-activity-paired-code-review-20261020-01','current57-restoration-opportunity-review-20261020-01','candidate57-delivery-readiness-20261020-01']
selected=[R/'docs/production-map.md',R/'docs/qualification-gaps.md',R/'docs/qualification-gaps-history-20261020-02.md',C/'checkpoint.py']
for name in roots:
 d=E/name;assert d.is_dir()
 selected += sorted(p for p in d.rglob('*') if p.is_file())
prior=E/'activity-kind-return-generic-checkpoint-20261020-01'
selected += [prior/n for n in ['commit-selection.json','commit-tool-terminal.json','postcommit-verification.json','postcommit-tool-terminal.json']]
assert len(set(selected))==len(selected)
for p in selected:
 assert not p.is_symlink() and p.stat().st_size<1048576,p
 with p.open('rb') as f:assert f.read(4)!=b'\x7fELF',p
manifest={str(p.relative_to(R)):{'sha256':sha(p),'bytes':p.stat().st_size,'mode':stat.S_IMODE(p.stat().st_mode)} for p in selected}
assert sum(v['bytes'] for v in manifest.values())<2097152
source=json.loads((E/'bitplane-pin-summary-integration-20261020-01/source-promotion.json').read_text())['files_sha256']
for n,h in source.items():assert sha(R/n)==h,n
put(C/'commit-selection.json',{'parent_head':parent,'selected':manifest,'source117_unchanged':source,'production':57,'new_engine_runs':0,'new_candidate_selected':False,'external_Bee_authorization_pending':True,'READY_written':False})
paths=list(manifest);git(['add','--']+paths);assert set(git(['diff','--cached','--name-only']).decode().splitlines())==set(manifest)
for n,v in manifest.items():assert hashlib.sha256(git(['show',':'+n])).hexdigest()==v['sha256']==sha(R/n)
z=subprocess.run(['/usr/bin/git','-c','core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol','diff','--cached','--check'],cwd=R,capture_output=True);(C/'whitespace.stdout').write_bytes(z.stdout);(C/'whitespace.stderr').write_bytes(z.stderr);assert z.returncode==0
message='Record native admission and lifecycle proof boundaries\n\nTie current57 arithmetic domains, local evaluation selection and cross-search table isolation to actual owners. Preserve rejected optimization studies, refresh the qualification map and prepare a locally verified opaque two-binary package without granting external execution. Production source and timing bests stay unchanged.\n\nCo-authored-by: Codex GPT-6.1 Sol <codex@openai.com>\nCo-authored-by: Codex GPT-6 Astra <codex@openai.com>\nDirected-by: Tobias Toland <github@thinktt.e4ward.com>\n';(C/'commit-message.txt').write_text(message)
assert message.rstrip().splitlines()[-3:]==['Co-authored-by: Codex GPT-6.1 Sol <codex@openai.com>','Co-authored-by: Codex GPT-6 Astra <codex@openai.com>','Directed-by: Tobias Toland <github@thinktt.e4ward.com>']
for n,v in manifest.items():assert sha(R/n)==v['sha256']
for n,h in source.items():assert sha(R/n)==h
x=os.environ.copy();x.update(GIT_AUTHOR_NAME='Imp2 (Codex)',GIT_AUTHOR_EMAIL='codex@openai.com',GIT_COMMITTER_NAME='Imp2 (Codex)',GIT_COMMITTER_EMAIL='codex@openai.com')
z=subprocess.run(['/usr/bin/git','commit','--file',str(C/'commit-message.txt')],cwd=R,env=x,capture_output=True);(C/'commit.stdout').write_bytes(z.stdout);(C/'commit.stderr').write_bytes(z.stderr);assert z.returncode==0,z.stderr
head=git(['rev-parse','HEAD']).decode().strip();print('DOMAIN_AND_LOCAL_PACKAGE_COMMITTED',head,len(manifest),sum(v['bytes'] for v in manifest.values()))
