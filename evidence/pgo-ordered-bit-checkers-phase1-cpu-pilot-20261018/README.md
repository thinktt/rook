# Ordered bitplane checker — matched own-PGO pilot

The candidate sums13.4018985s in six case CPU medians versus13.5684265s for
control: ratio0.9877268009,1.227320% lower. All six medians are lower; observed
ranges separate in its favor in01/02/04/29 and overlap in05/35. These finite
samples support composition testing, without a confidence band or complete
cost/reference/gameplay qualification.

| Case | Control median CPU s | Ordered bits median CPU s |
| --- | ---: | ---: |
| profile-01 |1.107423|1.085463|
| profile-02 |0.732662|0.696203|
| profile-04 |4.440302|4.4065395|
| profile-05 |2.463526|2.455705|
| profile-35 |4.5704675|4.5164965|
| profile-29 |0.254046|0.2414915|

Control e4921975 and candidate7b17c000 each use their own exact-source54-case
compiler profile,2e6ba24a ande55270f6 respectively. The same control is reused
after exact source/tools/compiler/settings/corpus checks; its profile is never
transferred to the changed candidate. Candidate143 native tests, own54 training,
byte-identical independent profile remerge,54 strict replays and eight-wire/24
searches pass with zero missing/stale profile warnings. The separate
`pgo-ordered-bit-checkers-phase1-preparation-20261018` closure binds these steps.

Only attacks.rs and movegen.rs differ from the old85 baseline. Full/capped
generation obtains exact first-two checker identities from existing persistent
tag planes. The projected Q mailbox remains unchanged. This is not the later
king-first, known-check, Q-bitview, observer88 or admission95 source; these CPU
results do not transfer to them.

All60 native lifetimes pass the unchanged strict oracle and exit normally:
12 excluded warmups and48 measurements, four per variant/case, alternating
forward/reverse rounds. CPU is whole native-process wait4 user+system time.
Engine affinity14 and helpers0-5,8-13 are independently checked from original
receipts. All owned native/build/test/engine/training/profiler/Git jobs were
terminal before collection; children did only small source/text work.

Parent actually observed53579/df8bc0 exit0 and separate raw reconciliation
6ab661 exit0. `analysis.json` binds all schedules, artifacts, strict/native
results and sample arithmetic. `tool-terminal.json` and
`reconcile-tool-terminal.json` retain actual terminal attribution.

Own-pane client109 threads had already been restricted to housekeeping. Other
guest panes/system/host were untouched. Whole-suite CPU15 snapshots nevertheless
contain46 nonidle ticks (40user/6system); they include helpers/waits and cannot
attribute interference to a variant or engine interval. No absolute sibling
idle, exclusive-host or PMU claim follows.
