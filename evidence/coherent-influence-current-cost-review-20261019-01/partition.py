"""Disjoint attribution of already selected SELF rows, no new annotation."""
from pathlib import Path
import json,hashlib
from collections import defaultdict
E=Path(__file__).resolve().parent
load=lambda n:json.loads((E/n).read_text())
save=lambda n,x:(E/n).write_text(json.dumps(x,indent=2)+'\n')
def owner(r):
    file=Path(r['file']).name;line=r['line']
    if line==0:return 'unidentified_line0_all_files'
    if file=='coherent.rs':
        if line in [29,31,57,61,65,69,75]:return 'setup_source_dispatch_return_known'
        if 33<=line<=51:return 'scalar_leapers_known'
        if line in [80,82,86,87,88,111,112,116,120,122,124,126,127]:return 'slider_mask_construction_known'
        if line==60:return 'explicit_per_color_vector_load_context'
        if line in [160,162,167,168,178,179]:return 'per_slider_expansion_emission_source_context'
        raise AssertionError(r)
    if file=='influence.rs':
        if line in [42,44]:return 'setup_source_dispatch_return_known'
        if line==167:return 'scalar_leapers_known'
        raise AssertionError(r)
    if file=='position.rs':
        assert line in [183,185,192,193];return 'setup_source_dispatch_return_known'
    if file=='attacks.rs':
        assert line==72;return 'slider_mask_construction_known'
    if '/stdarch/' in r['file'] and file in ['simd.rs','sse2.rs']:
        return 'vector_intrinsic_positive_context_unsplit_load_add_store'
    assert r['file'].startswith('/usr/src/rustc-1.85.1/'),r
    return 'other_core_positive_crosscutting_unknown'
results={}
for case in ['35','08']:
    raw=load('profile-'+case+'-self-selection.json');groups=defaultdict(list)
    for row in raw['raw_SELF_rows']:groups[owner(row)].append(row)
    ids=[r['raw_line'] for rows in groups.values() for r in rows]
    assert len(ids)==len(set(ids))==len(raw['raw_SELF_rows'])
    sums={key:{'Ir':sum(r['Ir'] for r in rows),'whole_percent':100*sum(r['Ir'] for r in rows)/raw['total_Ir'],'producer_SELF_percent':100*sum(r['Ir'] for r in rows)/raw['producer_exclusive_SELF'],'row_count':len(rows),'raw_rows':[r['raw_line'] for r in rows]} for key,rows in groups.items()}
    assert sum(g['Ir'] for g in sums.values())==raw['producer_exclusive_SELF']
    emission=sum(sums[key]['Ir'] for key in ['explicit_per_color_vector_load_context','per_slider_expansion_emission_source_context','vector_intrinsic_positive_context_unsplit_load_add_store'])
    results[case]={'whole_Ir':raw['total_Ir'],'producer_SELF':raw['producer_exclusive_SELF'],'disjoint_groups':sums,'emission_and_vector_context_Ir':emission,'emission_and_vector_context_whole_percent':100*emission/raw['total_Ir'],'all_groups_exactly_sum_SELF':True,'no_arc_or_other_owner_costs_added':True,'known_decode_rows_96_101_have_no_positive_source_attribution':True,'unmapped_is_not_zero_cost':True}
    print(case,'SELF',raw['producer_exclusive_SELF'])
    for key,g in sums.items():print(key,g['Ir'],round(g['whole_percent'],6))
    print('EMISSION_CONTEXT',emission,100*emission/raw['total_Ir'])
save('partition.json',{'complete':True,'event_scope':'Exact exclusive whole-lifetime simulated Ir; not PMU/CPU/traffic/cycles.','cases':results,'unknowns_retained':True,'all_rows_disjoint':True})
# Finite input hashes are rechecked; raw rows already matched original summary/totals and function displays.
pins=load('input-pins.json')
assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==meta['sha256'] for p,meta in pins.items())
print('All consumed inputs unchanged.')
