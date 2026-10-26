# Concrete source review before native admission

The implementation uses the positive64 source inventory as its sole base.
Changes are limited to the color worker, evaluator, Session/private CLI, and one
new evaluator test module. Search control, TT, learning, influence, pawn cache,
Activity, Shelter, whole-helper worker and Cargo build policy are unchanged.
The exact map and retained/root-weight inputs are passed through safe field
borrows. The owner body is shared, retaining inline Activity's original position
between pawn inputs and local terms; final score/R/retained/callback work follows
the joined result and standalone scope close. No unsafe evaluator alias exists.

The private EpochGuard is created before raw descriptor installation. Legacy
escaping dispatch tokens force owned snapshots. Both new actual mode3 paths
use with_epoch and identical owner/completion code. Only the concrete cell
container receives Send/Sync implementations. Helpers resolve raw pointers
within compute_input; its scalar return ends every Packet/input reference before
output write/done Release. The post-done SC latch touches synchronization only.
Control serializes output acquisition and the next request's reverse edge.

Success clears Input after both matching done Acquires and scalar output reads.
Healthy unwind/abandonment drains this published call despite other active
scopes. Unpublished failure clears only that installation without admitting a
reader or advancing an epoch. Terminal cleanup performs real joins before
clearing. A concurrent closer's Discarding claim remains until its parked/exited
retirement, unless real terminal shutdown joins everything. No fake completion,
background drain, second completion waiter, timeout-based borrow release or
forgettable public lifetime token is added. Cleanup recovers poisoned mutexes;
production abort and focused test unwind are separate execution policies.

Parent review found no concrete architectural blocker before frozen admission.
Imp2-lead independently reviewed the pre-publication proof and found no material
lifetime blocker. Executed focused controls are still required and do not prove
all possible interleavings. In particular live-reference delay controls pause
inside compute_input after actual references form, not merely before request
admission. Existing SC latch, output retirement, startup and terminal controls
remain part of the affected worker group.

No numerical kernel changes are attributed as speedups. Input enum storage,
common guard/refactor, descriptor retirement and source/stack layout differ from
retained7ac. Matching scoped-owned versus scoped-borrowed measures net supplied
input strategy under those common costs; comparison with7ac prices common drift.
512 samples still include real kernel/cache traffic. Cold mode/request/done and
actual joined Empty/None retirement establish activation only, not population,
universal safety or a hardware-cause explanation.
