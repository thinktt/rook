"""Offline saved-text reconciliation and conservative unchecked prefix path bound."""
from pathlib import Path
from collections import Counter
import hashlib,json,re
P=Path(__file__).resolve().parent
E=P.parent
A=E/'candidate25-callgrind-absolute-annotation-20261018-01'
B=E/'ordinary-projected-bits-pgo-codegen-review-20261018-01'
O=E/'candidate25-callgrind-20261018-01'
S=Path('/home/legolas/rook2-work/imp2-ordinary-projected-bits-20261018-txi745mj/src')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def put(name,value):
 with (P/name).open('x') as f: json.dump(value,f,indent=2);f.write('\n')
# Reuse the audited offline parser definition without running its guarded main.
namespace={'__file__':str(P/'analyze.py'),'__name__':'offline_parser_definitions'}
exec(compile((P/'analyze.py').read_text(),str(P/'analyze.py'),'exec'),namespace)
inputs=[A/n for n in ['input-pins.json','receipt.json','tool-terminal.json']]
inputs += [A/f'profile-{c}-{f}.stdout' for c in ['35','08'] for f in ['movegen','ordinary']]
inputs += [B/n for n in ['identity.json','function-capture.json','tool-terminal.json','review-summary.json','candidate/body-173a0.asm']]
inputs += [O/f'profile-{c}.callgrind' for c in ['35','08']]
inputs += [P/n for n in ['summary.json','input-pins.json','analyze.py']]
inputs += [S/n for n in ['attacks.rs','movegen.rs','ordinary.rs']]
pins={str(p):sha(p) for p in inputs}
asm={int(m[1],16):m[2] for line in (B/'candidate/body-173a0.asm').read_text().splitlines() if (m:=re.match(r'^\s*([0-9a-f]+):\s+(.*)',line))}
intervals=[(0x17425,0x175fb),(0x17d6c,0x17d7b),(0x17dba,0x17dd8),(0x17e0d,0x17e1c),(0x17e5b,0x17e79),(0x17eae,0x17ebd),(0x17efc,0x17f18),(0x17f4c,0x17f5b),(0x17f97,0x17fb3)]
blocks=[]
for lo,hi in intervals:
 assert lo in asm and hi in asm
 selected=[(k,v) for k,v in asm.items() if lo<=k<=hi]
 assert all(not v.startswith(('call','rep')) for k,v in selected)
 blocks.append({'first':hex(lo),'last':hex(hi),'instructions':len(selected),'saved_instructions':{hex(k):v for k,v in selected}})
assert [b['instructions'] for b in blocks]==[94,6,8,6,8,6,8,6,8]
limit=sum(b['instructions'] for b in blocks)
assert limit==150
summary=json.loads((P/'summary.json').read_text());cases={}
for c in ['35','08']:
 rows,arcs,total=namespace['raw'](O/f'profile-{c}.callgrind')
 annotations={}
 for name in ['movegen','ordinary']:
  file=str(S/f'{name}.rs');expected=Counter()
  for r in rows:
   if r['file']==file:expected[r['line']]+=r['Ir']
  active=False;line_number=None;observed=Counter();zero=None;footer=None
  for line in (A/f'profile-{c}-{name}.stdout').read_text().splitlines():
   if line.startswith('-- User-annotated source: '):
    assert line.split(': ',1)[1]==file;active=True;continue
   if not active:continue
   m=re.match(r'-- line (\d+) ',line)
   if m:line_number=int(m[1]);continue
   m=re.match(r'^\s*([\d,]+)\s+\(\s*[\d.]+%\)\s+(.*)$',line)
   if not m:continue
   cost=int(m[1].replace(',',''));text=m[2]
   if text.startswith(('=>','<=')):continue
   if text.startswith('<counts for unidentified lines'):zero=cost;continue
   if text=='events annotated':footer=cost;continue
   assert line_number is not None
   observed[line_number]+=cost
  positive=Counter({k:v for k,v in expected.items() if k>0 and v})
  assert observed==positive,(c,name,observed-positive,positive-observed)
  assert (zero or 0)==expected[0]
  assert footer==sum(positive.values())
  annotations[name]={'positive_source_Ir':footer,'unidentified_line0_Ir':zero or 0,'all_positive_lines_match_raw_exclusive_rows':True,'raw_positive_line_count':len(positive)}
 data=summary['cases'][c]
 ordinary=[r for r in data['full_generator_incoming_explicit_call_arcs'] if r['file']==str(S/'ordinary.rs') and r['line']==849]
 count=sum(r['explicit_calls'] for r in ordinary)
 direct=data['buckets']['ordered_attackers_unique_source_174_235']['Ir']+data['buckets']['generator_checker_binding_674_677']['Ir']
 cases[c]={'total_simulated_Ir':total,'absolute_annotation_reconciliation':annotations,'all_ordinary_full_generation_explicit_calls':count,'calls_from_raw_lines':[r['raw_line'] for r in ordinary],'maximum_old_unchecked_prefix_instructions_per_call':limit,'conservative_prefix_Ir_ceiling_all_ordinary_calls_assumed_unchecked':limit*count,'ceiling_percent_of_whole_lifetime_Ir':100*limit*count/total,'direct_ordered_and_binding_source_Ir_all_full_generator_callers':direct,'direct_source_percent':100*direct/total}
assert all(sha(Path(p))==h for p,h in pins.items())
put('bound-input-pins.json',pins)
put('unchecked-prefix-bound.json',{'cases':cases,'blocks':blocks,'unchecked_semantic_conditions':'Valid coherent Position; own king has no attacking pawn, knight, adjacent enemy king, or matching first-blocker slider. Thus no emit branch and each ray no-hit detour executes at most once.','retained_setup_before_17425_excluded':'List clear, function prologue, king lookup and count/range admission remain required.','all_inputs_unchanged':True,'new_native_binary_annotation_or_profile_runs':0})
print(json.dumps(cases,indent=2))
