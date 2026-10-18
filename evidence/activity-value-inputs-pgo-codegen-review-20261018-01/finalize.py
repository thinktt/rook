"""Offline call/section reconciliation; never invokes a native engine or tool."""
from pathlib import Path
import hashlib
import json
import re

HERE=Path(__file__).resolve().parent
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def load(path):return json.loads(Path(path).read_text())

def main():
    capture=load(HERE/'capture.json');calls={};sections={}
    for side,identity in capture['identities'].items():
        receipt_path=Path(identity['image']).parent/'receipt.json'
        receipt=load(receipt_path)
        profile=receipt['pgo']['profile']
        env=receipt['environment_overrides']
        canonical=json.dumps(env,sort_keys=True).replace(profile,'OWN_PROFILE')
        if side=='control':control_environment=canonical
        else:assert canonical==control_environment
        symbols={}
        for line in (HERE/side/'nm-demangled.txt').read_text().splitlines():
            match=re.match(r'^([0-9a-f]+)\s+[0-9a-f]+\s+\S\s+(.+)$',line)
            if match:symbols.setdefault(int(match[1],16),match[2])
        relative={}
        for line in (HERE/side/'relocations.txt').read_text().splitlines():
            match=re.match(r'^([0-9a-f]+)\s+[0-9a-f]+\s+R_X86_64_RELATIVE\s+([0-9a-f]+)$',line)
            if match:relative[int(match[1],16)]=int(match[2],16)
        calls[side]={}
        for name,metadata in capture['metrics'][side].items():
            result=[]
            for call in metadata['calls']:
                operands=call['operands'];target=operands
                slot=re.search(r'#\s*([0-9a-f]+)',operands)
                if slot:
                    address=int(slot[1],16)
                    target=symbols.get(relative.get(address),'GOT '+hex(address))
                elif '<' in operands:
                    target=re.search(r'<(.+)>',operands)[1]
                result.append(dict(offset=int(call['address'],16)-int(metadata['address'],16),target=target))
            calls[side][name]=result
        sections[side]={}
        for line in (HERE/side/'sections.txt').read_text().splitlines():
            match=re.match(r'^\s*\[\s*\d+\]\s+(\.text|\.rodata)\s+PROGBITS\s+[0-9a-f]+\s+[0-9a-f]+\s+([0-9a-f]+)',line)
            if match:sections[side][match[1]]=int(match[2],16)
    stable={}
    for name in ['evaluation','ordinary','q']:
        stable[name]=calls['control'][name]==calls['candidate'][name]
        assert stable[name],name
    assert all(any(call['target']=='rook2::activity::compute' for call in calls[side]['evaluation'])
               for side in calls)
    assert all(any(call['target']=='rook2::activity::compute' for call in calls[side]['ordinary'])
               for side in calls)
    assert all(sha(path)==digest for path,digest in capture['inputs_sha256'].items())
    result=dict(complete=True,scope='Bounded static own-PGO hot bodies only',
        source_changes=capture['source_changes'],identities=capture['identities'],
        metrics={side:{name:{key:value for key,value in m.items() if key!='calls'}
            for name,m in values.items()} for side,values in capture['metrics'].items()},
        resolved_calls=calls,same_scoped_call_offsets_and_targets=stable,
        sections=sections,section_delta={key:sections['candidate'][key]-sections['control'][key]
            for key in sections['control']},actual_table=capture['actual_table'],
        same_environment_except_own_profile_path=True,
        native_engine_runs=0,build_runs=0,probes=0,profilers=0,
        no_whole_function_or_cpu_equality_claim=True,all_owned_processes_terminal=True)
    with (HERE/'review-summary.json').open('x') as out:json.dump(result,out,indent=2);out.write('\n')
    print(json.dumps(dict(complete=True,section_delta=result['section_delta'],same_call_boundaries=stable,
        activity_call_targets=calls['candidate']['activity'],summary_sha256=sha(HERE/'review-summary.json'))))

if __name__=='__main__':main()
