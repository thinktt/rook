# Experiment52 parked after generic screen

Two separate constant Activity consumers and a permission-first any-slider guard
are present in the actual native caller. Thirteen focused controls pass. All70
original live/offline replays and native accounting pass independently.

The fixed seven-case CPU median sum is13.6015785s for51generic and13.6286095s
for52generic:0.198734%higher,2of7lower,worst ratio1.007862818. Aggregate<=0.995
and minimum5lower criteria fail; the1.02 worst-case guard passes. Park without
retry, PGO, full199/diagnostic validation or source adoption. Candidate51 remains
production, whole54=69.417194s and whole12=698.491201s.

Actual geometry frame is80B larger; scalar/full/Q/ordinary/root frames are
unchanged. Text grows7024B. These and the extra dispatcher/argument costs do not
identify a single cause of the screen result. Shorter code is not a speed proof.

The failed initial independent invocation4a6535/1 lacked the actual terminal
record at its expected output path and stopped before sample processing. The
correct record enabled96a7bb/0 on the unchanged70raw runs; no engine was rerun.
