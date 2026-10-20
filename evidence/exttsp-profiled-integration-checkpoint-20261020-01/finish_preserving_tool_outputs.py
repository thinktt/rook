from pathlib import Path
import hashlib,json,os,subprocess,tarfile
R=Path('/home/legolas/rook2');E=R/'evidence';C=E/'exttsp-profiled-integration-checkpoint-20261020-01'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
def git(*a,**kw):return subprocess.check_output(['/usr/bin/git',*a],cwd=R,**kw)
selection=json.loads((C/'commit-selection.json').read_text());selected=list(selection)
manifest=json.loads((C/'archive-manifest.json').read_text());archive=C/'closed-exttsp-profiled-integration.tar.gz'
promotion=json.loads((E/'exttsp-profiled-integration-20261020-01/source-promotion.json').read_text())
assert set(git('diff','--cached','--name-only','-z').decode().strip('\0').split('\0'))==set(selected)
for n,h in selection.items():assert sha(R/n)==h and hashlib.sha256(git('show',':'+n)).hexdigest()==h,n
v=json.loads((C/'archive-verification.json').read_text());assert sha(archive)==v['archive_sha256']
with tarfile.open(archive,'r:gz') as t:
 assert len(t.getmembers())==len(manifest)
 for m in t.getmembers():
  q=manifest[m.name];b=t.extractfile(m).read();assert hashlib.sha256(b).hexdigest()==q['sha256'] and len(b)==q['bytes'] and m.mode==q['mode'] and sha(R/m.name)==q['sha256']
raw=['evidence/current62-branch-cache-study-feasibility-20261020-01/annotator-help.stderr','evidence/current62-branch-cache-study-feasibility-20261020-01/callgrind-help.stdout']
check=subprocess.run(['/usr/bin/git','-c','core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol','diff','--cached','--check'],cwd=R,capture_output=True)
assert check.returncode==2 and not check.stderr
(C/'original-tool-whitespace.stdout').write_bytes(check.stdout)
for line in check.stdout.decode().splitlines():
 if not line.startswith('+'):assert any(line.startswith(n+':') for n in raw),line
for n in raw:assert selection[n]==manifest[n]['sha256']
git('-c','core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol','diff','--cached','--check','--',*[n for n in selected if n not in raw])
for n,h in promotion['files_sha256'].items():assert sha(R/n)==h,n
message=(C/'commit-message.txt').read_text()
# Resume the reviewed commit tail after exact original stage/archive verification.
original=(C/'checkpoint.py').read_text();tail=original[original.index('commit_env='):]
exec(compile(tail,str(C/'checkpoint.py')+'[verified commit tail]','exec'))
