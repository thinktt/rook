Ordered checker discovery from the existing persistent AttackBits is a plausible next bounded experiment. Phase1 should change only Position-based checker discovery in generate_bounded, leaving Q's current projected mailbox entirely alone. Phase2 could then replace Q's projected mailbox outright with one projected bit view shared by exact ordered check classification and the existing Boolean own-king-safety kernel. Neither phase needs a new persistent field, layout, maintenance path or new Boolean attack kernel. My preliminary ranking is phase1 first, with exact identity differential coverage; phase2 is a separate consumer-lifetime trial after phase1 semantics are established. No implementation or performance gain is selected here.

This is SOURCE/TEXT-ONLY work while parent CPU pilot92704 is live. No builds, tests, engines, profiler, executable/binary hash, symbol or disassembly scan was run. Commands were pinned to housekeeping0-5,8-13. Artifactd38ff03745c7fba981c22f12fdd7b10b78f539f9541faeb24b92bd263b116d45 is a declared identity read from its frozen JSON receipt, not rehashed from the executable during the pilot. Source authority is frozen correctedQ85 at /tmp/imp2-move-q-evaluation-combined-20261018: its complete43-file map equals that receipt's before/after source maps. Mutable root and the live king-first candidate do not define this audit's control. Normal speed was requested; no live speed control/readback is available. No Imp1 source was inspected.

The existing ownership is already suitable. Position owns four exact Piece-tag u64 planes alongside its mailbox and chronological lists. attack_view returns their Copy value; set_square updates actual old/new tags, including captures/promotion/castling/joined EP. Construction/recompute establishes coherence, validation decodes against the mailbox, and null changes turn/EP/halfmove without changing absolute tag planes. These adopted mechanics remain unchanged (decision0004). Evaluation influence is a different owner and must not be substituted for geometric Piece identities. Checkers remains a transient capped identity result; no per-position checker cache or extra attack representation is proposed.

All production mailbox/checker consumers in frozen85 are:

| Owner/source | Current route and observation | Phase1 | Phase2 Q-only |
|---|---|---|---|
|movegen.rs:640, generate_bounded<512>/<2>|find_attackers<2>(&position.board,king,opponent); exact lone-check identity drives evasion destinations/pawn prefix, len drives check/castles|Use already-owned Position bits for exact same capped identities|Same as selected phase1; no generation-order change|
|movegen.rs:224, check_routes|find_attackers<2> on projected mailbox; returns len!=0 and len==2 && first-two squares contains moved_to|Keep current mailbox route, avoiding a second Q representation|Q calls ordered-bits equivalent on its one projected view|
|quiescence.rs:302,307,354|One projected_board used first for check_routes, later mailbox attacked for final own-king safety|Entire route unchanged|Remove this projected mailbox local; share one projected AttackBits across both consumers|
|ordinary.rs:654-656, mate-probe loop|Project an ordinary legal candidate, Boolean check of opponent king, possibly enter a narrow-window Q mate probe|Unchanged|Unchanged; not part of Q-local replacement|
|ordinary.rs:730-733, frontier estimate|For an ordinary move at depth<=0, Boolean opponent check determines frontier estimate and child_checked|Unchanged|Unchanged; separate lifetime/scope|
|movegen.rs:132, public attacked(board,...)|Mailbox find_attackers<1>, used by the two ordinary paths and Q final safety today|Unchanged|Retained for ordinary and mailbox test oracle|

There is only one production check_routes caller: Q. Its other callers are native tests. projected_board also serves cfg(test) mailbox legality/projection comparisons; raw find_attackers calls in tests are not extra production consumers. No matching calls were found in the standalone Rust tools. Current in_check already uses persistent bits and is not a proposed optimization: ordinary root/entry, Q prepare/entry, timed root, session terminal classification and development admission all reach that existing Boolean path. Keep public attacked's mailbox API and the existing bits Boolean kernel stable. Removing Q's mailbox does not justify deleting projected_board globally while ordinary production still uses it.

The exact ordered contract is the main proof obligation, not merely Boolean attack equivalence:

