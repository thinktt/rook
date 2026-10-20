# Same-image mandatory completion

**Complete finite mandatory adapter coverage passes** on isolated diagnostic
SHA256 `68a1c304f76435e4c100086d1a303b8dc94d8b5ecd63d26be834e3737bca2dda`.
The source and exact diagnostic from the [first lane](../README.md) are unchanged;
no diagnostic rebuild or source promotion occurred.

| Evidence | Coverage | Outcome |
|---|---:|---|
| Reused first-lane released report |22 complete files /1,008 cases |pass, original report preserved |
| Fresh complementary released report |93 complete files /6,665 cases |pass, no successful case repeated |
| Independent two-report union |115 files /7,673 unique cases /117 operations |pass, exact fixture/source/image binding |
| Reused native library tests |196 |pass, not rerun |
| Fresh diagnostic tests |209 |pass,0 ignored |
| Fresh development tests |2 |pass,0 ignored |

[selected-fixtures.json](selected-fixtures.json) derives the exact complement
before execution. Released conformance README65–71 identifies only
`output.analysisCandidateReport` and `search.analysisRootSequence` as optional;
their two complete files are excluded. Every case in each mandatory file is
covered exactly once. Both original released reports stay intact; the union is
a separately labeled independent reconciliation, not a fabricated single-run
all-fixtures receipt.

The unchanged released runner retains its5-second per-case timeout and1MiB
capture buffer. The previous capture/native supervisor is reused byte-for-byte,
with helpers on H=`0–5,8–13` and diagnostic children on14; no owned15. Necessary
209/2 test-harness compilation uses separate output directories and does not
replace the qualified diagnostic. No native library/negative-control rerun,
production ordinary build, PGO, timing, gameplay, external action or promotion
was performed.

One1,200-second monotonic lane covers both test stages, the complement, gaps and
independent closure. It completed within that ceiling (544.290seconds resource
accounting only); actual tool terminal `be7f11/0`, session60489. All groups and
all diagnostic/supervisor PIDs are terminal. No runtime failures, source changes
or capture repairs occurred. Before activation, the plan gained an explicit
retained-DIAG image pin; the initial plan remains preserved.

`reconcile.mjs` independently reconsumes **both** reports' complete raw exchanges,
all case IDs/requests/results, native image/argv/affinity/wait records, source maps
and fixture hashes. Total retained raw protocol bytes:165,352,842. Post-exec
point observations exist for7,671/7,673 children; two short-lived children exited
before observation. All7,673 successful supervised exec, pre-exec affinity,
complete streams and native wait/exit0 receipts remain; absent observations are
explicit and were not retried.

[plan.json](plan.json) freezes exact commands, limits, environment, source and
artifact identities. [result.json](result.json) binds all records, both test
executables, both original reports and independent closure. Raw data/builds:

`/home/legolas/rook2-experiments/first-main-cutoff-mandatory-completion-20261020-01/`

The isolated118-file source and all117 canonical files remain unchanged. Both
retained62 images remain unchanged: ordinary `01237e6d…`, diagnostic `eda652ab…`.
Production receipts, Q1, specification-owner acceptance and final behavioral /
performance qualification remain separate. This directory appends evidence and
does not alter any frozen first-lane record.
