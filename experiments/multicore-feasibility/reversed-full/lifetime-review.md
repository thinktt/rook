# Reversed FULL source review

From: imp2-lead
To: imp2
Date: 2026-10-24

Review of the in-progress source, not a frozen-image qualification. No native
execution performed by the lead.

The extracted pawn body retains ordinary cache selection versus FRESH bypass,
weighted structure/progress and pawn relation/reuse outputs. Moving the cache
core separately from the optional serial Rc journal avoids asserting Send on
observer state. The normal cache is private; FAST consumes retained Node values
without a cache lookup or remote roundtrip.

Worker startup precedes taking the actual cache. Installation deposits the core
into recoverable storage before fallible activation/publication. Mode disable
joins the helper and reinstalls its actual core before reporting a recoverable
failure. The helper keeps the core outside disposable packet/output slots and
outside the test-unwind closure, so abandoning a FULL result does not erase a
completed selection/replacement. Reset is a distinct acknowledged command;
parking does not clear the cache. These are the right ownership boundaries.

Evaluator composition joins the pawn result before retained writes, combined
relation-count/stat publication, observers and final finishing. Root-bound
inputs and supplied Influence are copied for each call. Numerical and lifecycle
tests still need to establish these inspected paths on the actual implementation;
source inspection alone does not prove race freedom or complete fidelity.

The inline refactor groups progress with pawn selection/terms before Activity,
where the prior inline body placed Activity before progress. Pure calculations
appear numerically independent, but changed instruction/cache order belongs in
the performance interpretation. The old and new current-split images are both
needed to distinguish placement effects from refactor/layout effects.

The copied lifecycle worker is acceptable temporary research duplication. It
is not yet a conclusion that two transport implementations should ship. Existing
fixed CPU6 and wall-deadline failure behavior remain research limitations, and
test unwind recovery does not apply to production panic-abort execution.

No additional scope selected by this review. Proceed with the already assigned
focused controls and single generic comparison; preserve the positive PGO image.
