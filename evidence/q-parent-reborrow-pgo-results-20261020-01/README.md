# Experiment67 fresh own-PGO pipeline

All195 native tests, original54 training and independent54 raw/PID/replay checks pass. The independently merged profile is byte-identical. Genericx86-64 O3/thinLTO/CGU1/abort/debug1/jobs4 instrumented build and profile-use ExtTSP build pass with stable source and no missing/stale-profile warnings. Exact artifact/profile identities and actual tool handles are in report.json.

Only quiescence.rs differs from accepted62: delay the immutable parent-placement borrow until after evaluation. No66 code/profile is carried. Native tests and training are finite correctness evidence; actual copy erasure and native speed remain unproved. No optimized54/12, promotion, final qualification or external run follows.
