# Experiment26 generic backend gate

**GO for the frozen generic CPU prescreen once the independent functional gates close.** Actual lowering removes the four duplicated current-phase derivations selected by the source proposal. The transport and register-allocation costs are visible, but no static regression is large enough to reject the bounded measurement. This is neither a CPU benefit prediction nor ABI/stack neutrality; parent owns launch and selection.

| Emitted production owner | Control2940 bytes → triala26e bytes | Fixed `sub rsp` bytes | Static stack-reference instructions |
|---|---:|---:|---:|
| full_impl | 2,415 → 2,546 (+131) | 312 → 312 | 77 → 89 |
| activity compute → compute_with_phase | 7,884 → 7,696 (−188) | 456 → 440 | 198 → 206 |
| shelter compute → compute_with_phase | 857 → 638 (−219) | 56 → 56 | 16 → 17 |
| patterns → patterns_with_phase | 2,155 → 2,046 (−109) | 136 → 152 | 61 → 65 |
| pawn_terms::compute wrapper | 416 → absent/inlined into full | old24-byte frame disappears | old6, now part of full |
| standalone Position::phase | 214 → 214 | none | none |

These frame figures exclude six saved-register pushes (48 bytes) in full and the four framed leaves. They are actual adjustments, not complete peak-stack guarantees. Stack-reference counts cover whole static bodies, including cold branches, locals, result buffers and arguments; they are **not dynamic spill counts**. Whole image `.text` falls487,835→487,035 bytes (−800); `.rodata` stays319,720 bytes. Debug-section/file-size changes are irrelevant to this gate. Ordinary/Q emitted bodies remain8,766/7,224 bytes by nm; this does not establish full operand equivalence or recursive ABI/layout neutrality.

## Actual removed work and surviving ownership

The binary has one emitted full_impl in each image: control0x3f440, trial0x3f090. GOT relocation resolution verifies its actual calls, rather than assigning an arbitrary same-name symbol. At control0x3f6f8/0x3f71e/0x3f7dd it calls activity/shelter/pattern public owners; trial0x3f3f0/0x3f41f/0x3f4b9 calls the corresponding with-phase owners. The selected scalar producers and their original formula bodies remain source-owned; there is no runtime table/dispatch/cache addition.

Activity's count-normalization/clamp prefix begins at control0x18880 and its endgame clamp includes0x18929. The trial instead saves packed Phase fromr9 at0x18880 and unpacks endgame immediately; those count-normalization/opening/endgame prefix operations are absent. Its remaining scoring, relation and king-pressure traversal is still present; both king_pressure calls survive. Shelter's old count/clamp prefix from0x316f3 onward is gone. Trial0x31428 loads the incoming packed Phase from`[rsp+0x70]`, then unpacks fields to form the original shelter weights. The unchanged56-byte shelter frame does not make this extra argument free.

Patterns still reads piece counts needed for the pattern formulas themselves. Its separate phase/opening derivation near control0x3018e–0x301dd is removed, replaced by the incoming Phase saved fromrdx at trial0x2f7c1 and opening read/test at0x2ff07–0x2ff12. Its frame grows16 bytes and shows additional stack traffic, including transient piece bytes near0x2f7fb/0x2f837. This is a concrete cost risk to let the prescreen decide, rather than claiming every removed normalization instruction is a net saving.

The pawn public `compute` symbol is absent in the trial production image. Control full0x3f6d0 calls its416-byte wrapper, which derives phase and calls structure_terms plus conditionally raw_piece_terms. Trial full now calls those existing owners directly at0x3f32a/0x3f36c, preserving the conditional admission and weighting inside full. Thus the caller's static call-site count rises12→13, but the old wrapper's extra invocation/return disappears from a reached pawn evaluation; this is not a new algorithm or two added dynamic calls. The trial source already had an authorized `compute_with_phase`; thin-LTO inlined its small composition. No standalone full-helper relay is introduced.

