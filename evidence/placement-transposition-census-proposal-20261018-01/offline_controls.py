#!/usr/bin/env python3
"""Synthetic offline format/accounting tests only; no native, build, search or fixtures."""
from pathlib import Path
import json,struct,sys
sys.dont_write_bytecode=True
import parse_census as m
P=Path(__file__).resolve().parent

def build(epochs,limit=1024*1024):
    raw=bytearray(struct.pack('<8sIIQ',m.MAGIC,1,m.SIZE,limit));reports=[{'type':'header','schema':'rook2-placement-census-v1','pid':123,'byte_limit':limit}]
    total=[0]*4;queries=[0]*4;ordinal=0
    def record(tag,fresh,age,epoch,seq,board,payload,identity):return struct.pack('<BBBBQQ',tag,fresh,age,0,epoch,seq)+board+payload+struct.pack('<II',*identity)
    root=bytearray(64);root[4]=6;root[60]=14;root=bytes(root)
    for ep,(kind,events) in enumerate(epochs,1):
        raw.extend(record(kind,0,0,ep,ordinal,root,bytes(32),m.fingerprints(root)));counts=[0]*4;rq=[0]*4
        for board,payload,fresh,age in events:
            ordinal+=1;q=struct.unpack_from('<Q',payload,24)[0];c=2*fresh+int(age!=0);counts[c]+=1;rq[c]+=q;total[c]+=1;queries[c]+=q
            raw.extend(record(3,fresh,age,ep,ordinal,board,payload,m.fingerprints(board)))
        reports.append({'type':'epoch','id':ep,'kind':kind,'encounters':counts,'queries':rq})
    raw.extend(record(4,0,0,len(epochs),ordinal,bytes(64),bytes(24)+struct.pack('<Q',sum(queries)),(0,0)))
    reports.append({'type':'end','epochs':len(epochs),'ordinal':ordinal,'raw_bytes':len(raw),'encounters':total,'queries':queries})
    return bytes(raw),reports

def main():
    out=P/'offline-controls-01';assert not out.exists();out.mkdir();checks=[]
    board=bytearray(64);board[4]=6;board[60]=14;board[1]=2;board=bytes(board)
    payload=struct.pack('<6iQ',1,-2,3,4,5,-6,7)
    raw,report=build([(1,[]),(2,[(board,payload,0,9),(board,payload,0,9),(board,payload,1,0)]),(2,[(board,payload,0,0)])])
    def run(name,data,rows,accepted=False,pid=123):
        d=out/name;d.mkdir();a=d/'raw.bin';b=d/'report.jsonl';a.write_bytes(data)
        b.write_text(''.join(json.dumps(x)+'\n' for x in rows) if isinstance(rows,list) else rows)
        try:result=m.parse(a,b,pid)
        except (AssertionError,ValueError,KeyError,TypeError,struct.error) as e:
            assert not accepted,(name,repr(e));checks.append({'name':name,'rejected':True,'error':repr(e)});return
        assert accepted,name;checks.append({'name':name,'accepted':True});return result
    valid=run('complete-epochs',raw,report,True)
    assert valid['total_encounters']==4 and len(valid['epochs'])==3 and valid['epochs'][0]['encounters']==[0]*4
    assert valid['encounters']==[1,2,1,0]
    for cap in m.CAPACITIES:
        assert valid['epochs'][1]['capacities'][str(cap)]['hits']==[0,1,1,0]
        assert valid['epochs'][2]['capacities'][str(cap)]['hits']==[0]*4
    a,b=build([]);run('no-epochs-complete',a,b,True)
    def mutation(offset,data):return raw[:offset]+data+raw[offset+len(data):]
    bad=[('magic',mutation(0,b'?')),('version',mutation(8,struct.pack('<I',2))),('record-size',mutation(12,struct.pack('<I',116))),('partial-header',raw[:23]),('partial-record',raw[:-1]),('missing-end',raw[:-m.SIZE]),('unknown-record',mutation(24,b'\x07')),('reserved',mutation(27,b'\x01')),('unknown-fresh',mutation(24+2*m.SIZE+1,b'\x02')),('epoch-gap',mutation(24+4,struct.pack('<Q',2))),('ordinal-gap',mutation(24+2*m.SIZE+12,struct.pack('<Q',2))),('bad-tag',mutation(24+2*m.SIZE+20,b'\x10')),('bad-fingerprint',mutation(24+2*m.SIZE+116,b'\x00\x00\x00\x00')),('trailing-raw',raw+b'X'),('payload-mismatch',mutation(24+3*m.SIZE+84,struct.pack('<i',999))),('ceiling-too-large',mutation(16,struct.pack('<Q',m.MAX+1)))]
    for name,data in bad:run(name,data,report)
    copied=json.loads(json.dumps(report));copied[2]['encounters'][1]+=1;run('native-epoch-mismatch',raw,copied)
    copied=json.loads(json.dumps(report));copied[-1]['queries'][0]+=1;run('native-total-mismatch',raw,copied)
    copied=json.loads(json.dumps(report));copied[-1]['encounters'][0]=True;run('boolean-counter',raw,copied)
    run('missing-native-end',raw,report[:-1]);run('native-extra-record',raw,report+[report[-1]])
    run('wrong-pid',raw,report,pid=124)
    a,b=build([(1,[(board,payload,0,1)]*80)],limit=4244);run('combined-byte-ceiling',a,b)
    # Force a direct-map collision independently of actual hash distribution.
    model=m.Model(1);other=bytearray(board);other[1]=0;other[18]=2;other=bytes(other)
    model.visit(board,payload,0,0,7);model.visit(other,payload,0,0,7);model.visit(board,payload,0,0,7)
    assert model.stats['hits']==[0]*4 and model.stats['replacements']==[2,0,0,0]
    checks.append({'name':'exact-board-required-after-index-collision','accepted':True})
    verifier=m.IdentityVerifier();identity=m.fingerprints(board);verifier.verify(board,identity)
    bad_identity=(identity[0]^0x10000,identity[1])
    try:verifier.verify(board,bad_identity)
    except AssertionError:checks.append({'name':'identity-verification-cache-cannot-hide-corruption','rejected':True})
    else:raise AssertionError('corrupted identity admitted')
    result={'complete':True,'synthetic_format_controls_only':True,'cases':checks,'native_runs':0,'builds':0,'collections':0,'parser_capacity_policy':list(m.CAPACITIES)}
    (out/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'complete':True,'controls':len(checks),'native_runs':0}))
if __name__=='__main__':main()
