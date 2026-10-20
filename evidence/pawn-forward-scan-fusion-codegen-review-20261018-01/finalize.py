"""Offline bounded call/section review, without engine or build execution."""
from pathlib import Path
import hashlib
import json
import re
HERE=Path(__file__).resolve().parent
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def load(path):return json.loads(Path(path).read_text())

def main():
    identity=load(HERE/'identity.json');analysis=load(HERE/'bounded-analysis.json')
    functions=load(HERE/'function-capture.json')['functions'];calls={};sections={}
    for side in identity['images']:
        names={}
        for line in (HERE/side/'nm-demangled.stdout').read_text().splitlines():
            match=re.match(r'^([0-9a-f]+)\s+[0-9a-f]+\s+\S\s+(.+)$',line)
            if match:names.setdefault(int(match[1],16),match[2])
        relocations={}
        for line in (HERE/side/'relocations.stdout').read_text().splitlines():
            match=re.match(r'^([0-9a-f]+)\s+[0-9a-f]+\s+R_X86_64_RELATIVE\s+([0-9a-f]+)$',line)
            if match:relocations[int(match[1],16)]=names.get(int(match[2],16),'UNNAMED '+match[2])
            match=re.match(r'^([0-9a-f]+)\s+[0-9a-f]+\s+R_X86_64_(?:GLOB_DAT|JUMP_SLOT)\s+[0-9a-f]+\s+(\S+)',line)
            if match:relocations[int(match[1],16)]=match[2]
        calls[side]={}
        for name,data in analysis['metrics'][side].items():
            found=[]
            for call in data['calls']:
                op=call['operands'];slot=re.search(r'#\s*([0-9a-f]+)',op)
                if slot:target=relocations.get(int(slot[1],16),'UNRESOLVED '+slot[1])
                else:
                    label=re.search(r'<(.+)>',op);target=label[1] if label else op
                found.append(dict(offset=int(call['address'],16)-int(functions[side][name]['address'],16),target=target))
            calls[side][name]=found
        sections[side]={}
        for line in (HERE/side/'sections.stdout').read_text().splitlines():
            match=re.match(r'^\s*\[\s*\d+\]\s+(\.text|\.rodata)\s+PROGBITS\s+[0-9a-f]+\s+[0-9a-f]+\s+([0-9a-f]+)',line)
            if match:sections[side][match[1]]=int(match[2],16)
    stable={}
    for name in ['selected','pawn-ending','evaluation','ordinary','q']:
        stable[name]=calls['control'][name]==calls['candidate'][name]
        assert stable[name],(name,calls['control'][name],calls['candidate'][name])
    assert any(x['target']=='rook2::pawn_progress::raw' for x in calls['control']['candidates'])
    assert all('raw' not in x['target'] for x in calls['candidate']['candidates'])
    assert all(sha(path)==digest for path,digest in identity['source_input_sha256'].items())
    result=dict(complete=True,images=identity['images'],source_changes=identity['changed_native_sources'],
        metrics={side:{name:{key:value for key,value in m.items() if key!='calls'} for name,m in values.items()}
                 for side,values in analysis['metrics'].items()},
        resolved_calls=calls,unchanged_scoped_call_offsets_and_targets=stable,sections=sections,
        section_delta={name:sections['candidate'][name]-sections['control'][name] for name in sections['control']},
        current_raw_only_emitted_consumer_present=False,supplemental_probes=0,
        native_engine_runs=0,builds=0,profilers=0,all_owned_processes_terminal=True,
        no_cpu_or_whole_function_equality_claim=True)
    with (HERE/'review-summary.json').open('x') as out:json.dump(result,out,indent=2);out.write('\n')
    print(json.dumps(dict(complete=True,section_delta=result['section_delta'],stable_call_boundaries=stable,
        candidate_calls=calls['candidate']['candidates'],summary_sha256=sha(HERE/'review-summary.json'))))

if __name__=='__main__':main()
