# Addendum: IIO diagnostic admission is normative

**Finding: (a).** For `search.ordinaryIterations`, the adapter's tail/additional-pass/nonzero-ordering-extension rejections enforce explicit released DIAG restrictions. They are not evidence of an incomplete transport rejecting otherwise admitted requests. No valid counterexample to those three gates is identified, and this finding does not justify changing them.

Released `spec/ordinary-iterations.md:17–25` permits the exact neutral vector with2..6 completions but expressly subjects neutral IIO requests to the later produced-search boundary; the four-field controls and30-field vector do not alone establish semantic admission. Lines39–44 require an error, without a prefix/last-complete response, for produced search outside the qualified rules.

The decisive clause is `ordinary-iterations.md:358–365`: the published route admits only initial phases with exactly one shallow target and zero fresh and accumulated ordering extensions; a required tail phase, second target or nonzero ordering extension must fail without a partial response. Lines515–518 and538–540 repeat this as a diagnostic admission/qualification limit, while fully specifying broader ordinary production behavior. `diagnostic-interface.md:65–70` independently summarizes bounded initial/single-pass/zero-extension IIO. “Complete unrestricted root iterations” describes the root pass and is not authority to discard these explicit recursive limits.

Adapter `diagnostic/src/root_iterations.rs:122–135` executes the actual native fixed search, requires normal completion, and calls qualified_ordinary before constructing any response. Lines157–165 map the produced boundary as follows:

| Adapter gate | Released limit |
| --- | --- |
|iio_tail_phases !=0 |No tail phase in this route. |
|iio_passes !=iio_initial_phases |Exactly one shallow target per entered initial phase. Each completed initial phase has D>=4 and includes offset2, so at least one target exists; with tails excluded, equal totals prove one per phase. |
|iio_nonzero_fresh_extensions !=0 |No nonzero fresh ordering extension. This does not ban unrelated fresh main extensions. |
|accumulated_extension_uses !=0 |No accumulated ordering flags changing later pass/main extension context. |

These are intentionally observed-search checks. The contract does not require all semantic-domain failures to be predictable from lexical schema before search. The adapter returns an error before response serialization, satisfying the no-partial-response rule. Whether every counter is correct remains a native-owner obligation already examined in the separate closed review; this addendum adds no new run or general counter proof.

Existing original `ordinary-iterations-iio-nonempty-depth5` and `ordinary-iterations-iio-empty-depth5` illustrate admitted bounded initial IIO; they are not tail/multipass/nonzero-extension witnesses. A normal production search may require the broader specified rules while lying outside this DIAG route. Therefore the remaining production-tail coverage question cannot be repaired by silently accepting a tail request through this versioned operation. It needs suitable separate production evidence/authority. All117 passing fixture coverage remains finite and does not prove the entire produced admission domain, nor other profile/setup/resource checks or other operations sharing this helper.

The preceding current25 report is unchanged. No engine/build/test/profiler/static-binary tool/Git/archive or source edit ran; only source/spec reads and this new addendum's metadata writes. No implementation is proposed.
