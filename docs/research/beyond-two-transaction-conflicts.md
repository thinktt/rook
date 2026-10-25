# Beyond two threads: transaction conflicts and recovery boundaries

2026-10-25. Source and existing raw evidence only; no execution, build or engine
change. Read against the restarted [mission](../deterministic-multicore-mission.md).
The original whole-branch pilot remains negative: **0/36 ahead tasks accepted**.
The two accepted 877-node branches were the same profile08 head with
`ahead_distance=0`, repeated at queue depths 2/4. This does not establish a limit
on a different recovery architecture.

Evidence is the [committed report](../../experiments/multicore-feasibility/branch-transactions/report.md),
[lead assessment](../../experiments/multicore-feasibility/branch-transactions/lead-assessment.md)
and [hash-bound results](../../experiments/multicore-feasibility/branch-transactions/results.json).
Pilot source was `48271d5d304a85969ca9959ca85ce54fc5d703a4`, ELF SHA256
`165d240a0315b1c372e254e57398584b043f2722b6fc58055f9c0999adc5cf40`.
Raw files below are under
`/home/legolas/rook2-experiments/branch-transactions-20261024-01/pilot/`.
Each table basename has the suffix `.stdout`.
Candidate `index` is the reported native root index; journal events are zero-based.

| Raw stdout / candidate | Actual first rejection | Speculative / canonical N | What the retained evidence establishes |
|---|---|---:|---|
| `02-profile-08-q2`, index2, id1 `f3f4`, ahead1 | ordinary-order, event3 | 151 / 88 | Changed native initial ordering; complete uncapped 574-event certificate |
| Same file, index4, id2 `c2d1`, ahead1 | ordinary-order, event3 | 85 / 85 | Equal N does not rescue changed order; 307 events |
| `04-profile-04-q2`, index5, id30 `e2e4`, ahead1 | ordinary-order, event3 | 975 / 975 | The only other equal-N ahead witness; 3052 events |
| `00-profile-35-q2`, index5, id8 `f7f5`, ahead1 | pawn-selection, event6 | 2608 / 2630 | First ordinary order passed; a later native selection changed; 7762 events |
| `01-profile-35-q4`, index4, id7 `f7f6`, ahead3 | request-window, before replay | 2426 / 1917 | Uncapped 7570-event branch already has an obsolete entry request |
| `00-profile-35-q2`, index2, id4 `d7d6`, ahead1 | log-overflow, event16384 | 36985 / 43402 | 101277 attempted events; no semantic prefix was replayed |
| Every file, `late-probe-mismatch-rolls-back` control | TT probe, event30 | 13-node fixture | Artificial suffix observation rejects after24 staged write events; canonical state remains unchanged |

The retained JSON reports kind/index, N, pass count and costs; it does **not**
serialize journal payloads, actual/expected move inventories, pawn identities or
descriptors, requests, per-candidate R, or the canonical execution trace. Thus no
specific changed killer, moved inventory slot, hit→miss direction, or descendant
call path can honestly be recovered from these files. `oracle_match=false` on
rejection is initialized before replay and is not a separate measured output
comparison ([driver](../../src/branch_transactions.rs:533)).

The prototype already validates native operation results rather than broad
snapshot equality ([journal](../../src/branch_journal.rs:75)). It reruns mutable
TT probes, native replacement stores, pawn selection, learning clears/records,
and native sorts against detached **current canonical** staging. Speculative
final table/cache bytes are never installed. Whole-state equality is the
independent canonical audit after a certificate passes, not its read predicate
([driver](../../src/branch_transactions.rs:536)). No pilot audit failed.

All 22 natural ordinary-order first rejections are event 3. At that first sort,
the entry clear, TT observation and FULL pawn selection have passed. The fixed
Position, RootContext, Influence and preferred hint leave current learning as
the varying ordering input: current-ply killers and/or history change the native
inventory, not merely numerical priorities. At root-child ply 1 the earlier-ply
killer pair is absent. `clear_next(1)` clears ply 2, not ply 1. Native priority
uses killers and history; native sorting also partitions at priority > 1 and uses
its prescribed reverse/gap 6/gap 1 chronology
([learning](../../src/ordinary_policy.rs:407),
[priority](../../src/ordinary_policy.rs:534), [sort](../../src/tactical.rs:338)).
The raw evidence cannot distinguish a changed first item from an unused suffix.

Complete inventory equality can therefore be conservative, but replacing it
with “same best move” is unsound. The quiet-mate loop examines ordered candidates;
initial IIO searches/promotes candidates; tail IIO can reorder after child0;
ordinary main order sets full/scout windows, frontier skips and retries.
Learning records, including global history rescaling, and TT stores follow those
decisions ([mate/IIO gates](../../src/ordinary.rs:910),
[main control](../../src/ordinary.rs:985), [IIO body](../../src/ordinary.rs:1151),
[learning](../../src/ordinary_policy.rs:414)). A narrower order observation must
cover every actual consumer, including IIO and mate probes, and preserve later
effects. Recomputing the sort alone does not validate the old recursive suffix.

