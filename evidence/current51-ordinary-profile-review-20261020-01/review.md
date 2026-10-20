# Current51 ordinary opportunity: defer an exact final-pass merge

**One distinct mechanism is source-feasible, but remains deferred and unselected:** preserve the modulo-six first pass, then replace native `order_by`'s final gap-one insertion/gather with a stable merge of its six already-sorted residue streams directly into the original MoveList. This is an algorithmic reduction in repeated comparisons/shifts, not a retry of49's equal-length bound-check specialization. Parent currently prefers a separate Activity shortcut; no prototype or new candidate is requested here.

## Actual current cost, without a savings claim

The closed exact51 own-PGO image `48ee57b14e436338037e21f0f01f0f340959d7b05771f5cd759a3eab38d655b4` performed **44,100,272,048 simulated Ir** in one original profile35 lifetime. Collector a56e88/0, verifier d074ab/0, SELF ranking5a5071/0 and annotations913727/0 are closed. Root current source matches compiled W51 for the five inspected source owners (`input-pins.json`). No old43/40 cost is transferred.

`self-ranking.json` records `visit_ordinary_impl'2` SELF8,959,930,803, including tactical.rs1,493,465,378 and types.rs1,346,982,031. These inline file partitions are subsets of that same SELF total, not additional costs. The independent ordinary-family raw SELF rows at tactical.rs275,277–279,282–283 sum **1,129,045,776 Ir (2.56018% of this one program)**:

| Source line | Actual operation | Mixed SELF Ir |
|---|---|---:|
|275|load current priority|137,464,964|
|277|cursor/key comparison loop|561,670,989|
|278|shift Move|240,965,116|
|279|shift priority|60,241,279|
|282|place Move|96,527,571|
|283|place priority|32,175,857|

Both gaps execute these same lines. This is a **mixed retained-and-replaceable sorting attribution**, not a removable envelope: the retained first pass is included, comparisons/output remain necessary, inlined core/index costs are outside the table, and unidentified line0 stays unknown. There is no measured final-pass share, list-length/inversion distribution, crossover or CPU prediction. Recorded arcs confirm ordinary invokes legal generation/order/IIO and recursively visits children; their inclusive values are preserved separately in `attribution.json`, never added to SELF or used to infer physical clone identity.

The selected types display is whole-program source attribution. Even ordinary-family Piece::kind line113 contributes336,186,871 Ir and Move::kind line194 contributes208,582,977, but those are entire decoder-attributed instruction rows across multiple consumers, not counts of redundant validity branches. Existing generated-move tag work already found raw predicates in the relevant ordinary sites. This evidence does not justify treating the entire types overlay as removable or reopening that NO-GO.

## Concrete mechanism and correctness discriminator

Current `tactical.rs:271–285` performs gap6 then gap1 stable insertion; `order_by:343–361` first constructs a preferred reversed suffix and a deferred original-order prefix. After gap6, each residue class r contains a nonincreasing sequence at positions r,r+6,r+12,... . A six-stream merge chooses the head with greatest unsigned priority, breaking ties by its **post-gap6 position**. Each stream's later equal item has a greater such position, so choosing the best head yields exactly the globally stable descending permutation of the post-gap6 sequence. Induction on emitted items proves equivalence to gap1, including duplicates and every u32 key. No board legality or geometry permission is needed.

Tie order must not be changed to original input order: preferred keys `[2,5,2,2,2,2,5]` move original item6 before item1 in gap6; the final stable pass retains that order for the two5s. A direct original-order stable sort would be wrong. This follows the released mathematical permutation (`tactical-capture-order.md:9–26`), which explicitly does not require the current sorting implementation.

A prospective private native path could emit selected Moves into `list.moves[..preferred]`, which is no longer needed as input after all priority callbacks completed, while reading sorted streams from workspace suffixes. The disjoint low-priority workspace prefix is appended afterward. This avoids a new512-entry allocation or persistent fields and removes final-pass repeated priority shifts rather than merely rearranging their copies. It still needs bounded local cursors/head selection and one final Move write per item. An actual implementation must prove alias/range safety and preserve callback invocation once per original candidate in the original order, priority normalization, all opaque Move bits, and relation charges. None is implemented or claimed compiled here.

The public `priority_sequence` should retain its original API/body and mismatched-slice partial-panic behavior; a native constructed equal-length workspace route may change independently. Preferred reversal, deferred0/1 order and all ties must remain exact (`search-candidate-order.md:109–125`; `quiescence-candidates.md:138–146`). Captures, promotions, checks, low-material positions and custom maps remain unchanged priority inputs; this mechanism needs no additional admission restriction.

## Remaining decision evidence

Before any selection: a concise full-permutation proof plus independent original two-pass oracle comparisons on unsigned extremes, duplicate Move identities, repeated keys, lengths around6 boundaries and full512 capacity; preserve public mismatch behavior separately. Backend would then need to price six-head selection/local cursor state, stack/code/bounds effects and direct destination writes in actual ordinary and Q owners. Zero/singleton/all-deferred and short nearly-sorted lists can lose to insertion; no outcome-tuned threshold or density switch is proposed. The current profile cannot resolve that distribution. Keep49 parked and do not transfer its generic or PGO results.

All work here was cold text/JSON/source analysis. No engine, tests, build, new profile/annotation, binutils, runtime source edit, archive or Git operation occurred. Normal speed was requested; this tool interface exposes no runtime speed-control readback.
