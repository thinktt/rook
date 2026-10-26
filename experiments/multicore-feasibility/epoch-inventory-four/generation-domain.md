# Eager ordinary inventory: bounded generation domain

Source-only challenge, 2026-10-26. Source pins below refer to the frozen
`/home/legolas/rook2-experiments/workspaces/epoch-colors-20261026-01/src/`
snapshot, before inventory4 edits. No engine, build, test or native experiment
was executed for this argument.

**Conclusion:** eager `generate_legal` is total on private coherent ordinary
ancestry with exactly one king per color. The opposite king need not be safe.
It can safely run even when canonical control flow later skips generation.
No additional attack/population/capacity restriction or production panic
recovery is needed. This conclusion does not admit arbitrary public `Position`
values merely because their king counts are one.

## Admission and maintained state

The private coherence permission is established by `Position::validate`, not
inferred from a supplied Influence: `engine.rs:195-205`. Validation checks total
population at most 16 per color, at most 8 pawns, exactly one king, in-board unique
list entries, mailbox/list agreement, canonical tag-plane agreement and rule
flags (`position.rs:431-479`). Those facts make every `piece_squares` group slice
valid (`position.rs:181-198`) and every nonempty mailbox piece a valid code;
the possible `Piece::kind` panic is therefore excluded (`types.rs:94-121`).

Native descendants preserve these facts: captures remove an existing ordered
entry; promotions remove the pawn before appending its replacement, so the
append has at most 15 entries; castling relocates an existing rook; each mailbox
replacement also updates maintained attack planes (`position.rs:201-247,
274-351`). Native generation excludes king victims in pawn, piece and EP
candidates (`movegen.rs:371-375,502-505,557-560`), preserving both king entries.
Null descendants change side/EP/clock only (`position.rs:354-359`). Thus
generation reads the maintained `attack_view` (`position.rs:170-173`) rather
than rebuilding or mutating Position. Generation itself never calls the
Position mutators or their locate/capacity assertions.

The producer rejects unavailable coherence before publication and checks king
counts before generation's king indexing. On admitted coherent state, both
king slices already contain one in-board square (`movegen.rs:645-650`): the
count check is defensive, with failure unreachable under this private ancestry
invariant. An extra `in_check(position, position.side.opponent())` rejection is
unnecessary. Neither the current-side nor opposite king must initially be safe
for totality: checker discovery and projection query the moving king, their
geometric operations are bounded on coherent placement, and no generator path
creates a child or executes Position's king-victim assertion. The native king
victim exclusions above remain unconditional. At eventual canonical demand,
the exact same immutable Position goes to the exact same unchanged producer;
opposite-king safety is not an additional list-equivalence condition.

## Capacity, indices and finite control flow

`generate_legal` fixes `LIMIT = MOVE_CAPACITY = 512` and clears the initialized
output's length before producing (`movegen.rs:10-43,634-646`). Maintain
`len < LIMIT` before each possible push. Every push site returns at the limit
before another push: EP `380-387`, castles `448-455`, promotions **inside** their
four-choice loop `474-477`, pawn destinations/double steps `507-530`, and pieces
`563-570`; stage boundaries also check the limit (`652-673,698-700`). Therefore
the 512th push is valid and no 513th push reaches the capacity assertion. This
uses the existing bounded producer, not a new theorem about the maximum legal
chess inventory; existing truncation semantics remain identical.

All generated endpoints come from in-board source lists, checked `offset`
results or the fixed castle squares (`types.rs:68-76`; `movegen.rs:359-457,
499-575`). The sole generation unwrap is a double pawn step from rank 1 for
White or rank 6 for Black, reaching rank 3 or rank 4 (`520-521`). Fixed `pieces`
callers pass only N/B/R/Q/K, excluding its Pawn `unreachable!` arm
(`545-550,664-665,688-698`). Promotion kinds are exactly Q/R/B/N, excluding
`Move::new`'s invalid-promotion panic; generated move tags are valid
(`movegen.rs:53-58,467-487`; `types.rs:173-202`). Nonzero direction offsets and
fixed distinct castle endpoints satisfy its debug endpoint assertion.

Single-check prefix permutation has
`start <= next <= cursor < end <= len <= 512`. Its `copy_within` destination
ends at `cursor + 1 <= end`, and incremented `next` remains at most `end`
(`movegen.rs:581-629,670-684`). Checker indexing is conditional on exactly one
checker. Checker squares differ from the king because all source masks exclude
the queried square; aligned king-to-checker walks have a nonzero step and end
within seven squares (`280-298,608-618`). Other loops are over bounded lists,
fixed directions or rays terminated by board boundaries.

## Attack projection and remaining assertions

`ordered_attackers::<2>` emits at most two entries: each emit that fills the
array immediately returns from its caller; its LIMIT debug assertion is met
(`attacks.rs:237-297`). Its knight table has at most 8 in-board sources, built
from checked offsets (`geometry.rs:60-89`). Mask construction likewise uses
only checked offsets (`attacks.rs:21-66`). All king/move mask indices and
bit shifts therefore use squares 0..63.

For both `attacked` and `ordered_attackers`, any matching slider/king bit is
also an occupied bit. The nonempty matching-ray guard consequently implies
nonzero blockers, satisfying debug assertions and making the decreasing-ray
`63 - leading_zeros` shifts valid (`attacks.rs:194-229,243-295`). Pin scans
explicitly reject empty blocker/remainder sets (`161-188`). Pawn bit clearing
subtracts one only while nonzero (`261-267`).

Projection uses only generated valid tags and endpoints. EP first checks an
in-board target and obtains the victim with a successful backward offset;
therefore its later White `to-8` / Black `to+8` cannot overflow or leave the
board (`movegen.rs:359-385`; `attacks.rs:300-318`). Castles use the fixed home
rank, confirmed rook and empty transit/destination geometry, so rook offsets
also stay within 0..63 (`movegen.rs:403-452`; `attacks.rs:320-329`). Projection
mutates only a copied `AttackBits`, with canonical piece replacements
(`attacks.rs:138-144,300-333`), and cannot hit Position list mutation assertions.

No unresolved fatal access was found within this admitted producer. Its output
remains speculative physical work until original demand; this proof neither
moves logical accounting nor authorizes broader public/FRESH/root/Q admission.
If unavailable settlement needs a direct control, a conditional test-only hook
may force it before production. Such a control checks fallback/receipt behavior;
it is not evidence of a coherent production position failing the king guard.
