from pathlib import Path
import hashlib,json
E=Path(__file__).resolve().parent
source=(E/'proposed-src/activity.rs').read_text()
assert 'static PRESSURE_VALUES: [u8; 256] = {' in source
assert 'let weights = [16u8, 24, 8, 16, 8, 16, 8, 16];' in source
assert 'i32::from(PRESSURE_VALUES[usize::from(mark)])' in source
weights=(16,24,8,16,8,16,8,16)
payload=bytes(sum(weight for bit,weight in enumerate(weights) if mark & (1<<bit)) for mark in range(256))
for mark,actual in enumerate(payload):
    old=16*bool(mark&1)+24*bool(mark&2)+8*(mark&0x54).bit_count()+16*(mark&0xa8).bit_count()
    assert actual==old,(mark,actual,old)
assert min(payload)==0 and max(payload)==112
assert hashlib.sha256(payload).hexdigest()=='a001834848c9ebea7c64fd3385aacf4c26068a72771047a1d1876382fa0cde63'
(E/'pressure-values.bin').write_bytes(payload)
proof={'schema':'offline-exhaustive-pressure-v1','checked_inputs':256,'input_domain':'all u8, including every coexistence pattern','weights':weights,'maximum':max(payload),'minimum':min(payload),'payload_bytes':len(payload),'payload_sha256':hashlib.sha256(payload).hexdigest(),'all_match_original_count_ones_formula':True,'constant_evaluation_bound':'all intermediate sums nonnegative and <=112; u8 additions exact','native_test_or_compiler_runs':0,'scope':'analytical source/formula proof; generated lowering remains unverified'}
(E/'exhaustive-proof.json').write_text(json.dumps(proof,sort_keys=True,indent=2)+'\n')
print(json.dumps(proof,sort_keys=True))
