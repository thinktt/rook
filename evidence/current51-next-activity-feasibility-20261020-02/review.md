# Unselected current51 Activity question: paired uncapped support counts

**One distinct small source/compiler hypothesis remains plausible:** compute the two existing uncapped source-profile sums together in independent16-bit lanes of one u32, without an opponent-zero branch, table, cache or geometry path. Recommend only a prospective compiler discriminator, not an implementation, candidate number or timing admission. Current Activity/source owners match immutable W51; production remains51.

## Actual cost context and history

Closed exact51 profile35 is44,100,272,048 simulated Ir; Activity SELF9,154,116,962 (20.757507%) includes all inline file partitions and is not removable. The existing raw-row review isolates **588,605,983Ir (1.334699%)** at `influence.rs:219` inside Activity, plus a separate150,296,832Ir comparison context at `activity.rs:366`. Only two production profile_sum calls occur in Activity, for the two source bytes (`activity.rs:363–368`). Neither row subset gives an eligible frequency or an instruction saving; unidentified line0 and other owners remain unknown. This memo reuses the approved raw-row proof, not new annotations or other-image costs.

History exclusions:53's conditional opponent-zero shortcut is parked; this proposal counts every pair unconditionally. The historical profile_sum LUT is parked after own-PGO and supplies no gain transfer.27's paired radix arithmetic decoded pressure **mark weights**, including extra knight weights, not two uncapped Influence counts; the algebraic pairing technique is related, but this owner/output and two-lane packing mechanism are different.31 mark construction,32 coordinate-table pressure traversal,35 category masks,41 shelter table,42/52 borrowed/separated Activity geometry and cache/pawn-scan fusion are not revived or composed. No profile total from those images is used.

## Exact all-pair algebra, including carry and borrow

For byte b, write its four base4 digits as a0=(weak+2queen), a1=rook, a2=minor, a3=pawn. Here weak/queen are0..1 and the others0..3. The required uncapped count is

`S(b)=a0+a1+a2+a3−queen = weak+queen+rook+minor+pawn`, in0..11.

For own byte o and opponent byte e, define pure mathematical u32 expressions:

```
x = u32(o) | (u32(e) << 16)
t = (x & 0x00330033) + ((x >> 2) & 0x00330033)
s = (t & 0x000f000f) + ((t >> 4) & 0x000f000f)
    - ((x >> 1) & 0x00010001)
Sown = s & 15
Sopponent = s >> 16
```

Each nibble of t is a sum of two base4 digits<=6, so there is no carry into the adjacent nibble or16-bit lane. The next sum in each lane is<=12, so it remains wholly inside that lane. Its correction is exactly the byte's queen bit0/1. The pre-correction lane sum is at least2·queen, hence subtracting that bit is independently nonnegative: **the low lane cannot borrow from the upper lane**. Each final lane equals S(b)<=11, so the low nibble and upper shift recover the exact counts, with all other lane bits zero. x<=0x00ff00ff, t<=0x00660066, pre-correction sum<=0x000c000c; every intermediate fits u32 without wrapping/saturation. This establishes the identity for all65536 byte pairs by independent-lane algebra; no enumeration or executed test was performed.

Retain the original penalty predicate `Sown<=Sopponent` and subtraction `5*Sopponent+2`. Its maximum57 fits existing i64 score arithmetic. Both-zero still subtracts2; (255,255) uses11/11 and subtracts57; own120/opponent104 uses6>5 and subtracts0. Do not cap counts at relation multiplicity4 or replace them with bit-popcounts.

The prospective change belongs only at the private piece-score support block, shared by all N/B/R/Q callers. Public `Influence::profile_sum` and every other consumer remain unchanged. Both original bytes stay live for the normalized-pawn knight exemption and later unadjusted source relation; all mobility/curve/phase/casts/rounding, source/destination query charges, marks, pressure and caller order stay in their current numerical owners. This identity needs no placement coherence, valid-tag shortcut, mutable-state witness or added public admission condition: all supplied u8 pairs are already covered.

## Falsifiable mechanism, risk and boundary tests

A later paired baseline/trial **actual whole Activity** compiler gate would need to show the two scalar five-digit expansions replaced by shared lane arithmetic in real kind/color paths, without a new lookup/call, scalar recomputation, duplicated body, frame/spill growth or lost later-byte reuse. Count total packing, masks, shifts, correction, extraction and comparison in that same scope. Reject absent/relocated work: source algebra alone does not prove fewer instructions. LLVM may already CSE/vectorize enough; u32 packing/extraction and lane masks can erase the expected saving, larger immediates can grow code, and register pressure/PGO factoring can dominate. No CPU prediction follows from the1.334699% mixed owner.

Meaningful prospective controls: all65536 pairs through each of four piece_score_kind specializations/both colors against an independent mixed-radix division/remainder oracle for the **old** support formula; both-zero, maximal/equal counts and uncapped6vs5 explicitly; low-C source R increments, normalized-pawn knight exemption and nonzero unfavorable relation; full public Activity custom maps with exact pieces/weighted/pressure/work. The already independent53 test design can be reused as oracle source if separately selected, but its parked runtime authority/results cannot transfer. It contains no candidate lane arithmetic. No additional architecture/cache/fusion probe or new pipeline is recommended now.

Disposition: conditionally worth one source/compiler question only if root selects it; no evidence yet establishes actual benefit. Otherwise leaving current51 unchanged is justified. All work here is bounded source/history/algebra review; no source edit, exhaustive run, parser, engine, test, build, binary inspection, profiler, archive, Git or advisor action occurred. Normal speed policy requested; no runtime speed-control readback exists in this tool interface.
