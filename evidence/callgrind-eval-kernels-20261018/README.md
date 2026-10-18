# Current canonical instruction simulation

The exact canonical8c4619a7 ordinary artifact runs unchanged profile-01 under
Callgrind and passes the independent strict replay oracle with normal exit.
The locally extracted public Valgrind3.24.0 package/tool identities are checked
against the retained original provenance. Source43, public inputs, binary,
driver, profile/log and annotations are hash-bound in
[provenance.json](provenance.json); the actual successful process observation is
retained in `terminal.json`.

Whole-lifetime simulated Ir is **12,027,315,634**. The earlier3660fecf run has
13,607,144,696 (historical ratio0.883897092). Multiple implementation/profile
changes and altered inlining prevent isolated attribution. These are simulated
instructions, not PMU retired instructions, cycles, CPI/IPC or native CPU time.

`functions.stdout` retains the complete attribution report. The largest source
row is activity compute:1,531,400,778 (12.73%). Legal-reply/generation rows,
influence construction and tactical generation also remain substantial.
`activity-lines.stdout`, `influence-lines.stdout` and `movegen-lines.stdout`
retain source-line evidence. Inlined source rows must not be treated as
independent function totals or compared by label with earlier builds.

The engine was restricted to CPU14 and helpers to0–5,8–13. No owned native
collection, build or other profiler overlapped. Instruction simulation guides
experiments and supplies no qualification or CPU speedup claim.
