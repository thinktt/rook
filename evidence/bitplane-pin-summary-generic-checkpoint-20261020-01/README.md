# Experiment57 generic checkpoint

The isolated pin summary replaces only unchecked GenerationSafety's mailbox ray
scan with first/second occupied-square queries on the existing placement planes.
Existing unchecked/enemy-slider guards, move enumeration, ordering, special moves,
legality fallbacks, numerical owners and work charges remain unchanged. Correctness
imports the established plane/mailbox invariant; checked=false is not a certificate.

Source74 changes only attacks.rs and movegen.rs. All193 library tests pass,
including two new independent mailbox/pin witness tests and existing legal-list
differential checks. Two development tests are declared but unrun here. The generic
image is5d10b2fa; its exact74-source archive independently reopens against the build.

Actual normal and bounded-reply callers invoke the same changed summary function.
That function falls4086 to1538B; its frame grows16B. Existing placement planes are
decoded once, and baseline x86-64 bit operations find the two occupied squares.
These static facts establish the mechanism, without predicting CPU savings.

The first and only fixed70 generic screen passes original live/offline replays
and independent native accounting. Summed case medians are13.570519 versus13.427078
CPU seconds: ratio0.9894299547423353,1.0570045%lower,7of7lower,worst0.9923191376.
All preset advancement gates pass. This is a seven-case development result, not
full54/12 timing or performance qualification. Production remains51.

Advance once to fresh own-source PGO under the separately frozen selection.
No source retuning, timing retry or inherited generic speedup is allowed.
The341-member closed archive preserves original raw runs, helpers, reviews,
source snapshots/patches, build/native/compiler evidence and both selections.
Its manifest and receipt bind every member. The frozen ELF remains local and
hash-bound; this is not a deployment bundle.
