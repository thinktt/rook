# Closed three-unit functional study

The four routes produce the exact released projections. In this opening sample,
standalone position history and evaluation show no large relative cost deficit;
the composed light search remains slower than the reference observation. Keep
the current Position/Node ownership for now and proceed with the planned pressure
producer/consumer compiler discriminator. These observations do not identify
which search component owns the remaining difference.

CPU times below are **microseconds per complete sequence**, including real reset,
native operations, typed normalization and full projected-field consumption.
Ranges retain all three measured batches; one warmup per row is excluded.

| Route | Frozen sequences/batch | Local CPU min / median / max | Whole-owned CPU median | Reference local CPU median | Local/reference median |
| --- | ---: | ---: | ---: | ---: | ---: |
| Opening evaluation, scalar | 43,999 | 8.800 / **8.955** / 8.972 | 9.001 | 15.753 | 0.5685 |
| Opening evaluation, coherent | 47,673 | 8.239 / **8.307** / 8.385 | 8.349 | 15.753 | 0.5274 |
| Opening position history | 213,636 | 1.873 / **1.888** / 1.991 | 1.897 | 11.562 | 0.1633 |
| Light-start composed search | 8,965 | 43.298 / **44.451** / 44.941 | 44.864 | 38.986 | 1.1402 |

Reference local CPU ranges are 15.752–15.771us (evaluation), 11.514–11.573us
(position), and 38.490–39.048us (search). The observed search ratio envelope is
1.1088–1.1676. Median local wall times are 8.957, 8.308, 1.888 and44.457us in
the same row order. The coherent evaluation median is7.24% below scalar in this
driver; production62 already uses the coherent producer, so this is no new
production gain. Position's observed spread is about6.2% of its median and
search's about3.7%; none of those samples was replaced.

## Execution and validation

Derivative ELF: `a93ffb871ed8912c5af3b9ac94c8d4a63d4f71616a39785c062b7423938c5836`,
7,390,304bytes, mode0555. Source76 graph:
`62893b9fe8c5ef7c9d93dcac9aa0d7439d3ee592987c8f407cd432486c37fa93`.
It adds the study driver and locked serde_json dependency to the retained62
source; native numerical/search routines remain byte identical. Canonical74
source/tool files were rechecked unchanged after the stream, and retained62's
ELF remains `01237e6dfe89822e540d0f07c7b70f7227537a846ce8c69ea9e91167b759e98d`.

Generic x86-64, Rust1.85.1/LLVM19, O3/thinLTO/one codegen unit, panic abort,
debug1, fresh own-source PGO and profiled-only ExtTSP were used. Own profile
`fbc299d355940b6f80978dee70fd75391bbcbfbcd2a1e30013e3abe34cd44c53`
contains54 original wire training lifetimes plus four explicit functional
**verify** coverage lifetimes. It does not train the measure loop itself. The
original54 replay checker and independent offline replay check pass; independent
profile remerge is byte identical. There are no missing/stale-profile diagnostics;
two ordinary unused-code warnings remain. The existing library suite passes193
tests. All four frozen-use original projections pass before calibration.

One probe per row (256/256/256/1024 sequences) froze counts aiming400ms. Then
16 timed batches and32 separate bracketing verify lifetimes completed without
failure. Measured batches used387–425ms process CPU. Every evaluation sequence
has17 complete observations and39 charged relation queries; each search has
54N/234R, completed depth2, the exact PV and20 ordered final root scores.
The existing seeded callback supplies raw returns in last-iteration visitation
order. The search count includes35 TT generation-wrap scans per batch, derived
from the unchanged clear owner; the calibration count includes four. Real pawn,
learning and TT logical clears stay inside the local clock.

All52 calibration/collection native lifetimes are uniquely identified, reaped,
untruncated and hash stable, with actual wait4 user+system accounting and observed
single-task CPU14 placement. Helpers use0–5,8–13. CPU15 guest snapshots show zero
user/system ticks and927 additional idle ticks during collection; these are point
observations, not continuous host isolation proof. Offline verification rechecks
the original32 projections, all20 timed outputs including probes, counts,
native-account receipts and the still-exact source/provenance closure. Actual
outer completions: calibration `36bc17/0`, collection `3d40ab/0`, offline audit
`4a5c93/0`. One precollection metadata scan falsely matched a compiler flag as a
warning; its assertion was corrected before the first probe, and its failure
record is retained. No engine/training/measurement launch was retried.

## Interpretation and next step

Evaluation binds its fixed RootContext once outside the local clock. Each
sequence clears the actual pawn/stats state and creates a fresh Node, retaining
state only through its own16 moves. Position similarly performs all16 actual
transitions and consumes initial plus every descendant state. Neither local
row includes JSON or legal descriptor preparation. Both use reusable typed
observation storage and injective semantic encodings for consumption; no
synthetic control is subtracted. Reference observer and allocation costs can
differ, so these low ratios do not prove a proportional production advantage.

Search includes native root preparation, real logical resets, callback/vector
work and full root-result consumption. Physical table/arena provisioning is
cold and reused; final destruction belongs to the whole-owned guard. This is
an owned-call/enclosing-local comparison. The narrower reference controlled-call
ratio is unavailable. Subtracting position/evaluation times from search or
assigning the14.02% descriptive difference to TT, generation, restoration,
pressure or root context would be unsupported.

The reference observations came from Bee, using separate local/search adapter
images `a74c7fc6…` / `1460aabc…`; production-context `bf71485c…` does not establish
their exact compiler/profile recipe. Host, profile, observer, reset/allocation
and three-sample uncertainty remain. No PMU, universal Vic/Bee conversion,
precise production partition, production speedup or qualification is claimed.

The useful next decision is a bounded code/frame review of the already proposed
pressure producer/consumer representation, with focused semantic controls before
timing. This study supplies no case for a broad ownership rewrite. It also does
not rule out Position/Node copy or middlegame pressure costs inside composed
search. The separate checked-slider source prototype can remain isolated until
the lead selects its native discriminator.

Raw/build/profile evidence is external at
`/home/legolas/rook2-experiments/functional-cost-three-unit-20261020-01`.
`closed-summary.json` pins named supports and exact artifact identities; the
reproducible setup and complete derivative patch are beside this report.
