# Owner-local inventory: evaluator hook and numerical boundary

Base is exact positive epoch64 copied to
`/home/legolas/rook2-experiments/workspaces/owner-local-inventory-20261026-01`.
This assignment changes evaluator/session/CLI plus six focused evaluator tests.
It imports no borrowed-input factoring, replica logic or inventory producer /
transport. Existing owned color Packet publication, numerical kernels, spin and
512-epoch sampling remain the baseline mechanisms. No unsafe code is added.

## Private ordinary hook

The original `full_impl` signature remains the entry for public FULL, observed,
detailed and FRESH paths. It delegates to `full_impl_hook` with const `HOOK=false`
and a zero-sized no-op closure. The numerical body stays in its original order;
it is neither copied nor extracted into a new owner computation subsystem.

Only crate-private `full_ordinary_inventory(node, influence, checked, coherent,
list)` requests const `HOOK=true`. It passes a safe FnOnce closure borrowing only
the caller's disjoint mutable MoveList and one local prepared Boolean. The closure
uses the body's immutable Position to call unchanged `generate_legal` directly
into that list, then marks prepared true. The result is `(Evaluation, bool)`;
the Boolean means this actual invocation generated the row. It never infers
preparation from list length or old row contents. An empty prepared list is a
real generated result, not a miss. No allocation, intermediate inventory, copy,
publication or extra worker is introduced by the production hook.

The insertion is inside the existing color-worker branch, immediately after
original `owner_ready(token)` and before original `complete()`. Only when const
HOOK, the default-false runtime option and private coherent permission are all
true does it query `is_complete_now(token)`. False triggers generation; true
leaves the caller destination untouched. Modes1/2 cannot enter that branch.
Const-disabled public/FRESH/observed/root/Q entries perform no readiness loads;
disabled option or denied coherence also short-circuits before the query.

Admission trusts the existing private coherent-ancestry permission. This layer
does not validate positions, probe the opposite king, inspect another candidate
row, query learning/TT, create a child, observe a clock or charge N/R/generated
work. The reviewed generation-domain argument applies even if the opposite king
is attacked or later search bounds avoid ordinary inventory demand.

## Readiness and numerical authority

The worker's matching done Acquires supply only a scheduling observation. Pending
can be conservative or become stale immediately; it promises no useful remaining
slack. The query grants no Flight or output ownership and hides no terminal
error. Query failure propagates through the existing infallible FULL panic/error
policy rather than becoming an inventory miss. Original `complete()` remains
the sole scalar-output acquisition and input/output retirement authority.

After optional generation, the original composition continues unchanged:
complete/join, call-scope finish, tempo, rounded Activity/Shelter insertion,
retained positional/progress and age reset, exact pawn+Activity R and diagnostic
statistics, observers and native final-score/bound calculation. Pawn cache
selection/order/collisions, FRESH bypass, custom supplied Influence, root weights,
all integer rounds and numerical bodies remain the same source operations.

`owner_ready` retains its original pre-hook boundary. `complete` starts its
sampled join clock after the hook, so that residual join interval excludes the
coordinator generation. Whole search timing includes generation, readiness,
acquisition, discarded work, cache/layout effects and helper spinning. Neither
readiness nor subtracting sampled intervals establishes saved physical work.

Parent-owned ordinary integration receives the activation-local Boolean and
keeps demand-time charges, empty handling, current-learning ordering, TT and
extension setup at their original points. Null descendants own their other ply
rows. Early cutoff/stop/error discards the Boolean and private scratch; the
evaluator adds no semantic poll/count. Physical stop latency can grow by one
speculative native generation interval. Parent integration controls establish
actual consumption, discard and null/descendant behavior separately.

## Cold option and assurance

`owner_local_inventory` defaults false and is copied only with existing detached
research evaluator copies. Evaluator/Session setters change this coordinator
option without creating a worker, changing its transport or moving cache state.
The private CLI switch is `--owner-local-inventory`; configured thread budgets,
available-CPU fallback/cap3 and two-field inspect JSON are unchanged.

Six source controls under `evaluator::owner_inventory_tests` cover:

- Forced pending generation with exact native ordered castling, promotion,
  joined EP/double-check, checked and ending inventories; detailed FULL, signed
  root-owned asymmetric weights, contrary supplied maps, retained state and R;
  both diagnostic settings and differently colored root bindings.
- Forced actual-ready completion with untouched destination and native results.
- Disabled/coherence-denied and budget1/2/affinity fallback, with zero queries and
  no generation or destination mutation.
- Public FULL/FRESH/observed/detailed entries with zero test-only readiness probes
  and serial-equivalent component/result/retained/statistical observations.
- Per-call prepared reset under one outer activation, old nonempty row ignored
  when ready, subsequent pending generation, native pawn reuse and final parking.
- Coherent opposite-king-pressure admission and genuinely prepared empty mate /
  stalemate inventories.

Test-only TLS readiness controls force pending conservatively or wait for real
done before returning ready; they never fake an acknowledgment. A TLS query count
exists only in tests. Worker-owned controls establish terminal and epoch validity;
parent-owned actual Search controls establish root/Q exclusion and ordinary
consumption/ordering/cutoff behavior. No hot production census is added.

No builds, tests, engine runs, Git actions or subagents were used by this source
owner. These controls await native admission and do not qualify complete gameplay.
