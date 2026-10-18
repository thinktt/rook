# External position/phase diagnostics

This report uses the unchanged released conformance runner. The three complete
new files cover position setup (25 cases), explicit-order move history (58),
and normalized setup plus history (62). The retained selected fixture adds22
phase and3 identity cases from two partially supported source files, with their
source hashes and selected IDs in `selection.json`. Five previously implemented
complete files add246 regression cases. The adapter contains no case IDs or
fixture data; these external expected records are test inputs only.

The first artifact has415 passes and one failure. The setup-history adapter
incorrectly applied the lower established-state initial-check restriction to a
broad setup position. The failing original request, stderr and cause are retained;
no native-engine change was needed. The correction and full rerun are in the
sibling `diagnostic-positions-20261018-02` evidence.
