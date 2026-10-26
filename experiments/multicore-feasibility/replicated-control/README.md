# Replicated control: park this fixed implementation

**Replicas cost3.95% more search wall than matched packet3 and4.76% more than
preserved-source packet3.** Case35 loses with separated ranges; short-case
median gains over matched packet do not offset it. Park unchanged: no layout,
transport or PGO rescue, adoption or extra run is selected.

[Timings/ranges](timings.csv), [results](results.json), [closure](closure.json),
[plan](plan.md), [policy](policy.json), [source review](source-review.md),
[collective proof](collective-proof.md), [evaluator proof](evaluator-proof.md),
[runner proof](runner-proof.md), [source patch](source.patch).

These are **matched generic panic=unwind library/driver builds**, actual seeded
NoHost fixed-completion depth8, timing absent and unrestricted fixed root policy.
They use the original35/08/43 placements/history/config/parameters, seed0/rnd0,
but are not the original timed protocol, original7ac executable, full54 timing
or production qualification. Every replica retains the original input TT capacity.

One excluded warmup plus three fixed rotations per case/configuration:60 timing
lives (45 measured/15 warmups), no idle series. Values are sums of case medians.

| Case | Preserved inline1 | Preserved packet3 | New inline1 | New packet3 | Replicas3 | Replica vs matched packet |
|---|---:|---:|---:|---:|---:|---:|
|35|6.937886s|6.051800s|6.970736s|6.094073s|6.355377s|+4.29%|
|08|0.309434s|0.309490s|0.311815s|0.316453s|0.312752s|-1.17%|
|43|0.080313s|0.078763s|0.080133s|0.079989s|0.078599s|-1.74%|
|Median sum|7.327634s|6.440053s|7.362684s|6.490515s|6.746727s|+3.95%|
|Joined CPU median sum|7.334560s|19.326059s|7.369463s|19.477928s|20.245315s|1.03940x|
|Native lifetime wall median sum|7.354940s|6.498890s|7.390485s|6.550838s|6.808447s|1.03932x|

Case35 supplies about94% of the summed wall. Its replica range6.284767–6.359438s
is above matched packet6.089717–6.104448s and preserved packet6.031399–6.058424s:
+4.29%/+5.02% by median. Cases08/43 gain1.17%/1.74% over matched packet, with
overlapping ranges; versus preserved packet they cost1.05% and improve0.21%,
also overlapping. The finite samples establish the large35 loss, not universal
repeatability or useful gains in the short cases.

New inline costs0.478% and new packet0.784% over their preserved-source controls
in aggregate. Per-case new packet drift is+0.70%/+2.25%/+1.56%; common extraction,
audit-disabled guards, feature code and layout remain priced. Replicas still
beat preserved inline by7.93% wall but use2.76026x CPU. Existing packet3 remains
the stronger three-thread option in this study.

Median native peak RSS is53004–53068KiB for replicas, versus19188–19328KiB
preserved packet and19296–19456KiB matched packet (about2.74x). Three complete
private TTs, duplicated state/control/Influence/finishing and the collective are
real costs. The aligned per-role publication/double-slot choice was fixed before
data; its native Shared body is704B, excluding Arc/allocator overhead and Search
state. This is a layout fact, not a measured cache-miss cause.

Search wall begins after saved GO is accepted, immediately before native call /
replica-gate release, and includes all actual Search calls,
normal finish and real helper/peer joins. The coarse replica join median sums
0.516685ms versus matched packet0.196366ms; these are final-call shutdown tails,
not per-FULL collective latency. Cold output/state comparisons and TT teardown
are outside search wall. Whole native wait4 CPU/wall/RSS includes startup,
allocation, comparisons, teardown, joined threads and Python pre-exec prefix.
No duplicate work or setup cost is subtracted away.

All29 focused controls pass first attempt:8 two-slot/cancellation controls,
5 evaluator simulation/audit controls,4 runner startup/failure/divergence controls,
8 original color-owner/3 color-scope and1 original two-thread numerical matrix.
They cover a fast lane one epoch ahead, delayed reader/parity reuse, missing
future demand, cancellation/overflow, actual joined startup/entry/callback failures,
owner-only pawn collisions/reset/FRESH/custom maps, original rounds and R/N.
Both study lib/bin effective compiler recipes prove panic=unwind, with cold
assertions; failed FULL cancels and unwinds rather than returning a dummy score.
This does not replace the ordinary release panic=abort policy.

Three separate depth2 native audits pass. Independent serial execution records
61/59/121 structured FULLs (241 total); each of three replicas compares every
actual input/output/root context/retained state/N/R against that trace. Cold final
TT fields, learning/history/PV/root returns/work agree, and owner PawnCache equals
serial. Shared arithmetic means independent execution, not an independent numerical
implementation. Final-state checks can miss a transient unrelated write later
overwritten; this is finite plumbing/state assurance, not exhaustive per-node
proof or depth8 FULL-input auditing.

Depth8 performance uses Search<false>, with no trace, expected future FULLs,
audit signatures or state snapshots. Every complete structured output agrees in
all20 lives per case, including warmups: final score/PV, raw root-return sequence,
per-iteration candidate order/score/PV and logical N/R. Necessary final epochs
match on all three unique roles; no success is fabricated. Physical replica node
counts are never summed into King's logical work. Cold outcomes and counts bind
in results; raw structured streams remain outside Git.

Each lane actually traverses private deterministic control. Role0 alone selects
PawnCache and calculates pawn/local components; roles1/2 calculate original
White/Black Activity and opposite shelter. One scalar allgather feeds original
composition/finishing locally, without a second final-score broadcast. Two slots
and monotone ready>=g preserve reverse read retirement. All-active spin/cancel
uses no single-waiter latch, and the concrete guard joins every started peer.
This removes Position/Influence publication but introduces no independent branch
search or new numerical width. Integrated results price the complete tradeoff;
they do not isolate copying, TT traffic, arrival skew or scalar-reduction costs.

Actual roles were verified at main14/peers6/4 before GO, with H0-3,8-13 reversibly
placed and restored; owned siblings15/7/5 were unassigned. Guest placement is not
host exclusivity. All63 native audit/timing receipts are terminal exit0; all10
command stages exit0. No native-lane source/tool repair, benchmark repeat or clock
reset occurred. Original pipeline249.451s/collection150.311s are within3600/1800s.
No native work remains, and no further lane was started.

Exact matched study images:

- Preserved-source control: `d61a38fe72e51bf14ef63e43d34488b07631d4c7b4fafde01ab23037fefd62f1`,7608904B.
- New study: `92a3abe42b1e78d372d9bfebdabdb6761979a30e1d889c7f7be4bba3aab5c149`,8427592B.

The65-input preserved overlay retains all positive64 engine files except an empty
feature declaration, plus the byte-identical driver. New overlay has68 inputs.
Driver hash, recipes, source maps and actual output bindings are in
[preparation](preparation.json) and closure. Raw builds/streams:
`/home/legolas/rook2-experiments/replicated-control-20261026-01`.
Source overlays:
`/home/legolas/rook2-experiments/workspaces/replicated-control-20261026-01` and
`/home/legolas/rook2-experiments/workspaces/replicated-control-preserved-20261026-01`.

Retained67d011/profile948747, main and all21 protected artifacts remain unchanged.
This negative does not rule out borrowed input or all replicated controllers;
no production Host/protocol, >3 scaling, PGO, qualification, adoption or external
execution follows from this finite study.
