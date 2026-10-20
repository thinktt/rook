#!/usr/bin/env python3
"""After actual collection terminal, independent binary/private-counter/offline cache model."""
from common import *
from parse_census import parse,CAPACITIES

def main():
    plan=guard('model');collection=Path(plan['collection']);terminal(collection/'tool-terminal.json')
    result=load(collection/'result.json');assert result['complete'] and result['native_runs']==54 and [x['case'] for x in result['cases']]==plan['case_order']
    out=Path(plan['model']);assert not out.exists();out.mkdir();rows=[]
    totals={str(c):{k:[0]*4 for k in ['probes','hits','empty_misses','replacements','hit_activity_queries']} for c in CAPACITIES}
    for case in result['cases']:
        d=collection/case['case'];raw=d/'encounters.bin';report=d/'native-counts.jsonl'
        assert sha(raw)==case['raw_sha256'] and sha(report)==case['report_sha256'] and sha(d/'comparator.stdout')==case['comparator_sha256']
        parsed=parse(raw,report,case['native_pid']);write(out/(case['case']+'.json'),parsed)
        assert parsed['raw_sha256']==case['raw_sha256'] and parsed['report_sha256']==case['report_sha256']
        for epoch in parsed['epochs']:
            for c,s in epoch['capacities'].items():
                for name,values in s.items():
                    for i,v in enumerate(values):totals[c][name][i]+=v
        rows.append({'case':case['case'],'encounters':parsed['encounters'],'activity_queries':parsed['activity_queries'],'epochs':len(parsed['epochs']),'parsed_sha256':sha(out/(case['case']+'.json'))})
    child(['/usr/bin/node',str(P/'recheck54.mjs'),str(collection)],out/'original-oracle54')
    assert (out/'original-oracle54.stderr').read_bytes()==b'' and load(out/'original-oracle54.stdout')['original_oracle_calls']==54
    guard('model')
    write(out/'summary.json',{'complete':True,'cases':rows,'capacities':totals,'class_order':['normal_age0','normal_aged','fresh_age0','fresh_aged'],'native_runs':0,'new_native_runs':0,'original_oracle_calls_offline':54,'total_private_bytes':result['total_private_bytes'],'interpretation':'Exact-board recurrence/collision counts only; every producer actually ran; represented hit R must remain charged; no unbounded unique set or CPU benefit inference'})
    print(json.dumps({'complete':True,'cases':54,'new_native_runs':0}))
if __name__=='__main__':main()
