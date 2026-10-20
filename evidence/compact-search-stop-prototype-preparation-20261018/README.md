# Compact recursive stop — source-only prototype

Status: UNPARSED / UNFORMATTED / UNBUILT / UNRUN. No compile or backend approval is implied. Prepared during live parent CPU12 session96272/PID480262 with only small source/text reads, copying, edits and textual diff. Helpers used CPUs0-5,8-13; no owned15 task. No engine/profiler/version/parser/import/build/test/Git/hash/archive job was launched. Root and all frozen native trees are untouched.

## Basis and deliverables

This is a three-file overlay, not a new independently buildable crate. `base-src/src/{quiescence,ordinary,engine}.rs` were copied from `evidence/complete117-pgo-use-build-20261018/source-before`. `proposed-src/src/` holds only their changed versions. `trial.patch` is the combined textual diff, also split into three named patches. No other optimization or source is composed.

Existing parent pins, quoted rather than newly computed: source archive `ea8963b2f5d082e2d12f026f9a14e84df9d38a8f9b3bfb78014cbb3dea555652`; basis quiescence `491d612aec3dcaff246e97541667d1296735d810e7a86e1b16889ebddf6ef838`; ordinary `3813b729fda01f46216a30ed82ed514548397fb9db8bd79b616ca8612711f0e9`; engine `fd78963c25f8a2c50e0a4184413fe7f344ac637fd467bd54b5df7ddedbecdbf4`. No new source hash or archive was produced during timing.

## Chosen boundary

Public `Stopped` remains byte-for-byte source unchanged, including `NodeLimit(u64)` and `HostIo(ErrorKind)`. Existing public Q APIs and crate-facing `visit_q`, `visit_ordinary`, const `visit_ordinary_impl<ALLOW_IIO>` and `charge_node` retain their signatures. They are outward wrappers; fixed roots, timed ActualEffects and first-iteration consumers continue to receive the same public error types. Timed source, graceful-stop matching, cleanup and public ordinary Error are untouched.

A crate-private `InternalStop` carries unit NodeLimit, the other four distinct stop reasons, and the full native ErrorKind. Ordinary/Q recursive bodies, null/scout/retry calls, ordinary-to-Q handoffs, observer Q recursion and both IIO phases use compact workers. Existing private test-facing ordering_phase remains a public-error wrapper; production calls ordering_phase_compact. Default and explicit-false IIO paths pass the same method-local const through every recursive and IIO worker. No new runtime policy channel is introduced.

Only charge_node_compact converts a rich error into the internal carrier: it invokes the unchanged generic work_clock::charge_search_unit, then the unchanged work_poll at exactly the old credited-positive4096 condition. No charge, poll or limit arithmetic is copied. This seam may still construct/translate a rich return; whether the backend erases that cost is open.

At actual recursive outward wrappers, NodeLimit is reconstructed with the retained CONFIGURED `self.limits.nodes`, never `stats.nodes`. `into_public` requires Some for that reason; there is no guessed fallback. The only production NodeLimit origin remains the generic primitive called with that exact option, which can return it only for Some. Neither recursion unwind nor history.pop changes the configured option; begin_sequence installs it before entry. Host polling cannot manufacture a NodeLimit through Hosts