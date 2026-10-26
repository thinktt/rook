# Owner-local ordinary inventory during epoch3 FULL

2026-10-26; source/existing-evidence recommendation only. Base: positive epoch64
(`epoch-colors/preparation.json`,64 inputs), not borrowed84d6128b or inventory4.
No implementation, build, engine/helper execution, new census or timing.

Recommend one small generic discriminator, if selected: **prepare directly into
row[p] only when the color pair is not already complete after pawn/local work**.
Otherwise leave generation at original demand. This is untested in the recorded
experiments: earlier inventory2/4 used an additional inventory producer and output
transfer; they did not use the epoch3 coordinator at this boundary. The source
supports exact reuse. Profitability remains uncertain; leaving it parked is
reasonable if another architecture offers substantially more independent work.

The safe seam is concrete. In positive64 `ordinary.rs:813–814`, obtain the exact
map as today, then call an ordinary-private FULL wrapper with a mutable borrow of
`self.candidates[p]`. Evaluator and candidates are disjoint Search fields. Insert
one private preparation hook after squares/pawn/local terms and before color
complete (`evaluator.rs:671–695`), in the existing numerical body. Keep the owned
packet, scalar combination and original final rounding/retained/R/callback order.
No borrowed-input factoring, unsafe alias, new publication, helper, output list,
Arc, Box or list copy is necessary. Public/FRESH/observed/root/Q and modes1/2 use
the original no-hook instantiation; do not add readiness loads to those paths.

At that seam, preserve owner_ready at the original pawn/local boundary. Check
both matching done epochs with Acquire, without taking ownership, reading output
or altering Flight. True proves the existing pair finished; false is only a
racy scheduling hint, possibly stale, and guarantees no useful remaining slack.
Only false plus the private coherent-ancestry permission runs unchanged
`generate_legal(position, row[p])`, then returns an activation-local prepared
boolean. The original complete still owns all joins/output reads/retirement.
A terminal worker error must propagate normally, never become an inventory miss.
This conditional policy avoids known closed-window speculation at the cost of
up to two loads and a branch; freeze it once, without an unconditional variant.

Admission uses the existing validated coherent ancestry. It supplies consistent
mailbox/lists/planes and exactly one in-board king per side. The reviewed
[generation-domain proof](../../experiments/multicore-feasibility/epoch-inventory-four/generation-domain.md)
therefore applies: bounded native generation is total even if a later cutoff
avoids demand; no child is created, no mutable search state is consulted and the
opposite king need not be safe. A per-call validation or opposite-king attack
probe would add redundant work. Arbitrary public positions acquire no permission.

At original generation (`ordinary.rs:867–898`), skip only the producer when that
activation's flag is true. Keep count/generated accounting, empty/mate and ply
bounds, current learning/TT-dependent ordering and extension setup exactly there.
Do not infer preparation from row length. Between FULL and demand, threat reads
no candidate row (`687–700`); bounds/cheap/null cutoffs can discard the flag with
no logical generated/N/R charge. Null descends at p+1 (`841–856`), Q replies write
at their own ply+1 (`quiescence.rs:447–450`), and later IIO follows original demand.
Thus row[p] survives null continuation without restore/storage; descendant learning
changes are still observed by sorting at actual parent demand. Scratch is private
and initialized before consumption (`engine.rs:92–105`); a new activation carries
its own false flag. Stop/error/early return discards scratch, preserves the current
worker close/failure path and emits no invented empty list. Generation has no poll
or ledger operation: prescribed polls/history paths stay at their original points,
while physical responsiveness may change by one speculative generation interval.

The cost contest is short. From the post-owner seam, ideal consumed costs are
`T + J + F + G` now and approximately `max(T, G) + J + F` if generation overlaps,
before readiness-check cost, layout/cache effects and interference. T is remaining
helper work, J actual acquisition, F numerical finish, G native generation. Any
G overrun delays FULL/bounds/stop handling; early-return nodes originally had no
G at all. The readiness hint reduces some waste but cannot prevent overruns or
prove nonregression. Fixed three-thread CPU can still increase through discarded
work and helpers spinning while the coordinator extends the critical path.

Historical ordinary demand76.33/98.41/76.99% and generation medians370/191/250ns
on35/08/43 come from the instrumented serial [census](../../experiments/multicore-feasibility/inventory-overlap/report.md).
The old273ns all-FULL sampled join mean includes acquisition/observation, a different
population and timing boundary; neither value is promised idle slack. Negative
inventory2/4 and lean/layout trials caution against tiny-window optimism, but this
mechanism removes their producer handoff, extra core, output transfer and late
accounting locks. Borrowed scoped-owned's1.738% drift does not identify any single
refactor cost and is not imported or subtracted here.

Smallest decisive next step, only if selected: original35/08/43, preserved7ac3 and
same-image hook-off3/hook-on3 with the existing rotated small replay/idle tools.
Focused controls should cover exact unsorted special/checked lists and ordering,
null continuation/cutoff, early bounds/stops, actual mode3 admission/fallback and
no public/observer hook. Preserve existing lifetime proofs; no hot census or new
framework is needed. Report total wall/CPU and common-path drift, not estimated
saved nanoseconds. Preserve strongest67d and all parked source/results; no PGO,
qualification, adoption or execution is authorized by this recommendation.
