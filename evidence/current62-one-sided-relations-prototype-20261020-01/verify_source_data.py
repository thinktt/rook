from pathlib import Path
import json,hashlib,re,difflib,time
r=Path('/home/legolas/rook2');w=Path('/home/legolas/rook2-work/imp2-one-sided-relations-20261020-01');e=Path(__file__).parent
started=time.monotonic();base=json.loads((e/'baseline-manifest.json').read_text());names=base['files_sha256'];after={n:hashlib.sha256((w/n).read_bytes()).hexdigest() for n in names};changed=[n for n in names if after[n]!=names[n]];assert sorted(changed)==['src/influence.rs','src/relation_table.rs']
# Compare every returned value using independently written radix/Boolean formula.
def feature(x):
    digits=[]
    for radix in (2,2,4,4,4):x,d=divmod(x,radix);digits.append(d)
    return min(sum(digits),4),min([t for d,t in zip(digits,(99,9,5,3,1)) if d] or [0])
def reference(o,a,t):
    d,u=feature(o);n,v=feature(a)
    if n==0 or (d!=0 and v>t and (n<=d or v>t+u)):return 2
    if n!=0 and d!=0 and v==t and n<=d:return 1
    return 0
source=(w/'src/relation_table.rs').read_text();ids_text=source.split('pub(crate) static OWN_ROWS: [[RowId; 256]; 4] = [',1)[1].split('pub(crate) static RELATIONS:',1)[0];ids=[int(x) for x in re.findall(r'\bR(\d+)\b',ids_text)];assert len(ids)==1024
row_text=source.split('pub(crate) static RELATIONS: [[Relation; 256]; 27] = [',1)[1];rows=bytes({'U':0,'C':1,'F':2}[x] for x in re.findall(r'\b[UCF]\b',row_text));assert len(rows)==6912
old=(r/'src/relation_table.rs').read_text().split('pub(crate) static RELATIONS: [[Relation; 65_536]; 4] = [',1)[1];old=bytes({'U':0,'C':1,'F':2}[x] for x in re.findall(r'\b[UCF]\b',old));assert len(old)==262144
variants=[(int(a),int(b)) for a,b in re.findall(r'^    R(\d+) = (\d+),$',source,re.M)];assert variants==[(i,i) for i in range(27)]
assert min(ids)==0 and max(ids)==26 and set(ids)==set(range(27))
checked=0;seen_rows={};next_id=0;per=[]
for k,t in enumerate([1,3,5,9]):
    bank=[]
    for own in range(256):
        rid=ids[k*256+own];row=rows[rid*256:(rid+1)*256];bank.append(row)
        if row not in seen_rows:seen_rows[row]=next_id;next_id+=1
        assert seen_rows[row]==rid,'not deterministic first appearance'
        for opp in range(256):
            actual=row[opp];assert actual==old[k*65536+own*256+opp]==reference(own,opp,t),(k,own,opp);checked+=1
    per.append(len(set(bank)))
assert len(seen_rows)==27 and per==[12,9,6,3]
old_owner=(r/'src/influence.rs').read_text();new_owner=(w/'src/influence.rs').read_text();new_lookup='    let row = crate::relation_table::OWN_ROWS[tested][own as usize] as usize;\n    crate::relation_table::RELATIONS[row][opponent as usize]';old_lookup='    crate::relation_table::RELATIONS[tested][((own as usize) << 8) | opponent as usize]';assert new_owner.replace(new_lookup,old_lookup)==old_owner
oldgen=(r/'scripts/generate_relation_table.py').read_text();newgen=(w/'scripts/generate_relation_table.py').read_text();assert oldgen[oldgen.index('def features('):oldgen.index('def generate():')]==newgen[newgen.index('def features('):newgen.index('def generate():')];assert oldgen[oldgen.index('def main():'):]==newgen[newgen.index('def main():'):]
assert old_owner[old_owner.index('#[cfg(test)]\nmod tests'):]==new_owner[new_owner.index('#[cfg(test)]\nmod tests'):]
assert sum((w/n).read_text().count('#[test]') for n in names if n.startswith('src/') and n.endswith('.rs'))==195
patch_names=sorted(changed+['scripts/generate_relation_table.py']);patch=''.join(''.join(difflib.unified_diff((r/n).read_text().splitlines(True),(w/n).read_text().splitlines(True),fromfile='a/'+n,tofile='b/'+n)) for n in patch_names);inverse=''.join(''.join(difflib.unified_diff((w/n).read_text().splitlines(True),(r/n).read_text().splitlines(True),fromfile='a/'+n,tofile='b/'+n)) for n in patch_names);(e/'trial.patch').write_text(patch);(e/'inverse.patch').write_text(inverse)
graph=hashlib.sha256(json.dumps(after,sort_keys=True,separators=(',',':')).encode()).hexdigest();(e/'source-manifest.json').write_text(json.dumps({'files_sha256':after,'source74_graph':graph,'native51_tools23':True,'native_changed':['src/influence.rs','src/relation_table.rs'],'maintenance_generator_outside74':{'path':'scripts/generate_relation_table.py','sha256':hashlib.sha256((w/'scripts/generate_relation_table.py').read_bytes()).hexdigest()}},indent=2,sort_keys=True)+'\n')
proof={'schema':'rook2-global-row-relation-prototype-source-proof-v1','complete':True,'typed_tuples_checked':checked,'all_match_canonical_typed_source_and_independent_radix_boolean_model':True,'global_first_appearance_row_order_verified':True,'per_tier_unique_rows':per,'global_unique_rows':27,'row_id_count':1024,'row_id_min':0,'row_id_max':26,'row_enum_repr':'u8','typed_outcome_count':6912,'logical_payload_bytes':7936,'row_enum_is_crate_private':True,'unsafe_or_enum_decoder_added':False,'source_changes_exactly_selected_lookup_table_and_generator':True,'original_kind_and_opponent_zero_prefix_byte_equal':True,'original_adjusted_relation_byte_equal':True,'original_influence_producer_and_tests_byte_equal':True,'original_generator_numeric_functions_and_CLI_byte_equal':True,'other72_native_tools_files_byte_equal':True,'old_test_declarations':195,'new_test_declarations':195,'new_tests':0,'tests_or_build_or_engine_executed':False,'source74_graph':graph,'actual_compiler_bounds_or_size_claim':False,'elapsed_s':time.monotonic()-started}
(e/'source-proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof,indent=2))
