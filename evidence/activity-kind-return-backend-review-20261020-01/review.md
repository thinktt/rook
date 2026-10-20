# Experiment60 generic kind-return mechanism gate

**The selected mechanism is present.** Candidate d310d5e5 actually outlines four typed accumulators, passes the six original thin inputs, and receives score/query scalars in RAX/RDX without a private hidden output buffer or mutable total-output pointers. This is a mechanism GO for the parent's functional/screen decision, not a favorable cost or speed claim. The real call/frame/footprint costs below prevent a caller-frame-only conclusion.

Exact control57 generic5d10b2fa and candidate60 generic d310d5e5/source74 bd5b9c9f are stable before/after. Frozen source-before maps differ only in activity.rs, with tools23/toolchain/flags generic x86-64/noPGO paired. Parent freeze SHA bc1a617a is checked. Both complete compute bodies and four actual consumed accumulator bodies are captured: six full bodies/144880 stdout bytes, within10/2MiB. All nm/readelf/objdump child exits are0, exact commands/PIDs/raw hashes retained. Caller capture420386/0; groups02678c/0. Parent library tests could overlap untimed onH; these captures run no engine/tests/builds or timing.

## Actual native caller, arguments and results

Both compute symbols start0x18850. Source keeps White then Black, N/B/R/Q. Candidate calls0x189c1→0x1a570 (N),0x189e6→0x19fe0 (B),0x18a15→0x18d50 (R),0x18a3e→0x194d0 (Q), then0x18a7a/0x18aa3/0x18adc/0x18b0e repeat those exact targets for Black. This mapping uses actual call addresses and source chronology, corroborated by group counts/knight geometry/rook king gate; identical demangled names alone do not identify the instantiations. Baseline has no outlined group symbols/calls and retains the inlined accumulation inside compute.

At actual group calls, RDI holds Position, RSI Influence, EDX color0/1, RCX oriented destination views, R8 the caller's marks address rsp+0x50, R9w endgame. There is no seventh outgoing stack argument and no leading result pointer shifting those inputs. The outer public compute still has its existing Activity result buffer, saved at rsp+0x48; that is distinct from the private groups and is not removed.

All four group returns are direct scalars. N exits0x1a9bd with RAX score/RDX queries (from r12); B0x1a4c9, R0x19411 and Q0x19f31 copy query total from rsi into RDX while RAX holds score. Empty paths zero both before the same epilogue. Caller immediately consumes those values as scalar arithmetic/liveness: first N score→r13 and query→rsp+8 (0x189c6/0x189c9), B then adds at0x189f1/0x189f4. R returns spill score/query to rsp+8/+0x10 (0x18a1a/0x18a1f) across the subsequent Q call; analogous Black spills/adds remain. No aggregate return memcpy, temporary group-array or pointers to caller score/query totals appear. These scalar return spills are real staging costs and must not be mislabeled zero output traffic. Arithmetic reparenthesization/order correctness remains the parent's source proof under admitted bounded sums.

## Complete consumed cost inventory

| Body | Address | Code bytes | Local stack reservation | Saved GPRs |
| --- | --- | ---: | ---: | ---: |
| Baseline compute |0x18850|7884|456 (0x1c8)|6 /48B|
| Candidate compute |0x18850|1279|216 (0xd8)|6 /48B|
| Candidate N |0x1a570|1259|120 (0x78)|6 /48B|
| Candidate B |0x19fe0|1418|136 (0x88)|6 /48B|
| Candidate R |0x18d50|1906|184 (0xb8)|6 /48B|
| Candidate Q |0x194d0|2817|104 (0x68)|6 /48B|

The four group bodies total7400B; caller+consumed groups total8679B versus7884B, **+795B** excluding inter-symbol alignment. Actual.text grows0x340/832B; .rodata size remains0x4e2b8. The caller's smaller reservation is not whole-chain stack saving: below compute's entry RSP, baseline saves+reserve=48+456=504B. With R active, candidate=48+216+8 return-address+48+184=504B as well. N/B/Q analogous totals are440/456/424B. These figures cover only these frames before any deeper cold failure calls; they are neither whole-search peak-stack nor memory-traffic measurements.

All eight group calls occur unconditionally from compute, including zero-source groups. Each callee pushes six GPRs/reserves its frame BEFORE the group-count-zero branch (N0x1a5a8, B0x1a022, R0x18da4, Q0x19525); empty work still pays entry/exit and inventory checks. R's opposing king/inventory/seventh-row setup is after its own nonzero-rook gate, so no new empty-rook king lookup is visible. Caller still initializes and retains128B marks and phase/material/weights across group calls; it adds spill/reload/save/return traffic. Each callee has its own loop-local stack state and compiler-expanded count/group checks. No aggregate group population/frequency is inferred from static bytes. Loss of cross-kind optimization is a real unresolved cost, not offset by source work removal.

Actual nonfailure direct calls inside the scoped set are the eight group calls and the unchanged two king_pressure calls from compute (baseline0x1a460/0x1a474, candidate0x18bba/0x18bce). Group-internal calls are only the emitted indirect failure tails associated in source with bounds/tag/panic guards; their external bodies are not expanded or assigned dynamic cost. No supplemental probe or unrelated root/Q/search disassembly was captured. No saved-register/spill neutrality or full semantic machine-code equivalence is claimed. Empty/nonempty ABI, frame and call costs are now exposed; later generic and own-sourcePGO outcomes, if authorized, remain empirical gates.
