from pathlib import Path
import json,hashlib,os
HERE=Path(__file__).parent
load=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):
 with p.open('x') as f:json.dump(d,f,indent=2);f.write('\n')
def check():
 p=load(HERE/'plan.json');assert sorted(os.sched_getaffinity(0))==p['affinity'] and os.environ['TMPDIR']=='/home/legolas/rook2-build-tmp';assert load(HERE/'execution-clearance.json')['authorized'];S=Path(p['source']);F=Path(p['frozen_source']);assert all(sha(S/n)==v and sha(F/n)==v for n,v in p['source_sha256'].items());assert all(sha(Path(n))==v for n,v in p['fixtures'].items());return p
