# Activity value inputs: matched own-PGO backend

No new backend blocker to a matched CPU trial was found. The candidate retains the physical-square view lookup in the actual production image, reduces activity code by393 bytes and its stack allocation by16 bytes, and introduces no scoped caller growth or call-boundary change. This is static evidence only; fresh functional closure and parent clearance remain required before timing. No CPU, cache, copy-neutrality or ABI benefit is inferred.

## Identity and own profiles

Control: `complete117-pgo-use-build-20261018/rook2-exact`, SHA256 `6a5ce6e27b74490e623fbb705f70c770ec12ff7e88f761fb0c7119ca2aee4a50`. Candidate: `activity-value-inputs-pgo-use-build-20261018-01/rook2-exact`, SHA256 `d5ee1f3f7258f152c0a9c50664855c46f6b631e611a85bdfdae07f509654decc`.

The capture rehashes both images, receipts, all frozen source46/tool23 snapshot files and their two recorded PGO inputs. Before/after source/tool maps match; the sole native change is activity.rs. All23 tools are identical. Compiler/cargo identities and versions, generic x86-64 target, jobs4 and Cargo configs match. Exact flags are target-cpu=x86-64 plus profile-use to each side's own profile and llvm-args=-pgo-warn-missing-function. Effective flag overrides match after substituting only those exact own-profile paths. Unchanged Cargo.toml establishes opt3, ThinLTO, CGU1, panic=abort, debug1. Retained build logs pass the scoped missing/stale/hash-mismatch warning checks; no build or version tool was invoked here.

Control profile SHA256 is `1ffe7dc53d8c7caca4f052bf429ee5b2244f927ada3e85f8ecce1d2bb01311c5`; candidate profile is `17dab14f1c3f69bc39c2994d53caa376f8c41fd97e72f0ae2d03ce1b4440670f`. The profiles differ. Each training record identifies its own exact source,54 raw images and the same four original replay/corpus input pins. Each verification record identifies that training record, the matching profile and byte-identical independent remerge. This bounded static review rechecks those bindings and profile bytes; it does not rerun or independently repeat training/remerge/raw54 validation.

## Actual bodies

| Production body | Control bytes | Candidate bytes | Main stack subtraction, control→candidate | Static call sites, control→candidate |
|---|---:|---:|---|---|
| activity::compute | 9545 | 9152 | 0x228→0x218 | 14→14 |
| full evaluator | 5192 | 5192 | 0x168→0x168 | 18→18 |
| ordinary | 29895 | 29895 | 0x518→0x518 | 118→118 |
| Q | 19522 | 19522 | 0x5c8→0x5c8 | 89→89 |

All four retain six saved-register pushes. Activity static decoded instruction lines decrease2238→2160; this is not dynamic retired work. Whole .text decreases400 bytes; whole .rodata increases72 bytes. This is the actual PGO section delta, distinct from generic's -560/+184. The complete constant-pool/alignment difference was not decomposed; net section growth must not be described as the new table's object size.

Exactly one named256-byte DESTINATION_VALUES object is emitted at0x8eb44. The capture reads its entire ELF payload, checks all color/variant/physical-square bytes against the source matrix/rook-row construction, and finds one full payload occurrence. Candidate0x116d7-0x116e7 selects color*128 plus the RIP-relative static base and retains one pointer. Rook gate/variant selection remains before traversal;0x11fca-0x11fce adds variant*64 to that selected pointer. A representative ray value load at0x120d1 is byte `[r9+physical_square]`, followed by the original multiplication/vertical weighting. No builder, selector, table copy or allocation call is introduced. Activity's14 emitted calls resolve only to panic_fmt, panic_bounds_check and slice_end_index_len_fail; there is no added successful-path helper call. Their exact offsets differ with the changed activity body, so no whole-body equality is asserted.

## Call boundaries and generic risk

The actual ordinary body already includes inlined evaluator work on BOTH own-PGO sides. It calls activity through GOT0xace60 at control0x313fc/candidate0x3126c; that slot resolves to compute0x114a0 in both images. The standalone full evaluator calls the same slot at0x36f8f/0x36dff. Q retains its full-evaluator calls at0x2aebf/0x2ad2f and0x2d426/0x2d296. Ordinary retains its Q handoffs and recursive/scout transfers. The offline resolver checks all static call offsets and resolved targets in the three unchanged scoped caller bodies: they match between these two own-PGO images. Their decoded instruction counts and frames also match.

This is not a full instruction/payload equivalence proof, nor a statement that generic and PGO lower alike. In particular PGO has much larger ordinary/Q/evaluator bodies than the earlier generic capture on BOTH sides; no candidate-only growth is observed there. The default WireHost production ownership remains the unchanged ordinary binary's Session<false>/go_live path. Only one recursive body per scoped function was found. No NoHost or false-guard probe was built or compared.

The generic risk assessment therefore remains: a selected immutable pointer introduces setup/dependency work and changes instruction/data placement, while removing destination-coordinate arithmetic. PGO does not introduce a new call, larger activity frame or propagated scoped caller frame/body in this comparison. Its activity frame is16 bytes smaller, but that does not establish fewer dynamic spills or a measurable stack/cache benefit. The candidate's actual net CPU effect remains unknown. If parent accepts fresh strict/wire/independent functional closure, comparing exact6a against exactd5 is warranted; no generic timing result or historical attribution transfers automatically to it.

## Scope and closure

Only existing own images were inspected with nm/readelf/objdump. Sixteen pinned static child commands completed under actual outer fa5517/0. Offline receipt/call/section reconciliation completed6c1f19/0; both were fast actual completions with no session. All captured stdout/stderr, identities/profile bindings, metrics and call targets are retained in this directory. Helper processes used0-5,8-13 with HOME TMPDIR; no owned15 task or absolute-idle claim. Parent post-use regression could overlap on housekeeping, and this review is untimed.

No engines, builds, probes, profilers, timing or Git ran here; root/native/other evidence is unchanged. Parent owns functional acceptance and any CPU launch. Final manifest helper terminal is reported separately; all owned processes are terminal.
