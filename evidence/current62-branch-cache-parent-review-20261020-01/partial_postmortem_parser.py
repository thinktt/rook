"""Pure bounded-schema Callgrind v1 line-only named-event vector reader.

No subprocesses, target execution or file writes on import. Cost is not cycles.
The general format permits partial summaries; this reader requires a complete
single-part whole-program dump whose SELF/summary/totals vectors agree.
"""
from pathlib import Path
import hashlib,json,re
U64=(1<<64)-1
EVENTS=('Ir','Dr','Dw','I1mr','D1mr','D1mw','ILmr','DLmr','DLmw','Bc','Bcm','Bi','Bim')
POS=re.compile(r'(?:[+-]?(?:\d+|0x[0-9a-fA-F]+)|\*)\Z')
NAME=re.compile(r'(fl|fi|fe|cfi|cfl|fn|cfn|ob|cob)=(.*)\Z')
def require(value,message):
    if not value:raise ValueError(message)
def model_rates(cost):
    result={}
    for numerator,denominator in [('Bcm','Bc'),('Bim','Bi')]:
        if numerator in cost and denominator in cost:
            require(cost[numerator]<=cost[denominator],'prediction misses exceed branches')
        result[numerator+'_div_'+denominator]=(cost[numerator]/cost[denominator]
            if numerator in cost and denominator in cost and cost[denominator] else None)
    return result