1. Initialize the same two-square result and len0. For by=White use pawn source rank one below the target; by=Black one above. Visit source file offsets[-1,+1] for both colors. This is not the side-dependent tactical-pawn prefix order.
2. Visit KNIGHT_SOURCES[target] in its existing table sequence, derived from KNIGHT offsets[(1,2),(-1,-2),(-1,2),(1,-2),(2,1),(-2,-1),(-2,1),(2,-1)]. Numeric bit order is not that sequence.
3. Then visit ray directions[(1,1),(-1,-1),(-1,1),(1,-1),(0,1),(0,-1),(1,0),(-1,0)]. Inspect only the nearest occupied square on each ray. It contributes if it is the matching-color queen/appropriate slider, or a matching-color king at distance0. Stop at the first occupied square even when it is an own piece or a nonmatching enemy type.
4. Stop immediately when two identities are found, preserving their order and len saturation exactly. Do not replace these outputs with an all-attackers count/mask or sorted square list. Pinned enemies still attack geometrically.

Adjacent kings are interleaved with sliders in the ray sequence; the Boolean bits kernel's early pawn|knight|king existence test cannot be reused as an ordered emission order. Likewise multiple slider matches cannot be emitted by a global low-bit scan. A nearest-occupied implementation can use each existing ray mask and increasing flag: lowest set bit on numerically increasing rays, highest on decreasing rays. It must still loop directions in existing order and enforce adjacent-only kings. The current increasing construction from df+8*dr matches those monotonic rays.

Concrete adverse3-route witness (source-level geometric analysis, not executed): projected placement `4k3/3P4/5N2/8/8/8/4R3/K7 w - - 0 1`, query e8 byWhite, moved_to=e2. The old ordered finder first emits pawn d7 then knight f6 and stops. The rook e2 is a third route. Existing check_routes returns checking=true, double_check=false because e2 is absent from the first two. An all-attackers>=2 && membership(e2) rewrite would return true and incorrectly bypass Q's reply restriction. One parent form is `4k3/3P4/5N2/8/8/8/R7/K7 w - - 0 1` with ordinary a2e2. The opponent is already attacked in the parent; such broad constructed/joined domains must not be silently narrowed to the standalone quiescence diagnostic's safer ingress. This audit preserves the actual native capped rule rather than reinterpreting the intuitive phrase direct+discovered on3+ routes. Also test adjacent-king rays versus earlier/later slider rays and multiple knights whose square order differs from KNIGHT_SOURCES.

A bounded phase1 design can decode existing tag planes into by-color pawn/knight/king/diagonal-slider/orthogonal-slider masks plus occupancy, then select identities in the exact sequence above. Existing MASKS supplies pawn/knight/king/ray masks and numeric ray direction, and geometry already supplies ordered KNIGHT_SOURCES. There is no need for new global tables. Optional zero-candidate mask prefilters can avoid scanning absent classes/directions, provided they do not alter emission order. Retain occupied=a|b|c and exact valid-tag semantics; White's !black color complement must never make empty squares into attackers. The implementation should not scan/rebuild all64 mailbox squares or reconstruct a view from chronological lists for this consumer.

Keep the transient result's existing owner/fields or use a small private return wrapper immediately converted into the current Checkers. A private ordered-query method inside attacks.rs can access MASKS without exposing/mutating the persistent planes; a thin movegen wrapper can retain consumer ownership. API details remain unselected, and no new hot-field/layout change follows from this option. Keep the current mailbox finder available as an independent cfg(test) identity oracle and as the unchanged production mailbox Boolean route where needed. Phase1 changes only the current generate_bounded checker-discovery call. In particular, do NOT feed Q's existing board into AttackBits::from_board: that adds a full reconstruction/second temporary view while leaving the mailbox projection, which violates this experiment's ownership goal.

Phase2, conditional on exact ordered-query semantics, has a natural single temporary lifetime. At the original Q projection site, form `projected = position.attack_view().projected(&position,movement)` once; preserve stats.projections at its existing site. Use ordered first-two discovery on this projected view for checking/double_check and later `projected.attacked(king_after,opponent)` for final safety. Remove the Q local projected_board and its two mailbox consumers as a unit. Keep the original optimistic-best update, initial eligibility, forcing/recapture/double-route gates, produced-child repetition probe and history push/pop, prepared_child reuse, unsafe rejection and child entry in exactly their original order. Do not reject king-unsafe candidates early: Q's tactical producer is intentionally pseudo-legal, and unsafe ordinary captures can update optimistic best before that rejection. Do not force Node::child earlier just to obtain its planes; the local projection supplies check classification before that optional semantic child currently exists.

