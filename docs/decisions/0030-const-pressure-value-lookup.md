# Reject const pressure lookup before native validation

Experiment39 replaces activity pressure-value bit arithmetic with a256-byte
compile-time u8 table. Only activity.rs changes from retained37; all256 mark
values match offline and all185 old tests remain exact but unrun.

Actual generic ray code constructs a256-byte temporary using memcpy on each
admitted square, then indexes it on the stack. king_pressure reserves0x188
instead of0x58 (+304B). Its knight path uses direct read-only data, replacing
already-cheap arithmetic. Reject this exact const-storage implementation before
focused tests, timing, PGO or broad qualification. This is an emitted-code
rejection, not a measured CPU loss or observed functional failure.

Production37 remains exact. Distinct40 selects shared static storage before
speed data and requires its own gates. No39 result transfers. See the
[closed decision](../../evidence/pressure-value-lookup-backend-decision-20261019-01/README.md)
and [actual backend](../../evidence/pressure-value-lookup-backend-review-20261019-01/report.md).
