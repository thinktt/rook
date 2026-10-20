#!/usr/bin/env python3
"""Offline general EVAL-KING-SHELTER algebra; no fixtures or native execution."""
from pathlib import Path
import hashlib,json,re
P=Path(__file__).resolve().parent
# Decoded normalized tier formula, matching the released general rule.
def tiers(code):
 weak=code&1;queen=(code>>1)&1;rook=(code>>2)&3;minor=(code>>4)&3;pawn=code>>6
 if not queen:return 14*int(rook%2==1)+24*int(rook>=2)+8*int(minor>0)
 return (48 if pawn>0 or weak else 20)+18*int(rook>0 or minor>0)
# Independent direct-bit characterization of the same rule.
def bits(code):
 if code&2:return 20+28*int(bool(code&0xc1))+18*int(bool(code&0x3c))
 return 14*int(bool(code&4))+24*int(bool(code&8))+8*int(bool(code&0x30))
source=(P/'shelter.rs').read_text();old=(P/'basis-shelter.rs').read_text()
m=re.search(r'static RING_BASE_VALUE: \[u8; 256\] = \[(.*?)\];',source,re.S);assert m
values=[int(x) for x in re.findall(r'\d+',m[1])];assert len(values)==256
assert bytes(values)==(P/'ring-base-values.bin').read_bytes()
assert values==json.loads((P/'ring-base-values.json').read_text())['values']
for code,value in enumerate(values):assert value==tiers(code)==bits(code),(code,value)
assert min(values)==0 and max(values)==66
# Invert exactly the two allowed source hunks, proving every other byte unchanged.
a=old.index('            let weak = code & 1;');b=old.index('            if influence.code(color, square) >= 2 {',a)
replacement='            let mut value = i32::from(RING_BASE_VALUE[code as usize]);\n'
assert source.count(replacement)==1
restored=source.replace(replacement,old[a:b],1)
static_start=restored.index('// Opposing byte base value for EVAL-KING-SHELTER;')
static_end=restored.index('pub fn compute(\n',static_start)
restored=restored[:static_start]+restored[static_end:]
assert restored==old
marker='#[cfg(test)]';assert old.count(marker)==1
assert old[old.index(marker):]==source[source.index(marker):]
assert old.count('#[test]')==source.count('#[test]')==6
sha=lambda data:hashlib.sha256(data).hexdigest()
result=dict(complete=True,all256_exact=True,minimum=0,maximum=66,declared_static_bytes=256,payload_sha256=sha(bytes(values)),basis_sha256=sha(old.encode()),proposed_sha256=sha(source.encode()),inverse_reconstruction_exact=True,existing_shelter_test_bodies_byte_identical=6,new_native_tests=0,whole_native_declarations_unchanged=185,engine_runs=0,scope='Finite exhaustive byte algebra and exact source inversion only; no Rust parse/build/test/codegen/timing claim.')
with (P/'offline-proof.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps(result,indent=2))
