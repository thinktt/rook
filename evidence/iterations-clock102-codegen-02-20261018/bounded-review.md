# Combined102 bounded native/codegen gate — stop before strict/DIAG

The single exact102 source closure passed153native tests (151lib+2dev). Generic native artifact is `c4df447422ff8666ede8e15d8d599889a9cf1d2d4316c241dd313be1a15454d5`, frozen and archived before tests. Comparison control is the exact tested generation2 generic `e77e90d6c8f155e2fe09d32bd05e985ba3b15542bf847efb991be23bf772ff54`. Both receipts match rustc1.85.1/LLVM19.1.7, cargo1.85.1, generic target x86-64, opt3/thinLTO/codegen-units1/panic-abort and no PGO. Frozen102 source, execution source and all frozen dependencies rechecked unchanged at this gate.

No extra extension query, observer record/dispatch/allocation, recursive wrapper detour, evaluator scope or charge operation was found in the bounded default production functions. This supports proceeding to functional regression if parent accepts the measured layouts. It is not whole-artifact CPU neutrality, an instruction-retirement comparison, final qualification or adoption. No strict/DIAG ran; parent decision remains required.

## Measured layouts and material displacement risk

Abort-matched probes against each existing generic rlib measured:

| Type | generation2 | combined102 |
|---|---:|---:|
| Stats |224|232|
| Search<false,NoHost> / Search<true,NoHost> |25600|25600|
| OrdinaryOutcome / FirstOutcome |368|376|
| QOutcome |320|328|
| Work |16|16|
| Node |176|176|
| Retained |16|16|
| Evaluation |24|24|
| Evaluator<false> |9736|9736|
| Position |160|160|

All measured alignments remain unchanged. The Search size numbers are explicitly the default NoHost instantiations, not a size claim for every production Host monomorph. Public offset probes prove NoHost Search.evaluator12488->12264 and config22224->22000 (both-224), Stats initial-phase counter168->176 and accumulated-use counter184->192 (+8), with outcome Stats offsets unchanged. Rust aggregate reordering absorbs the new size into total Search padding while moving existing fields. Same total size does NOT mean same layout/locality.

Actual production ordinary/Q/order code has31 changed instructions:17ordinary,13Q,1ordering. Every one changes only an existing Search-relative displacement by-224; instruction addresses, opcode/register sequence, lengths, direct targets and relevant GOT targets are unchanged. The ordering difference is3d909 `lea0x50f0(%rdx),%rax` ->`lea0x5010(%rdx),%rax`. Source annotations and offset probes bind these to the moved evaluator/config and adjacent existing search-owned state rather than new observer storage. Public evaluator/config probes corroborate the displacement direction; private active-Host layout is not extrapolated from NoHost total sizes.

The charge_node owner was also inspected:275instructions/19static calls in both, same stack/control shape. Its actual nodes load/store moves0x2fb0->0x6340 relative to its Search pointer; other changed fields use the same-224 shift. This is the moved Stats storage itself, not a claim that every changed displacement is-224. Source engine.rs charge_node still has the same limit check, one nodes increment and4096-poll chronology. store_ordinary remains22instructions/2calls with no actual operand changes. These are existing charge/state accesses, with no added query or charge; their changed storage locality is a real layout risk retained for later cost checks.

## Default function scope, frames and actual calls

| Default function | bytes both | instructions both | static calls both | main RSP subtraction both |
|---|---:|---:|---:|---:|
| visit_ordinary |8736|1716|73|1080|
| visit_q_impl |7358|1566|55|1224|
| ordering_phase |2494|522|23|504|
| Extensions::for_move |522|150|2|56|
| Evaluator::full_impl |2415|577|12|312|
| evaluator Parameters::bind |1335|286|6|1496|

These count static emitted sites, not calls executed at runtime. Full stack-adjustment/push/pop sequences match, including ordering's temporary outgoing-argument stack use; the main RSP column alone is not a total frame-size formula. The same function symbol extents and existing ABI argument/return windows are retained in named-transfer-abi-windows.json. Actual recursive transfers are3direct ordinary self-call sites,1Q self-call site,1ordering->ordinary call,2ordinary->Q calls,1ordinary->full and2Q->full calls. Calls are conditional paths, not a runtime evaluator count. There is no added visit_q/observer wrapper hop at these actual transfers; wrappers remain inlined along these caller paths, established by actual direct destinations and matching argument/return instructions rather than merely absent symbols.

Extensions::for_move and full_impl have exact instruction bytes equal, as does evaluator Parameters::bind; some anonymous LLVM symbol comments differ only by module suffix. The other selected functions are NOT byte-identical because of the field displacements above. All captured indirect-call GOT slots resolve to the same initial target addresses/symbols, with the same call instruction sites. Numeric code/frame equality here is a bounded static fact, not a reason to generalize all layout/code/cache behavior.

## Counter erasure and full/fast ownership

The only production source change beyond the Stats scalar is `if DIAGNOSTICS && fresh!=0` immediately after actual Extensions::for_move in ordering_phase. D=false production ordering_phase differs in exactly one existing evaluator-base displacement, with no extra branch/test/increment/store or call instruction anywhere in that body. Its actual fresh-extension call at3dc04 uses the same rdi/rsi/edx argument setup and return consumption; the same GOT slot resolves to Extensions::for_move. The source's normal accumulated-flag union/store follows unchanged. Thus erasure is demonstrated at the actual operation site, not by searching for a counter symbol. Existing D=true tests passed both admitted zero-extension contexts and the strengthened actual nonzero tail case.

The native evaluator source is unchanged from generation2. Production fast is inlined into Q/ordinary; emitted source annotations cover evaluator.rs508-520 and finish467-483, while Q full calls cover the default full wrapper311. At these inlined scopes the instruction sequences are unchanged apart from the bound Search field offsets. Default full_impl itself is byte-equal, with the same12static calls and312main RSP subtraction. Actual full/fast wrappers retain the no-op static observers and one native finishing path. No extra Influence construction, pawn probe, callback, snapshot argument, allocation or duplicate finishing arithmetic was introduced by the counter. Existing allocator/panic/library call sites remain existing sites; no assertion is made that native search has no allocations at all.

## Failed harness01, corrected02 and actual closure

Freeze22698/c22c7c->8132cb exit0. Generic85988/e30d4a->bb1e5a exit0. Native75246/10640b->c2e7b5 exit0. First codegen65d148 exit1 is preserved in iterations-clock102-codegen-20261018: the standalone layout readout accidentally used unwind while the existing release crate requires abort. This was a harness compile mismatch, not a test or production mismatch. Parent authorized a new codegen02 directory and corrected capture driver with explicit panic=abort for BOTH probes; no native source/build/unit was rerun. Exact retry/old-driver/failure hashes are in retry-plan.json.

Codegen02 actual40272/1d32ea->e5480c exit0. Public-offset readout helper5b28b1 exit0, both baseline/candidate abort-matched children synchronously awaited; it creates no Search instance or engine. A later read-only comparator initially asserted byte equality too early and failed276463; its failure is preserved in analysis-reader-failure.json. Corrected comparison records the actual displacement differences instead of treating equal instruction counts as byte equality. No source fix, byte/frame-equality chase or ordinary replay followed either harness issue.

All native/build/probe children are terminal. Final gate packaging is source/text/hash only and reports its actual helper terminal separately. Authorized sibling phase2 own-PGO training/build may overlap untimed housekeeping; this validation owns noCPU14/15 work and no CPU/Callgrind measurement. Original proposal and failure directories remain immutable. Parent must decide whether the measured layout risks permit strict/DIAG; no codegen-acceptance file or automatic acceptance is created here.
