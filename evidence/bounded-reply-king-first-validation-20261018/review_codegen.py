#!/usr/bin/env python3
"""Read-only static artifact comparison; never executes either engine."""
from pathlib import Path
import subprocess,re,json,hashlib,difflib
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
CONTROL=ROOT/'evidence/quiescence-evaluation-default-build-20261018'
TRIAL=ROOT/'evidence/bounded-reply-king-first-build-20261018'
PREP=ROOT/'evidence/bounded-reply-king-first-preparation-20261018/prepared.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def symbols(image):
    s=subprocess.check_output(['nm','-S','-C',str(image)],text=True)
    result={}
    for line in s.splitlines():
        m=re.match(r'([0-9a-f]+)\s+([0-9a-f]+)\s+\w\s+(.+)',line)
        if m:result[m[3]]=dict(address=int(m[1],16),size=int(m[2],16))
    return s,result

def normalized(asm,begin,end):
    result=[]
    for line in asm.splitlines():
        m=re.match(r'\s*([0-9a-f]+):\s+(.+)',line)
        if not m:continue
        text=m[2].split('#')[0].strip()
        text=re.sub(r'-?0x[0-9a-f]+\(%rip\)','<RIP>(%rip)',text)
        target=re.search(r'\b([0-9a-f]+) <([^>]+)>',text)
        if target:
            value=int(target[1],16)
            replacement='local+'+hex(value-begin) if begin<=value<end else '<'+target[2]+'>'
            text=text[:target.start()]+replacement+text[target.end():]
        result.append(text)
    return result

prepared=json.loads(PREP.read_text());control=json.loads((CONTROL/'receipt.json').read_text());trial=json.loads((TRIAL/'receipt.json').read_text())
assert control['source_sha256_before']==control['source_sha256_after']==prepared['baseline_source_sha256']
assert trial['source_sha256_before']==trial['source_sha256_after']==prepared['variant_source_sha256']
assert control['rust_flags']==trial['rust_flags'] and control['build_effective_environment']==trial['build_effective_environment']
records={};selected={}
for tag,directory,receipt in [('control-d38',CONTROL,control),('king-first',TRIAL,trial)]:
    image=directory/'rook2-exact';assert sha(image)==receipt['binary_output']['sha256']
    s,table=symbols(image);(OUT/(tag+'-symbols.txt')).write_text(s)
    selected[tag]={}
    for name,item in table.items():
        if any(k in name for k in ['rook2::movegen::generate_legal','rook2::movegen::legal_replies_up_to_two','rook2::quiescence::<impl','rook2::session::Session']) and any(k in name for k in ['generate_legal','legal_replies_up_to_two','visit_q','adjudicate']):
            key='full-generator' if 'generate_legal' in name else 'capped-reply' if 'legal_replies' in name else 'default-Q' if 'visit_q' in name else 'session-adjudicate'
        elif 'rook2::evaluator::Evaluator' in name and 'full_impl' in name:key='default-full-evaluation'
        else:continue
        begin=item['address'];end=begin+item['size']
        asm=subprocess.check_output(['objdump','-d','-C','--no-show-raw-insn',f'--start-address={begin}',f'--stop-address={end}',str(image)],text=True)
        rawasm=subprocess.check_output(['objdump','-d','-C',f'--start-address={begin}',f'--stop-address={end}',str(image)],text=True)
        (OUT/(tag+'-'+key+'.asm')).write_text(rawasm)
        norm=normalized(asm,begin,end);(OUT/(tag+'-'+key+'.normalized.txt')).write_text('\n'.join(norm)+'\n')
        selected[tag][key]=dict(symbol=name,address=hex(begin),bytes=item['size'],stack_subtractions=re.findall(r'sub\s+\$([^,]+),%rsp',asm),normalized=norm)
    records[tag]=dict(artifact_sha256=sha(image),receipt_sha256=sha(directory/'receipt.json'),symbols=selected[tag])
comparisons={}
for key in sorted(selected['control-d38'].keys()&selected['king-first'].keys()):
    a=selected['control-d38'][key];b=selected['king-first'][key]
    diff='\n'.join(difflib.unified_diff(a['normalized'],b['normalized'],fromfile='control/'+key,tofile='trial/'+key,n=3))+'\n'
    (OUT/(key+'-normalized.diff')).write_text(diff)
    comparisons[key]=dict(control_bytes=a['bytes'],trial_bytes=b['bytes'],control_stack_subtractions=a['stack_subtractions'],trial_stack_subtractions=b['stack_subtractions'],relocation_normalized_instructions_identical=a['normalized']==b['normalized'],normalized_diff_lines=len(diff.splitlines()))
for rec in records.values():
    for item in rec['symbols'].values():del item['normalized']
result=dict(scope='Static generic codegen only; not CPU timing/profile/invocation counts',normalization='Drop disassembly addresses/comments, normalize RIP data/GOT displacement and resolve intra-function branch targets to relative labels; preserve instruction/reg/immediate/stack operands. This comparison alone does not prove pointed-to data identity.',generic_flags_and_effective_environment_match=True,prepared_sha256=sha(PREP),driver_sha256=sha(Path(__file__)),artifacts=records,comparisons=comparisons)
(OUT/'codegen-review.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(comparisons,indent=2))