One temporary bit projection can remain live across the existing reply/repetition path and be reused for safety. A subsequently produced semantic child necessarily owns its own persistent planes, as it already does; no additional local projection is needed from that child and no persistent field/cache is added. Do not use the parent's chronological piece lists as post-move identity sources: they retain old source/victim locations. The projected tag planes must be the sole temporary placement truth for both Q queries. The parent remains immutable. Holding that32-byte view across helper calls can still create register/spill costs, so source-level footprint alone does not establish a frame saving.

The existing projector already handles actual normal captured tags, promotion tag replacement, joined EP's actual behind-target victim and castling rook movement. It is pure by-value, and the existing broad projection tests compare it with mailbox and produced/null children. Those mechanics stay unchanged. Phase2 must apply them to the actual pseudo-candidate domain as well: mover promotions, source vacating slider rays, capture of blockers, moving-king destination safety and joined EP removing a non-pawn attacker/blocker. An opposing king behind an EP target remains the separate cold exceptional ingress; normal Q generation excludes it. Do not widen normal Q admission or introduce a missing-king lookup in that path. Q never generates castle candidates, but the generic projector's existing castling behavior should remain untouched/tested.

Ordinary mate and frontier paths are valid later independent Boolean-only consumers, but not phase2 scope. They use one mailbox projection per admitted ordinary candidate and query only enemy-king checking. Replacing their mailbox alone with the existing Boolean bits projector is conceptually simpler than ordered Q classification, yet each is a separate phase/lifetime and should not be silently bundled. The mate-probe loop and later main/frontier loop can visit or reorder candidates separately around IIO/search effects; do not add cross-loop projected-view storage or cache reuse without another ownership audit. Neither path needs a new all-checker identity query. Leave them unchanged for the two proposed phases.

Source-level static-cost hypotheses, without codegen/measurement:

| Change | Work potentially avoided | New or remaining cost/uncertainty |
|---|---|---|
|Phase1 Position checker identities|Mailbox ray walks and repeated Piece-tag equality loads for checker discovery|Four-plane loads/kind decoding, mask-table reads, ordered knight/ray selection and nearest-bit scans; sparse early mailbox exits may already be cheap|
|Phase2 Q local projection|One64-byte mailbox projection and its tag writes; old mailbox final Boolean query|A32-byte Copy bit view, four-plane updates per changed square, ordered bit-query decoding, liveness across reply calls; actual copies/frame/CPU unknown|
|Shared projected view|Avoids constructing separate Q views for route classification and own safety|Two distinct queries still occur, by opposite colors/targets; they cannot be collapsed into one Boolean result|

For a normal move the bits projector changes source and destination using four planes each; special moves touch additional actual squares. Current mailbox copying can be vectorized and cheap, while new mask/bit-scan work can be costly. No retired-instruction/CPU gain, Amdahl bound or profile percentage is inferred. No current binary/disassembly was inspected. Maintaining both projected mailbox and projected bits in Q would pay both preparation costs and is explicitly rejected for phase2. Existing Position planes/maintenance/copy tax are already adopted and are not remeasured/reproposed here.

Correctness/differential plan for a later selected prototype:

