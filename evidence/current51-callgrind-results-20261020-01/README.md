# Current51 one-case diagnostic profile

Exact retained51 `48ee57b14e436338037e21f0f01f0f340959d7b05771f5cd759a3eab38d655b4` completed one unchanged original profile35 replay through Valgrind3.24.0. Its raw output matches its own-PGO strict reference byte for byte, original offline checkReplay passes and all observed children exit with confirmed owned-tree cleanup. Collector a56e88/0, independent verifier d074ab/0, raw SELF ranking5a5071/0 and four selected source annotations913727/0 are actual successful tool terminals.

Raw exclusive rows and function ranking both sum exactly to **44,100,272,048 simulated user instructions**. Inclusive caller arcs remain separate. Leading recorded object/function identities are:

| Recorded function | Exclusive simulated Ir | Share |
|---|---:|---:|
| `rook2::activity::compute` | 9,154,116,962 | 20.758% |
| `rook2::ordinary::<impl rook2::engine::Search<_,H>>::visit_ordinary_impl'2` | 8,959,930,803 | 20.317% |
| `rook2::influence::Influence::build_coherent` | 4,789,148,713 | 10.860% |
| `rook2::movegen::generate_legal` | 3,714,861,352 | 8.424% |
| `rook2::shelter::compute` | 2,150,286,988 | 4.876% |
| `rook2::quiescence::<impl rook2::engine::Search<_,H>>::visit_q_impl` | 1,830,042,385 | 4.150% |
| `rook2::position::Position::apply_unchecked` | 1,785,966,274 | 4.050% |
| `rook2::quiescence::<impl rook2::engine::Search<_,H>>::visit_q_impl'2` | 1,769,583,441 | 4.013% |
| `rook2::pawn_terms::compute` | 1,448,897,987 | 3.285% |
| `rook2::pawn_terms::structure_terms` | 1,213,025,562 | 2.751% |

Source annotations were selected after the actual ranking for activity.rs, types.rs, ordinary.rs and shelter.rs. They use the same original1200second study deadline,60second per-command bound and128MiB storage envelope; no second engine lifetime. All frozen inputs remain unchanged. Inline/core attribution and unidentified line0 costs are retained. Demangled suffixes do not establish physical clone identity.

This is a whole-lifetime diagnostic including startup, ordinary search, quiescence and exit. Ir is simulated instruction work, not PMU retired instructions, cycles, measured CPU cost or a corpus-wide percentage. Linux executes the Valgrind translator; exact Rook2 bytes and replay equality are independently bound. There is no native speedup or qualification claim.

The largest recorded function is Activity; ordinary search also owns substantial inlined policy, tactical and evaluator work. Select mechanisms from actual source rows and caller evidence. Earlier parked trials remain parked: in particular52 separation and41 shelter base lookup are not revived by this profile.

Production remains51: whole54 69.417194 CPU seconds and whole12 698.491201 CPU seconds in their prior separate local windows. Full behavioral/performance qualification and external3288 remain open.
