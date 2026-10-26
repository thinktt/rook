# Scoped owned/borrowed FULL input: safe evaluator integration

Source workspace:
`/home/legolas/rook2-experiments/workspaces/borrowed-full-input-20261026-01`,
copied from positive epoch64. This integration adds no unsafe code to evaluator,
session, CLI or tests. Transport publication/retirement is governed by the
separate reviewed `ownership-proof.md`; this file establishes the safe caller
boundary and numerical composition. These are source findings, not passing
native evidence.

## Enclosing operation and disjoint ownership

Every actual mode3 FULL call, with either configured owned or borrowed input,
uses `ColorsWorker::with_epoch`. Evaluator no longer obtains a color dispatch
token or calls color completion separately. The returned pair is owner scalar
work plus the joined native Activity/Shelter chain; it carries no guard, worker
borrow or cleanup token that a caller could forget.

`full_impl` takes immutable references to the current node's Position and exact
supplied Influence. It copies current Retained, Weights, phase and material,
borrows `self.root` immutably and `self.pawns` mutably, and separately borrows
`self.colors_worker` mutably. Its owner closure captures only these disjoint
fields/references. It has neither a whole `&mut Evaluator` nor a mutable Node.
No alias, lifetime extension, transmute, raw pointer or caller-side unsafe escape
is introduced. Position and Influence remain immutable and address-stable for
the entire enclosing call. The worker's inaccessible guard must retire all
actual input references on success/error/unwind before that operation returns.

The helper sees the exact supplied map in public, detailed, ordinary and FRESH
calls; this layer does not rebuild, normalize, substitute or retain a different
Influence. Root phase/material/weights are current on each call. No callback can
move or mutate the source input during the guarded interval.

After `with_epoch` returns, the disjoint temporary borrows have ended. Only then
does `full_impl` close a standalone call activation, calculate original tempo,
update node retention and age, publish diagnostic/cache statistics and R, invoke
component callbacks, and perform the original native final-score/bound finish.
An existing outer search activation can remain active, but its per-call input
borrow has already retired. Standalone calls close their activation before the
first user callback. An owner-closure unwind relies on the enclosing worker
guard, not the optional standalone activation or eventual outer search exit.

## One numerical owner body and preserved execution order

`full_owner_work<FRESH>` takes only explicit Position/Influence, Retained copy,
RootContext reference, Weights copy, mutable PawnCache, phase/material and an
inline-chain `FnOnce`. It performs the original native sequence:

1. Ordinary cache selection or forced-fresh pawn structure, then current pawn
   terms and their exact repeated relation-query charges.
2. Invoke the inline-chain producer.
3. Original structure weighting, phase-gated selected pawn progress, central
   influence, fixed patterns and root/current square balance.

It returns Components with Activity/Shelter/tempo zero, pawn R/reuse scalars and
an optional inline chain. There is one source body for pawn/cache/progress/local
arithmetic. Both mode3 transports call it with a producer returning None; the
worker concurrently runs the original two color chains. Mode1 calls the original
Activity/Shelter kernel between pawn inputs and local terms. Mode2 still dispatches
the existing whole helper before pawn inputs and joins it after local terms.

All routes converge on the existing final tempo, component insertion, retention,
R and native finishing body. No intermediate round, material clamp, side sign,
pressure production, cache match/collision/order rule or FRESH bypass is replaced.
R remains `pawn R + Activity R`, published once on the coordinator. Physical
transport and waiting add no logical work. Existing numerical tests remain
applicable to the unchanged component kernels.

The archived child-preparation feature retains its existing `take_chain` result
authority and original inline position through the callback. A configured pool
cannot coexist with color/whole helpers, and enabling borrowed inputs or a new
pool rejects their combination. No new preparation mechanism is added.

## Configuration and cold reporting

`borrowed_inputs` defaults false. Evaluator and Session expose the private
research setter; an existing ColorsWorker applies it through its fully-idle
configuration API before the evaluator flag changes. If mode3 is configured
later, a new worker applies the stored flag before any old worker is retired.
Failure leaves the old evaluator choice intact. Budget1/2 and the existing
requested/permitted-CPU cap of three retain their execution policy.

The private `--borrow-full-inputs` CLI switch sets the choice before thread
configuration. `--inspect-threads` retains exactly the existing requested/configured
two-field JSON response. No protocol command or production default changes.

`finish_colors_report` first shuts down and joins the color worker, then appends
its fallible `scoped_report()` as `scopedInput` to the original readiness JSON.
That cold record witnesses actual configured mode, request/done epochs and true
retirement. Budget1/2 append `scopedInput:{enabled:false}`. The preserved7ac image
and its original report schema remain untouched. Reporting performs no hot
arrival census or transport timing observation.

## Added focused source controls

Five tests under `evaluator::borrowed_tests` cover:

- Detailed/full/FRESH equivalence against inline1 and scoped-owned3, with both
  diagnostic settings, root-side/phase rebinding, asymmetric/zero weights, check,
  retained input and authoritative contrary supplied maps; exact R/statistics.
- Cleared zero identity, group-zero replacement, real full pawn-identity
  collision, retained descriptor reuse, FRESH bypass and repeated search resets.
- Callback unwind after a retired epoch while an outer activation stays active,
  source input mutation, a second FRESH call and successful reuse/park/report.
- Actual root preparation and seeded Search depth1/depth2 for fixed initial and
  ending positions, comparing candidates, root returns, steps/PV, score, complete
  work/evaluation statistics and parked completion against independent serial.
- Stored/toggled mode configuration, requested1/2/3 and permitted1/2/3 fallback,
  later creation of a color worker, and cold actual epoch/mode/retirement reports.

Existing color numerical, evaluator lifecycle and unaffected whole-helper controls
can be reused. Worker-owned tests separately establish owner-work unwind with a
delayed reader, peer failure/close/drain and input/output retirement. The finite
controls do not imply full conformance/gameplay qualification.

No build, test, engine run, Git action or subagent was used by this source owner.
