# One fixed epoch-slot colors discriminator

Scope: `/home/legolas/agent-memos/imp2-lead-to-imp2-epoch-colors-discriminator-20261026.md`.
The [ownership/cold-wakeup proof](ownership-proof.md) was reviewed and released at
`/home/legolas/agent-memos/imp2-lead-to-imp2-epoch-proof-review-20261026.md`.
Keep the exact proof obligations attached to unsafe accesses; tests supplement them.

Isolated source: `/home/legolas/rook2-experiments/workspaces/epoch-colors-20261026-01`.
Begin from all64 exact files of the tested old colors source; change only
`src/colors_worker.rs`. Preserve every numerical/composition/caller/configuration
body, current2 transport, default1 and affinity fallback. Old b837 colors3 is the
immutable generic control; never rebuild it. The new generic image supplies
inline1/current2/epoch3. Main and66/8f/positive profiles remain unchanged.

One valid initialized input cell is written only by a single coordinator under
Control with one checked nonwrapping epoch in flight. Two separate output cells
are written only by their respective reader. Acquire request precedes immutable
input borrowing; input/timing references end before output writes and release-done.
Matching done acquires precede coordinator copying outputs under Control; those
reads finish before the later request release that permits output overwrite.
Neither parking nor a Send scope guard mutates cells. Close claims Discarding and
waits for both actual parked/exited acknowledgments; terminal observation is not
peer retirement. No fabricated zero Position, per-FULL allocation or reader-local Packet copy;
the coordinator still pays its one owned snapshot.

Cold completion uses one waiter, a Sleep mutex/condvar and an unconditional SeqCst
swap chain on the latch by every publisher/terminal handler and waiter registration/
loop-exit. Notification after consuming a registration takes Sleep, excluding the
check-to-sleep race; no code holds Control and Sleep together. Preserve all memory
orders and4096 spin policy. No wall-abort or engine affinity writes. Descheduling
between done and latch exchange may delay progress; it cannot authorize reuse.
Panic-abort is distinct from test-build unwind cleanup.

Keep the512th-dispatch sampling phase and fixed histograms. Publication excludes
coordinator snapshot preparation but precedes request; side-ready is immediately
before release-done, after kernels/output preparation. The legacy input interval
included lock/copy; direct-read mode's corresponding interval ends at immutable
borrow acquisition. That metric is not a copy cost anymore; cache traffic may move
inside kernels. Whole search includes all Control/RMW/publication/access costs.
No interval subtraction yields isolated mutex savings or an arithmetic floor.
Freeze exact observation semantics in preparation/plan before data.

Reuse baseline38 evidence with an explicit partition: unchanged17 controls reused,
old10 protocol controls superseded,11 colors integration controls rerun. Add only
new protocol controls for close/dispatch, both-reader/input/output retirement,
wait registration/spurious/terminal transitions, discard/reactivation, startup,
unpublished failure and checked epoch exhaustion. Fresh CLI/affinity admission
may reuse existing small controls; no broad numerical campaign.

[Policy](policy.json): original35/08/43; oldcolors3/new inline1/current2/epoch3;
one excluded warmup plus three fixed interleaved observations per configuration,
48 successful replay lives plus4 separate idle probes. No selector or automatic
extension. Coordinator14, white6, black4; build/harness0–3,8–13, unused15/7/5.
Reuse repaired native placement/gate/direct-wait4 and strict saved-record replay.
Record/restore selected user-owned housekeeping. Guest placement is not exclusive
host isolation. Native startup, idle, joined lifetime/CPU/RSS and go-to-move remain
separate. Record source/ELF layout drift; no mutex-only attribution.

Freeze source/scripts/artifacts/schedule before data and announce quiet windows.
One supervised3600s pipeline,1800s collection,180s native life; retain failures and
never repeat a completed life to improve a result. Normal source/tool repairs are
delegated. A negative result parks this partition with no padding/spin/transport
sweep. No PGO/inventory/fusion/full54/qualification/adoption/external action.
