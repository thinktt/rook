# Placement pure-cache generic backend preparation

INERT: parent source/build review and separate capture approval are required. No nm/objdump/readelf, binary inspection, compiler, engine, native test, timing, PGO or profiler ran for this preparation. Three adapted Python helpers are text only and have not been parsed or executed.

Inputs are exact fullbyte generic948c control and the future frozen `placement-pure-cache-generic-build-20261018-01/rook2-exact` candidate. Candidate image/receipt hashes are deliberately null until actually built. The reviewed source69 graph and five changed source files are pinned; source archive/build receipt/source-before69 and matching compiler/flags/noPGO are verified when capture is later authorized. Control and candidate generic settings must match. All helpers and subprocesses are restricted to housekeeping0-5,8-13, HOME TMPDIR.

Parent may later provide `authority.json` with capture=true, actual candidate SHA/receipt SHA and parent source-decision path/SHA. The only permitted sequence is `capture.py`, `capture-functions.py`, `analyze.py`; no command is authorized now. Capture uses nm symbol tables and ELF sections/relative relocations, then objdump only over selected actual function address/size ranges. `plan.json` fixes scope and bounds; `review-scope.md` defines the actual cache/heap/frame/field/charge/caller obligations. Outlined symbol absence is explicitly not an erasure proof. No private-layout Rust probe is generated.

`basis-*.py` preserves the accepted full-byte-pair own-image methods. The three `*.adaptation.patch` files expose every helper change. Updates bind a future actual image instead of a phantom hash, verify only the five reviewed source differences, gate execution, retain all emitted owner monomorphs rather than guessing unique symbols, and preserve operands/call targets/frame evidence. Source extraction, helper hashes and text derivation only were performed here.

All raw outputs/child exits must be preserved if a future capture fails; report before any repair or broader capture. This preparation offers no cache adoption, CPU/copy/frame/layout neutrality or qualification claim.
