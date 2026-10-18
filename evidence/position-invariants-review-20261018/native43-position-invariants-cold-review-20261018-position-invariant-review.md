# Native43 positional invariants: bounded cold review

To: Imp2 parent/coordinator
From: position_invariant_review subagent
Date: 2026-10-18 UTC

## Finding and scope

The actual board states admitted by the ordinary wire/session path, and actual
board states produced from them by normal search and protocol transitions,
support these premises at their normal evaluator/generator consumers:

- mailbox, per-color/type counts, ordered lists, and exact attack-tag planes
  describe the same occupied squares;
- each color has at most 16 pieces, at most 8 pawns, and exactly one king;
- active ordered-list squares are distinct and in 0..64, tails are NO_SQUARE,
  and no pawn occupies a promotion rank.

There is one expressly admitted exception to the king premise: the exact
constructed king-victim coordinate continuation. It retains a coherent board
with no Black king, but the session sentinel prevents that state from entering
normal evaluator/generator lookup. No production concern against these bounded
premises was found. This is a source proof with explicit ingress/transition
premises, not whole-engine qualification, a new numerical proof, or an audit of
all released requirements.

No legal ancestry is assumed. An admitted setup may attack the nonmoving king,
retain an unusual EP target, or contain promoted-type populations impossible
from a natural game. The usable bound is 15 non-kings per color, including up
to 15 of one non-pawn type, and up to 30 non-kings combined. A bound of ten
knights/bishops/rooks from a narrower diagnostic is not an ordinary-ingress
premise. Combined same-type counts can exceed a nibble; this review does not
remove the need for specified packed-material carries.

## Identity and method

Native baseline: native43, supplied build receipt
`evidence/production-activity-specialization-use-build-20261018/receipt.json`.
Its SHA-256 is `da7d3c7ffb7cc42db36838a13fdfb6ff3895f254dd71c07b808f87ee5ef0be1f`.
The receipt records source git HEAD
`7d5809fd21561f7c171e0d9339b736568a11d702` plus its recorded source snapshot;
the hash table below, rather than HEAD alone, identifies audited code.
The actual current binary file at
`target/dev-generic-pgo-use/x86_64-unknown-linux-gnu/release/rook2` was read and
hashed as `8d9dddc58d3b5dd1128bc7cedb4ee83a0df6310d33fb5f377f13a1a46ce7f79d`,
matching the receipt. Every audited source hash below matches that receipt's
`source_sha256_before` entry. The receipt states stable before/after inputs.

Released authority: `/home/legolas/king-spec`, SOURCE.yaml version `v2.5.0`,
commit `80550dd37d09293f179abd0e0c7ec06390dcfbbb` in
`https://github.com/thinktt/king-recovery`, directory `spec/package/`.
Relevant release hashes are recorded below.

This review read AGENTS.md and `/home/legolas/imp-perf-mission.md`. All shell and
Python reading/hashing/writing commands ran under `taskset -c 0-5,8-13`.
No build, test, engine execution, profiling, simulation, CPU14/15 command,
Herdr use, subagent spawning, or Imp1/Rook inspection occurred. One memo is the
only write. Requested Normal speed could not be read back from live controls.

## Admission establishes the base case

`src/bin/rook2.rs:84` constructs `Session<false>`; ordinary input is routed to
`Session::idle`, then `go_live` for an Action::Search. The ordinary executable
accepts no diagnostic JSON. Input records and idle token parsing do not expose
raw Rust board/list/count setters.

`Position::from_fen` (`src/position.rs:48`) starts with an empty mailbox,
zero counts, NO_SQUARE list tails, and empty attack planes. It parses exactly
64 board cells without duplicate writes, excludes promotion-rank pawns, counts
actual parsed piece tags, and checks exactly one king, <=8 pawns and <=16 total
pieces per color before indexing the 16-slot lists. It fills each type's list
from the actual mailbox. `recompute_derived` (`:417`) then builds identities,
starting units and attack planes from that mailbox. Counter accumulation cannot
overflow u8 during admission: even a rejected board has only 64 cells.

