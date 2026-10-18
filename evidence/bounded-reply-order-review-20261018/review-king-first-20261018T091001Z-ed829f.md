Checked king-first threshold generation is sound for the two audited production consumers, provided it is confined to the capped helper and retains a complete legal inventory whenever the result is0 or1. I recommend one small reversible native prototype for that proposition. No implementation, build, test, engine, profiler or timing run was performed for this audit; only source/spec/evidence reads and this report write ran on housekeeping CPUs0-5,8-13. Normal speed was requested; live speed control/readback is unavailable. Parent owns selection.

The audited files relevant to ownership and consumers—movegen, quiescence, session, Position, AttackBits, engine charging and timed polls—are byte-identical to their old8d profile source anchors. Evaluation files elsewhere in current root differ; the current complete43-file source identity is retained below. All searches covered every current src/**/*.rs file, including bin and diagnostic module source. No Imp1/private source was inspected.

The only production callers are Q at src/quiescence.rs:338 and Session::adjudicate at src/session.rs:198. The other three identifier occurrences are the helper definition and two native test calls; no public diagnostic calls this helper directly. Public full legal generation has its own generate_legal -> generate_bounded::<MOVE_CAPACITY> path. Its generated order remains observable and must remain unchanged.

| Result | Q consumer | Session consumer | Required capped-list contract |
|---|---|---|---|
|0|Sets complete_replies and enters checked child with the empty list; child can return mate without regenerating|Classifies no successors as checkmate or stalemate before other terminal reasons|Exactly empty, with count0|
|1|Sets complete_replies and reuses the sole legal move at the checked child, subject to its earlier terminal gates|Only observes nonempty, then checks later terminal reasons|The exact sole move, including its kind; complete list, count1|
|2 (means >1)|Pops trial history and continues/rejects this parent candidate before recursion; list moves are discarded|Only observes nonempty|Any two distinct legal moves proving >1; order/particular witnesses are unobserved|

Session imposes no extra enumeration order or exact count requirement. It ignores the returned usize and only reads legal.len==0. Its precedence remains no successors, halfmove>99, repetition, material units<=1, then move-list capacity. reset_position/accept_move/undo-remove all reach this same predicate; the exceptional king-victim branch returns before querying missing-king geometry. No other session state, selected move or output depends on these witness moves.

Q lifetime and scratch proof: the reply probe is after the checking/nonforced/nonrecapture gate and a produced-child repetition check. It has already constructed the child and pushed its history; the helper changes neither. On >1, Q pops and continues. On0/1, it sets complete_replies, pops, retains the same prepared child and later passes that Boolean to visit_q. Every parent candidate resets complete_replies=false. visit_q reuses candidates[child_ply] only when checked && replies_available; otherwise a fresh legal/tactical producer clears len and writes its new valid prefix. Generation and ordering/selection read only len or as_slice/moves[..count]. Thus changed >1 witnesses in scratch, or stale bytes beyond len, cannot feed a later search, preference, PV or cache. Existing exact0/1 moves preserve recursive order by induction. Count0 can return before any ordering, count1 cannot have a relative-order change.

The released requirements support this private threshold specialization. SEARCH-QUIESCENCE-TREE step4 (quiescence-tree.md:153-157) explicitly says only the greater-than-one reply predicate matters. Its production/early-mate section (:101-117) requires ordinary ordered evasions when actually searched and allows reuse of available replies. SEARCH-ORDINARY-CANDIDATE-PRODUCTION (:101-179) exposes complete base order, prefixes, generated and ordered inventories; this proposal must not reorder that producer. Joined ingress (ordinary-play-ingress.md:49-60,289-305) additionally admits an opposing non-pawn/non-king EP victim behind the target, and preserves terminal precedence. Native movegen has witnesses where joined EP removes a non-pawn checker and blocks another route. Consequently neither standard-chess-only domain narrowing nor a double-check king-only shortcut is justified.

The small proposed implementation, not made here, is limited to movegen.rs:

1. Keep list.clear, king/checker discovery, existing legal EP prefix and castling path exactly where they are. Keep the existing early return if EP already proves two. Castling already returns immediately when checked.
2. Construct the same immutable GenerationSafety. Define king_early as LIMIT==2 && checkers.len!=0. Only on this path, call existing pieces::<LIMIT>(..., PieceKind::King), then return if len reaches2.
3. Continue the existing pawns/pawn-prefix and Knight/Bishop/Rook/Queen sequence. Skip the final King iteration only if king_early already visited it. If fewer than2 replies exist, enumerate every remaining original candidate exactly once. Do not replace any legality filter or move transition.
4. Leave public generate_legal, its ordering contract and the unchecked capped path semantically unchanged. The LIMIT==2 specialization should compile out of the complete generator; verify actual emitted code instead of assuming unrelated native scope stayed byte-identical.

