# Current43 bounded instruction study

The accepted own-PGO image36251ecf ran one instrumented fresh lifetime for
original profile35 and one for08, serially in that fixed order. Original replay
outputs and native exits pass. The independent verifier reran both original
checkReplay assertions offline, launched no engine, and checked202 pinned
inputs plus all28 recorded profiling/annotation command outcomes and streams.
Collector actual6e7a77/0; independent actual704fc5/0.

Whole-lifetime simulated user instruction counts are45,281,552,465 for35 and
3,931,023,836 for08. These are Callgrind Ir, not PMU retired instructions,
cycles, physical memory traffic, CPU time or a performance qualification.
Source/inlined cost partition and optimization selection remain separate work.
No45 experiment is selected by these totals.

The new supervisor passed six separately bounded canaries before this study
(actual826409/0, independently checked64d2b3/0): normal exits, deadline,
detached/adopted TERM-ignoring child, captured-output cap and RSS cap. All owned
cleanup was confirmed; emergency teardown was not needed. The actual study
preserves per-command supervision and sampled resource peaks. Sampled descendant
RSS/storage observations exclude monitor overhead and do not establish hard
cgroup limits, exact transient peaks or exclusive host use.

The deterministic archive contains191 files across the frozen study preparation,
canary preparation/execution, parent review and closed raw profiles/annotations.
Every member header, mode, byte stream and original was reopened and compared.
Historical inert/live snapshots retain their original flags; actual completion
is recorded in raw/tool-terminal.json and raw/verify-tool-terminal.json.
No additional engine/profile run, external transfer or qualification follows.
