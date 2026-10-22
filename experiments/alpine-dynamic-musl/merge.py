import hashlib,json,subprocess
from pathlib import Path
B=Path(__file__).resolve().parent
x=json.loads((B/'training/result.json').read_text());assert x['complete'] and x['strictCases']==54
raw=sorted((B/'profile-raw').glob('*.profraw'));assert len(raw)==54
for p in raw:assert hashlib.sha256(p.read_bytes()).hexdigest()==x['rawProfileSha256']['/work/profile-raw/'+p.name]
for name in ('merged.profdata','independent-merged.profdata'):
 cmd=['/usr/bin/llvm-profdata-19','merge','-o',str(B/name),*map(str,raw)]
 cp=subprocess.run(cmd,capture_output=True,text=True,timeout=60)
 assert cp.returncode==0 and not cp.stderr,(cp.returncode,cp.stderr)
assert (B/'merged.profdata').read_bytes()==(B/'independent-merged.profdata').read_bytes()
x.update(profileSha256=hashlib.sha256((B/'merged.profdata').read_bytes()).hexdigest(),independentRemergeIdentical=True,mergeToolVersion=subprocess.check_output(['/usr/bin/llvm-profdata-19','--version'],text=True),mergeToolSha256=hashlib.sha256(Path('/usr/bin/llvm-profdata-19').resolve().read_bytes()).hexdigest())
(B/'training.json').write_text(json.dumps(x,indent=2)+'\n')
print(json.dumps({'strictTrainingCases':54,'profileSha256':x['profileSha256'],'independentRemergeIdentical':True}))