`Session::default` (`src/session.rs:111`), `new` (`:351`) and `setboard` (`:170`)
all use this constructor. `setboard` rewrites the textual counters to `0 1`
before admission; parsing completes before `reset_position` changes retained
state. Supported castling rights are normalized against real home pieces;
retained EP is an empty rank-three/six target with a geometrically adjacent
moving-side pawn. This normalization does not assert a behind-target pawn or
legal ancestry, consistently with released POSITION-SETUP and ordinary ingress.
`reset_position` clears old history and the king-victim sentinel before
adjudicating a newly admitted position.

## Transitions preserve the inductive premises

`remove_ordered` (`src/position.rs:204`) removes the actual matching piece,
shifts surviving slots, fills the former last slot with NO_SQUARE and decrements
the matching count. `append_ordered` (`:213`) inserts at the end of the matching
type group and increments its count. Ordinary movement changes its existing
slot. Captures remove the actual victim's type/color; promotion first removes
one pawn and then inserts one promoted piece, so even a full 16-piece side has
space at the insertion. Castling moves the admitted existing rook's slot.
Survivors retain relative order. At completed transitions, counts and lists
therefore describe exactly the resulting mailbox, and population never grows.
Promotions cannot increase pawn count and never promote to king or pawn.

`set_square` (`:225`) uses the actual old mailbox tag and next tag for every
changed square, updates identities and starting units, calls
`AttackBits::replace`, and stores the new tag. `replace`
(`src/attacks.rs:111`) toggles precisely the old XOR next tag bits at that
square; from a matching plane state this gives the next matching plane state.
All mailbox mutation in these actual Position transitions goes through this
setter. Transient list/mailbox differences inside a mutation are not exposed
to generator/evaluator callbacks.

`apply_unchecked` (`src/position.rs:269`) requires caller-admitted geometry;
it is not a standalone arbitrary-move validator. Normal production callers
supply legal-generator candidates, or tactical pseudo-candidates with valid
piece/occupancy/special geometry. Legal generation excludes destination king
victims (`src/movegen.rs:497,551`) and behind-target king victims (`:366`),
checks promotion kind/rank and castle home pieces/empty paths (`:386,452`),
and uses actual moving pieces. Tactical generation likewise excludes king
victims and limits promotion to queen (`src/tactical.rs:34`). Some tactical
children/reply probes are constructed before final own-king safety admission
(`src/quiescence.rs:331`); those children can be unsafe chess positions, but
still preserve the structural/population/king premises proved here. Structural
proof therefore does not depend on each helper state already being legal.

Joined EP specifically accepts an opposing non-king pawn/knight/bishop/rook/
queen behind an empty retained target (`movegen.rs:351`, `tactical.rs:47`).
The source, destination and behind-target square are distinct. The transition
looks up the actual victim tag at that behind square and removes its actual
list/count entry, rather than decrementing pawn count unconditionally. Both
mailbox and attack projections remove that actual tag
(`movegen.rs:144`, `attacks.rs:172`). A target on rank three or six cannot put
the surviving pawn on a promotion rank. Thus unusual non-pawn victims or the
opposite target-rank orientation do not break the bound/coherence proof.

`Node::child` (`src/evaluator.rs:38`) computes the retained non-king square
delta using that same actual behind-target victim and delegates the board
transition to `played_unchecked`. King square values are excluded before the
five-kind square table lookup. `Position::null_child` (`position.rs:348`) and
`Node::null_child` (`evaluator.rs:83`) copy all placement/count/list/attack
state; only side/EP/counter and retained age change. Neither creates/removes a
piece. Root preparation (`quiescence.rs:106`) refreshes evaluation from the
current root; it does not alter the board. Normal recursive candidates are
consumed from generated lists; remembered hints rank those inventories rather
than injecting a raw move (`ordinary.rs:615`). Output token replay validates
list membership before playing (`output.rs:113`); null status steps copy the
placement unchanged (`:74`).

## Exceptional king victim and every idle continuation category