The full evaluation's original phase producer remains near its entry (trial0x3f0b6 onward), packed into rbp after pawn selection at0x3f2d8–0x3f2f5. Phase travels inr9 to activity (0x3f3ed), in one outgoing stack qword to shelter (0x3f40a), and inrdx to patterns (0x3f4b6). It spans intervening calls and is split/spilled as needed (`[rsp+0x18]`, opening at`[rsp+0x40]`). Full's static body grows35 instructions (576→611), its stack-reference count grows12, and its fixed frame remains312. These are transport/inlining consequences, not erased overhead.

The narrow source scope does **not** unify all remaining phase producers. Full still contains later count/clamp blocks for square_balance_from_phase, endgame finishing and the late-endgame flag (trial near0x3f5f6,0x3f733,0x3f946 respectively); RootContext::material is still separately called at0x3f189. The out-of-line214-byte Position::phase body has identical instruction text in both images. It remains available to other consumers. No fast_impl symbol exists in these default images; fast behavior is inlined elsewhere, and no supplemental probe was built. Public wrappers need not remain separate symbols under whole-program LTO.

## Calls, copies and bounded risks

`lowering.json` records every captured call site and resolves GOT slots from each image's own relocation table. Full keeps native material, pawn-cache fresh construction, selected pawn progress, central, square balance and endgame owners. No allocation, memcpy/memmove or new indirect policy call appears in the captured full body. Existing pawn-selection vector copies remain (hit path control0x3f56c–0x3f59a versus trial0x3f1b3–0x3f1dc, with analogous miss/retention copies); their shifted result slots do not imply removal or expansion of their semantic payload. Phase crosses the three outlined calls as a small packed value, not a copied Position/Node or newly allocated object. Source fields are unchanged; no layout probe or whole-program copy-neutrality claim follows.

Relevant risks for measurement are the16-byte larger patterns frame and altered spills; extra full stack traffic and131 bytes of caller growth; packed argument unpacking and shelter's stack argument; changed call/code placement from pawn inlining and leaf factoring. Against these, repeated leaf derivation is genuinely absent and total text shrinks. Static counts do not establish branch frequency, cycles, cache behavior, CPU gain, or a transferable old Callgrind percentage. No further annotation/probe/variant is needed for this gate. Run exactly the frozen seven-case prescreen if functional closure passes; preserve its predetermined rule and no-retry policy. Own-PGO would require its own later build/backend gates if advanced.

## Identity and actual work

Control: `2940ae5c003fa396b31639749b4c3ba29e52e8aebabfc96a7dde565b6d9abd04`. Trial: `a26e8bef2fc8e0a39112d38c68c0b23c7efa964eb30cb899bb50935bc55c1a65`.

Both exact images match their build receipts. Frozen source-before69 files were individually checked against before/after receipts: four changed native files(activity/evaluator/positional_terms/shelter), other65 members and all23 tools exact. Compiler/flags/effective build environment match: rustc1.85.1/LLVM19.1.7, x86-64 generic, opt3/thin-LTO/CGU1/panic-abort/debug1, no PGO. `input-pins.json` and summary's extra pins bind exact images/receipts/source/reviews, actual standalone build terminal, and current binutils. No mutable root is used for source attribution.

Captured only our own exact binaries:15 successful nm/size/scoped objdump commands, then two relocation captures. Actual outerbd2eac/0 and227a95/0, sessionless; all child commands exited0. Initial preflight439aad/1 assumed a missing generic-build/tool-terminal.json and stopped before binutils. Its helper and failure are preserved; correction pins the actual build-validation/result.json. Parent subsequently wrote the real24846/bfec05→1ca8e8/0 terminal, now separately pinned. No tool/child ID was invented. No builds, probes, engines, tests, profiles, timing, Git, or source modifications were performed. Parent's native validation may overlap on housekeeping; no measurement interpretation is made. All owned tool jobs are terminal.
