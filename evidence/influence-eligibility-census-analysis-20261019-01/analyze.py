#!/usr/bin/env python3
"""Offline additive census analysis. No native execution or imports of runners."""
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
E = HERE.parent
PREP = E / 'influence-eligibility-census-run-preparation-20261019-01'
RUN = PREP / 'run'
CASES = ('profile-35', 'profile-08')
BASELINE = json.loads((PREP / 'plan.json').read_text())['census_schema_contract']['baseline_fields']
SOURCE = Path('/home/legolas/rook2-work/imp2-influence-eligibility-census-20261019-01/src/influence_census.rs')
INPUTS = [PREP/'plan.json', PREP/'run.py', PREP/'verify.py', PREP/'check-raw.mjs',
          RUN/'plan.json', RUN/'result.json', RUN/'tool-terminal.json',
          RUN/'independent-verification.json', RUN/'independent-tool-terminal.json',
          E/'influence-eligibility-census-source-preparation-20261019-01/source-manifest.json',
          E/'influence-eligibility-census-source-preparation-20261019-01/source-proof.json',
          E/'influence-eligibility-census-source-preparation-20261019-01/schema.md', SOURCE,
          E/'influence-delta-demand-census-20261019-01/README.md',
          E/'influence-delta-exact-image35-ir-preparation-20261019-01/run/README.md',
          E/'influence-delta-exact-image-ir-preparation-20261019-01/run/README.md',
          E/'influence-delta-decision-20261019-01/README.md',
          E/'influence-delta-inplace-decision-20261019-01/README.md']
for case in CASES:
    INPUTS += [RUN/case/name for name in ('census.json', 'native.json', 'command.json')]

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def pin_inputs():
    return {str(p): {'sha256': digest(p), 'bytes': p.stat().st_size} for p in INPUTS}

def load(path):
    return json.loads(path.read_text())

def write(name, value):
    with (HERE/name).open('x') as f:
        json.dump(value, f, indent=2, sort_keys=True)
        f.write('\n')

def total(rows):
    result = Counter()
    for row in rows:
        result.update(row['counts'])
    return result

def check_baseline(c):
    assert c['producer_calls'] == c['samples']
    assert c['zero_result_payload_bytes'] == c['output_payload_bytes'] == 128*c['samples']
    assert c['bitplane_colors']+c['scalar_colors'] == 2*c['samples']
    assert c['counter_plane_words_initialized'] == 8*c['bitplane_colors']
    assert c['transpose_colors'] == c['bitplane_colors']
    assert c['full_sources'] == sum(c[f'sources.{k}'] for k in range(6))
    assert c['full_slider_sources'] == sum(c[f'sources.{k}'] for k in (2,3,4))
    assert c['full_slider_sources'] == c['slider.source_calls'] == c['slider.slider_sources']
    assert c['full_slider_directions'] == c['slider.directions'] == 4*c['sources.2']+4*c['sources.3']+8*c['sources.4']
    assert all(c[f'slider.source_kind.{k}'] == c[f'sources.{k}'] for k in (2,3,4))
    assert c['slider.normal_targets']+c['slider.weak_targets'] == c['slider.targets']

