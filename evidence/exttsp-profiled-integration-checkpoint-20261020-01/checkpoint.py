from pathlib import Path
import hashlib,json,os,subprocess,tarfile,io,stat
R=Path('/home/legolas/rook2');E=R/'evidence';C=E/'exttsp-profiled-integration-checkpoint-20261020-01'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
def git(*args,**kw):return subprocess.check_output(['/usr/bin/git',*args],cwd=R,**kw)
assert not git('diff','--cached','--name-only').strip(),'Preexisting staged changes'
promotion=json.loads((E/'exttsp-profiled-integration-20261020-01/source-promotion.json').read_text())
for n,h in promotion['files_sha256'].items():assert sha(R/n)==h,n
for p,h in [(E/'exttsp-profiled-pgo-use-build-20261020-01/rook2-exact',promotion['ordinary_image_sha256']),(E/'bitplane-pin-summary-conformance-build-20261020-01/rook2-diag-exact',promotion['diagnostic_image_sha256']),(E/'bitplane-pin-summary-pgo-training-20261020-01/merged.profdata',promotion['profile_sha256'])]:assert sha(p)==h,p
roots=['exttsp-profiled-games12-execution-20261020-01','exttsp-profiled-games12-results-20261020-01','exttsp-profiled-integration-20261020-01','exttsp-profiled-integration-preparation-20261020-01','exttsp-profiled-games12-parent-review-20261020-01','exttsp-profiled-games12-postpromotion-review-20261020-01','current57-remembered-retention-parent-review-20261020-01','current57-remembered-diagnostic-admission-parent-review-20261020-01','current57-learned-cutoff-lifetime-parent-review-20261020-01','current57-learned-remembered-independent-review-20261020-01','current62-learned-remembered-parent-acceptance-20261020-01','current62-branch-cache-study-feasibility-20261020-01']
files=[]
for root in roots:
 for p in sorted((E/root).rglob('*')):
  assert not p.is_symlink(),p
  if p.is_file():files.append(p)
old=E/'exttsp-profiled-standard54-checkpoint-20261020-01'
late=['commit-selection.json','commit-message.txt','initial-commit-tool-terminal.json','initial-whitespace.stdout','initial-whitespace.stderr','finish_preserving_raw_csv.py','postcommit-verification.json','postcommit-tool-terminal.json']
files += [old/n for n in late]
manifest={str(p.relative_to(R)):{'sha256':sha(p),'bytes':p.stat().st_size,'mode':stat.S_IMODE(p.stat().st_mode)} for p in files}
archive=C/'closed-exttsp-profiled-integration.tar.gz'
assert not archive.exists()
with tarfile.open(archive,'w:gz',compresslevel=6) as t:
 for p in files:t.add(p,arcname=str(p.relative_to(R)),recursive=False)
with tarfile.open(archive,'r:gz') as t:
 members=t.getmembers();assert len(members)==len(manifest)
 for m in members:
  v=manifest[m.name];b=t.extractfile(m).read();assert len(b)==v['bytes'] and hashlib.sha256(b).hexdigest()==v['sha256'] and m.mode==v['mode']
  assert sha(R/m.name)==v['sha256'],m.name
save(C/'archive-manifest.json',manifest)
save(C/'archive-verification.json',{'complete':True,'members':len(manifest),'original_bytes':sum(v['bytes'] for v in manifest.values()),'archive_sha256':sha(archive),'originals_reopened_byte_exact':True,'modes_verified':True,'native_images_not_embedded':True,'source117_revalidated':True})
# Raw CSV and strict whitespace failure captures remain exact inside the archive.
selected=['tools/build.py','STATUS.md','docs/decisions/0048-exttsp-profiled-layout.md','docs/production-build.md','docs/production-map.md','docs/qualification-gaps.md','docs/production-map-history-20261020-03.md','docs/qualification-gaps-history-20261020-03.md','docs/research/remaining-performance.md']
for root in roots:
 if root=='exttsp-profiled-games12-execution-20261020-01':continue
 selected += [str(p.relative_to(R)) for p in sorted((E/root).rglob('*')) if p.is_file()]
selected += [str((E/'exttsp-profiled-games12-execution-20261020-01'/n).relative_to(R)) for n in ['collector-terminals.json','independent-tool-terminals.json','input-before.json','input-after.json','reconciliation/result.json']]
selected += [str((old/n).relative_to(R)) for n in late if n not in ['initial-whitespace.stdout','initial-whitespace.stderr']]
selected += [str(p.relative_to(R)) for p in [archive,C/'archive-manifest.json',C/'archive-verification.json',C/'checkpoint.py']]
assert len(set(selected))==len(selected)
message='Adopt the validated profile-covered compiler layout\n\nRetain candidate62 and close its regular12 timing record. Preserve raw evidence,\nexplicit unchanged-source test reuse and outstanding qualification scope.\n\nCo-authored-by: Codex GPT-6.1 Sol <codex@openai.com>\nCo-authored-by: Codex GPT-6 Astra <codex@openai.com>\nDirected-by: Tobias Toland <github@thinktt.e4ward.com>\n'
(C/'commit-message.txt').write_text(message)
selection={n:sha(R/n) for n in selected};save(C/'commit-selection.json',selection)
git('add','--',*selected)
actual=set(git('diff','--cached','--name-only','-z').decode().strip('\0').split('\0'));assert actual==set(selected),(actual-set(selected),set(selected)-actual)
for n,h in selection.items():assert hashlib.sha256(git('show',':'+n)).hexdigest()==h,n
# Permit literal CRLF in historical raw files only; do not change global configuration.
git('-c','core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol','diff','--cached','--check')
for n,h in promotion['files_sha256'].items():assert sha(R/n)==h,n
commit_env=dict(os.environ,GIT_AUTHOR_NAME='Imp2 (Codex)',GIT_AUTHOR_EMAIL='codex@openai.com',GIT_COMMITTER_NAME='Imp2 (Codex)',GIT_COMMITTER_EMAIL='codex@openai.com')
assert message.endswith('Co-authored-by: Codex GPT-6.1 Sol <codex@openai.com>\nCo-authored-by: Codex GPT-6 Astra <codex@openai.com>\nDirected-by: Tobias Toland <github@thinktt.e4ward.com>\n')
print(git('commit','--file',str(C/'commit-message.txt'),env=commit_env).decode())
head=git('rev-parse','HEAD').decode().strip()
assert git('show','-s','--format=%B','HEAD').decode().strip()==message.strip()
assert git('show','-s','--format=%an <%ae>|%cn <%ce>','HEAD').decode().strip()=='Imp2 (Codex) <codex@openai.com>|Imp2 (Codex) <codex@openai.com>'
for n,h in selection.items():assert hashlib.sha256(git('show','HEAD:'+n)).hexdigest()==h and sha(R/n)==h,n
for n,v in manifest.items():assert sha(R/n)==v['sha256'],n
for n,h in promotion['files_sha256'].items():assert sha(R/n)==h,n
assert not git('diff','--cached','--name-only').strip()
save(C/'postcommit-verification.json',{'complete':True,'head':head,'selected_files':len(selected),'archive_members':len(manifest),'archive_sha256':sha(archive),'all_head_blobs_and_originals_equal':True,'current_source117_equal':True,'identities_and_trailers_verified':True,'index_empty':True})
print(json.dumps({'complete':True,'commit':head,'files':len(selected),'archive_members':len(manifest),'archive_sha256':sha(archive)}))
