#!/usr/bin/env python3
"""Independently parse retained original streams; never execute an engine."""
import hashlib,json,re
from pathlib import Path
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
SPEC=Path('/home/legolas/king-spec/conformance')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text())
def semantic(s,wire=False):
    if s.startswith('move '):return dict(type='move',move=s[5:])
    if s.startswith('stat01: '):
        m=re.fullmatch(r'stat01:\s+(-?\d+)\s+(\d+)\s+(-?\d+)\s+(\d+)\s+(\d+)(?: (.*))?',s);assert m
        a,b,c,d,e=map(int,m.groups()[:5]);return dict(type='status',engineCentiseconds=a,searchId=b,depthToken=c,remaining=d,total=e,pv=(m[6] or '').replace('0','O'))
    m=re.fullmatch(r'\s*(-?\d+)\s+([+-]?\d+)\s+(\d+)\s+(\d+)(?:\s+(.*))?',s);assert m,s
    a,b,c,d=map(int,m.groups()[:4]);pv=(m[5] or '').strip().replace('0','O')
    return dict(type='post',depthToken=a,evaluation=b,engineCentiseconds=c,searchId=d,pv=pv) if wire else dict(depth=a,score=b,workThousands=c,searchId=d,pv=pv)
def main():
    assert load(OUT/'tool-terminal.json')['exit_code']==0
    inputs=load(OUT/'input-closure.json');assert all(sha(Path(p))==h for p,h in inputs.items())
    report=load(OUT/'profile-all.stdout');work=load(SPEC/'profiling/workloads.json');oracle=load(SPEC/'profiling/replay-oracle.json')
    assert report['status']=='pass' and len(report['results'])==len(work['cases'])==len(oracle['cases'])==54
    assert report['selectedCases']==[c['id'] for c in work['cases']]
    raw=OUT/'independent-retained-replays';raw.mkdir()
    for row,c in zip(report['results'],work['cases']):
        expected=next(x for x in oracle['cases'] if x['id']==c['id'])
        assert row['case']==c['id'] and row['status']=='pass' and row['exit']==expected['exit']==dict(code=0,signal=None)
        assert row['error'] is None and row['complete'] and not row['truncated'] and not row.get('cleanupUnconfirmed',False)
        assert row['discardedObservedBytes']==0 and row['stderr']==expected['stderr']==''
        assert row['stdout'].endswith('\n')
        lines=row['stdout'].splitlines();acks=[x for x in c['protocol']['recordsBeforeSearch'] if x.startswith('cm_parm ')]+['cm_parm rnd=0']
        assert lines[:len(acks)]==acks;lines=lines[len(acks):]
        assert [semantic(x) for x in lines[:len(expected['posts'])]]==expected['posts']
        assert lines[len(expected['posts']):]==['move '+expected['move']]+expected['resultRecords']
        d=raw/c['id'];d.mkdir();(d/'stdout.raw').write_text(row['stdout']);(d/'stderr.raw').write_text(row['stderr'])
        # Reconstructed input from the exact released checker, not an observed stdin tap.
        stdin='\n'.join(c['protocol']['recordsBeforeSearch']+['cm_parm rnd',c['protocol']['searchRecord'],c['protocol']['cleanupRecord']])+'\n'
        (d/'stdin.reconstructed').write_text(stdin)
    wire=ROOT/'evidence/admission-combined95-interruption-wire-20261018';wr=load(wire/'receipt.json');fixtures=load(SPEC/'fixtures/interrupted-sessions-v1.json')['cases']
    assert wr['pass'] and len(wr['results'])==len(fixtures)==8
    searches=0
    for row,c in zip(wr['results'],fixtures):
        assert row['id']==c['id'] and row['status']=='pass' and row['complete_streams'] and row['exit_code']==row['observed_exit_code']==0
        for k,v in row['raw'].items():
            p=wire/c['id']/(k+'.raw');assert p.stat().st_size==v['bytes'] and sha(p)==v['sha256']
        assert (wire/c['id']/'stderr.raw').read_bytes()==b''
        text=(wire/c['id']/'stdout.raw').read_text();assert text.endswith('\n');lines=iter(text.splitlines());stdin=[]
        for request,expected in zip(c['request']['input']['searches'],c['expected']['results']):
            commands=request['commands'];stdin+=commands+[f"time {request['allowanceCs']}",'cm_parm','go']+request['queued']
            for command in commands:
                if command.startswith('cm_parm '):assert next(lines)==' '.join(command.split())
            assert next(lines)=='cm_parm'
            assert [semantic(next(lines),True) for _ in expected['events']]==expected['events']
            if request['queued'] and request['queued'][-1]=='force':assert next(lines)=='aborting search ...'
            searches+=1
        assert list(lines)==[]
        assert (wire/c['id']/'stdin.raw').read_text()=='\n'.join(stdin+['quit'])+'\n'
    assert searches==24
    native=ROOT/'evidence/admission-combined95-native-validation-20261018';nr=load(native/'native-verification.json');assert nr['complete'] and nr['inputs_stable']
    for target,count in [('rook2',149),('rook2-dev',2)]:
        s=(native/(target+'-tests.stdout')).read_text();assert len(re.findall(r'^test .* \.\.\. ok$',s,re.M))==count
        assert f'test result: ok. {count} passed; 0 failed;' in s
    build=ROOT/'evidence/admission-combined95-native-build-20261018';br=load(build/'receipt.json')
    assert sha(build/'rook2-exact')==br['binary_output']['sha256']==wr['engine_sha256_before']==wr['engine_sha256_after']
    result=dict(status='pass',strict_replays=54,interruption_fixtures=8,interruption_searches=24,native_tests=151,artifact_sha256=sha(build/'rook2-exact'),scope='Independent parsing of original retained streams; UNTIMED, no CPU gain claim',input_closure_sha256=sha(OUT/'input-closure.json'),driver_sha256=sha(Path(__file__)),raw_files_sha256={str(p.relative_to(ROOT)):sha(p) for p in sorted(raw.rglob('*')) if p.is_file()})
    with (OUT/'independent-verification.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps({k:v for k,v in result.items() if k!='raw_files_sha256'}))
if __name__=='__main__':main()