def check_demand(c):
    check_baseline(c)
    # Exclusive ladder; do not sum its nested cumulative fields as peers.
    assert sum(c[k] for k in ('no_parent_context','no_movement','not_two_cell_shape',
                             'parent_native_unavailable','mask_coherence_unavailable',
                             'certified_two_cell_for_masks')) == c['samples']
    assert c['ordinary_or_promotion']+c['special_not_two_cell_candidate'] == c['two_cell_shape']+c['not_two_cell_shape']
    assert c['two_cell_shape'] == c['parent_native_unavailable']+c['parent_native_available_two_cell']
    assert c['parent_native_available_two_cell'] == c['mask_coherence_unavailable']+c['certified_two_cell_for_masks']
    assert c['promotion'] <= c['certified_two_cell_for_masks']
    assert c['parent_checked'] <= c['certified_two_cell_for_masks']
    for p in ('remove_mover','remove_victim','add_mover','replay_old_complete_source','replay_new_complete_source'):
        assert c[p+'.source_calls'] == sum(c[f'{p}.source_kind.{k}'] for k in range(6))
        assert c[p+'.slider_sources'] == sum(c[f'{p}.source_kind.{k}'] for k in (2,3,4))
        assert c[p+'.directions'] == 4*c[p+'.source_kind.2']+4*c[p+'.source_kind.3']+8*c[p+'.source_kind.4']
        assert c[p+'.normal_targets']+c[p+'.weak_targets'] <= c[p+'.targets']
    assert c['remove_mover.source_calls'] == c['add_mover.source_calls'] == c['certified_two_cell_for_masks']
    assert c['remove_victim.source_calls'] <= c['certified_two_cell_for_masks']
    assert c['affected_origins'] == c['affected_origins.color0']+c['affected_origins.color1']
    assert c['affected_origins'] <= c['affected_directions'] <= c['replay_old_complete_source.directions']
    for p in ('replay_old_complete_source','replay_new_complete_source'):
        assert c[p+'.source_calls'] == c[p+'.slider_sources'] == c['affected_origins']
    assert c['replay_old_complete_source.directions'] == c['replay_new_complete_source.directions']
    for weight in ('normal','weak'):
        assert c['changed_'+weight+'_targets'] == c[weight+'_remove_only_targets']+c[weight+'_add_only_targets']
        assert c['replay_old_complete_source.'+weight+'_targets']+c['replay_new_complete_source.'+weight+'_targets'] == c['changed_'+weight+'_targets']+2*c['same_'+weight+'_targets']
    assert max(c['changed_normal_targets'],c['changed_weak_targets']) <= c['changed_union_targets'] <= c['changed_normal_targets']+c['changed_weak_targets']
    assert c['unexpected_other_source_change'] == 0

def scope(rows):
    c = total(rows)
    # Only homogeneous all-eligible rows can supply exact eligible fresh features.
    pure = [r for r in rows if r['counts'].get('certified_two_cell_for_masks',0) == r['counts']['samples']]
    mixed = [r['json_pointer'] for r in rows if 0 < r['counts'].get('certified_two_cell_for_masks',0) < r['counts']['samples']]
    ec = total(pure)
    return {'row_pointers': [r['json_pointer'] for r in rows], 'counts': dict(c),
            'eligible_fresh_work_from_homogeneous_rows': {k: ec[k] for k in ['samples']+BASELINE},
            'mixed_eligibility_rows': mixed,
            'old_plus_new_unchanged_slider_weight_targets': c['replay_old_complete_source.targets']+c['replay_new_complete_source.targets'],
            'changed_weight_targets': c['changed_normal_targets']+c['changed_weak_targets'],
            'separate_mover_victim_add_targets': {p:c[p+'.targets'] for p in ('remove_mover','remove_victim','add_mover')},
            'separate_mover_victim_add_targets_sum': sum(c[p+'.targets'] for p in ('remove_mover','remove_victim','add_mover'))}

