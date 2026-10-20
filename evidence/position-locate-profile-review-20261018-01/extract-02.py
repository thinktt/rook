"""Offline exclusive position locate source-row extraction from two closed profiles."""
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
        if fn=='rook2::position::Position::apply_unchecked':whole_function[file]=whole_function.get(file,0)+cost
        if not file or not file.endswith('/src/position.rs'):continue
        rows[position]=rows.get(position,0)+cost
        byline=contexts.setdefault(fn,{})
        byline[position]=byline.get(position,0)+cost
    assert total==EXPECTED[case],(case,total)
    selected={}
    for context,byline in contexts.items():
        locate={line:cost for line,cost in byline.items() if 195<=line<=201}
        prefix={line:cost for line,cost in byline.items() if 176<=line<=180}
        piece_slice={line:cost for line,cost in byline.items() if 184<=line<=187}
        sites={line:byline[line] for line in [206,309,325] if line in byline}
        if context=='rook2::position::Position::apply_unchecked':
            selected[context]=dict(locate_rows=locate,locate_Ir=sum(locate.values()),
                shared_group_start_rows=prefix,shared_group_start_Ir=sum(prefix.values()),
                shared_piece_squares_rows=piece_slice,shared_piece_squares_Ir=sum(piece_slice.values()),
                parent_source_site_rows=sites,parent_source_site_Ir=sum(sites.values()))
    display=(PROFILE/f'profile-{case}-functions.stdout').read_text().splitlines()
    shown={}
    for text in display:
        m=re.match(r'\s*([\d,]+) \([^)]*\)\s+(.+):rook2::position::Position::apply_unchecked(?: \[.*)?$',text)
        if m:shown[m[2]]=int(m[1].replace(',',''))
    assert all(whole_function.get(file)==cost for file,cost in shown.items())
    results[case]=dict(total_exclusive_Ir=total,source_owner_Ir=sum(rows.values()),
        all_position_source_rows=rows,locate_contexts=selected,
        locate_known_rows_total=sum(cost for line,cost in rows.items() if 195<=line<=201),
        parent_source_sites_total=sum(rows.get(line,0) for line in [206,309,325]),
        shared_group_start_all_contexts_Ir=sum(cost for line,cost in rows.items() if 176<=line<=180),
        shared_piece_squares_all_contexts_Ir=sum(cost for line,cost in rows.items() if 184<=line<=187),
        apply_unchecked_exclusive_by_file=whole_function,apply_unchecked_exclusive_total=sum(whole_function.values()),
        apply_unchecked_display_sum=sum(shown.values()),whole_exclusive_total_verified=True,
        standalone_locate_context_names=[name for name in functions.values() if 'Position::locate' in name])
    print(json.dumps({k:results[case][k] for k in ['total_exclusive_Ir','locate_contexts','locate_known_rows_total','parent_source_sites_total','shared_group_start_all_contexts_Ir','shared_piece_squares_all_contexts_Ir','apply_unchecked_exclusive_total','apply_unchecked_display_sum','standalone_locate_context_names']},sort_keys=True))
(HERE/'source-row-counts-02.json').write_text(json.dumps(results,indent=2)+'\n')
