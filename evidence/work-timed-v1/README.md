# Native work-timed CPU baseline

Actual ordinary/tactical recursion now produces the charged work driving the
reset-safe ledger, adaptive limits and native root controller. Search increments
N at its actual entry charge, then checks each positive 4096 multiple before
continuing that frame. An interrupted child returns no fabricated score or PV;
the selected capture and its metadata remain independent of terminal work.
Completed-root and completed-iteration stopping are separate boundaries.

The controller includes explicit-seed randomization, unrestricted and restricted
windows, stable retained-work tail ordering, retries, score-drop/best-change
adjustments, easy adjustment and the terminal iteration rule. The measurements
below exercise unrestricted scheduling. Restricted numerical primitives are
checked separately; natural larger-tree coverage is still pending.

Generic x86-64 release SHA256:
`6bef55aae6dc3f12fbc4ffbc18bc0354ecc408ef34696c7e09be0992a238851e`.
The exact executable stays locally as `rook2-dev-exact`. The neighboring build
receipt, verified source archive and 117 passing native tests bind this version.
The 70-case timing checker and 1,352-case evaluator/root regression use these
same engine source bytes.

| Seed/boundary | Searches/process | Terminal N/R | Captured N/time | Full/fast | CPU median on/off |
| --- | ---: | --- | --- | --- | --- |
| 0, poll interruption | 128 | 4096/20629 | 3046/0cs | 3431/3706 | 0.889448/0.890844 s |
| 2147483648, completed root | 128 | 4018/20697 | 3292/0cs | 3482/3736 | 0.915829/0.908052 s |

Both stop at 1cs, depth5. The first interrupts root index 2; its retained capture
belongs to root index 0. The second completes root index 1, while also retaining
root index 0's earlier capture. These demonstrate why terminal work cannot
restamp the selected SearchID or elapsed value.

Each of four schedules has one excluded fresh-process warmup and three
measured fresh processes. All outputs agree byte-for-byte within a schedule.
Diagnostics on/off preserve capture, stop, work, immediate-publication capture
count and consumption witness. Diagnostic-on clock-check projections match
the released expectations; diagnostic-off omits those rows. CPU range/median
spans 0.62–0.98%; these samples do not establish small observer-overhead effects.

The development CLI uses neutral sel14/md99/ana0/TT64MiB, explicit seed,
randomness 50 and allowances 1cs/1cs. Its md99 differs from the fixture md20;
the projected results/work/time observations agree. The separate native
checker binds every fixture parameter exactly. `workloads.json`, `collect.py`
and raw receipts preserve this distinction; this is not a complete CLI fixture
admission claim or the released qualification endpoint.

Each repetition starts fresh logical learned/pawn/TT state while reusing
allocated storage within the process. CPU includes startup/preexec, initial
allocation, root preparation, all repetitions, logical clears and output.
Semantic N/R begin after root preparation. Engines request CPU14; helpers use
0–5,8–13. CPU15 recorded two user ticks and 1472 idle ticks during collection.
PMU instructions/cycles remain unavailable. No reference ratio, PGO result or
whole-engine performance acceptance is claimed.

Public command ingress, allowance allocation, seed acquisition, persistent
session state, host command servicing and literal post/PV rendering are not
implemented by this native endpoint. Eligible publication captures are retained;
this does not yet stream real public posts.