def parse_text(text,expected_events=None):
    require(isinstance(text,str) and text.isascii(),'profile must be ASCII')
    if expected_events is not None:
        require(bool(expected_events) and len(expected_events)==len(set(expected_events)),'expected events not unique')
    names={'file':{},'fn':{},'ob':{}}
    def resolve(kind,value):
        match=re.fullmatch(r'\((\d+)\)(?: (.*))?',value)
        if not match:
            require(not re.match(r'\(\d',value),'malformed compressed name')
            return value
        ident=int(match[1]);dictionary=names[kind]
        if match[2] is not None:
            require(ident not in dictionary or dictionary[ident]==match[2],'compressed name redefinition')
            dictionary[ident]=match[2]
        require(ident in dictionary,'unresolved compressed name')
        return dictionary[ident]
    events=None;summary=None;totals=None;headers={};descriptions=[];event_descriptions=[]
    rows=[];arcs=[];position=0;pending=None;body=False
    ctx={'object':None,'file':None,'function':None,'fn_name_token':None}
    callee={'callee_function':None,'callee_object':None,'callee_file':None}
    object_explicit_since_function=False
    def vector(tokens,pad):
        require(events is not None,'events header absent')
        require((0<=len(tokens)<=len(events)) if pad else len(tokens)==len(events),'counter width mismatch')
        require(all(re.fullmatch(r'\d+',value) for value in tokens),'invalid nonnegative counter')
        values=[int(value) for value in tokens]
        require(all(value<=U64 for value in values),'64-bit counter overflow')
        values += [0]*(len(events)-len(values))
        return dict(zip(events,values))
    for number,raw_line in enumerate(text.splitlines(),1):
        line=raw_line.strip()
        if not line or line.startswith('#'):continue
        match=NAME.fullmatch(raw_line)
        if match:
            require(totals is None,'body after totals')
            require(pending is None,'call association missing its cost row')
            key,value=match.groups();body=True
            kind='fn' if key in ('fn','cfn') else 'ob' if key in ('ob','cob') else 'file'
            value=resolve(kind,value)
            if key in ('fl','fi','fe'):ctx['file']=value
            elif key=='fn':ctx['function']=value;ctx['fn_name_token']=match[2];object_explicit_since_function=False
            elif key=='ob':ctx['object']=value
            elif key=='cfn':callee['callee_function']=value
            elif key=='cob':callee['callee_object']=value;object_explicit_since_function=True
            else:callee['callee_file']=value
            continue
        if line.startswith('calls='):
            require(totals is None and pending is None,'invalid call association')
            values=line[6:].split()
            require(len(values)==2 and values[0].isdigit() and POS.fullmatch(values[1]),'invalid calls syntax')
            require(0<int(values[0])<=U64,'invalid explicit call count')
            pending=(int(values[0]),values[1]);continue
        if ':' in line:
            require(pending is None,'call association missing its cost row')
            key,value=line.split(':',1);value=value.strip()
            if key=='totals':
                require(totals is None,'duplicate totals');totals=vector(value.split(),False);continue
            require(not body,'header inside profile body')
            if key=='desc':descriptions.append(value);continue
            if key=='event':
                require('=' not in value,'derived event declarations unsupported')
                event_descriptions.append(value);continue
            require(key in ('version','creator','pid','cmd','part','positions','events','summary'),'unsupported header '+key)
            require(key not in headers,'duplicate header '+key);headers[key]=value
            if key=='version':require(value=='1','unsupported format version')
            elif key=='part':require(value=='1','noninitial/multiple parts unsupported')
            elif key=='positions':require(value=='line','only line positions supported')
            elif key=='events':
                events=value.split()
                require(bool(events) and len(events)==len(set(events)) and all(re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*',v) for v in events),'invalid/duplicate event names')
                if expected_events is not None:require(set(events)==set(expected_events),'unexpected event schema')
            elif key=='summary':summary=vector(value.split(),False)
            continue
        require(totals is None,'cost after totals')
        values=line.split()
        require(bool(values) and POS.fullmatch(values[0]),'unsupported/malformed body row')
        token=values[0]
        if token!='*':
            value=int(token,16) if '0x' in token.lower() else int(token)
            position=position+value if token[0] in '+-' else value
        require(position>=0,'negative resulting source position')
        require(ctx['file'] is not None and ctx['function'] is not None,'missing SELF owner')
        cost=vector(values[1:],True)
        row=dict(raw_line=number,raw_cost_text=raw_line,**ctx,line=position,events=cost)
        if pending is None:rows.append(row)
        else:
            require(callee['callee_function'] is not None,'missing called function')
            row.update(callee)
            row.update(explicit_calls=pending[0],callee_target_position_token=pending[1],inclusive_arc=True,
                callee_object_context='explicit_since_function' if object_explicit_since_function else 'unresolved_inherited_context',
                resolved_callee_object=callee['callee_object'] if object_explicit_since_function else None)
            arcs.append(row);pending=None
    require(pending is None and events is not None and summary is not None and totals is not None,'incomplete profile')
    sums={event:sum(row['events'][event] for row in rows) for event in events}
    require(all(value<=U64 for value in sums.values()),'summed counter overflow')
    require(sums==totals and all(summary[event]>=sums[event] for event in events),'partial postmortem still requires SELF==totals and nonnegative gap')
    return dict(schema='rook2-callgrind-partial-postmortem-v1',original_strict_study_complete=False,unattributed_summary_events={event:summary[event]-sums[event] for event in events},events=events,headers=headers,
        descriptions=descriptions,event_descriptions=event_descriptions,summary=summary,totals=totals,
        SELF_sum=sums,model_rates=model_rates(sums),raw_SELF_rows=rows,
        raw_inclusive_call_arcs_NOT_ADDED=arcs,
        ranking_identity='Coalesced object/function-NAME attribution, not unique physical function owners',
        ownership_limit='Same-name functions within one object may coalesce. Raw defining/inline file and function-name tokens remain available. Inherited callee_object is not physical ownership proof.')

def rank(data):
    grouped={};parts={}
    for row in data['raw_SELF_rows']:
        key=(row['object'],row['function'])
        grouped.setdefault(key,{event:0 for event in data['events']});parts.setdefault(key,{})
        part=parts[key].setdefault(row['file'],{event:0 for event in data['events']})
        for event,value in row['events'].items():grouped[key][event]+=value;part[event]+=value
    result=[]
    for key,cost in grouped.items():
        result.append(dict(object=key[0],function=key[1],SELF_events=cost,file_partitions=parts[key],attribution='coalesced object/function-NAME',model_rates=model_rates(cost)))
    require(all(sum(row['SELF_events'][event] for row in result)==data['SELF_sum'][event] for event in data['events']),'ranking vector mismatch')
    return sorted(result,key=lambda row:(-row['SELF_events'].get('Ir',0),str((row['object'],row['function']))))

def parse_file(path,expected_events=None):
    path=Path(path);raw=path.read_bytes()
    require(hashlib.sha256(raw).hexdigest()=='0cb25d4d181b32f95555f077b96b36cdc9afdc11168f9f77262e7177d8a885d8','postmortem bound to exact original failed capture only')
    result=parse_text(raw.decode('ascii'),expected_events)
    result.update(raw_path=str(path),raw_sha256=hashlib.sha256(raw).hexdigest())
    return result

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('profile');parser.add_argument('--expected-events',required=True)
    parser.add_argument('--output',required=True);args=parser.parse_args()
    result=parse_file(args.profile,args.expected_events.split(','));result['ranking']=rank(result)
    with Path(args.output).open('x') as stream:json.dump(result,stream,indent=2);stream.write('\n')
