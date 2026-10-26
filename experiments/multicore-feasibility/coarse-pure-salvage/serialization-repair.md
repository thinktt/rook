# Census stop and serialization accounting repair

The first attempt passed11 affected controls and its generic build, then stopped
with WorkPoll before returning a census report. Its cold error path hid the
observer reason. All bytes remain at
`/home/legolas/rook2-experiments/coarse-pure-salvage-20261026-01`.

A diagnostic-only source change exposed that reason and added one focused
propagation control. The bounded diagnostic reproduced `pure-demand-json-cap`
with unchanged keys/caps. It produced no census report and is not a timing result:
`/home/legolas/rook2-experiments/coarse-pure-salvage-diagnostic-20261026-01`.

The original accounting reserved1536 bytes for every unique demand key, allowing
for all9 scope rows even when only one scope occurred. The serializer emits only
nonempty rows. This admitted at most65536 keys under the96MiB partition before
considering its actual sparse shape.

The repair tracks a proved upper bound in O(1), combined across Influence/chain:
`256 × unique keys + 128 × nonempty key/scope cells`. A new key charges384 bytes;
a first occurrence in an additional scope charges128; a repeat in the same scope
charges0. Maximum-width serialization controls cover0..9 cells, shared-kind
accounting and exact-budget admission. The96MiB demand partition,256MiB total
report, key/call/memory/task/time caps are unchanged. No query, key equality,
native payload, candidate threshold or numerical path changes.

Canonical demand observation attaches only at the selected parent's boundary.
Scope guards cover coordinator/queued0..6/later parent suffix. Normal end detaches
it; parent Drop deactivates it on abandoned/error paths. Subsequent root search
stores no demand keys. The prefix pass stores fixed tally vectors only for the
bounded producer set, updated after exact pool lookup; it does not retain every
prefix position/key. It detaches at the frozen boundary.

Original setup tools are preserved byte-for-byte in the failed attempt's
`frozen-tools/` archive. Original receipts are unchanged. The completion reuses
the passed50 historical+11 initial+1 diagnostic controls, executes only the3
new serialization controls, then builds and attempts the same bounded census.
A source/receipt manifest and independent ledger audit bind the completion.
There is still no optimized consumer, cap expansion or parallel campaign.
