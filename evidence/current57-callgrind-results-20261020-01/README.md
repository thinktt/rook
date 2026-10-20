# Current57 one-case diagnostic profile

Exact accepted57 `af849f920897ec1f174b16718be5d6886158913ee4819f84273f15bd8c23e5b8` completed one unchanged original profile35 replay. Original live and offline outputs match; observed owned descendants exit and cleanup is confirmed. Actual collector909932/0, verifier30975c/0, SELF rankingea0b02/0 and selected annotationsf0bbea/0 all pass.

Exclusive SELF rows sum exactly to **43,940,740,008 simulated user instructions** across511 recorded function identities. Inclusive caller arcs remain separate.

| Recorded function | Exclusive simulated Ir | Share |
| --- | ---: | ---: |
| `rook2::activity::compute` | 9,154,116,962 | 20.833% |
| `rook2::ordinary::<impl rook2::engine::Search<_,H>>::visit_ordinary_impl'2` | 8,959,930,803 | 20.391% |
| `rook2::influence::Influence::build_coherent` | 4,789,148,713 | 10.899% |
| `rook2::movegen::generate_legal` | 3,557,014,852 | 8.095% |
| `rook2::shelter::compute` | 2,150,286,988 | 4.894% |
| `rook2::quiescence::<impl rook2::engine::Search<_,H>>::visit_q_impl` | 1,830,042,385 | 4.165% |
| `rook2::position::Position::apply_unchecked` | 1,785,966,274 | 4.064% |
| `rook2::quiescence::<impl rook2::engine::Search<_,H>>::visit_q_impl'2` | 1,769,583,441 | 4.027% |
| `rook2::pawn_terms::compute` | 1,448,897,987 | 3.297% |
| `rook2::pawn_terms::structure_terms` | 1,213,025,562 | 2.761% |
| `rook2::tactical::generate_for_search` | 1,174,454,735 | 2.673% |
| `rook2::pawn_structure::fresh_with_order` | 1,076,435,404 | 2.450% |

Source annotations for activity.rs, types.rs, ordinary.rs and position.rs use exact original compiled source bytes and the original1200s shared deadline; no extra target lifetime. All four have recorded information. Inline/core and line0 rows remain explicit; demangled suffixes do not identify physical clones.

Activity remains the largest recorded owner. The complete apply_unchecked machine body also retains intermediate capture-plane writes. A bounded source review identifies a smaller destination-clear deferral question, without claiming the entire transition cost removable. Phase-sharing26 and other parked trials stay parked.

This is whole-lifetime translated instruction work including startup/ordinary/quiescence/exit. It is not native CPU, retired PMU instructions, cycles, memory traffic or a corpus-wide speed result. Production stays57 at69.051049 whole54 and689.783349 whole12 CPU seconds in separate prior windows. Qualification and external3288 remain open.
