# Bounded pure child preparation

This experiment prepares pure numerical inputs for actual ordinary-main children;
it does not validate or reuse speculative search. The previous whole-branch pilot
is closed:34/36 ahead tasks already differed in native node count, including all
12 ahead overflowed tasks (lead assessment `ffa9dba3`).

## Finite mechanism

At ordinary parent request.depth==2, after actual legal generation, sorting and any
initial IIO, offer the first six eligible moves from the current inventory to one
shared bounded pool. Initial IIO requires depth>=4, but publication remains after
that site explicitly. Require Search's guarded coherent descendant permission;
restrict jobs to MoveKind::Ordinary, excluding king victims before constructing
children. The admitted standard workloads begin with valid orthodox games; no
claim covers malformed native placements, promotions, castling or EP preparation.
Those moves retain the original inline behavior. Workers receive owned child
Position, material scalar and White/Black-bound mobility/shelter coefficients.
They build coherent Influence and invoke the same Activity→Shelter helper as
inline FULL. Parent retained state, pawn cache, TT, learning, poll paths and all
logical counters remain exclusively on the coordinator.

The pool has six slots total including cancelled in-flight tasks. One scope is
active at a time; each is a unique token. An owned RAII guard cancels on parent
exit, cutoff, interruption or unwind. Pending/ready slots clear; old running work
can finish but cannot publish into another token. begin_search invalidates the
old scope before root/weights rebinding. No task stores stack references. Each
result checks exact Position chronology/geometry identity; Activity also checks
authoritative Influence, material and bound weights. Sorting indices are never
identities, and pure results can be reused on retries while the scope remains.

Workers park on an idle condition variable. Coordinator lookup is opportunistic:
never wait for preparation; execute the original producer if unavailable. A ready
map is selected **inside** original scratch-None ensure_influence_for_search, with
its original one influence_builds diagnostic charge. Supplied Some maps remain
authoritative. A ready Activity result substitutes only the original numerical
chain in FULL, preserving R publication, pawn selection, retained writes, finishing
and check-dependent tempo at the original boundaries. Unused work charges nothing.
The earlier per-FULL worker mode cannot be enabled alongside this pool.

## Selected checks and collection

Focused numerical/lifecycle and native search-state comparisons precede collection.
Compile generic O3/ThinLTO, no PGO, feature child-preparation only for the measured
candidate. Preserve the original control compiled without this new feature.
Four variants: original control, new budget1(no pool), budget2(one worker),
budget4(three workers). Fixed workloads35/08/04: one excluded warmup each variant,
then three rotated repeats each variant;48 fresh lifetimes. Compare original wire
replay strictly; write pool diagnostics to a separate fresh local file after joined
shutdown, never mix diagnostics into the wire response. Full process wait4 CPU and
RSS include worker lifecycle; search wall endpoints retain original replay boundary.

Coordinator14; worker CPUs6,4,2; siblings7,5,3,15 unused by owned work. Helpers and
builds0–1,8–13. This is observed guest affinity, not a host-isolation claim. One
collection stream, each life bounded180s, total1800s. No PGO/full suites, queue-size
sweep, policy retune, nested workers or general scheduler. Count published/started/
completed, exact-position demands, unique tasks used, repeated map/chain uses,
cancellation and discarded expensive results. Enqueue count alone proves no utility.

Compare budget1 against original for serial hook cost, higher budgets against new
budget1 for mechanism effect, and original for net benefit. Report complete costs
and uncertainty for the three cases, without claiming full-workload scaling or
qualification. Preserve all failures/caps and raw evidence outside Git. Return the
finite result and strongest next recommendation to imp2-lead before another policy.
