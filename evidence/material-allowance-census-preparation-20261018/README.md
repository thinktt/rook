# Material allowance census: cold preparation

Prepared on the exact current79 source at `/tmp/imp2-eval-pawn-observers-20261018`, independently matched to all43 root native/build hashes before and after preparation. The isolated derivative is `/tmp/imp2-material-allowance-census79-20261018-a1gikj0f`. It has44 native/build files: four existing Rust files changed and a separate diagnostic wrapper added. Root sources and the79 source are unchanged. Prior reports/proposals are untouched.

This is **uncompiled and unexecuted**. Only cold file preparation, source-scope checks, hashes, offline workload metadata inspection and archive verification occurred. No builds, rustc, tests, engines, profilers or benchmarks ran. The source preparation script runs only those cold file operations. Shell commands used `taskset -c 0-5,8-13`. No Imp1/Herdr/advisor was used.

## What changed and what did not

- quiescence.rs adds diagnostic aggregate structs in Stats, starts a local u16 key bitset for each candidate inventory lifetime and counts actual Q allowance branches.
- ordinary.rs starts the corresponding local bitset for one immutable parent visit's legal inventory and supplies a diagnostic observer at the actual frontier allowance branch.
- ordinary_policy.rs preserves the public frontier_estimate signature/admission and delegates its unchanged body to a crate-private observed helper. The original ordinary/nonchecking/occupied tests remain in that one body. The callback is inserted only inside its actual occupied branch, immediately before the unchanged allowance expression. The ordinary caller uses the observed helper with a callback whose only action is inside DIAGNOSTICS; the public helper supplies a no-op callback. This avoids duplicating the frontier gates in the counter caller.
- session.rs adds only a cold stats snapshot accessor, following the prior null-opportunity wrapper pattern.
- rook2-material-allowance-probe.rs is the existing ordinary wire source copied into a new binary with Session<true> and a private create_new JSON file written on the existing quit path. It uses ROOK2_MATERIAL_ALLOWANCE_PROBE. Standard output, normal option parsing, search/idle command parsing and public protocol admission stay unchanged. The original rook2.rs bytes are unchanged.

RootContext/material formula, evaluator/Node/Retained, Position, quiescence_policy::allowance, wire parsing and existing test code are byte-identical. No result cache, skipped material computation, persistent Node field, material-value array, storage redesign, charge modification or changed allowance policy is present. The only new persistent data are diagnostic aggregate Stats, matching the earlier opportunity-counter pattern; local bitsets contain seen tags, never scores. With DIAGNOSTICS=false, counter begins/observations have no effect, and the frontier callback is a no-op. This is source-level behavioral equivalence, not a claim of identical emitted code/size or a production timing artifact.

## Exact counter lifetime and increment placement

A loop is counted after its candidate inventory size is known, **before the original count==0 early return**. Thus it includes empty inventories as zero-call lifetimes, but excludes invocations returned before candidate production (repetition/reversal/TT/static cutoffs and other preceding gates). This is intentionally a candidate-inventory lifetime, not every search visit. A local seen mask is initialized once for that immutable parent and never reset by candidate ordering, a later child return, a main-loop suffix permutation, IIO or scout activity. Recursive invocations have separate stack-local masks and aggregate into shared search Stats. Returning/breaking/error propagation naturally discards the local mask; counts are updated as events occur, so no deferred Drop/finalization event is required.

**Q:** begin occurs at `let count = self.candidates[ply].len`, after either existing checked legal/reused inventory or non-check tactical generation. checked_loops records the current parent check flag; checked Q loops make no allowance requests. The observation is inside the original `if !special && !victim.is_empty()` after the non-check branch and late nonrecapture screen. Here special already means promotion or EP. The victim passed is the original actual board occupant at the candidate destination, before the original `standing + policy::allowance(...)`. It therefore counts ordinary nonempty non-king captures that actually request allowance, including those later rejected by optimistic threshold, eligibility, check/reply or king safety. It does not count generated-but-gated candidates or promotion/EP allowances that never happen.

