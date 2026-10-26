# Preserve the failed epoch/count assertion

Initial setup `b7465ceb` compiled successfully. The first native worker group
passed all29 controls. The owner group passed7/8; its full-bound-return control
passed score/generated checks, then incorrectly expected inventory_request=1.
Actual value2 is an epoch, not a count: prepare_root_with_influence performs a
public FULL at epoch1 before the ordinary-only request at epoch2.

Preserve the initial failed pipeline, stdout/stderr and exact65 source/37 input
snapshot at `/home/legolas/rook2-experiments/observer-free-inventory-20261026-01/failed-preparation-01`.
The original pipeline remains failed, with owner exit101. No benchmark life or
production build was started. This is a test-adaptation repair, not observed
engine semantic failure or a second production variant.

Only that test changes: capture the real post-root colors epoch, assert that
public root preparation leaves the private inventory request0, then bind the
ordinary request to the next colors epoch. Score/generated/settlement checks
remain. Production source is byte-identical to the initial attempted source.

Continue under the original start/deadline in `continuation-01`; never reset the
3600-second clock or repeat worker29. Bind the earlier worker receipt and its
actual argv/target directory honestly. Rerun the failed owner group, then the
unstarted scope/build/CLI/collection/audit stages. Seven passing owner tests
will therefore have two successful executions; this is not another benchmark
observation. No additional fixture matrix or semantic relaxation is selected.