- First compare exact len and ordered two-square identities against the frozen old mailbox finder on broad constructed placements, every target square and both colors, not only king targets or legal game histories. Include exact0/1/2 and3+ attack routes, two pawns, nonmonotonic knight order, adjacent kings interleaved with sliders, near/far blockers of either color, pins, promotions and broad joined setups. Preserve zero initialization/unused result slots or compare only the declared valid slice consistently.
- Existing Boolean_queries_and_projections_match_mailbox_on_broad_setups covers10000 placements, all target/color Boolean queries and legal projections for the first500; special_and_joined_projections_keep_actual_tags covers castling, underpromotion and unusual EP victims. every_tag_replacement tests all valid tags. These remain useful but Boolean equality does not prove ordered identities.
- Existing generation_summary_matches_projection_on_constructed_setups and joined witnesses check full/capped legality, while fixed released pawn-prefix/order/perft tests protect visible generation. The FORCE_PROJECTION comparison shares checker-discovery/prefix production, so it is NOT an independent oracle for a new ordered-discovery bug. Add explicit old-mailbox identity differential rather than relying solely on that shared-producer check.
- Phase2 must additionally test every produced tactical pseudo-candidate, including king-unsafe pinned captures/quiet checks, before any legality filtering. Compare projected tags against projected_board and exact ordered identities/route flags plus final own-safety result. Testing only generate_legal projections misses the primary Q hazard. Keep known direct-only/discovered-only/simultaneous/no-check route fixtures and add the3-route witness above.
- At composed search level preserve optimistic best, admission, retained state, charges, PV, child order/history restoration, repetition bypass and exact reply-list behavior. Native tests and strict54 replay/eight interruption fixtures with complete original raw streams/actual exits are later prerequisites, separately for each phase. No such run occurs now. Inspect emitted full/default/ordered/Q scopes only after parent clearance; avoid repeating the earlier mistake of inferring unchanged compiled scope from equivalent helper math.

If ordered identities and projected placements match exactly, no semantic cache, hash, RNG, evaluator, relation charge or node charge changes. The kernels are pure and existing charge/poll sites remain in place. Deterministic work-poll and queued-interruption behavior should therefore agree; changed actual runtime may naturally change wall-arrival availability or real-clock stopping, as with any performance change. Hardware cache accesses are deliberately different; semantic pawn/TT/learning/history lifetimes must not be. These are proof obligations, not a completed runtime validation.

Preliminary decision: phase1 is the smallest independently falsifiable next trial and does not violate the no-second-Q-view caution. Phase2 is credible only as replacement/removal of Q's whole temporary mailbox scope, using exact ordered identities and the unchanged Boolean bits kernel. It has broader pseudo-candidate/liveness obligations and no assumed32-byte/frame/runtime win. Parent selects any implementation and future control identity after the live pilot; no source/prototype change is made by this report.

Complete source/text occurrence inventory (includes native tests, classified above):
- `src/attacks.rs:316` — `movegen::attacked(&position.board, Square(square), side)`
- `src/attacks.rs:325` — `let board = movegen::projected_board(&position, movement);`
- `src/attacks.rs:382` — `let board = movegen::projected_board(&position, movement);`
- `src/attacks.rs:388` — `movegen::attacked(&board, Square(square), side)`
- `src/movegen.rs:82` — `fn find_attackers<const LIMIT: usize>(board: &[Piece; 64], square: Square, by: Color) -> Checkers {`
- `src/movegen.rs:132` — `find_attackers::<1>(board, square, by).len != 0`
- `src/movegen.rs:144` — `pub(crate) fn projected_board(position: &Position, mv: Move) -> [Piece; 64] {`
- `src/movegen.rs:180` — `let board = projected_board(position, mv);`
- `src/movegen.rs:218` — `pub(crate) fn check_routes(`
- `src/movegen.rs:224` — `let routes = find_attackers::<2>(board, king, by);`
- `src/movegen.rs:640` — `let checkers = find_attackers::<2>(&position.board, king, position.side.opponent());`
- `src/movegen.rs:894` — `let board = projected_board(&position, mv);`
- `src/movegen.rs:896` — `check_routes(&board, Square::parse("e8").unwrap(), Color::White, to),`
- `src/movegen.rs:970` — `find_attackers::<2>(&double.board, king, Color::Black).len,`
- `src/ordinary.rs:654` — `let board = movegen::projected_board(&position, movement);`
- `src/ordinary.rs:656` — `if !movegen::attacked(&board, king, position.side) {`
- `src/ordinary.rs:730` — `let board = movegen::projected_board(&position, movement);`
- `src/ordinary.rs:732` — `let checking = movegen::attacked(&board, king, position.side);`
- `src/quiescence.rs:302` — `let board = movegen::projected_board(&position, movement);`
- `src/quiescence.rs:307` — `movegen::check_routes(&board, enemy_king, position.side, movement.to());`
- `src/quiescence.rs:354` — `if movegen::attacked(&board, king_after, position.side.opponent()) {`

