"""Bounded offline data/algebra check only; no Rust or production candidate."""
from pathlib import Path
import hashlib,json,re
P=Path(__file__).resolve().parent
ROOT=Path('/home/legolas/rook2')
inputs=[ROOT/'src/influence.rs',ROOT/'src/relation_table.rs',ROOT/'src/types.rs',ROOT/'scripts/generate_relation_table.py',Path('/home/legolas/king-spec/spec/evaluation-relations.md')]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
pins={str(p):sha(p) for p in inputs}
source=(ROOT/'src/relation_table.rs').read_text()
data=source[source.index('pub(crate) static RELATIONS'):].split('=',1)[1]
values=[{'U':0,'C':1,'F':2}[x] for x in re.findall(r'\b[UCF]\b',data)]
assert len(values)==4*65536
rows=[values[i*65536:(i+1)*65536] for i in range(4)]
radices=[2,2,4,4,4]
def digits(code):
 out=[]
 for radix in radices:
  out.append(code%radix);code//=radix
 return out
def classify(own,opponent,tested):
 d=min(sum(own),4);a=min(sum(opponent),4)
 def tier(profile):return min((v for v,n in zip([99,9,5,3,1],profile) if n),default=0)
 u,v=tier(own),tier(opponent)
 if a==0:return 2
 if d==0 or v<tested:return 0
 if v==tested:return 1 if a<=d else 0
 return 2 if a<=d or v>tested+u else 0
def exclude(own,category):
 out=own.copy()
 for at in range(category,5):
  if out[at]:
   out[at]-=1
   for lower in range(category,at):out[lower]=radices[lower]-1
   return out
 return [0]*5
def magnitude(profile):return sum(n*w for n,w in zip(profile,[1,2,4,16,64]))
profiles=[digits(i) for i in range(256)]
packed=bytes(sum(rows[t][i]<<(2*t) for t in range(4)) for i in range(65536))
checks=0
for own in range(256):
 for opponent in range(256):
  index=(own<<8)|opponent
  for t,tested in enumerate([1,3,5,9]):
   assert ((packed[index]>>(2*t))&3)==rows[t][index]==classify(profiles[own],profiles[opponent],tested)
   checks+=1
 # Prove every adjusted domain maps to an already exhaustively proved table row.
 for category,weight in enumerate([1,2,4,16,64]):
  adjusted=max(own-weight,0)
  assert magnitude(exclude(profiles[own],category))==adjusted
assert all(packed[own<<8]==0xAA for own in range(256))
assert all(((b>>(2*t))&3)!=3 for b in packed for t in range(4))
assert pins=={str(p):sha(p) for p in inputs}
result={'complete':True,'scope':'Offline algebra and current typed-data parse only; no Rust/native execution or performance estimate','pair_count':65536,'four_tier_extraction_and_independent_formula_checks':checks,'adjusted_digit_borrow_identities':256*5,'adjusted_four_tier_queries_covered_by_composition':256*256*5*4,'opponent_zero_packed_byte':170,'all_extracted_codes_in':[0,1,2],'old_typed_payload_bytes':262144,'conceptual_packed_payload_bytes':len(packed),'conceptual_packed_payload_sha256':hashlib.sha256(packed).hexdigest(),'source_inputs_sha256':pins,'all_inputs_unchanged':True,'engine_runs':0,'production_table_file_written':False}
(P/'model-result.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='source_inputs_sha256'}))
