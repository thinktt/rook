from pathlib import Path
import subprocess,json,hashlib,os
R=Path('/home/legolas/rook2');E=R/'evidence';C=E/'activity-kind-return-generic-checkpoint-20261020-01'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(args,**kw):
 z=subprocess.run(['/usr/bin/git']+args,cwd=R,capture_output=True,**kw);assert z.returncode==0,(args,z.stderr);return z.stdout
assert run(['rev-parse','HEAD']).decode().strip()=='041faa51417fbdde77ecdcf07e85a46f44955ad5'
assert not run(['diff','--cached','--name-only'])
selected=[R/'STATUS.md',R/'docs/production-map.md',R/'docs/decisions/0046-activity-kind-return.md']
selected += [C/n for n in ['archive_and_verify.py','commit_checkpoint.py','README.md','closed-activity-kind-return-generic.tar.gz','member-manifest.json','excluded-members.json','verification.json','tool-terminal.json']]
for dirname,files in {
 'activity-kind-return-generic-decision-20261020-01':['decision.json','README.md'],
 'activity-kind-return-generic-screen-20261020-01':['independent-reconciliation.json','tool-terminal.json','independent-tool-terminal.json'],
 'activity-kind-return-parent-review-20261020-01':['source-freeze.json','source-semantic-acceptance.json','backend-parent-acceptance.json','tool-terminal.json'],
 'activity-kind-return-backend-review-20261020-01':['review.md'],
 'activity-kind-return-source-20261020-01':['source-proof.json','closure.json'],
 'activity-kind-return-selection-20261020-01':['selection.json'],
 'current57-retained-origin-review-20261020-01':['review.md','proof.json','parent-acceptance.json','production-map-reviewed-before.txt'],
 'current57-retained-origin-independent-review-20261020-01':['review.md','proof.json','closure.json'],
 'current57-activity-kind-boundary-review-20261020-01':['review.md'],
 'current57-activity-ray-gather-review-20261020-01':['review.md'],
 'current57-activity-tag-review-20261020-01':['review.md'],
 'deferred-capture-clear-generic-checkpoint-20261020-01':['commit-selection.json','commit-tool-terminal.json','postcommit-verification.json','postcommit-tool-terminal.json'],
}.items():selected += [E/dirname/n for n in files]
assert len(selected)==len(set(selected))
manifest={str(p.relative_to(R)):sha(p) for p in selected}
source=json.loads((C/'verification.json').read_text())['canonical_source117_unchanged']
for n,h in source.items():assert sha(R/n)==h,n
(C/'commit-selection.json').write_text(json.dumps({'parent_head':'041faa51417fbdde77ecdcf07e85a46f44955ad5','selected_sha256':manifest,'source117_unchanged':source},indent=2)+'\n')
args=list(manifest);run(['add','--']+args)
assert set(run(['diff','--cached','--name-only']).decode().splitlines())==set(manifest)
for n,h in manifest.items():assert hashlib.sha256(run(['show',':'+n])).hexdigest()==h,n
z=subprocess.run(['/usr/bin/git','-c','core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol','diff','--cached','--check'],cwd=R,capture_output=True);(C/'whitespace-check.stdout').write_bytes(z.stdout);(C/'whitespace-check.stderr').write_bytes(z.stderr);assert z.returncode==0
message='Park the Activity group-return experiment\n\nRetain production57 after the fixed generic screen costs1.036641% more CPU. Preserve original tests, backend captures, all70 fresh replays and independently checked raw evidence, plus scoped native retained-origin proof.\n\nCo-authored-by: Codex GPT-6.1 Sol <codex@openai.com>\nCo-authored-by: Codex GPT-6 Astra <codex@openai.com>\nDirected-by: Tobias Toland <github@thinktt.e4ward.com>\n'
(C/'commit-message.txt').write_text(message)
trailers=['Co-authored-by: Codex GPT-6.1 Sol <codex@openai.com>','Co-authored-by: Codex GPT-6 Astra <codex@openai.com>','Directed-by: Tobias Toland <github@thinktt.e4ward.com>'];assert message.rstrip().splitlines()[-3:]==trailers
for n,h in manifest.items():assert sha(R/n)==h
for n,h in source.items():assert sha(R/n)==h
ident='Imp2 (Codex)';email='codex@openai.com';env=os.environ.copy();env.update(GIT_AUTHOR_NAME=ident,GIT_AUTHOR_EMAIL=email,GIT_COMMITTER_NAME=ident,GIT_COMMITTER_EMAIL=email)
z=subprocess.run(['/usr/bin/git','commit','--file',str(C/'commit-message.txt')],cwd=R,env=env,capture_output=True);(C/'commit.stdout').write_bytes(z.stdout);(C/'commit.stderr').write_bytes(z.stderr);print(z.stdout.decode(),z.stderr.decode());assert z.returncode==0
head=run(['rev-parse','HEAD']).decode().strip();print('COMMITTED60',head,len(manifest))
