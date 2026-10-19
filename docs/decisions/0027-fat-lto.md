# Test whole-program fat LTO on retained25

Experiment36 changes only Cargo release lto="thin"→"fat". All44Rust files,
all178 test bodies,23tools and generic target/compiler/other settings stay
exact25. The released reference also declares fatLTO. Most library code already
shares oneCGU; the hypothesis is final crosscrate integration, not first exposing
all modules together or a guaranteed fraction of the reference gap.

Actual normal-WireHost code inlines scalar activity and other owners into full
evaluation. Total text shrinks22080B, while combined full/root frame reservations
grow and ordinary/Q shrink16B. Copies and scalar work remain; static changes
supply no speed prediction. Fixed70 strict live/original offline replay and
independent wait4 accounting pass. Sum case medians14.078437→13.720597s,
2.541759%lower,7/7lower,worst0.97956294 meets the existing advancement rule.

Advance only to fresh own-source fat PGO and a distinct fixed70 against25PGO.
Native178 has not been rerun; no broad117/54/wire/games or source promotion
follows from this generic result. Production/root and immutable delivery remain25.

See the [generic decision and identities](../../evidence/fat-lto-generic-decision-20261019-01/README.md).
