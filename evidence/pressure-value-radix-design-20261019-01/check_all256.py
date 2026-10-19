"""Offline arithmetic analysis only: no Rust import/parser/compiler/native test."""
from pathlib import Path
import hashlib,json
out=Path(__file__).resolve().parent
payload=[]
max_high=max_low=0
for x in range(256):
    high=((x>>2)&3)+((x>>4)&3)+(x>>6)
    low=16*(x&1)+24*((x>>1)&1)
    radix=8*high+low
    old=16*bool(x&1)+24*bool(x&2)+8*(x&0x54).bit_count()+16*(x&0xa8).bit_count()
    paired=(x&0x33)+((x>>2)&0x33)
    previous27=8*((paired&15)+(paired>>4)+(x&1)+((x>>1)&1))
    assert radix==old==previous27,(x,radix,old,previous27)
    assert 0<=high<=9 and 0<=low<=40 and 0<=radix<=112
    max_high=max(max_high,high);max_low=max(max_low,low)
    payload.append(radix)
result={'scope':'offline analytical equality, not Rust/native tests or generated-code evidence','checked_inputs':256,'domain':'all u8 marks including weak/strong coexistence','matches_original_count_ones':True,'matches_experiment27_algebra':True,'max_three_high_digits':max_high,'max_knight_subtotal':max_low,'max_score':max(payload),'min_score':min(payload),'payload_sha256':hashlib.sha256(bytes(payload)).hexdigest(),'candidate_selected':False,'native_runs':0}
(out/'all256-result.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
print(json.dumps(result,sort_keys=True))