This tries king evasions before the bulk pawn/nonking work, while retaining EP first. It is intentionally not a global king-first search order. No new Position/Node/Retained/cache field, state copy, allocation, attack representation or charged-work site is needed. GenerationSafety::accepts for a king always reaches the existing full projected geometric king-safety test. It cannot accept a king move merely through the pinned/non-check shortcuts. If two king evasions exist, remaining bulk generation is avoided; if zero/one king evasion exists, the unchanged other producers still run. A unique nonking, king, promotion or joined-EP reply remains complete; promotion's multiple legal type choices correctly prove >1 rather than being collapsed to one.

Source proof obligations are explicit: king visited exactly once; EP preserved; every original candidate retained on below2 paths; no >=2 result leaks into a searched list; public full-generation order unchanged; and count saturation exactlymin(2,N). Single-check pawn prefix acts only on its pawn segment. On the capped checked path a preceding king item cannot change a0/1 complete list, and if the segment combines with that king to reach2 the witnesses are discarded. On the full path no king item moves. Checked positions with zero king evasions must still search pawn blocks, captures, promotion choices and joined EP. Do not turn double check into a new king-only rule.

Semantic work and state are unaffected if those obligations hold. The helper and its callees read &Position/immutable tables and write only MoveList/local summaries. Position::attack_view returns a Copy AttackBits value; projected takes it by value. There is no mutable interior state, RNG, TT, pawn cache, history learning, retained evaluation, evaluator call, relation-query charge, search-unit charge, host callback or timing sample in this helper. FORCE_PROJECTION is cfg(test)-only and only reads its selected comparison mode here. Q's reply_probes increment is at the unchanged call site and reused_reply_lists remains governed by the same threshold. Actual projected legality-check counts and hardware memory/cache accesses may change; they are the optimization hypothesis, not semantic counters.

Interruption qualification needs care. Search::charge_node services work_poll at every4096th entered node (engine.rs:131-141). Identical threshold decisions and0/1 lists preserve child-entry order and charged node/relation counts, hence deterministic queued-command work-poll boundaries and semantic cache access sequences. No poll moves inside generation. This does not promise the same host-wall-time availability: a faster/slower helper can change whether an externally arriving line is available at a poll or change real-clock stopping/publication intervals. ordinary-session-lifecycle.md:171-177 explicitly binds consumption to available lines at polls and does not promise universal equality from wall-arrival time alone. Work-clock strict replay and prequeued interruption tests are therefore the appropriate deterministic comparison; unchanged physical elapsed time is not required.

Existing native checks already express the right private contract. capped_reply_predicate_matches_complete_inventories_and_reuses_small_sets (movegen.rs:846) walks six setup families through depth2, asserting bounded==min(2,full) and exact lists only below2. compare_projection (:703) also checks those conditions against full mailbox-projection admission, with ordered full-list equality. generation_summary_matches_projection_on_joined_witnesses (:726) covers EP removing non-pawn pieces, pins, promotion, check, castling, mate and king geometry; generation_summary_matches_projection_on_constructed_setups (:770) covers10000 admitted constructed placements, including adjacent kings, already-attacked nonmoving kings and promoted material. These existing tests must not be weakened to force an arbitrary >1 capped order. Full generation order tests/perft remain unchanged. Q mate/evasion-boundary, explicit-stop restoration, diagnostic specialization, released PV/work tests, tactical shared-evasion order and session lifecycle/host-abort tests provide adjacent regression coverage. They were inspected, not rerun.

Meaningful additions for a selected prototype: explicit checked cases for0,1,>=2 king replies and for no king reply but other legal evasions; retain joined-double-check EP witness coverage. Simple fixed king cases include checkmate `7k/6Q1/5K2/8/8/8/8/8 b - - 0 1`, sole king reply `7k/7R/6K1/8/8/8/8/8 b - - 0 1` (h8g8), and at least two king replies with earlier rejected nonking candidates `nnn4k/ppp5/8/8/8/8/8/K6R b - - 0 1`. Confirm the latter fixtures against the complete mailbox projection, not the new threshold implementation. Add a case whose two easier pawn replies precede expensive king failures so the cost downside is visible rather than assuming king-first always wins. No fixture is a workload frequency estimate.

Cheap falsification and downstream validation: first run the existing native bounded-versus-full/projection checks over those broad domains in an isolated source copy, keeping full order assertions intact. Any changed count or0/1 witness disproves the candidate immediately. Then original strict54 replays, independent complete-stream/exit/work comparison and8 interruption fixtures/24 searches. Bind exact build/source snapshots and actual process terminals. Check complete-generator code/frame versus identical control because the generic body is shared. If semantic checks pass, parent may select a balanced generic whole-engine CPU pilot; no such run is authorized/performed by this report. A scoped diagnostic census could separately record checked bounded calls, exit stage, and tested king/nonking candidates to establish whether two king replies often avoid bulk work. Current evidence supplies no such denominator. Reordering may lose when two pawn/other replies already suffice, when king projections are expensive and fail, or when code layout grows. No speedup is predicted.

