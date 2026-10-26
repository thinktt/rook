# Q owner-local tactical preparation: caller proof

2026-10-26. Bounded implementation under
`/home/legolas/agent-memos/imp2-lead-to-imp2-q-owner-local-discriminator-20261026.md`.
The active RESET policy requests a stop only on the external manager's explicit
RESET alert; no alert was present and no local quota monitoring was performed.

Base: exact ordinary owner-local66 source in
`/home/legolas/rook2-experiments/workspaces/owner-local-inventory-20261026-01`.
Destination: isolated `q-owner-local-20261026-01` under that workspaces directory.
This owner edits only `src/quiescence.rs`, its new cfg(test) test module and this
proof. Evaluator/CLI/tool changes belong to other owners.

## Admission and row lifetime

The actual Q body initializes `q_inventory_prepared = false` on each activation,
after the existing draw/terminal-ply returns. Checked nodes bypass selection.
Observed nodes retain select_noncheck_stages_observed. Only the unchecked,
non-observed branch calls the agreed private API:

```rust
select_noncheck_q_inventory(
    node, lower, entry.upper, entry.capture_exception, &mut influence,
    coherent_geometry, !replies_available, &mut self.candidates[ply],
) -> (Selection, bool)
```

Evaluator and candidate row are disjoint mutable Search fields and are borrowed
safely in the call; no raw alias, list copy, allocation or new sharing is added.
The evaluator owner retains the original mutually exclusive sparse-FULL and
FAST/optional-refresh selection, authoritative supplied/lazy map and one FULL
numerical body. Its boolean starts false and becomes true only after the exact
native tactical producer completes. The existing post-owner readiness check
admits preparation only with the Q flag, coherent permission, allowed non-reuse
and configured colors3. Ready skips preparation; pending does not grant output
ownership or imply useful remaining time. Original complete still joins.

The caller stores that returned boolean. Evaluation bounds and stand-pat retain
their original position after evaluation. If either returns, any prepared row is
discarded private scratch, with no generated/examined/child charge. Otherwise,
at original unchecked tactical demand, skip only generate_for_search when this
activation actually prepared. There is no null descent or intervening recursion
between the hook and this demand. The row remains owned by this activation;
subsequent descendants use higher rows and cannot overwrite it before demand.

Count publication, empty return, tactical sorting against current learning,
observer events, frontier/recapture/capture screens, projected legality, reply
probes, actual child construction, history push/pop, N/R charges and logical
polls remain in their original order. No FULL is forced for FAST-only work.
Checked/reused replies, terminal-ply FAST, public permission-clearing calls,
observed/FRESH routes and modes1/2 cannot prepare or query readiness through this
hook. Ordinary owner-local behavior remains separately controlled and unchanged.
One speculative pure generation interval may extend physical stop latency;
it adds or moves no logical poll.

## Accepted totality bound and exact producer binding

Private root validation and maintained ancestry provide canonical mailbox/list/
attack-plane agreement, valid squares and exactly one king with at most sixteen
pieces per color. Legally reachable orthodox positions are not required.
Every nonking contributes at most queen geometry's27 destinations, and king
captures at most8. Each slider emits only empty squares before the first blocker
plus at most that blocker, a subset of its original disjoint movement rays.
Checking-mask extension cannot extend those movement rays. Pawn main emits at
most two captures plus one quiet move: quiet queen promotion and quiet ordinary
are mutually exclusive. Global EP and quiet-pawn-check prefixes add at most2
each. Thus `15*27 + 8 + 2 + 2 = 417 < MOVE_CAPACITY(512)` even with duplicates.

All capture arms exclude king victims. Joined EP admits the actual opposing
nonpawn victim and emits a descriptor without applying it; promotions emit one
queen choice. Bounded offsets, validated lists, guarded bit extraction and the
promotion condition guard indices/shifts/unwrap. First-blocker occupancy really
is nonempty mailbox occupancy under coherence. The king-victim assertion in
tactical preference belongs to later ordering, not this pure producer. No
child, score, Influence, root-value or learning dependency is introduced by
moving production before evaluation_return. No extra runtime probe/validation
or bounded-generator variant is needed on the admitted domain.

SHA256 bindings in the isolated source (all unchanged from base):

| File | SHA256 |
|---|---|
| src/tactical.rs | 22fb473a0c3288a1ce392833e1dd09749bc77d795d3b697ba1071f21b58d3d4d |
| src/tactical/check_masks.rs | 8468db1a066e1e6983271e3b54d6023c20d3b55386a775098f0db48472cec626 |
| src/movegen.rs | 2665dfbc957191b06f82c35412f72be94943944cffd0c04851bdcdc91086dcc8 |
| src/position.rs | e85eb42304bb010ea199160568b215958f9de966cc71d398e8e0e42553054d82 |
| src/attacks.rs | 00d4d2a89c32626be5ef501bc377d427a90588f28b2913e59438a1772e4494f3 |
| src/types.rs | 2a202da079b16b3becb6651427701ec8e40aed88bd19550854c800b842b22feb |
| src/geometry.rs | 582a2e8ad2672a937062ae829ae596ee263b69c6ec52103c55c658a6ecc225f1 |

Relevant unchanged anchors: tactical.rs:81-183; tactical/check_masks.rs:9-32,
45-81,85-150; movegen.rs:10-43; position.rs:431-462; attacks.rs:21-84;
types.rs:68-75,173-185. Base caller seams are quiescence.rs:275-285 terminal,
290-314 selection/return and325-347 demand/count/order.

## Focused caller controls and handoff

Six new `quiescence::q_inventory_tests::q_inventory_` controls use cfg(test)-only
TLS snapshots immediately after parent selection and at original unsorted demand.
They use the existing forced-readiness and query-entry probes. No production
counter/storage/test framework is introduced.

- Actual sparse FULL with queen promotions and joined nonpawn EP, plus START's
  actual FAST-to-FULL refresh and empty tactical list: preparation/demand vectors
  equal direct native unsorted production and the off route; original charges
  and sorted rows agree.
- Actual sparse static return: nonempty physical preparation is discarded with
  generated/examined/children uncharged and identical score/state/N/R.
- Strict refresh-edge FAST-only and configured1/2 actual FULL: no Q readiness
  query/preparation; FAST-only retains zero Influence builds.
- Checked mate/reused replies, explicit unchecked reused admission and maxply
  FAST: no Q readiness query/preparation.
- Public subtree/root and observed private Q with coherent permission retained:
  no Q readiness query/preparation; observed FULL remains visible.
- Real child NodeLimit(1), capture-promotion ordering and subsequent ready-arm
  reuse of the same owner/node/history: exact work/state/learning/used-row
  equality, one actual child charge path, and a fresh false preparation flag.

Fixtures: START; `1r5k/P7/8/8/8/8/8/7K w - - 0 1` (quiet/capture promotion);
`7k/8/8/3Pr3/8/8/8/K7 w - e6 0 1` (joined rook-victim EP); and
`7k/6Q1/5K2/8/8/8/8/8 b - - 0 1` (checked mate). Tests create independent
SearchHistory values and use public set_threads(3), not evaluator-private
affinity APIs. Source count is six tests; no execution result is claimed.

Existing cfg(test) row snapshots copy only within tests. Unused scratch bytes may
differ after static discard and are deliberately excluded from persistent-state
equality. Parent owns affected-filter freeze, compilation/repair and native
admission. This owner performed no builds, tests, native/helper execution,
profiling, binutils, Git or subagent work.