def main():
    pins = pin_inputs()
    write('input-pins.json', pins)
    write('script-pin.json', {'path':str(Path(__file__).resolve()),'sha256':digest(Path(__file__))})
    for name, chunk in [('tool-terminal.json','23963a'),('independent-tool-terminal.json','931ae0')]:
        t=load(RUN/name)
        assert t['actual_tool_terminal_observed'] and t['exit_code']==0 and t['terminal_chunk_id']==chunk
    independent=load(RUN/'independent-verification.json')
    assert independent['complete'] and independent['all_inputs_unchanged'] and independent['native_engine_runs']==0
    results=load(RUN/'result.json')
    assert results['complete'] and results['engine_runs']==2 and not results['performance_claim']
    historical=(E/'influence-delta-demand-census-20261019-01/README.md').read_text()
    def old_row(label):
        m=re.search(r'\|'+re.escape(label)+r'\|(\d+)\|(\d+)\|',historical)
        assert m, label
        return [int(m[1]),int(m[2])]
    output={'complete':False,'cases':{},'logical_counts_only':True,'native_runs':0,
            'input_pin_count':len(pins), 'source_graph_sha256':'30465c9cf73196438a8b466b8d98a0f27addc9a9ee795bd304d8566897788578'}
    selected={}
    for ci,case in enumerate(CASES):
        x=load(RUN/case/'census.json'); t=Counter(x['totals'])
        assert digest(RUN/case/'census.json') == results['cases'][ci]['census_sha256']
        assert x['complete'] and x['engine_success'] and x['diagnostic_only']
        assert not x['invalid_or_overflow'] and x['live_frames']==x['pending_edges']==0
        assert x['native_pid']==results['cases'][ci]['native_pid']==load(RUN/case/'native.json')['native_pid']
        rows=[{'json_pointer':f'/joint_bins/{i}',**r} for i,r in enumerate(x['joint_bins'])]
        assert len({r['cohort'] for r in rows})==len(rows)
        for row in rows:
            assert all(type(v) is int and 0<=v<2**64 for v in row['counts'].values())
        demands=[r for r in rows if r['cohort'].startswith('demand/')]
        frames=[r for r in rows if r['cohort'].startswith('frame/')]
        producers=[r for r in rows if r['cohort'].startswith('producer/')]
        for r in demands: check_demand(Counter(r['counts']))
        for r in producers: check_baseline(Counter(r['counts']))
        dc,fc,pc=total(demands),total(frames),total(producers)
        assert dc['samples']==pc['samples']==t['native_none_completed']==t['producer_completed']
        assert all(dc[k]==pc[k] for k in BASELINE)
        assert fc['samples']==t['frames_entered']==t['frames_left']
        assert fc['native_demands']==t['native_none_associated']
        assert fc['some_events']==t['ensure_some_associated']
        assert sum(fc['frame_map_status.'+k] for k in ('native_map','some_only','unassociated_map_activity','no_map_events'))==fc['samples']
        assert t['native_none_unassociated']==t['native_owner_position_mismatch']==t['producer_scalar']==t['unassociated_direct_producer']==0
        assert t['edges_opened']==t['edges_closed']==t['edges_consumed']+t['edges_unconsumed']
        assert sum(v for k,v in t.items() if k.startswith('immediate_edge.'))==fc['samples']
        assert sum(v for k,v in t.items() if k.startswith('immediate_changes.'))==fc['samples']
        assert dc['samples']==old_row('All fresh builder calls')[ci]+old_row('Eligible ordinary main updates')[ci]
        groups=defaultdict(list); framegroups=defaultdict(list)
        for row in demands:
            p=row['cohort'].split('/')
            for g in ('all',p[1],p[1]+'/'+p[2]):groups[g].append(row)
            if p[1]=='ordinary' and p[2] in ('main_child','scout_retry'):
                groups['ordinary/main_plus_scout'].append(row)
        for row in frames:
            p=row['cohort'].split('/')
            for g in ('all',p[1],p[1]+'/'+p[2]):framegroups[g].append(row)
        scopes={g:scope(r) for g,r in sorted(groups.items())}
        ordinary=total(groups['ordinary']); narrow=total(groups['ordinary/main_plus_scout'])
        assert ordinary['samples']==old_row('Ordinary first map fills')[ci]
        assert narrow['certified_two_cell_for_masks']-narrow['promotion']==old_row('Eligible ordinary main updates')[ci]
        assert not any(s['mixed_eligibility_rows'] for s in scopes.values())
        frame_summary={}
        for g,rr in sorted(framegroups.items()):
            c=total(rr)
            parent_native_no_map=sum(r['counts'].get('frame_map_status.no_map_events',0) for r in rr if r['cohort'].endswith('/parent_native'))
            frame_summary[g]={'counts':dict(c),'row_pointers':[r['json_pointer'] for r in rr],
                              'parent_native_at_entry_no_map_events':parent_native_no_map}
        checked={status:dict(total([r for r in demands if '/'+status+'/' in r['cohort']]))
                 for status in ('checked','unchecked','check_unknown')}
        output['cases'][case]={'native_pid':x['native_pid'],'totals':dict(t),'demand_scopes':scopes,
            'frame_scopes':frame_summary,'current_checked_demand_scopes':checked,
            'fresh_full_producer_work':dict(pc),'producer_rows':[r['json_pointer'] for r in producers],
            'historical_reconciliation':{'all_fresh_current':dc['samples'],
                'old_trial_fresh':old_row('All fresh builder calls')[ci],
                'old_trial_updates':old_row('Eligible ordinary main updates')[ci],
                'old_ordinary_first_fills':old_row('Ordinary first map fills')[ci],
                'current_main_plus_scout_certified':narrow['certified_two_cell_for_masks'],
                'current_main_plus_scout_promotions':narrow['promotion'],
                'current_main_plus_scout_nonpromotion_equals_old_updates':True}}
        selected[case]={'path':str(RUN/case/'census.json'),'sha256':digest(RUN/case/'census.json'),'rows':rows}
    assert pin_inputs()==pins
    output['complete']=True
    output['all_inputs_unchanged']=True
    write('row-selection.json',selected)
    write('analysis.json',output)
    print(json.dumps({'complete':True,'cases':list(output['cases']),'input_pins':len(pins),
                      'all_inputs_unchanged':True,'new_native_runs':0,'logical_counts_only':True}))

if __name__=='__main__':
    main()