Old8d profile motivation only: frozen artifact8d9dddc58d3b5dd1128bc7cedb4ee83a0df6310d33fb5f377f13a1a46ce7f79d has whole-lifetime11603840314 simulated Ir for profile01. functions.stdout includes a source-labelled row544450783 (4.69%) for src/movegen.rs:legal_replies_up_to_two. This is not an isolated total for all instructions of that helper: other source rows include its inlined code. I do not add overlapping source/function/line views, infer function entry counts from IR counters, or convert that row into a timing/savings bound. No fresh Callgrind/native measurement was run. The profile merely makes the private threshold path worth considering; the frequency of early king success remains unknown.

Identifier occurrence audit:
- `src/movegen.rs:632` — `pub(crate) fn legal_replies_up_to_two(position: &Position, list: &mut MoveList) -> usize {`
- `src/movegen.rs:707` — `legal_replies_up_to_two(position, &mut capped);`
- `src/movegen.rs:854` — `legal_replies_up_to_two(position, &mut capped),`
- `src/quiescence.rs:338` — `let replies = movegen::legal_replies_up_to_two(`
- `src/session.rs:198` — `movegen::legal_replies_up_to_two(&p, &mut legal);`

Exact source identity (current audited43; relative to /home/legolas/rook2):

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
  "src/evaluator.rs": "248e8e782110bf596fc82bbf2bbf67e13492de1386a52792c6123ac076baf6bb",
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
  "src/quiescence.rs": "dddd6a260805a7a53ee61ceb74141cb52f9a3fdc899f2350412ffa86be439e33",
  "src/quiescence_policy.rs": "07ed6db1af2d7fc21f093aa619f5a931aa32d594f4c1b435968ad95691b8bda4",
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

Exact specification/evidence/authority anchors:

```json
{
  "/home/legolas/rook2/AGENTS.md": "92da23830dd55e4073d227f7989339a4933f13a0844f2a50e49884466d12da39",
  "/home/legolas/imp-perf-mission.md": "74b8793052d559de9258f522f62afe2e89b271ac599dd5f48fe136ccd861067b",
  "/home/legolas/king-spec/spec/search-candidate-production.md": "d1e22f64f8a69783f9a88a1e5004e0493ede34bdeea103bf0ebf6e13a17e038e",
  "/home/legolas/king-spec/spec/quiescence-tree.md": "7531628c8680387e56253c671dfd9e77ca1b04b63a767f034f2c6b34666a97d3",
  "/home/legolas/king-spec/spec/ordinary-play-ingress.md": "772224e1bc51bfcd7a248d36511367bd52f5aeb7da6579f7d83ac175f65d3959",
  "/home/legolas/king-spec/spec/ordinary-session-lifecycle.md": "35dd68d3193bc3743033126f1d28494dd1d9d583d972f52ca2dde47c5967a0ec",
  "/home/legolas/king-spec/spec/ordinary-xboard-wire.md": "5292029af4fca1299e8600194b197720d625cb5231d0672f804e788d0b9961f5",
  "/home/legolas/king-spec/spec/quiescence-candidates.md": "5baa58c51eebf8f6bcda855b1ae305525ce88b2344fe8124cf44331c1a1fec74",
  "/home/legolas/rook2/evidence/callgrind-activity-specialization-20261018/README.md": "9b8feb4d155bd1f5551a7b3ce767a6d8f5c46edff5c4067d9081874e55cb2b19",
  "/home/legolas/rook2/evidence/callgrind-activity-specialization-20261018/provenance.json": "9990111619222e74aee3e5d944cd08d7f3a6182eb0ef7c3c1c04d742f52e281a",
  "/home/legolas/rook2/evidence/callgrind-activity-specialization-20261018/verification.json": "5a4d1a21828cef9d1491b80ce1b7aa7379e43534562606e274c61d9806d8a24c",
  "/home/legolas/rook2/evidence/callgrind-activity-specialization-20261018/tool-terminal.json": "1bfc9e4b31934996c7c6e36af90093650eac84fd043d13e907f15764f3c02399",
  "/home/legolas/rook2/evidence/callgrind-activity-specialization-20261018/profile-01.callgrind": "f512b4dc32493ee906694e2593fabaa309f7a0bafba300f9a24c5be341842495",
  "/home/legolas/rook2/evidence/callgrind-activity-specialization-20261018/functions.stdout": "608b9e0d094beeaaebf8e07184d7f7d4ff000e097184d1ed4503f8709ca72fe4",
  "/home/legolas/rook2/evidence/callgrind-activity-specialization-20261018/movegen-lines.stdout": "5b351f4593bffc09749da3620233a093b33e87fb3626e24d1bca524c59899a45",
  "/home/legolas/rook2/evidence/production-activity-specialization-use-build-20261018/receipt.json": "da7d3c7ffb7cc42db36838a13fdfb6ff3895f254dd71c07b808f87ee5ef0be1f"
}
```