Exact frozen85 source identity (relative to /tmp/imp2-move-q-evaluation-combined-20261018):

```json
{
  "Cargo.toml": "6199772414ef5972898842d76472301d256e42f9dd2181fa421ff5cbc21c85d1",
  "Cargo.lock": "d34b5888f77c0319fb614ba5701a4a1177af31b803054ad3a8251926ba237c97",
  "src/activity.rs": "07d1b062f5ce6a4ffb66bd57eb3570f9221f42d7105b1df1f11e3039caf93c38",
  "src/attacks.rs": "9d44681cf9098548a32ae06463bdb4e769c4e20eff9ac175ba725afae6a0ac50",
  "src/bin/rook2-dev.rs": "1eea8e56f268a3fd943d1dc2d2ccd0c7607c80793c1a8f41eb464bdc53853c34",
  "src/bin/rook2.rs": "26849c997a5c564076dc5c6703dcdce783e900b0c221d7938f540664edd1a3b8",
  "src/clock.rs": "4b1d6f18e94d3161cefa8b4a5daafddffd1aba5d3d4ade182a03eed3ee493a79",
  "src/development.rs": "e25b082c342df61b2aa8c30e2970e65007ad3e99750807724bda42ab59a3045f",
  "src/endgame.rs": "4f382e7b5359f1956a0e155328aad08f35dab74252ee0794d61dafcd1cd2214a",
  "src/engine.rs": "2e3105e7a7802c4061c0d0cd0ddc4d4629a2c362297fb1f4e18ddc7e7d566e08",
  "src/eval_basis.rs": "5b369b122dc69aa40e5f8b81c3153173e633c9cfec89f160cef49886b5c36647",
  "src/evaluation.rs": "767b1ef83fea5d30d1b5a6edaa259fa718c666cfdb568fb9ad7b2aca2e9f33f7",
  "src/evaluator.rs": "40d6139b836e5b2cf16c5d9d7a9c7141d8f53bbe26f1b2fdda1f979065de70ac",
  "src/first_iteration.rs": "713830b62783a81033e1355687534783647b243c51e10f829546d080ce157722",
  "src/geometry.rs": "582a2e8ad2672a937062ae829ae596ee263b69c6ec52103c55c658a6ecc225f1",
  "src/history.rs": "f6b2a5073307d655e33e774900c9fea26f4bdfefbdd2cd9848ff0758c4b34fde",
  "src/host.rs": "9e9221287442d6b74825e291a6e9924a2ae78b7aa10ba42b8ae431a401639dee",
  "src/identity.rs": "761779f7f2e0186dfbe28e162bf5fc8c8461d9f9c342787ebe2becfd0914a376",
  "src/influence.rs": "05b402b7e0137720d5fb4d2f062601ebf5abf61411fe648531cdc94e2959843e",
  "src/lib.rs": "268a76071644eee4c4d7daba742d349089fd00b7e3f4d088496c679c6d9ec9b0",
  "src/movegen.rs": "9e645384baf5177697c5125df2e15db70eefac440ed63289435adddf6a514617",
  "src/ordinary.rs": "446b518a5824a8a60b65666d1b841d959ab2964c995739a2bc44d27bd5a9c442",
  "src/ordinary_policy.rs": "a79ec111e2d34bb9e4a3c2a7953c5b2a82b011016982fd2b63d6769da3036bf6",
  "src/output.rs": "180adf6062883c839a17ffa038ef30c6dd236661d94bdd61086c11c795b46247",
  "src/parameters.rs": "30dd03e5ead3df289b25929c7bea81e72d1e2b9a2250916883107f0cfaf7f42e",
  "src/pawn_progress.rs": "0bca6bb9678657b2efadc023c07d1ffcc9ff91c1c97553b84e2131c6ce30d9dc",
  "src/pawn_structure.rs": "b9d0921514c5ba7ba7532f07501fae7dc38b707f6c2f2f0bb01787be5263be13",
  "src/pawn_terms.rs": "a2081196fb0bfdbd1ac7830d2f668009b267e77d3e56b92c249af709cd99fff3",
  "src/position.rs": "749f9fa1e90684c4df670c115c3c7f7dbdb196cf62b5eb267900ba217143ce3a",
  "src/positional_terms.rs": "053b04b8f434db2ddadda71686831b40baf3c59d09be6cde5895af1b7d430260",
  "src/quiescence.rs": "1006c4a96307da25ccf96222afae2bdf21aa07b20852aedc30cb90a546e8c4b4",
  "src/quiescence_policy.rs": "baeb3f40c47f119481f0040b1c9bb15f9af25ee39376cf0c01d1a06091011468",
  "src/relation_table.rs": "2d0942b0fd96b25caeb9824f3dd2a41952356299019ba8d9a9d089f65c41e1e1",
  "src/remembered.rs": "af2eb6046fd7e58b1a35e7ed3051936559b7f739224ed698b54c49317faec293",
  "src/session.rs": "9cb1c85ee9e11452a980233b66c0e817d0e6309dd6d425ae90721f04cc46c19b",
  "src/shelter.rs": "d6012e72cda2502538c215e074b2ebcba396342b903d9d431cc257eb3f9e5811",
  "src/tactical.rs": "8c11bb2a3469c0a431900ff9b7613d30a89913bcb6094dc0cf29f5c61683f6a9",
  "src/time_powers.rs": "8332a3c4516496ebfb77ab9426e35ae1c94108f21dbd071b8baf9ac3c4c2215e",
  "src/timed.rs": "1aca5ca308e2fc92b8a2b144dcc12f49e14990c9e5f34ce941fc37bfb4182f45",
  "src/timing.rs": "fb7c256ececf164c1ce3bd476b997b9cd2b20aef1eaf4b22776c6f6b33efd5b8",
  "src/types.rs": "2a202da079b16b3becb6651427701ec8e40aed88bd19550854c800b842b22feb",
  "src/wire.rs": "f851e0b386db01debc0107e01be64ebef0454934673bece463ecd39d0d984841",
  "src/work_clock.rs": "8cfc3b6de931144bb738516fb95e023d89ddd5449d1cde21d3dea352f01380ab"
}
```

