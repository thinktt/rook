#!/usr/bin/env python3
"""Independent finite ray-class model; no engine or production-code imports."""
import itertools,json,hashlib,os
from pathlib import Path
assert set(os.sched_getaffinity(0)) == {0,1,2,3,4,5,8,9,10,11,12,13}
# E empty; T transparent (matching friendly slider/opponent king);
# Q friendly queen; P opaque friendly pawn; O all other opaque occupants.
checks=0
for n in range(8):
 for tokens in itertools.product('ETQPO',repeat=n):
  for extension in (False,True):
   expected=[0]*n;weight=2;i=0
   while i<n:
    expected[i]=weight;t=tokens[i]
    if t=='Q':weight=1
    elif t in 'PO':
     if t=='P' and extension and i+1<n:expected[i+1]=weight
     break
    i+=1
   for increasing in (False,True):
    positions=list(range(n)) if increasing else list(reversed(range(n)))
    ray=sum(1<<p for p in positions)
    opaque=sum(1<<positions[j] for j,t in enumerate(tokens) if t in 'PO')
    queen=sum(1<<positions[j] for j,t in enumerate(tokens) if t=='Q')
    def first(mask):return (mask&-mask).bit_length()-1 if increasing else mask.bit_length()-1
    def suffix(p):return sum(1<<q for q in positions if q>p) if increasing else sum(1<<q for q in positions if q<p)
    visible=ray
    if opaque:
     block=first(opaque);visible=ray & ~suffix(block)
     j=positions.index(block)
     if tokens[j]=='P' and extension and j+1<n:visible |= 1<<positions[j+1]
    q=visible&queen;weak=visible&suffix(first(q)) if q else 0;normal=visible&~weak
    assert not normal&weak
    actual=[2 if normal&(1<<p) else 1 if weak&(1<<p) else 0 for p in positions]
    assert actual==expected,(tokens,extension,increasing,expected,actual)
    checks+=1
r={'complete':True,'cases':checks,'lengths':list(range(8)),'alphabet':'empty/transparent/friendlyQueen/friendlyPawnOpaque/otherOpaque','both_step_polarities':True,'pawn_extension_enabled_and_disabled':True,'normal_and_weak_disjoint':True,'scope':'Exhaustive abstract ray classes only; native tag decoding, actual board geometry, SIMD emission and integrated search remain unproven here.','script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
Path(__file__).with_name('ray-model-result.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
