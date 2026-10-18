# External position/phase diagnostics

This report uses the unchanged released conformance runner. The three complete
new files cover position setup (25 cases), explicit-order move history (58),
and normalized setup plus history (62). The retained selected fixture adds22
phase and3 identity cases from two partially supported source files, with their
source hashes and selected IDs in `selection.json`. Five previously implemented
complete files add246 regression cases. The adapter contains no case IDs or
fixture data; these external expected records are test inputs only.

The corrected artifact passes all416 cases and seven adapter unit tests.
Setup history retains POSITION-SETUP's broad initial placement domain, while
all played moves use native own-king legality. Lower moveSequence preserves
supplied raw flags and ordered pieces; setup history normalizes them first.
The library source before/after maps match the verified native source archive
in `../generation-integrated-build-20261018/`. The adapter has its own sibling
build receipt/archive, and Cargo.lock pins cold public parser dependencies.
Eleven operations are now implemented; all other mandatory operations remain
explicitly unsupported. This is not complete mandatory acceptance.
