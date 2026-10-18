# Checked bounded king-first reply — matched own-PGO pilot

The candidate's sum of six case CPU medians is13.340055s versus13.544937s for
control, ratio0.9848739053 (1.512609% lower). All six medians decrease. Observed
ranges are separated in its favor in five cases; profile29 overlaps. These
finite samples support adoption pending validation of composition with current88
source. They are not a confidence band or complete54/12 cost qualification.

| Case | Control median CPU s | King-first median CPU s |
| --- | ---: | ---: |
| profile-01 |1.116072|1.0769465|
| profile-02 |0.7308675|0.7118765|
| profile-04 |4.4245015|4.379721|
| profile-05 |2.459392|2.4267525|
| profile-35 |4.562190|4.4987665|
| profile-29 |0.251914|0.245992|

Controle4921975 and candidate52ec6b9e each use their own exact-source54-case
compiler profile. Their only native source difference is the previously tested
checked-only LIMIT2 king-first change in movegen.rs, including its two tests.
Each profile independently remerges byte-for-byte from54 PID-linked raw files.
Each use artifact passes54 strict replays and eight interruption fixtures/24
searches, with no missing/stale/malformed profile warnings. See the separate
`pgo-bounded-reply-matched-validation-20261018` closure.

All60 fresh native lifetimes pass the unchanged strict oracle and exit normally:
12 excluded warmups and48 measurements, four per variant/case, with alternating
forward/reverse order. CPU is whole native-process wait4 user+system time.
Engine affinity is14, helpers0-5,8-13; the before/after guest snapshots and raw
records are retained. All owned native work was terminal before collection;
children did only source/text work throughout. No owned build, other engine,
training, profiler, binary scan or Git packing overlapped measurement. This
coordination does not assert exclusive host ownership or provide PMU data.

Parent actually observed session66087 terminate at chunk50b7af/exit0, then
independent original-byte reconciliation terminated at4607ea/exit0. The checked
schedule, native exits/affinities/identities, comparator results and input hashes
are retained in `analysis.json`; `tool-terminal.json` binds the actual terminal
and suite summary. No old8d profile or performance result is reused. These
frozen85 artifacts do not qualify the later87/88 diagnostic source, ordered-bit
checker prototype, gameplay or reference comparison.

Later isolation audit: the retained whole-suite guest CPU15 snapshots contain46
nonidle ticks. Own server/code-mode/launcher threads were still eligible on14/15;
109 verified own-pane threads were subsequently restricted to housekeeping.
Other guest panes/system remain outside that correction. These aggregate ticks
cannot establish per-variant interference or its cause; no zero-interference
claim follows. See `../own-helper-affinity-refresh-20261018/`.