The eight request rejections occur before any certificate inspection. The gate
compares depth, complete Attempt and history; its label does not itself report
which field differs ([gate](../../src/branch_transactions.rs:262)). In this fixed
root tail, proposal preserves the old best whereas native `next` recomputes
`aspiration(best,previous)` after preceding returns; best/window changes are the
source-supported explanation, without retained endpoint values
([proposal](../../src/root_schedule.rs:90), [next](../../src/root_schedule.rs:140)).
Bounds affect TT usability, FAST/FULL returns, NULL and child/scout requests;
they also determine stored lower/upper flags and root retry/ranking. A matching
returned score does not preserve prescribed work or stores.

The one pawn rejection compares the entire returned `Selection`, not the 8 KiB
cache. Different old victims are already accepted when miss remains miss: the
native miss overwrites them with the same pure construction. A hit instead
retains its prior descriptors and order ([cache](../../src/pawn_structure.rs:121),
[replay](../../src/pawn_structure.rs:172)). Those descriptors feed base scores,
weakness-dependent R, retained pawn arrangements and ordered progress candidates
([terms](../../src/pawn_terms.rs:337), [piece terms](../../src/pawn_terms.rs:242),
[progress](../../src/pawn_progress.rs:249)). One cannot substitute fresh placement
for a hit or keep old FULL components after a changed selection. A repair may
rerun selection and its pawn consumers while retaining exact-input independent
Activity/Shelter calculations. Hit/miss diagnostics and FULL retained publication
must follow the canonical result too ([FULL](../../src/evaluator.rs:581)).

There is **no natural first TT rejection** in the pilot. The suffix control is
particularly narrow: an originally empty group is probed at ply 1/target 3 with
window [-10000,10000]; the perturbed entry stores 777, no hint/mark/quiet flag.
Both probes have `score=None`; the changed field is `Bound::None→Exact` because
777 crosses neither endpoint. The appended probe's result is discarded by the
fixture. This proves rollback machinery, not an observed search dependency
([fixture](../../src/branch_transactions.rs:768),
[perturbation](../../src/branch_transactions.rs:876),
[probe semantics](../../src/remembered.rs:110)). Complete ProbeResult equality
can exceed actual consumption: on a usable score ordinary search immediately
returns it, ignoring other metadata. On a miss, hint, quiet flag, marked depth
and bound have distinct later consumers. Any narrower predicate must still
execute mate-depth mutation and native stores against current replacement state;
ignoring an unconsumed field must not preserve a store derived from its stale
value. The accepted untouched-TT/pawn-victim control already rejects the claim
that entire unchanged groups are required.

Overflow is a certificate limit, not a demonstrated dependency. Replay rejects
an overflowed log immediately, so event 16384 is not a first divergent operation
([journal](../../src/branch_journal.rs:86)). There are 16 capped tasks but only 9
first overflow rejections because request validation wins first. Nevertheless,
all 12 capped **ahead** tasks already have different speculative/canonical N.
Across 36 ahead tasks, 34 differ in N; the remaining 85/975-node tasks above both
fail actual order. Raising the cap cannot make these unchanged whole branches
valid. It could expose earlier conflicts or recoverable subsegments, which is a
different experiment. Full 16 MiB TT copies and 352-byte events also remain major
prototype costs; this serial pilot measures no queue speedup.

**Strongest next discriminator, unimplemented:** keep the fixed-completion
NoHost/timing=None/inline-evaluator environment and existing cap; use profile08
queue 2 indices 2/4 as uncapped natural ordering fixtures. Index recursive entry/
return segments within a shadow branch. At canonical consumption, execute the
parent natively from entry, including its current sort and original control.
At each actual child
demand, try a recorded segment only with exact entry Node/retained state,
history, Request, predecessor, root epoch/weights, geometry provenance, phase/
pass and candidate occurrence; then replay that segment's native operations
against current staging. Commit only its validated effects, output and exact
N/R delta. Otherwise execute that call natively. Identify segments by path and
immutable move identity, not the new sorted index. This tests recovery after an
observed conflict without pretending the old whole branch accepted. Logging the
first changed inventory positions and exact segment miss reasons would fill the
specific missing evidence above. Report reused canonical N/R and removed native
cost against repair/replay/copy/waste costs, with the canonical full-state oracle.

An exact-input pure-result memo can supplement failed segments: Influence,
Activity/Shelter, and fresh pawn-miss construction, with logical charging and
authoritative cache/retained effects still performed at original demand. It
needs exact Position chronology/map/root-weight inputs, not only hashes or a
score. This is fallback salvage, not evidence that segments survive. Pausing
before the first unresolved TT read leaves only entry/check preparation before
FULL and exposes little branch depth; pausing before event 3 saves at most that
node's preparation unless descendant work speculates. Neither cheaper validation
nor wider queues alone addresses the observed disagreement.

Live stopping remains outside this discriminator: admission precedes N increment,
polls follow each 4096th canonical charge, and polls can consume Host commands with
the current history path ([charge](../../src/engine.rs:223),
[poll](../../src/timed.rs:400)). Full segment N/R totals cannot reproduce an
interrupted prefix. Timed/Host use would require canonical charge/poll/effect
prefixes or conservative boundary rejection before any adoption.