Exact text authority/specification/receipt anchors:

```json
{
  "/home/legolas/rook2/evidence/quiescence-evaluation-default-build-20261018/receipt.json": "45631ac24e12ce8a1ea067b84665401c00591a10e21d01157afe12ec3367daf5",
  "/home/legolas/rook2/AGENTS.md": "92da23830dd55e4073d227f7989339a4933f13a0844f2a50e49884466d12da39",
  "/home/legolas/imp-perf-mission.md": "74b8793052d559de9258f522f62afe2e89b271ac599dd5f48fe136ccd861067b",
  "/home/legolas/rook2/docs/decisions/0004-persistent-attack-planes.md": "276967f7032d1bb5fb806061e3782e064befb6e2fa8f80243d2e76cf650b0d3f",
  "/home/legolas/king-spec/spec/quiescence-tree.md": "7531628c8680387e56253c671dfd9e77ca1b04b63a767f034f2c6b34666a97d3",
  "/home/legolas/king-spec/spec/quiescence-candidates.md": "5baa58c51eebf8f6bcda855b1ae305525ce88b2344fe8124cf44331c1a1fec74",
  "/home/legolas/king-spec/spec/search-candidate-production.md": "d1e22f64f8a69783f9a88a1e5004e0493ede34bdeea103bf0ebf6e13a17e038e",
  "/home/legolas/king-spec/spec/ordinary-play-ingress.md": "772224e1bc51bfcd7a248d36511367bd52f5aeb7da6579f7d83ac175f65d3959",
  "/home/legolas/king-spec/spec/ordinary-iterations.md": "a16d33b123d67f0ae82384bd6d24dba4163685400b00f188f46f13c511fcaafb",
  "/home/legolas/king-spec/spec/history-admission.md": "d60e6b6246b47abdbb20f6b6f46bbf50a0200621721f667fc888e5ee0a9ea408",
  "/home/legolas/king-spec/spec/ordinary-session-lifecycle.md": "35dd68d3193bc3743033126f1d28494dd1d9d583d972f52ca2dde47c5967a0ec"
}
```