Released ordinary ingress explicitly specifies only
`8/8/8/3Pk3/8/8/8/K7 w - e6 0 1`, coordinate `d5e6`, then immediate fatal `go`;
broader kingless continuations remain unspecified. This proof does not
manufacture a general king-removal rule from that example.

`Session::coordinate` (`session.rs:240`) tests exact text, side, retained EP,
placement and rights for this construction before normal generation.
`Position::exceptional_en_passant` (`position.rs:252`) removes the actual Black
king from its list and mailbox through the same helpers, then calls ordinary
apply with the behind square already empty. The result remains structurally
coherent, within capacity, and has no Black king. The session immediately
pushes the state/move, sets `king_victim=true`, sets no game result, and returns;
it does not call `adjudicate` on that child.

The subsequent paths do not accidentally use the missing king:

- `prepare_go` (`session.rs:430`) returns FatalKingVictim before pondering,
  parameter binding, work/clock preparation, search-history construction or
  search root preparation. Both `go` and `go_live` use it. The wire maps this
  error to a silent fatal return and ExitCode 1 (`bin/rook2.rs:56,121`), with no
  search post, selected move or game-result publication. If non-force mode
  automatically requests search after the coordinate, the same guard applies.
- Any other coordinate first fails the exact exceptional-placement test, then
  short-circuits on `king_victim` before `generate_legal` (`session.rs:261`).
  That early exact test calls only placement rendering and scalar checks.
- `adjudicate` (`:192`) itself returns None before normal generation when the
  sentinel is set. `undo`/`remove` (`:358`) truncate to copied saved predecessors,
  recompute the sentinel from the restored counts, then adjudicate. A normal
  predecessor therefore restores its coherent extant kings before lookup;
  saturating rewind cannot leave a stale false flag on the exceptional child.
- `new`/`setboard` replace retained state through the admitted constructor and
  clear the flag as described above. An invalid replacement is evaluated before
  mutation and cannot clear the flag on the old exceptional state.
- `force`, color selectors, post/easy/hard controls, scalar clock/schedule/depth/
  parameter commands, result/no-op/unknown/bk commands and quit do not perform
  board evaluator/generator lookup (`session.rs:316`). `time` reads only game
  ply and initial side. A later `go` still hits the sentinel. Search-time wire
  commands cannot install a new board/history (`wire.rs:196`).

`Session::search_history` (`session.rs:152`) and SearchHistory push/pop/reset
(`history.rs:19,60,70`) retain scalar boundary/arrival information; they never
reconstruct a Position or mutate a board. Ordinary protocol rewind restores
saved whole Positions, preserving semantic list chronology and attack planes,
rather than rerunning setup or trying to reverse moves against a missing king.

## Deliberately excluded non-board states and proof limits

`quiescence_policy::allowance` (`src/quiescence_policy.rs:51`) copies the parent
and decrements only the actual ordinary capture victim's count. This temporary
is intentionally inconsistent with its copied mailbox/lists/planes. Its only
consumer is `RootContext::material` (`evaluation.rs:94`), which reads counts
only; it does not escape as a child, retained session state, Influence input,
or normal board evaluator/generator input. The victim has an existing list
entry/count in an admitted parent and is non-king, so the decrement cannot
underflow and only tightens population bounds. Do not claim every local Rust
Position value is coherent or diagnose this count-only calculation as a board
coherence defect.

Likewise, public Rust `Position`/`Session` fields and unchecked transition APIs
allow a direct caller to construct inconsistent states. `recompute_derived`
rebuilds hashes/starting units/planes, not counts/lists, and is not a validator
or arbitrary-field repair mechanism. Development diagnostics and unit tests
can deliberately change fields. The production binary does not expose those
assignments to ordinary wire input. No finding here is based on such a
helper-only state or on a diagnostic domain assumed to be production ingress.

This memo establishes prerequisites only for this ordinary ingress/produced
state boundary. It does not establish numeric extrema for individual terms,
whole-engine correctness, safety of arbitrary public Rust calls, or behavior
of unspecified kingless command sequences.

