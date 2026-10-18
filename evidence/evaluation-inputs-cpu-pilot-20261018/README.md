# Pure evaluation-input reuse: local generic pilot

The frozen prototype3cc6dda6 and baselinee7344948 each pass all54 strict
released replays. The declared six cases use one excluded fresh-process warmup
per variant and four alternating AB/BA measured rounds:60 native lifetimes.
All60 were independently reconciled against original native receipts, strict
comparator results, empty comparator stderr, normal exits, engine hashes and
CPU14 placement. Raw reports and build identities are retained.

The sum of case medians is16.7847165s baseline and16.6589185s reuse, ratio
0.9925052056 (0.74948% lower). Per-case samples and ranges remain in
`suite-summary.json`; multiple sample ranges overlap. This descriptive result
has no confidence interval, reference calibration or production-PGO implication.

Decision: retain the isolated prototype and its exact archived source; do not
adopt it into production on this modest generic-only evidence. No persistent
node state or cache was added. A future PGO comparison would be a separate
experiment, rather than a speedup inferred from these samples.
