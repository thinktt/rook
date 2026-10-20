from pathlib import Path
import hashlib,json,tarfile,stat,subprocess,os
R=Path('/home/legolas/rook2');E=R/'evidence';C=E/'current62-branch-cache-checkpoint-20261020-01'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
def git(*args,**kw):return subprocess.check_output(['/usr/bin/git',*args],cwd=R,**kw)
assert not git('diff','--cached','--name-only').strip()
roots=['current62-branch-cache-parent-selection-20261020-01','current62-branch-cache-preparation-20261020-01','current62-branch-cache-parser-20261020-01','current62-branch-cache-parser-20261020-02','current62-branch-cache-parser-review-20261020-01','current62-branch-cache-execution-20261020-01','current62-branch-cache-parent-review-20261020-01','current62-branch-cache-gap-review-20261020-01','current62-capture-override-opportunity-20261020-01','current62-branch-cache-results-20261020-01']
files={}
for name in roots:
 for p in sorted((E/name).rglob('*')):
  assert not p.is_symlink()
  if p.is_file():files[str(p.relative_to(R))]=p
O=Path('/home/legolas/rook2-private/current62-branch-cache-20261020-01')
for p in sorted(O.rglob('*')):
 assert not p.is_symlink()
 if p.is_file():files['private-output/'+str(p.relative_to(O))]=p
late=E/'exttsp-profiled-integration-checkpoint-20261020-01'
late_names=['commit-message.txt','commit-selection.json','initial-tool-terminal.json','finish_preserving_tool_outputs.py','original-tool-whitespace.stdout','postcommit-verification.json','postcommit-tool-terminal.json']
for n in late_names:files[str((late/n).relative_to(R))]=late/n
manifest={n:{'original_path':str(p),'sha256':sha(p),'bytes':p.stat().st_size,'mode':stat.S_IMODE(p.stat().st_mode)} for n,p in files.items()}
archive=C/'closed-current62-branch-cache.tar.gz';assert not archive.exists()
with tarfile.open(archive,'w:gz',compresslevel=6) as t:
 for n,p in files.items():t.add(p,arcname=n,recursive=False)
with tarfile.open(archive,'r:gz') as t:
 assert len(t.getmembers())==len(manifest)
 for m in t.getmembers():
  v=manifest[m.name];b=t.extractfile(m).read();assert hashlib.sha256(b).hexdigest()==v['sha256'] and len(b)==v['bytes'] and m.mode==v['mode'] and sha(Path(v['original_path']))==v['sha256']
save(C/'archive-manifest.json',manifest)
save(C/'archive-verification.json',{'complete':True,'members':len(manifest),'archive_sha256':sha(archive),'original_bytes':sum(v['bytes'] for v in manifest.values()),'every_original_and_archive_member_reopened':True,'binary_images_not_embedded':True,'original_strict_study_complete':False,'partial_postmortem_checks_complete':True})
promotion=json.loads((E/'exttsp-profiled-integration-20261020-01/source-promotion.json').read_text())
for n,h in promotion['files_sha256'].items():assert sha(R/n)==h,n
runtime=json.loads((O/'input-closure.json').read_text())
for n,h in runtime.items():assert sha(Path(n))==h,n
selected=['STATUS.md','docs/research/remaining-performance.md']
# Preserve complete raw/text/patch/private/large payloads in verified archive;
# stage small reviewable code and structured evidence separately.
for n,p in files.items():
 if not n.startswith('private-output/') and p.suffix in ['.md','.py','.json'] and p.stat().st_size<=262144:selected.append(n)
selected += [str(p.relative_to(R)) for p in [archive,C/'archive-manifest.json',C/'archive-verification.json',C/'checkpoint.py']]
assert len(selected)==len(set(selected))
selection={n:sha(R/n) for n in selected};save(C/'commit-selection.json',selection)
message='Preserve the current62 diagnostic and partial attribution scope\n\nKeep the strict counter study incomplete, retain two unknown simulated Ir,\nand preserve the separate checked postmortem without a profiling retry.\n\nCo-authored-by: Codex GPT-6.1 Sol <codex@openai.com>\nCo-authored-by: Codex GPT-6 Astra <codex@openai.com>\nDirected-by: Tobias Toland <github@thinktt.e4ward.com>\n'
(C/'commit-message.txt').write_text(message)
git('add','--',*selected)
assert set(git('diff','--cached','--name-only','-z').decode().strip('\0').split('\0'))==set(selected)
for n,h in selection.items():assert hashlib.sha256(git('show',':'+n)).hexdigest()==h,n
git('diff','--cached','--check')
assert message.endswith('Co-authored-by: Codex GPT-6.1 Sol <codex@openai.com>\nCo-authored-by: Codex GPT-6 Astra <codex@openai.com>\nDirected-by: Tobias Toland <github@thinktt.e4ward.com>\n')
env=dict(os.environ,GIT_AUTHOR_NAME='Imp2 (Codex)',GIT_AUTHOR_EMAIL='codex@openai.com',GIT_COMMITTER_NAME='Imp2 (Codex)',GIT_COMMITTER_EMAIL='codex@openai.com')
print(git('commit','--file',str(C/'commit-message.txt'),env=env).decode())
head=git('rev-parse','HEAD').decode().strip()
assert git('show','-s','--format=%B','HEAD').decode().strip()==message.strip()
assert git('show','-s','--format=%an <%ae>|%cn <%ce>','HEAD').decode().strip()=='Imp2 (Codex) <codex@openai.com>|Imp2 (Codex) <codex@openai.com>'
for n,h in selection.items():assert sha(R/n)==h and hashlib.sha256(git('show','HEAD:'+n)).hexdigest()==h,n
for n,v in manifest.items():assert sha(Path(v['original_path']))==v['sha256'],n
for n,h in promotion['files_sha256'].items():assert sha(R/n)==h,n
for n,h in runtime.items():assert sha(Path(n))==h,n
assert not git('diff','--cached','--name-only').strip()
save(C/'postcommit-verification.json',{'complete':True,'head':head,'selected_files':len(selected),'archive_members':len(manifest),'archive_sha256':sha(archive),'all_HEAD_blobs_originals_source117_runtime130_equal':True,'author_committer_trailers_verified':True,'index_empty':True})
print(json.dumps({'complete':True,'commit':head,'files':len(selected),'archive_members':len(manifest),'archive_sha256':sha(archive)}))
