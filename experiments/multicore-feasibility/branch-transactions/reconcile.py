#!/usr/bin/env python3
"""Check closed pilot identities/accounting; produce concise derived results."""
import argparse, collections, hashlib, json, os
from pathlib import Path

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def reconcile(raw):
    plan=json.loads((raw/'plan.json').read_text());closure=json.loads((raw/'closure.json').read_text())
    assert closure['complete'] and len(closure['rows'])==len(plan['schedule'])==6
    for name,digest in plan['inputs'].items():assert sha(Path(name))==digest,(name,'changed')
    rows=[]
    for i,(receipt,step) in enumerate(zip(closure['rows'],plan['schedule'])):
        assert all(receipt[k]==step[k] for k in step)
        assert receipt['exit']==0 and not receipt['timed_out']
        stem=f'{i:02d}-{step["case"]}-q{step["queue_depth"]}'
        for kind in ['stdout','stderr']:assert sha(raw/(stem+'.'+kind))==receipt[kind+'_sha256']
        d=json.loads((raw/(stem+'.stdout')).read_text());cs=d['candidates'];t=d['timings']
        assert d['zero_randomness'] and not d['unsafe_validation']
        assert d['restricted_entry_nodes']>=25000 and d['caps']==dict(max_depth=8,max_tail_candidates=8,queue_depth=step['queue_depth'],log_events=16384)
        assert all(c['passed'] for c in d['controls'])
        assert any(c['accepted'] and c['nodes']>1 and c['differs_from_speculative_final'] for c in d['controls'])
        assert any(not c['accepted'] and c['staged_writes_before_rejection']>0 and c['canonical_unchanged'] for c in d['controls'])
        assert d['candidate_nodes']==sum(d[k] for k in ['accepted_nodes','rejected_nodes','unsafe_nodes','abandoned_nodes'])
        assert d['candidate_nodes']==sum(c['speculative_nodes'] for c in cs)
        assert d['canonical_nodes']==d['prefix_nodes']+sum(c['canonical_nodes'] for c in cs)
        assert d['oracle_nodes']==d['canonical_nodes']-d['prefix_nodes']
        assert d['incomplete_nodes']==sum(c['speculative_nodes'] for c in cs if c['log_overflowed'])
        assert all(c['rollback_unchanged'] and not c['audit_failed'] for c in cs)
        assert all(c['oracle_match'] and c['semantic_accepted'] for c in cs if c['accepted'])
        assert all(c['log_events']<=16384 for c in cs)
        assert d['accepted_nodes']==sum(c['speculative_nodes'] for c in cs if c['accepted'])
        accepted_cost=sum(c['timings']['oracle_ns'] for c in cs if c['accepted'])
        coordinator=sum(t[k] for k in ['snapshot_ns','request_validation_ns','staging_ns','replay_ns','commit_ns'])
        executor_proxy=t['prefix_ns']+coordinator+t['speculation_ns']+t['fallback_ns']
        audit_only=t['oracle_snapshot_ns']+t['comparison_ns']+t['oracle_ns']-t['fallback_ns']
        rows.append(dict(**step,restricted_depth=d['restricted_depth'],restricted_entry_nodes=d['restricted_entry_nodes'],
           stop=d['stopped_reason'],candidates=len(cs),candidate_nodes=d['candidate_nodes'],accepted_nodes=d['accepted_nodes'],
           accepted_tasks=sum(c['accepted'] for c in cs),ahead_tasks=sum(c['ahead_distance']>0 for c in cs),
           ahead_accepted_tasks=sum(c['accepted'] and c['ahead_distance']>0 for c in cs),
           ahead_accepted_nodes=sum(c['speculative_nodes'] for c in cs if c['accepted'] and c['ahead_distance']>0),
           rejected_nodes=d['rejected_nodes'],incomplete_nodes=d['incomplete_nodes'],
           capped_tasks=sum(c['log_overflowed'] for c in cs),
           reasons=dict(collections.Counter(c['rejection'] for c in cs if not c['accepted'])),
           canonical_nodes=d['canonical_nodes'],prefix_nodes=d['prefix_nodes'],event_size_bytes=d['event_size_bytes'],
           peak_queue_snapshot_bytes=d['peak_queue_snapshot_bytes'],peak_queue_log_bytes=d['peak_queue_log_bytes'],
           timing_ns=dict(accepted_native_cost_potentially_removed=accepted_cost,coordinator=coordinator,
           executor_serial_proxy=executor_proxy,audit_only=audit_only,phase_unaccounted=d['elapsed_ns']-executor_proxy-audit_only,
           **t),elapsed_ns=d['elapsed_ns'],raw_sha256=sha(raw/(stem+'.stdout'))))
    return dict(scope='Six serial feasibility samples; no parallel speedup, qualification, or statistical timing estimate',
                raw=str(raw),plan_sha256=sha(raw/'plan.json'),closure_sha256=sha(raw/'closure.json'),rows=rows)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('raw',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
    result=reconcile(a.raw.resolve());a.output.write_text(json.dumps(result,indent=2)+'\n');print('reconciled',len(result['rows']),'samples')
