# Compact recursive stop — source-only prototype

Status: UNPARSED / UNFORMATTED / UNBUILT / UNRUN. No compile or backend approval is implied. Prepared during live parent CPU12 session 96272/PID480262 with only small source/text reads, copying, edits and textual diff. Shell helpers used CPUs0-5,8-13; no owned15 task. No engine/profiler/version/parser/import/build/test/Git/hash/archive job was launched. Root and all frozen native trees are untouched.

The attempted README metadata write failed actual9151c8/127 because an apostrophe broke the outer shell quote. Partial README.md and preparation-failure.json preserve this failure. This file is the replacement rationale; no runtime source was changed to remedy the metadata failure.

## Basis and deliverables

This is a three-file overlay, not a new independently buildable crate. `base-src/src/{quiescence,ordinary,engine}.rs` were copied from `evidence/complete117-pgo-use-build-20261018/source-before`. `proposed-src/src/` holds only their changed versions. `trial.patch` is the combined textual diff, also split into three named patches. No other optimization or source is composed.

Existing parent pins, quoted rather than newly computed: source archive `ea8963b2f5d082e2d12f026f9a14e84df9d38a8f9b3bfb78014cbb3dea555652`; basis quiescence `491d612aec3dcaff246e97541667d1296735d810e7a86e1b16889ebddf6ef838`; ordinary `3813b729fda01f46216a30ed82ed514548397fb9db8bd79b616ca8612711f0e9`; engine `fd78963c25f8a2c50e0a4184413fe7f344ac637fd467bd54b5df7ddedbecdbf4`. No new source hash or archive was produced during timing.

## Chosen boundary

Public Stopped remains source unchanged, including NodeLimit(u64) and HostIo(ErrorKind). Existing public Q APIs and crate-facing visit_q, visit_ordinary, const visit_ordinary_impl<ALLOW_IIO> and charge_node retain their signatures. They are outward wrappers; fixed roots, timed ActualEffects and first-iteration consumers continue to receive the same public error types. Timed source, graceful-stop matching, cleanup and public ordinary Error are untouched.

A crate-private InternalStop carries unit NodeLimit, the other four distinct stop reasons, and the full native ErrorKind. Ordinary/Q recursive bodies, null/scout/retry calls, ordinary-to-Q handoffs, observer Q recursion and both IIO phases use compact workers. Existing private test-facing ordering_phase remains a public-error wrapper; production calls ordering_phase_compact. Default and explicit-false IIO paths pass the same method-local const through every recursive and IIO worker. No new runtime policy channel is introduced.

Only charge_node_compact converts a rich error into the internal carrier: it invokes the unchanged generic work_clock::charge_search_unit, then unchanged work_poll at exactly the old credited-positive4096 condition. No charge, poll or limit arithmetic is copied. This seam may still construct/translate a rich return; whether the backend erases that cost is open.

At recursive outward wrappers, NodeLimit is reconstructed with retained CONFIGURED self.limits.nodes, never stats.nodes. into_public requires Some for that reason; there is no guessed fallback. The only production NodeLimit origin remains the generic primitive called with that exact option, which can return it only for Some. Neither recursion unwind nor history.pop changes the configured option; begin_sequence installs it before entry. Host polling cannot manufacture a NodeLimit through the Host IO API. Non-NodeLimit reasons do not unpack the option. A hypothetical new producer from a different budget owner would invalidate this seam and must not be admitted silently.

The shared generic work primitive and its WorkSource consumer are unchanged. In particular units5/limit3 must still yield public NodeLimit3 while retaining units5; no shared arbitrary-counter caller reconstructs its limit from Search state. Limits remain enforced in both diagnostic modes.

## Semantic/source proof and test declarations

The textual patch changes recursive function names/result carriers, adds outward maps, and converts the same IIO stop reason. It leaves arithmetic, candidate order, observer enter/leave guards, successful-score scout retry guards, history push/pop placement and charge/poll ordering intact. Err propagation still precedes root commit/capture; a NodeLimit remains an error rather than a graceful timed interruption. All existing baseline tests are left textually unchanged.

Two added test declarations, neither executed:

- public_stop_recovers_configured_budget_even_when_counter_is_already_over: independent generic units5/limit3 witness, then real continued-Q refusal/repeated refusal and charge wrapper with nodes5/limit3 in Dtrue and Dfalse. Requires exact typed/debug NodeLimit3, unchanged work5 and history boundary. This distinguishes configured-budget recovery from counter reconstruction.
- timed_poll_io_kind_survives_compact_recursion_and_unwinds: actual timed ordinary recursion with a Host that fails the first command poll with PermissionDenied or ConnectionReset, in both diagnostic modes. Requires exact public HostIo kind at credited4096, one command read, restored root history and timing cleanup. It exercises the real rich-to-compact-to-public path, not a conversion-table mirror.

No full inventory, compilation or test count assertion was performed. Declaration delta is +2 unit-test functions. Existing initial/tail false-IIO tests, observer stop/unwind, fixed budgets and timed cleanup tests remain required if parent later authorizes execution.

## Cost uncertainty and later gates

Existing saved matched probes reported public Stopped16 and Result<i32,Stopped>16; ordinary Error24 is a separate type. This proposal does not claim a 24-to-small recursive Result change, removal of an sret, one-register lowering, layout reduction, copy neutrality or CPU gain. ErrorKind remains native and uncompressed. Compact success/error packing may introduce tag shifts/masks, spills, wrapper relays or code growth. Existing test-facing outward wrappers can also become unused-method warnings in a non-test build; no warning-suppression attributes were added speculatively.

Selection remains with parent after fixed35-to-08 attribution/backend evidence. If selected later, first prove native/default/false/observer behavior and exact public errors/work/output, including full strict54/eightwire and configured limits. Then inspect actual default WireHost and matched NoHost emitted return packing/charge transfers, ordinary/Q frames, root boundaries and conversion costs. Only matched CPU evidence could support a performance claim. No additional variant or test execution is authorized by this preparation.

Textual diff creation actual97ba2c/0; complete patch read actual08c0c7/0. Final metadata terminal is reported separately. All owned jobs are terminal; no long-running owned process was created.
