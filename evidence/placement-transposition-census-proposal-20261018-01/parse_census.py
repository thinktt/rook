#!/usr/bin/env python3
"""Offline only: complete exact-placement census decoding and bounded models."""
from pathlib import Path
import argparse,hashlib,json,struct
MAGIC=b'R2PLC001';SIZE=124;MAX=20*1024**3
CAPACITIES=(1024,4096,16384,65536)
MASK=(1<<32)-1

def keys():
    # Independent general POSITION-IDENTITY definition; never read fixtures/native tables.
    state=0x01234567;coeff=[]
    for _ in range(1920):
        state=(0xbb40e62d*state+1)%(1<<32)
        signed=state if state<(1<<31) else state-(1<<32)
        high=(signed//65536)&MASK
        state=(0xbb40e62d*state+1)%(1<<32)
        coeff.append(high^state)
    return tuple(tuple((coeff[80*t+10*(s//8)+s%8+1],coeff[960+80*t+10*(s//8)+s%8+1]) for s in range(64)) for t in range(12))
KEYS=keys()
def fingerprints(board):
    assert len(board)==64
    primary=secondary=0
    for square,tag in enumerate(board):
        if tag==0:continue
        assert tag in (1,2,3,4,5,6,9,10,11,12,13,14),'invalid raw Piece tag'
        a,b=KEYS[2*((tag&7)-1)+int(bool(tag&8))][square]
        primary^=a;secondary^=b
    return primary,secondary

def index_word(primary,secondary):return primary^(((secondary<<16)|(secondary>>16))&MASK)
class Model:
    def __init__(self,capacity):
        assert capacity>0 and capacity&(capacity-1)==0
        self.slots=[None]*capacity
        self.stats={k:[0]*4 for k in ['probes','hits','empty_misses','replacements','hit_activity_queries']}
    def visit(self,board,payload,word,kind,queries):
        at=word&(len(self.slots)-1);old=self.slots[at];s=self.stats;s['probes'][kind]+=1
        if old is None:s['empty_misses'][kind]+=1
        elif old[0]==board:
            assert old[1]==payload,'exact placement changed pure producer payload'
            s['hits'][kind]+=1;s['hit_activity_queries'][kind]+=queries
        else:s['replacements'][kind]+=1
        self.slots[at]=(board,payload)

class IdentityVerifier:
    def __init__(self):self.slots=[None]*65536;self.reconstructions=0;self.hits=0
    def verify(self,board,actual):
        # Verification-cache key admission is exact board equality, not its recorded hash.
        # Its index may use recorded identity, but every miss reconstructs independent keys.
        at=index_word(*actual)&65535;old=self.slots[at]
        if old is not None and old[0]==board:
            expected=old[1];self.hits+=1
        else:expected=fingerprints(board);self.reconstructions+=1
        assert actual==expected,'board fingerprint inconsistency'
        self.slots[at]=(board,expected)

def parse(raw_path,report_path,expected_pid=None):
    raw_path=Path(raw_path);report_path=Path(report_path)
    digest=hashlib.sha256();verify=IdentityVerifier();epochs=[];ordinal=0;epoch=0;kind=0
    total=[0]*4;total_q=[0]*4;current=[0]*4;current_q=[0]*4;models={};raw_bytes=0
    with raw_path.open('rb',buffering=2*1024*1024) as raw,report_path.open('rb') as report:
        def report_row():
            line=report.readline(8193);assert line and len(line)<=8192 and line.endswith(b'\n'),'missing/overlong report record'
            def unique(pairs):
                result={}
                for k,v in pairs:
                    assert k not in result,'duplicate report key';result[k]=v
                return result
            def invalid_constant(value):raise AssertionError('nonfinite JSON value')
            row=json.loads(line,object_pairs_hook=unique,parse_constant=invalid_constant);assert isinstance(row,dict)
            for k,v in row.items():
                if k in ['id','kind','epochs','ordinal','raw_bytes','pid','byte_limit']:assert type(v) is int and v>=0,'noninteger counter'
                if k in ['encounters','queries']:assert isinstance(v,list) and len(v)==4 and all(type(x) is int and x>=0 for x in v),'invalid counter vector'
            return row
        header=raw.read(24);assert len(header)==24,'partial header'
        digest.update(header);raw_bytes=24
        magic,version,size,limit=struct.unpack('<8sIIQ',header)
        assert magic==MAGIC and version==1 and size==SIZE,'unknown census format'
        assert 24+SIZE+4096<=limit<=MAX,'invalid byte ceiling'
        rh=report_row();assert set(rh)=={'type','schema','pid','byte_limit'}
        assert rh['type']=='header' and rh['schema']=='rook2-placement-census-v1' and rh['byte_limit']==limit
        assert type(rh['pid']) is int and rh['pid']>0
        if expected_pid is not None:assert rh['pid']==expected_pid,'native PID differs'
        def close_epoch():
            if not epoch:return
            expected={'type':'epoch','id':epoch,'kind':kind,'encounters':current,'queries':current_q}
            assert report_row()==expected,'native epoch counters disagree'
            epochs.append({'id':epoch,'kind':'new' if kind==1 else 'begin_search','encounters':current.copy(),'activity_queries':current_q.copy(),'capacities':{str(c):m.stats for c,m in models.items()}})
        while True:
            record=raw.read(SIZE);assert len(record)==SIZE,'missing end marker or partial record'
            digest.update(record);raw_bytes+=SIZE;assert raw_bytes<=limit,'raw exceeds byte ceiling'
            tag,fresh,age,reserved,ep,seq=struct.unpack_from('<BBBBQQ',record)
            assert reserved==0,'nonzero reserved field'
            board=record[20:84];payload=record[84:116];queries=struct.unpack_from('<Q',record,108)[0]
            identity=struct.unpack_from('<II',record,116)
            if tag in (1,2):
                assert fresh==age==0 and payload==bytes(32),'invalid lifecycle payload'
                assert ep==epoch+1 and seq==ordinal,'out-of-order lifecycle'
                verify.verify(board,identity);close_epoch();epoch=ep;kind=tag
                current=[0]*4;current_q=[0]*4;models={c:Model(c) for c in CAPACITIES}
            elif tag==3:
                assert epoch>0 and ep==epoch and seq==ordinal+1,'out-of-order encounter'
                assert fresh in (0,1),'unknown flags';ordinal=seq
                verify.verify(board,identity);word=index_word(*identity);category=2*fresh+int(age!=0)
                current[category]+=1;current_q[category]+=queries;total[category]+=1;total_q[category]+=queries
                for model in models.values():model.visit(board,payload,word,category,queries)
            elif tag==4:
                assert fresh==age==0 and ep==epoch and seq==ordinal and board==bytes(64) and record[84:108]==bytes(24) and identity==(0,0),'invalid end record'
                assert queries==sum(total_q),'end query total differs';close_epoch()
                expected={'type':'end','epochs':epoch,'ordinal':ordinal,'raw_bytes':raw_bytes,'encounters':total,'queries':total_q}
                assert report_row()==expected,'native whole-process totals disagree'
                assert raw.read(1)==b'' and report.read(1)==b'','trailing stream data'
                break
            else:raise AssertionError('unknown record type')
    assert raw_bytes==raw_path.stat().st_size and raw_bytes+report_path.stat().st_size<=limit,'private files exceed byte ceiling'
    with report_path.open('rb') as f:report_hash=hashlib.file_digest(f,'sha256').hexdigest()
    return {'complete':True,'format_version':1,'record_bytes':SIZE,'pid':rh['pid'],'limit':limit,'raw_bytes':raw_bytes,'report_bytes':report_path.stat().st_size,'raw_sha256':digest.hexdigest(),'report_sha256':report_hash,'epochs':epochs,'encounters':total,'activity_queries':total_q,'total_encounters':ordinal,'identity_verification':{'capacity':65536,'reconstructions':verify.reconstructions,'exact_board_verification_cache_hits':verify.hits},'class_order':['normal_age0','normal_aged','fresh_age0','fresh_aged'],'capacities':list(CAPACITIES),'index':'(primary ^ secondary.rotate_left(16)) & (capacity-1); actual fingerprints independently checked from board','limits':['Exact board equality admits a hypothetical hit; fingerprints select index only','All actual producers still executed; hit R is represented semantic work to retain, not eliminated work','Occupied replacements do not identify compulsory/capacity misses or global unique placements','Bounded hypothetical counts only, no CPU/cache benefit or production-cache decision']}

def main():
    a=argparse.ArgumentParser();a.add_argument('raw');a.add_argument('report');a.add_argument('--output',required=True);a.add_argument('--native-pid',type=int);x=a.parse_args()
    result=parse(x.raw,x.report,x.native_pid)
    with Path(x.output).open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps({'complete':True,'encounters':result['total_encounters'],'epochs':len(result['epochs'])}))
if __name__=='__main__':main()