**Ordinary:** begin occurs immediately after generate_legal and count extraction in visit_ordinary, before the existing count==0 return. Its mask survives this invocation's later mate/IIO/main-loop processing with the same immutable parent. Only the main-loop depth<=0 frontier call reaches the observed helper. Inside that helper, original `movement.kind()!=Ordinary || checking` returns10000 before observation; original empty-destination quiet frontier returns its unchanged formula without observation. Observation happens only inside the actual occupied ordinary nonchecking branch, immediately before its original allowance call. This counts capture estimates even if the estimate later prevents child production. Ordinary IIO/mate recursion contributes its own visits/loops; it does not observe allowances on behalf of the parent. Existing direct public frontier helper/diagnostic consumers supply a no-op observer and retain unchanged admission.

The counter adds no full/fast/material queries to discover victim tags. Tag is exactly `actual_victim.color().index()*5 + actual_victim.kind().index()`. Arrays use indices0..9: White P/N/B/R/Q then Black P/N/B/R/Q. One bit per tag in a u16 distinguishes the actual color/type tuple, not square, move descriptor, physical victim identity or fingerprint. Existing native producers exclude empty/king targets and own victims before these sites; existing allowance asserts ordinary and nonempty non-king. No new validation/admission gate was added. The normal loop's opponent color is fixed, so at most five distinct keys can occur; representing both colors keeps tuple ownership explicit.

Each observed allowance request increments calls A and old_endpoints by2, increments the matching calls_by_victim element, then on the first observed key of that lifetime increments nonempty_loops and lazy_endpoints by1 (the hypothetical current-parent endpoint). On each first occurrence of a tuple in that lifetime, it sets the corresponding local bit, increments unique_keys K and unique_by_victim, and increments lazy_endpoints by1 (the hypothetical after endpoint). Repeated keys still increment A/old2A and continue executing the original allowance/material calculations; they do not increment K.

These are **opportunity/source-demand counts**, not cache hits, emitted function calls or CPU savings. Aggregate `old_endpoints=2*sum(A)` and `lazy_endpoints=number_of_nonempty_loops+sum(K)`. The difference is the exact redundant endpoint-demand model `sum(2A-1-K)` for loops with A>0. Zero-call loops are `loops-nonempty_loops`; no endpoint is attributed to them in the hypothetical lazy model. No actual lazy endpoint is computed by this derivative.

## Reset, denominator and native lifecycle

The new aggregates live in existing Stats and reset at the existing begin_sequence assignment. Existing evaluator full/fast stats reset at that same boundary. The probe exports the current completed segment through the stored Session search on quit, exactly following the null-influence opportunity transport. No additional reset or protocol command is introduced.

For ordinary profiling wire search, all in-segment material source demands occur at full_impl (one/full), fast (one/fast) or these two allowance paths (two/request). The cheap unambiguous **search-segment** denominator is:

`full + fast + q_old_endpoints + ordinary_old_endpoints`.

No assumptions about compiler inlining/CSE are made. The denominator includes demands reached in retries and before eventual child/score rejection, because the existing full/fast counters and new branch counters observe actual source selections. Root preparation calls full once before begin_sequence and is excluded by the original reset; it must not be called a whole-lifetime denominator. The source timed path has exactly one preparation before its single begin_sequence. Offline inspection verified all54 released workloads specify one fresh process, one go and quit only after the selected-move record. Under those particular lifecycle conditions there is one additional root-preparation material demand outside the segment; adding1 is a source-schedule derivation, not an exported counter. Report the segment denominator directly and distinguish that optional whole-case derivation. Arbitrary multi-search sessions are not aggregated by this snapshot and must not reuse that inference.

The new root79 API extraction is the baseline source. Old8d Callgrind row percentages are not source attribution for this derivative. No IR block/counter0 is used as a call denominator.

## Transport schema and tuple ordering

The Session accessor returns `(c:[u64;14], tags:[[u64;10];4], evaluations:[u64;2])`. The standalone wrapper writes named JSON fields, schema `rook2-material-allowance-census-v1`, with no extra standard-output record.

| c index | Export field |
| --- | --- |
|0|q_loops|
|1|q_checked_loops|
|2|q_nonempty_loops|
|3|q_calls|
|4|q_unique_keys|
|5|q_old_endpoints|
|6|q_lazy_endpoints|
|7|ordinary_loops|
|8|ordinary_checked_loops|
|9|ordinary_nonempty_loops|
|10|ordinary_calls|
|11|ordinary_unique_keys|
|12|ordinary_old_endpoints|
|13|ordinary_lazy_endpoints|