## Audited native source SHA-256

All entries were read from the current filesystem and matched native43 receipt
source hashes exactly.

| Source | SHA-256 |
| --- | --- |
| `src/position.rs` | `749f9fa1e90684c4df670c115c3c7f7dbdb196cf62b5eb267900ba217143ce3a` |
| `src/session.rs` | `9cb1c85ee9e11452a980233b66c0e817d0e6309dd6d425ae90721f04cc46c19b` |
| `src/evaluator.rs` | `2b638e19566a69899e46cf6bf780271f07a9ac6d80cf1a3d51538b21a6558146` |
| `src/movegen.rs` | `9e645384baf5177697c5125df2e15db70eefac440ed63289435adddf6a514617` |
| `src/tactical.rs` | `8c11bb2a3469c0a431900ff9b7613d30a89913bcb6094dc0cf29f5c61683f6a9` |
| `src/attacks.rs` | `9d44681cf9098548a32ae06463bdb4e769c4e20eff9ac175ba725afae6a0ac50` |
| `src/history.rs` | `f6b2a5073307d655e33e774900c9fea26f4bdfefbdd2cd9848ff0758c4b34fde` |
| `src/quiescence_policy.rs` | `07ed6db1af2d7fc21f093aa619f5a931aa32d594f4c1b435968ad95691b8bda4` |
| `src/evaluation.rs` | `16f26f211a09ab3aa85045c58542f4b841fd6520381214db62bed4f6363b9b3c` |
| `src/output.rs` | `180adf6062883c839a17ffa038ef30c6dd236661d94bdd61086c11c795b46247` |
| `src/bin/rook2.rs` | `26849c997a5c564076dc5c6703dcdce783e900b0c221d7938f540664edd1a3b8` |
| `src/ordinary.rs` | `446b518a5824a8a60b65666d1b841d959ab2964c995739a2bc44d27bd5a9c442` |
| `src/quiescence.rs` | `dddd6a260805a7a53ee61ceb74141cb52f9a3fdc899f2350412ffa86be439e33` |
| `src/timed.rs` | `1aca5ca308e2fc92b8a2b144dcc12f49e14990c9e5f34ce941fc37bfb4182f45` |
| `src/engine.rs` | `2e3105e7a7802c4061c0d0cd0ddc4d4629a2c362297fb1f4e18ddc7e7d566e08` |
| `src/wire.rs` | `f851e0b386db01debc0107e01be64ebef0454934673bece463ecd39d0d984841` |
| `src/first_iteration.rs` | `713830b62783a81033e1355687534783647b243c51e10f829546d080ce157722` |
| `src/ordinary_policy.rs` | `a79ec111e2d34bb9e4a3c2a7953c5b2a82b011016982fd2b63d6769da3036bf6` |

## Released reference SHA-256

| Reference under `/home/legolas/king-spec` | SHA-256 |
| --- | --- |
| `SOURCE.yaml` | `8e00449a18c99eb016224d3dbb4f91a974d00b619099289526bb9b82f67d4fad` |
| `MANIFEST.sha256` | `b8ce317fa5577c28bc35f0cbadad61cd984bdd4824c59f2c37d4ebef55335e0d` |
| `spec/position-setup.md` | `93d94c7fdf8812b8a3eaabf4b66d796912bf53a994d406a107a6ca8e808cac3b` |
| `spec/ordinary-play-ingress.md` | `772224e1bc51bfcd7a248d36511367bd52f5aeb7da6579f7d83ac175f65d3959` |
| `spec/ordinary-xboard-wire.md` | `5292029af4fca1299e8600194b197720d625cb5231d0672f804e788d0b9961f5` |
| `spec/ordinary-session-lifecycle.md` | `35dd68d3193bc3743033126f1d28494dd1d9d583d972f52ca2dde47c5967a0ec` |
| `spec/move-sequence.md` | `7de9e266c728e1e52300b80b493a1413343eeed5f6e0f5bd9a1213244f8c3d2f` |
