from pathlib import Path
import subprocess,json,hashlib,re,os
R=Path('/home/legolas/rook2');C=R/'evidence/current57-domain-delivery-checkpoint-20261020-01'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def git(a):
 z=subprocess.run(['/usr/bin/git']+a,cwd=R,capture_output=True);assert z.returncode==0,(a,z.stderr);return z.stdout
s=json.loads((C/'commit-selection.json').read_text());assert git(['rev-parse','HEAD']).decode().strip()==s['parent_head']
assert set(git(['diff','--cached','--name-only']).decode().splitlines())==set(s['selected'])
for n,v in s['selected'].items():assert sha(R/n)==v['sha256']==hashlib.sha256(git(['show',':'+n])).hexdigest()
raws={'evidence/candidate57-delivery-readiness-20261020-01/rook2.readelf.stdout','evidence/candidate57-delivery-readiness-20261020-01/rook2-diag.readelf.stdout'}
text=(C/'whitespace.stdout').read_text();flagged=set(re.findall(r'^([^\n]+?):\d+: trailing whitespace\.$',text,re.M));assert flagged==raws
lines=text.splitlines();assert len(lines)%2==0 and all(lines[i].endswith('trailing whitespace.') and lines[i+1].startswith('+') for i in range(0,len(lines),2))
ids=json.loads((R/'evidence/candidate57-delivery-readiness-20261020-01/runtime-identities.json').read_text())
for n in raws:assert sha(R/n)==ids[Path(n).name.replace('.readelf.stdout','')]['stdout_sha256']
paths=[n for n in s['selected'] if n not in raws]
z=subprocess.run(['/usr/bin/git','-c','core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol','diff','--cached','--check','--']+paths,cwd=R,capture_output=True);(C/'whitespace-authored.stdout').write_bytes(z.stdout);(C/'whitespace-authored.stderr').write_bytes(z.stderr);assert z.returncode==0
(C/'raw-whitespace-disposition.json').write_text(json.dumps({'initial_stage':'b4dfc3/1','all_whitespace_findings_exact_two_readelf_raws':sorted(raws),'raws_byte_match_recorded_original_readelf_stdout':True,'all_other_selected_files_whitespace_check_pass':True,'raw_normalization':False,'source_changes':False},indent=2)+'\n')
for n,h in s['source117_unchanged'].items():assert sha(R/n)==h
message='Record native admission and lifecycle proof boundaries\n\nTie current57 arithmetic domains, local evaluation selection and cross-search table isolation to actual owners. Preserve rejected optimization studies, refresh the qualification map and prepare a locally verified opaque two-binary package without granting external execution. Production source and timing bests stay unchanged.\n\nCo-authored-by: Codex GPT-6.1 Sol <codex@openai.com>\nCo-authored-by: Codex GPT-6 Astra <codex@openai.com>\nDirected-by: Tobias Toland <github@thinktt.e4ward.com>\n';(C/'commit-message.txt').write_text(message);assert message.rstrip().splitlines()[-3:]==['Co-authored-by: Codex GPT-6.1 Sol <codex@openai.com>','Co-authored-by: Codex GPT-6 Astra <codex@openai.com>','Directed-by: Tobias Toland <github@thinktt.e4ward.com>']
x=os.environ.copy();x.update(GIT_AUTHOR_NAME='Imp2 (Codex)',GIT_AUTHOR_EMAIL='codex@openai.com',GIT_COMMITTER_NAME='Imp2 (Codex)',GIT_COMMITTER_EMAIL='codex@openai.com')
z=subprocess.run(['/usr/bin/git','commit','--file',str(C/'commit-message.txt')],cwd=R,env=x,capture_output=True);(C/'commit.stdout').write_bytes(z.stdout);(C/'commit.stderr').write_bytes(z.stderr);assert z.returncode==0,z.stderr
print('DOMAIN_LOCAL_PACKAGE_COMMITTED',git(['rev-parse','HEAD']).decode().strip(),len(s['selected']),sum(v['bytes'] for v in s['selected'].values()))
