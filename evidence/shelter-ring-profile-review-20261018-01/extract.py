"""Offline exclusive shelter source-row extraction from two closed profiles."""
from pathlib import Path
import json,re
ROOT=Path('/home/legolas/rook2')
HERE=Path(__file__).resolve().parent
PROFILE=ROOT/'evidence/complete117-callgrind-20261018'
EXPECTED={'35':48746346838,'08':4163216998}
results={}
for case in ['35','08']:
    lines=(PROFILE/f'profile-{case}.callgrind').read_text().splitlines()
    assert 'events: Ir' in lines
    files={};functions={}
    for text in lines:
        m=re.match(r'^(?:fl|fi|fe|cfi|cfl)=\((\d+)\) (.+)$',text)
        if m:files[m[1]]=m[2]
        m=re.match(r'^(?:fn|cfn)=\((\d+)\) (.+)$',text)
        if m:functions[m[1]]=m[2]
    base=None;file=None;fn=None;position=0;call=False;total=0;rows={};contexts={};whole_function={}
    for text in lines:
        m=re.match(r'^(fl|fi|fe)=\((\d+)\)',text)
        if m:
            file=files[m[2]]
            if m[1]=='fl':base=file
            continue
        m=re.match(r'^fn=\((\d+)\)',text)
        if m:fn=functions[m[1]];file=base;continue
        if text.startswith('calls='):call=True;continue
        m=re.match(r'^([*]|[+-]?\d+) (\d+)$',text)
        if not m:continue
        token=m[1]
        if token!='*':position=position+int(token) if token[0] in '+-' else int(token)
        cost=int(m[2])
        # Call-associated cost is inclusive and excluded. Position still advances.
        if call:call=False;continue
        total+=cost
        if fn=='rook2::shelter::compute':whole_function[file]=whole_function.get(file,0)+cost
        if not file or not file.endswith('/src/shelter.rs'):continue
        rows[position]=rows.get(position,0)+cost
        byline=contexts.setdefault(fn,{})
        byline[position]=byline.get(position,0)+cost
    assert total==EXPECTED[case],(case,total)
    display=(PROFILE/f'profile-{case}-functions.stdout').read_text().splitlines()
    display_rows={}
    for text in display:
        m=re.match(r'\s*([\d,]+) \([^)]*\)\s+(.+):rook2::shelter::compute(?: \[.*)?$',text)
        if m:
            key=m[2];assert key not in display_rows
            display_rows[key]=int(m[1].replace(',',''))
    # The function display is threshold-limited: record any omitted tiny contexts.
    assert all(whole_function.get(file)==cost for file,cost in display_rows.items()),case
    ring={line:cost for line,cost in rows.items() if 113<=line<=151}
    geometry={line:cost for line,cost in rows.items() if 115<=line<=122}
    results[case]=dict(total_exclusive_Ir=total,all_shelter_source_rows=rows,
        source_owner_Ir=sum(rows.values()),unidentified_line0=rows.get(0,0),
        ring_known_source_rows=ring,ring_known_Ir=sum(ring.values()),
        proposed_geometry_known_rows=geometry,proposed_geometry_known_Ir=sum(geometry.values()),
        shelter_function_exclusive_file_contexts=whole_function,
        shelter_function_exclusive_total=sum(whole_function.values()),
        displayed_function_contexts=display_rows,displayed_function_total=sum(display_rows.values()),
        display_omitted_file_contexts={file:cost for file,cost in whole_function.items() if file not in display_rows},
        whole_exclusive_total_verified=True,all_displayed_owner_contexts_exactly_reconciled=True,
        extraction='same compressed-position/file/function parser as accepted movegen context extraction; inclusive call cost skipped')
    print(json.dumps({k:results[case][k] for k in ['total_exclusive_Ir','source_owner_Ir','unidentified_line0','ring_known_source_rows','ring_known_Ir','proposed_geometry_known_rows','proposed_geometry_known_Ir','shelter_function_exclusive_total','displayed_function_total','display_omitted_file_contexts']},sort_keys=True))
(HERE/'source-row-counts.json').write_text(json.dumps(results,indent=2)+'\n')
