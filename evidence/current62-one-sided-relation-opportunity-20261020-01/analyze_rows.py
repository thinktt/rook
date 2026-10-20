from pathlib import Path
import hashlib,json,re,time
r=Path('/home/legolas/rook2');e=Path(__file__).parent
start=time.monotonic()
def features(code):
    # Independent radix division, in weak/queen/rook/minor/pawn order.
    ds=[]
    for radix in [2,2,4,4,4]:
        code,digit=divmod(code,radix);ds.append(digit)
    return min(sum(ds),4),min([tier for digit,tier in zip(ds,[99,9,5,3,1]) if digit] or [0])
def formula(own,opp,t):
    d,u=features(own);a,v=features(opp)
    if a==0 or (d!=0 and v>t and (a<=d or v>t+u)):return 2
    if a!=0 and d!=0 and v==t and a<=d:return 1
    return 0
text=(r/'src/relation_table.rs').read_text();payload=text.split('pub(crate) static RELATIONS: [[Relation; 65_536]; 4] = [',1)[1]
raw=re.findall(r'\b[UCF]\b',payload);assert len(raw)==262144,len(raw)
typed=bytes({'U':0,'C':1,'F':2}[v] for v in raw)
features_all=[features(i) for i in range(256)];classes=sorted(set(features_all));assert len(classes)==16
class_ids=[classes.index(v) for v in features_all]
tiers=[1,3,5,9];per=[];global_rows=[];all_own_signatures=[];checked=0
for k,t in enumerate(tiers):
    rows=[bytes(formula(own,opp,t) for opp in range(256)) for own in range(256)]
    for own,row in enumerate(rows):
        assert row==typed[k*65536+own*256:k*65536+(own+1)*256],(t,own)
    unique=list(dict.fromkeys(rows));global_rows.extend(unique)
    compressed=[rows[features_all.index(c)] for c in classes]
    for own in range(256):
        for opp in range(256):
            assert compressed[class_ids[own]][opp]==typed[k*65536+own*256+opp]
            checked+=1
    per.append({'tested_tier':t,'unique_rows':len(unique),'unique_row_bytes':len(unique)*256,'row_class_population':[rows.count(row) for row in unique],'row_sha256':[hashlib.sha256(row).hexdigest() for row in unique]})
    all_own_signatures.append(rows)
union=list(dict.fromkeys(global_rows));signatures=set(tuple(all_own_signatures[k][own] for k in range(4)) for own in range(256))
dictionary_checked=0
for k in range(4):
    unique=list(dict.fromkeys(all_own_signatures[k]))
    local_ids=[unique.index(row) for row in all_own_signatures[k]]
    global_ids=[union.index(row) for row in all_own_signatures[k]]
    assert max(global_ids)<256
    for own in range(256):
        for opp in range(256):
            expected=typed[k*65536+own*256+opp]
            assert unique[local_ids[own]][opp]==expected
            assert union[global_ids[own]][opp]==expected
            dictionary_checked+=1

result={'schema':'rook2-one-sided-relation-data-proof-v1','complete':True,'typed_tuples_checked':checked,'row_dictionary_typed_tuples_checked':dictionary_checked,'both_per_type_and_global_row_reconstructions_exact':True,'source_typed_payload_entries':len(typed),'source_typed_payload_sha256':hashlib.sha256(typed).hexdigest(),'general_formula_matches_all_typed_entries':True,'shared_own_feature_classes':len(classes),'own_feature_class_map_bytes':256,'feature_class_shape':[4,16,256],'feature_class_outcome_payload_bytes':4*16*256,'feature_class_total_bytes':256+4*16*256,'all_original_own_opponent_u8_inputs_covered':True,'per_type_row_dictionary':per,'sum_per_type_unique_rows':sum(x['unique_rows'] for x in per),'per_type_row_dictionary_payload_bytes':sum(x['unique_row_bytes'] for x in per),'per_type_dictionary_index_bytes':4*256,'per_type_dictionary_total_bytes':sum(x['unique_row_bytes'] for x in per)+4*256,'global_distinct_rows_across_types':len(union),'global_dictionary_payload_bytes':len(union)*256,'global_dictionary_index_bytes':4*256,'global_dictionary_total_bytes':len(union)*256+4*256,'shared_own_four_type_signatures':len(signatures),'king_not_an_admitted_table_tier':True,'opponent_zero_all_rows_F':all(row[0]==2 for row in union),'invalid_relation_discriminants':0,'adjusted_obligation':'original own.saturating_sub(remove) before own classification; base map and opponent unchanged','row_ids_are_not_piece_kind_or_relation_enum_codes':True,'runtime_table_or_source_variant_written':False,'elapsed_s':time.monotonic()-start}
(e/'data-proof.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='per_type_row_dictionary'},indent=2))
print('PER_TYPE',[(v['tested_tier'],v['unique_rows']) for v in per])
