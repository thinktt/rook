# Retained82 ordinary observation codegen

Frozen generic root79 artifact9709f8e9 and retained82 artifactc6839096 have
identical ordinary full_impl (2415 bytes), visit_ordinary (7983 bytes),
ordering_phase (2494 bytes), and store_ordinary (94 bytes), at identical
addresses. The fast implementation is inlined into the unchanged ordinary
caller. The sole emitted full_impl has no extra detail construction, callback,
return transfer or frame growth relative to root79. This actual machine-byte
comparison supports erasure of the additional full/fast diagnostic observations
for these ordinary instantiations.

visit_q remains7450 bytes at the same address. Its instruction operands differ
only at three RIP-relative table-base LEAs. The analyzer independently finds
those changes and decodes32-byte signed-relative windows from the respective
ELF .rodata locations; corresponding targets match. This does not assert every
word in each window is an admitted table entry. Node::child and parameter
binding have equal normalized instructions; their data referents are not
exhaustively compared. Normalization alone is not data-equivalence evidence.

The receipts and66-member archived source/tool snapshots are checked by
capture.py. evaluator.rs is the sole native-source difference. Both artifacts
use generic x86-64, rustc1.85.1/LLVM19.1.7, release thin LTO and no PGO.
Native data/state declarations are unchanged by the proposal; detail records
are cold returned values. Arithmetic and single finishing-call ownership are
separately reviewed in the retained proposal and parent source review.

Captured nm/disassembly/section/size/version outputs, exact command outcomes,
focused diffs, ELF-derived sections, function-byte hashes and the normalization
rule are retained. analyze.py rechecks the exact images and records its own
hash. File/path, panic data, linked data, other functions, other monomorphs,
PGO and the canonical-path rebuild are outside this bounded comparison.
No CPU, PMU, cache or complete-image neutrality claim follows. No engine or
compiler was run for this static review; helpers used housekeeping CPUs.
