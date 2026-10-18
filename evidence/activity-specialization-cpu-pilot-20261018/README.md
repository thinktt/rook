# Static piece-kind activity: complete generic CPU pilot

Generic control e7168491 and candidatec946104a differ only in private activity
specialization. The candidate passes134 native tests,10,000 independent prior
coordinate-oracle placements and54 strict replays. The identical frozen
control's previously completed54-case replay is explicitly reused. Source,
artifact and full validation identities are retained in the neighboring build,
preparation, oracle and check directories.

Six fixed public cases each run one excluded warmup per variant, then four
alternating forward/reverse measurement rounds:60 lifetimes total,48 measured.
Every run passes the strict oracle and exits normally. The engine uses CPU14;
helpers use0–5,8–13. All prior native builds/tests, focused/seed checks and other
engine executions actually terminate before this pilot starts. No owned build,
other engine collection or profiler overlaps it.

Summed case medians are15.0116965s control versus14.605204s candidate, ratio
0.972921615 (**2.707839% lower**). All six candidate medians are lower. Four
finite observed ranges are disjoint in its favor; profile02 and29 overlap.
These observations are not confidence intervals or a qualified reference pass.

`reconcile.py` independently verifies all60 original native wait4 receipts,
strict results, hashes, normal exits, CPU/task observations, schedule, sample
selection and aggregates. [analysis.json](analysis.json) retains every sample;
`driver-terminal.json` and `tool-terminal.json` bind actual successful returns.

[decision.json](decision.json) advances this isolated source to its own-profile
PGO comparison. Canonical8c source remains unchanged. Generic timing does not
establish PGO benefit, production adoption, full54/12 costs or final qualification.