Tags arrays0..3 are q_calls_by_victim, q_unique_by_victim, ordinary_calls_by_victim, ordinary_unique_by_victim. Each array uses the ten color/type indices above. Evaluation tuple0/1 is full/fast. Fixed numeric Rust array Debug output is valid JSON integer-array syntax. The wrapper opens its env-supplied private destination with create_new on the original quit path; absent/preexisting paths are collector errors. It changes no ordinary accepted wire command or public diagnostic input.

## Parent collector adaptation and required validation (not run)

1. Review this patch and cold scope first. Parent alone may compile/archive the isolated source as binary rook2-material-allowance-probe after other measurement work is terminal. Verify before/after source hashes against prepared.json and archive, and retain the exact derivative binary/build receipt. The derivative has not been syntax-compiled; type/borrow/payload and integration validation remain outstanding.
2. Adapt the existing null-influence-opportunity collect.py pattern into a **new** collection directory, leaving original evidence immutable. Substitute this preparation path/source map/archive, the new build receipt/binary hash and private ROOK2_MATERIAL_ALLOWANCE_PROBE env var. Remove the older artifact-specific terminal assumption and use explicit current parent-approved terminal/readiness records. Keep the released replay-check.mjs/workloads/oracle files unchanged and hash them with the collector/build/preparation/archive.
3. For each of all54 original cases, use the original checker command with case, then engine pinned14; keep helpers on0-5,8-13 and disclose guest interference. Provide a unique nonexisting per-case counts.json path, capture original comparator stdout/stderr, require checker exit0/pass/one result/no truncation/clean stderr/native exit0, and stop on first failure. Preserve original work/output comparison; D=true is not allowed to waive it. Require the private file only after the original selected-move/quit lifecycle finishes. Instrumented times are not production CPU measurements.
4. Validate schema/exact fields, integer nonnegative scalars, four ten-element nonnegative arrays, and relationships below before recording partial results. Independently sum original per-case records, reconcile all54 hashes and passes, and verify every frozen input remains byte-identical. Do not rely only on generated summary.json. Write both per-case and aggregate opportunities, never label them CPU gain.
5. Record zero/nonempty/checked loops, A calls, summed K, old2A/lazy1+K/difference, by-victim traffic, allowance share of source demands and segment denominator. Each family must satisfy checked<=loops, nonempty<=loops, nonempty<=K<=A, K<=5*nonempty, old=2*A, lazy=nonempty+K, lazy<=old, sum(calls_by_victim)=A, sum(unique_by_victim)=K and elementwise unique<=calls. Q additionally requires nonempty<=loops-checked. Derived zero=loops-nonempty must be nonnegative. Note K is a **sum of per-loop unique keys**, not global distinct victim types. These arithmetic reconciliations support counter interpretation but do not replace review of increment placement and native lifecycle.
6. This source-scope review does not itself prove counters count the intended admitted branches in a compiled artifact. Parent should inspect emitted/call-site source mapping as appropriate and retain the full54 strict replay before treating observations as native evidence. No result or later optimization decision exists yet.

## Exact source/evidence identities

prepared.json binds all43 baseline and44 derivative native/build files, all archived tools, patch and generator. The deterministic archive was read back and every member hash matched. The protected material/evaluator/Position/allowance/wire files and original binary source remain byte-identical. The identities below bind inherited-pattern and released-lifecycle anchors read during preparation.

```text
254455189f2d1ec8628457002feff1606eec78e0f8c5d5f358434add2c88ccee  /home/legolas/rook2/evidence/null-influence-opportunity-preparation-20261018/prepare.py
0158af0b7b7bf12dca889c7b234a2437b55daa64e6051692ac0568a41c2d81dd  /home/legolas/rook2/evidence/null-influence-opportunity-20261018/collect.py
883a31a23e55b3e7be15436854f9947f0507ee2e8bbc30377861d9965c3d5d4f  /home/legolas/rook2/evidence/null-influence-opportunity-build-20261018/source-before/src/bin/rook2-null-probe.rs
5fd3117420ce7a9813268dc0db322f339739061868395324c36ff3cebce6126e  /home/legolas/king-spec/conformance/profiling/workloads.json
f25d63ad547505d1b2ade6b294d0b4a4a3cdb7c29000634373521ca3dbaa88cd  /home/legolas/king-spec/conformance/profiling/replay-check.mjs
6719db738383dae810d49db96575dc981e5d83b57bd52acf7c5a23c1b22e09dc  /home/legolas/king-spec/conformance/profiling/replay-oracle.json
```
