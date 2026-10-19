#!/usr/bin/env python3
"""Offline source-data/algebra proof only; no Rust compiler or engine invoked."""
from pathlib import Path
import collections,hashlib,json,re
HERE=Path(__file__).resolve().parent
TRIAL=Path('/home/legolas/rook2-work/imp2-packed-four-tier-relations-20261019-01')
EXPECTED='8a8483ee5b00d8bdcac45caf2e371c8315510dfc542963a415717f8b407c66d4'
RADICES=[2,2,4,4,4]
WEIGHTS=[1,2,4,16,64]
TIERS=[99,9,5,3,1]
def digits(code):
 result=[]
 for radix in RADICES:
  result.append(code%radix);code//=radix
 assert code==0
 return result
def features(values):
 return min(sum(values),4),min((tier for count,tier in zip(values,TIERS) if count),default=0)
def classified(own,opponent,tested):
 d,u=own;a,v=opponent
 if a==0 or (d!=0 and v>tested and (a<=d or v>tested+u)):return 2
 if a!=0 and d!=0 and v==tested and a<=d:return 1
 return 0
def excluded(values,category):
 out=values[:]
 borrow=next((i for i in range(category,5) if out[i]),None)
 if borrow is None:return [0]*5
 out[borrow]-=1
 for i in range(category,borrow):out[i]=RADICES[i]-1
 return out

def main():
 packed=bytes(int(word,16) for word in re.findall(r'0x([0-9a-f]{2})',(TRIAL/'src/relation_table.rs').read_text()))
 assert len(packed)==65536 and hashlib.sha256(packed).hexdigest()==EXPECTED
 old_source=(HERE/'base-src/src/relation_table.rs').read_text().split('= [',1)[1]
 codes={'U':0,'C':1,'F':2};old=[codes[x] for x in re.findall(r'\b[UCF]\b',old_source)]
 assert len(old)==4*65536
 all_digits=[digits(code) for code in range(256)];all_features=[features(d) for d in all_digits]
 fields=collections.Counter();table_checks=0
 for own in range(256):
  for opponent in range(256):
   index=256*own+opponent
   for field,tested in enumerate([1,3,5,9]):
    actual=(packed[index]>>(2*field))&3
    expected=classified(all_features[own],all_features[opponent],tested)
    assert actual==old[field*65536+index]==expected,(own,opponent,field)
    assert actual!=3
    fields[actual]+=1;table_checks+=1
 exclusions=[]
 for own,values in enumerate(all_digits):
  row=[]
  for category,remove in enumerate(WEIGHTS):
   value=excluded(values,category)
   code=sum(a*b for a,b in zip(value,WEIGHTS))
   assert code==max(0,own-remove)
   row.append((code,features(value)))
  exclusions.append(row)
 species=[('pawn',0,1),('knight',1,3),('bishop',1,3),('rook',2,5),('queen',3,9)]
 adjusted_checks=0;species_checks=0
 for own in range(256):
  for opponent in range(256):
   for name,field,tested in species:
    index=256*own+opponent
    assert ((packed[index]>>(2*field))&3)==classified(all_features[own],all_features[opponent],tested)
    species_checks+=1
    for code,value in exclusions[own]:
     adjusted_index=256*code+opponent
     expected=classified(value,all_features[opponent],tested)
     assert ((packed[adjusted_index]>>(2*field))&3)==old[field*65536+adjusted_index]==expected
     adjusted_checks+=1
 before=(HERE/'base-src/src/influence.rs').read_text();after=(TRIAL/'src/influence.rs').read_text()
 new_decoder="""    let packed = crate::relation_table::RELATIONS[((own as usize) << 8) | opponent as usize];
    match (packed >> (2 * tested)) & 3 {
        0 => Relation::Unfavorable,
        1 => Relation::Contested,
        _ => Relation::Favorable,
    }
"""
 old_decoder='    crate::relation_table::RELATIONS[tested][((own as usize) << 8) | opponent as usize]\n'
 added_test="""
    #[test]
    #[should_panic(expected = "king has no tested-piece relation tier")]
    fn experiment38_king_dispatch_precedes_empty_opponent_shortcut() {
        relation(0, 0, PieceKind::King);
    }
"""
 assert after.count(new_decoder)==after.count(added_test)==1
 assert after.replace(new_decoder,old_decoder).replace(added_test,'')==before
 # This inverse preserves the complete previous dispatch/opponent0 prefix,
 # adjusted_relation and all185 old test bodies, not merely their names/count.
 (HERE/'packed-payload.bin').write_bytes(packed)
 result=dict(offline_source_algebra_only=True,complete=True,pairs=65536,fields_checked=table_checks,
  species_checked=species_checks,saturating_exclusion_categories=5,independent_borrow_identities=1280,
  adjusted_species_checks=adjusted_checks,field_counts=dict(fields),field3_count=0,
  payload_bytes=len(packed),payload_sha256=hashlib.sha256(packed).hexdigest(),
  old_payload_bytes=len(old),native_old_test_bodies_unchanged=True,
  dispatch_and_king_before_opponent0_unchanged=True,adjusted_relation_byte_exact=True,
  new_native_test_declarations=1,new_native_test_run=False,Rust_compiler_or_engine_runs=0)
 (HERE/'exhaustive-proof.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
 print(json.dumps(result,sort_keys=True))
if __name__=='__main__':main()
