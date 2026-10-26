# Conditional inventory4: bounded source review

Source-only challenge, 2026-10-26. Reviewed the landed isolated source at
`/home/legolas/rook2-experiments/workspaces/epoch-inventory-four-20261026-01/src/`.
Pins below refer to that source as read after the conditional worker landed.
The pre-data follow-up confirms removing its redundant opposite-king attack
check; the selected domain below includes that simplification. Numeric pins
identify the original landed read, before that deletion shifts later lines.
No worker/canonical source was edited and no engine, build, test or native
experiment was executed by this reviewer.

**Finding:** no blocking source defect found in the conditional input/output
lease, sparse requests, two-stage completion, lifecycle drain, caller scope or
activation-local receipt. The focused controls still require their owner's
execution; this is not a test-pass or behavioral qualification claim.

## Input and output ownership

- Dispatch takes Control, requires an active nonclosing scope and None flight,
  then initializes the one Packet (`colors_worker.rs:416-443`). The unpublished
  failure hook precedes counters and all publications (`445-449`). Participant
  metadata is installed before either request Release; the two stores and
  epoch advance form an infallible tail under Control (`451-473`). There is no
  partial-publication rollback or mutable Influence fill after publication.
- `inventory = coherent && inventory_enabled()` (`436`). The ordinary-only
  entry passes the trusted private ancestry permission. Public/root/Q/FRESH
  dispatch uses false, leaving the private request untouched (`390-405,
  468-471`; `evaluator.rs:608-629,664-673`). Only defensive king-count checks are
  required before generation's king indexing (`colors_worker.rs:831-858`). The
  extra opposite-king `in_check` rejection at original line 834 has no fatal
  dependency and should be removed before the one variant is frozen. The
  producer never creates a child or invokes Position's king-victim/list
  assertions; native king-victim exclusions remain unconditional. The same
  immutable input reaches the same unchanged producer at later canonical
  demand. The separate [generation-domain argument](generation-domain.md)
  closes totality without an initial safe-opposite-king condition.
- Inventory loads only its own request and permits increasing jumps
  (`733-736,879-880`). On skipped epochs it forms no Packet/output reference.
  A requested epoch cannot be skipped by a later dispatch: Published or Joined
  excludes dispatch until that participant completes or actual drain retires
  it. Private `seen` is updated after done (`746-758`), including when a helper
  is delayed after its final access. Packet and mutable output references are
  confined to `compute_inventory` and end before production counters and done
  Release (`845-872,749-757`).
- Color completion remains exactly two matching done Acquires (`897-899`).
  Complete rechecks Published ownership under Control, copies only the scalar
  color outputs and records color completion once, then chooses Joined for an
  inventory participant (`494-545`). It can return while inventory is still
  borrowing input; it cannot authorize the next Packet write.
- Settlement waits outside Control, then requires matching Joined ownership
  and inventory done under Control (`550-563`). Only available output copies
  its used slice and length; the lexical output borrow ends before None
  (`573-600`). Unavailable leaves the destination untouched and returns None
  (`578-588,602`). No whole MoveList return/read or extra Position copy occurs.
  The next private request Release carries these prior output reads to the
  inventory writer even across arbitrarily many color-only epochs.

## Close, wake and parked state

- Every normal inventory publisher performs the same unconditional SC latch
  exchange as colors; terminal publication does too, after releasing Control
  (`752-757,769-775,914-989`). The sole coordinator waits for colors and then
  inventory sequentially; only the predicate changes (`924-970`). An early
  signal from another publisher causes a recheck/re-registration, preserving
  the existing Sleep handshake. Delay after done but before latch may delay a
  cold waiter; it neither invalidates output nor permits a scheduling abort.
- Startup/activation state predicates, quiescence and terminal checks cover
  `[..helper_count]`, while colors done deliberately covers `[..2]`
  (`336-378,883-899`). Failed spawn marks only actually unstarted slots;
  shutdown joins every configured handle (`349-354,650-679`). No successful
  inventory done is fabricated on failure or on a root/Q epoch.
- Discard claims both Published and Joined and retains the flight until every
  configured helper has genuinely parked or exited (`992-1039`). The
  `colors_completed` bit excludes already-consumed color samples from later
  discard/failure accounting (`1003-1015`). Inventory park checks its own
  request under Control before publishing PARKED (`1044-1055`), and its loop
  checks that request before the inactive-scope branch (`733-779`). Thus even
  a published job not yet observed by the third helper prevents premature
  cold-park retirement. An unpublished dispatch is protected by Control until
  either full publication or its prepublication return.

## Caller and observation boundary

Nonparticipant calls close their standalone scope at the original
pre-composition boundary, including observers (`evaluator.rs:751-757`). Only an
actual third participant retains its call scope through numerical FULL finish
and settlement (`802-819`); no outer-search-scope assumption is required.
The ordinary owner receives a receipt only after installation and before null
recursion (`ordinary.rs:813-816`). Bound return, null error and shallow/null
cutoff consume discard; original demand consumes demand or runs the native
fallback (`822-883`). Generated counting and later ordering remain at original
demand (`884-898`). Receipts own no transport lease and are neither Copy nor
Clone (`colors_worker.rs:44-55`); their generation is used only for interposition
diagnostics, never as a pool-latest validity test (`605-629`).

The sampled inventory `ready_ns` ends the producer's Packet/output work
(`862-870`). It precedes unconditional production counter RMWs, done Release
and the completion latch (`752-757,1201-1207`), so ready-before-FULL does not by
itself prove that acquisition could finish before FULL. `generation_ns` also
includes the domain guard. Numerical-complete is sampled at settlement entry,
acquisition after its wait and ownership checks, installation after the used
slice copy (`554-597`). Report these exact boundaries; actual acquisition,
installation, eventual demand/discard and integrated wall/CPU costs determine
utility. Production atomics are observations and never confer cell ownership.

The source controls target sparse gaps, native unsorted special lists,
unavailable fallback, delayed third-reader Joined ownership, Published/Joined
close, failure, second-stage wake registration, used-slice close/reuse and
third-reader startup/overflow (`colors_worker.rs:2002-2327`). Caller controls
also require a receipt to survive 33 later public FULL epochs and actual null
descendant FULL epochs before parent demand/discard
(`evaluator/inventory_four_tests.rs:53-138`). Their structure addresses the
selected risks without adding a general capacity campaign or worker framework.
After the domain simplification, unavailable fallback may be forced by a
conditional test-only hook before the producer. This tests fallback/receipt
control flow, not a fabricated coherent position failing production admission:
both king populations are maintained invariants of private coherent ancestry.
