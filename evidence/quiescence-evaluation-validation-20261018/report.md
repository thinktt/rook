# Quiescence evaluation — completed untimed isolated validation

The frozen proposal passed 140 library and 2 development tests (142 total), 109 diagnostic tests, all 5,187 cases for 84 operations across 78 whole official fixture files, the original strict54 production replay, and eight interruption fixtures with 24 retained-process searches. The expansion contributes exactly 466 cases and 7,500 ordered result records. No partial fixture or duplicate case ID was selected. Native/adapter sources, bound dependencies and frozen image identities remained stable. No failure or source correction occurred.

Native generic SHA256: `106766f3f0b81ada9f2d6690d47738677934862cc67e67674b635475747f1d46`. Diagnostic generic SHA256: `e38c5542dad00b049fe74b7297688f78c66b21ed2daf7e10e09ca2bd30ed2cae`. Both images were frozen immediately after actual successful build-helper return and before another build could overwrite their target paths; pre-build source archives and verified tar archives are retained in the respective build directories. Native test images and the diagnostic test image were also frozen before execution and their raw unit outputs retained.

The execution copy `/tmp/imp2-quiescence-evaluation-validation-20261018` exactly matches the frozen proposal full-source manifest before/after. The original `/tmp/imp2-quiescence-evaluation-20261018-native-child` and its proposal evidence remain unchanged. Current `/home/legolas/rook2/tools/build.py` performed generic `--bin rook2` and `--bin rook2-diag` builds. The explicit native path dependency is bound by the native build receipt/source map; the frontend's 29 manifest/lock/source files are separately archived and hashed. Root source/docs/other proposals were not edited.

The diagnostic preparation's plan independently inventories baseline82 plus both new whole official fixture files: every source index, case ID and operation, original top-level field names and exact official file hashes are recorded. The official runner received those original whole-file paths directly, preserving their metadata headers. Its complete JSON output and raw exits are reconciled independently against the inventory, all frozen images, unit counts and before/after source/dependency snapshots. The successful full response comparisons cover every field of all 7,500 new records; no summary/score-only comparison was substituted.

Evidence paths under `/home/legolas/rook2/evidence/`:

- `quiescence-evaluation-validation-20261018/`: native test artifacts/commands, actual native pipeline/terminal records, full proposal identity and this final reconciliation.
- `quiescence-evaluation-build-20261018/`: frozen ordinary engine, build/terminal/source/archive receipts.
- `diagnostic-quiescence-evaluation-preparation-20261018/`: original whole-fixture plan, frontend preparation/archive, bounded verifier and independent reconciler.
- `diagnostic-quiescence-evaluation-build-20261018/`: frozen diagnostic image and build/terminal/source/archive receipts.
- `diagnostic-quiescence-evaluation-20261018/`: 109-test frozen image/raw output, all 5,187 raw official case exits and complete reports, stable input snapshots, identity and actual terminal receipts.
- `quiescence-evaluation-check-20261018/`: original strict54 full stdout/semantic work/exit report, wire-driver outputs, source/dependency snapshots and actual terminal identity.
- `quiescence-evaluation-interruption-wire-20261018/`: eight fixture receipts and literal stdin/stdout/stderr chunks for all 24 searches, with clean observed exits.

All helpers/tests/engines were confined to housekeeping CPUs 0-5,8-13. The active-process sample records the strict driver and native engine with that exact mask. The final owned-process check is empty; all owned subprocesses had reached actual terminal return before this handoff. No CPU/cycle/retired-instruction timing, PGO, Callgrind or other profiler was run. This is semantic/component/ordinary-wire regression evidence, not CPU neutrality, gameplay, complete mandatory coverage or final qualification.
