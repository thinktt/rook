# Hierarchical child-segment recovery pilot

Selected by Imp2-lead's2026-10-25 assignment. This is a bounded serial simulation
of queued branch reuse and executor costs, directed toward a later real2/4/8-worker
test. It is not a parallel speed result or completion of multicore research.

The isolated trial is
`/home/legolas/rook2-experiments/workspaces/hierarchical-recovery-20261025-01`,
based on `b5d55008` (a documentation checkpoint with frozen66 engine source).
Canonical source66, ordinary own-PGO8f, its profile/controls, all prior results
and main remain preserved. The [preceding census](../beyond-two-census/report.md)
parks Q certificates and identifies larger ordinary siblings; the
[recommendation](../../../docs/research/beyond-two-queue-recommendation.md)
describes the recovery boundary.

The coordinator reruns native parent logic when a parent certificate disagrees.
At actual recursive demand it may try a previously recorded child segment,
matching complete semantic entry inputs and stable phase/movement information.
Exact windows remain required. Rejection discards staging; native execution may
still reuse other valid descendants. Accepted maximal segments are disjoint;
their descendants cannot be counted or installed a second time. Ordinary-to-Q
handoffs are collapsed, not extra charged work.

TT staging lazily initializes native groups from the current canonical base,
uses common native probe/store kernels and commits only touched groups after
all observations pass. Learning and pawn replay use detached native copies.
Late failure must preserve canonical state, including mutating mate probes.
The selected scope is NoHost, timing absent, zero root randomness, no node limit,
and inline FULL; no branch workers or nested FULL helpers are created.

An independent canonical execution per root candidate records local entry/output
boundaries. Recovery must agree locally for each accepted segment, then agree
with the whole canonical branch's state, outputs and N/R. A false acceptance is
fatal, including a wrong local result later hidden by a parent update. Oracle
trace exhaustion disables reuse for that candidate. Oracle-only copies, tracing
and comparisons are reported separately from actual executor costs.

Shared state is independently compared at root-candidate completion, not at
every accepted boundary; transient erroneous writes later overwritten can escape
that audit. Lead accepted this finite-discriminator limit. No detected local
output/work or root-state discrepancy would not prove exhaustive per-segment
state equivalence. Stronger local-effects auditing remains necessary before
adoption or removing the oracle. Per-rejection rollback is a private-staging
construction invariant, supported by focused before/after controls rather than
a full-state runtime comparison on every rejection.

The fixed pilot is original profile08 then35, queue2, first naturally reached
Restricted root iteration, maximum depth6 and tail8. These materialized histories
and personalities do not constitute standard wire replay. Prospectively fixed
per-forest caps are524,288 journal events,131,072 segments,262,144 recorded nodes,
512MiB estimated retained bytes (256MiB journal +256MiB entries/outputs/index),
and131,072 touched TT groups. Oracle trace cap is131,072 calls. Old35/q2 had at
most36,985 speculative nodes and101,277 attempted events per task, so the new
bounds deliberately admit the known larger-grain witness. Exhaustion censors
recording; it does not silently alter native search or erase earlier complete
descendants. No cap retuning after results is selected.

Build/tests/supervisors use CPUs0–5,8–13; each serial native pilot is pinned14,
with the prior worker/sibling CPUs6/7/15 unused by this trial. Guest affinity does
not establish host isolation. External limits are180 seconds per life,900 seconds
for the collection,8GiB address space and16MiB per output. The pipeline has a
finite1800-second overall ceiling. It stops on failures and preserves receipts;
no successful native life is repeated.

Focused controls cover sparse native effects, valid early ranges despite later
caps, irrelevant-state acceptance, late rejection after writes, changed parent
order with surviving child work, and fatal oracle mismatch. No full qualification,
PGO, policy sweep, source promotion or external delivery is selected.

Costs must expose lookup, snapshots, journal/forest recording, native parent and
fallback work, staging/replay/commit, speculative/discarded CPU, memory and
independent audit work. Gross oracle segment intervals include instrumentation;
any subtraction of measured nonoverlapping hook costs remains an estimate of
native cost removed. Acceptance percentages or credited N alone do not establish
profitability. Preserve separate ahead tasks and head tasks with no overlap.

Status: closed. The initial positive fixture failure and diagnostics are
preserved; a fixture-only repair passes, followed by23 selected tests and the
two unrepeated pilot lives. See [results](report.md), [bound closure](closure.json)
and the [prefix assessment](../../../docs/research/hierarchical-recovery-prefix-assessment.md).
Runtime source/caps and policy are bound by `preparation.json` and `prototype.patch`.
