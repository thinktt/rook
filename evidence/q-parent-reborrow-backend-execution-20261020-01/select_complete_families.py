"""Pure prospective metadata selector; never runs tools, reads images or records a gate."""
import re
COLD=re.compile(r"\.cold(?:\.[0-9]+)?$")
def select_complete_families(mangled_rows, display_rows, role_specs, side):
    """Rows are (integer address, integer size, raw symbol/display string).

    This selects candidates, not semantic owners. Source/call-role confirmation
    is mandatory in the later manual gate. Same display names are NOT physical
    identity, and different compressed/profile suffix names are not clone proof.
    """
    assert side in ('control','candidate')
    request=[]
    for role in role_specs:
        # GNU c++filt may print a cold symbol with exactly the hot display NAME.
        # Exclude cold raw mangled symbols BEFORE display-name matching.
        hot=[]
        for a,n,symbol in mangled_rows:
            if COLD.search(symbol): continue
            if role.get('actual_mangled_symbol') and symbol!=role['actual_mangled_symbol']: continue
            displays=[d for x,z,d in display_rows if (x,z)==(a,n)]
            if role['display_name'] in displays: hot.append((a,n,symbol))
        assert len(hot)==1, ('missing/ambiguous sized noncold candidate',role['role'],hot)
        a,n,stem=hot[0]
        if role.get('actual_mangled_symbol'):
            assert a==int(role['expected_start'],16) and n==role['expected_bytes'], 'physical request range mismatch'
        assert n>0 and len([x for x in mangled_rows if x[:2]==(a,n)])==1, 'unsized/aliased hot candidate'
        family=[x for x in mangled_rows if x[2]==stem or re.fullmatch(re.escape(stem)+r'\.cold(?:\.[0-9]+)?',x[2])]
        assert not [x for x in mangled_rows if x[2].startswith(stem+'.') and x not in family], 'unsupported suffix: STOP'
        for j,(address,extent,symbol) in enumerate(sorted(family,key=lambda x:(x[2]!=stem,x[0]))):
            assert extent>0, 'unsized fragment: STOP'
            names={d for x,z,d in display_rows if (x,z)==(address,extent)}
            assert len(names)==1 and len([x for x in mangled_rows if x[:2]==(address,extent)])==1, 'ambiguous alias/display: STOP'
            request.append(dict(side=side,role=role['role'],actual_mangled_symbol=symbol,owner_mangled_symbol=stem,display_name=next(iter(names)),start=address,bytes=extent,fragment_kind='hot' if symbol==stem else 'cold',expected_source=role['source'],source_and_call_role_confirmed=False))
    ranges=sorted((x['start'],x['start']+x['bytes']) for x in request)
    assert all(end<=next_start for (_,end),(next_start,_) in zip(ranges,ranges[1:])), 'overlap/duplicate role: STOP'
    return request
