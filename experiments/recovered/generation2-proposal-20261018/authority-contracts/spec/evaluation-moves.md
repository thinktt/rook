# EVAL-MOVE-SEQUENCE — move-produced state through full/fast evaluation

Working composition contract. Establish a position and root context, perform
a full evaluation, then apply moves and evaluate their resulting positions.
This joins setup, chronological piece order, counters, incremental square
balance and retained evaluation information. Evaluation kind remains an
explicit diagnostic choice, not a search-admission rule.

## Diagnostic input

`evaluation.moveSequence` accepts exactly `fen`, `percentages`, `averageDepth`,
`cfd`, `sop` and `steps`.

The six-field FEN has the domain of
[POSITION-SETUP-MOVE-SEQUENCE](position-setup.md), including reversible count
0..255 and fullmove number 1..1000000. Establish the initial position using
POSITION-SETUP normalization and ordering. Root ownership is its side to move.
Percentages, averageDepth, cfd and sop retain the domains of
[EVAL-RETAINED-SEQUENCE](retained-evaluation.md).

`steps` is an ordered list of 1..256 objects, each containing exactly:

- `move`: a legal coordinate move with any required promotion suffix, or
  JSON `null` for a diagnostic null move;
- `kind`: `full` or `fast`, choosing evaluation after that transition.

Ordinary moves must be legal from the current normalized, history-preserved
state. The null diagnostic is limited to positions where neither king is in
check. This matches the non-check context of a legal null-search position;
it does not characterize invalid-position null calls. Null is a search
diagnostic transition, not a legal move in a played game.

Missing, extra, malformed or out-of-domain inputs are errors. No piece order,
pawn order, per-step reversible count, phase, identity, inherited score,
evaluation age or square subtotal is supplied by the caller.

## Initialization and fixed root context

Produce setup order and normalized rights/target, keeping the supplied FEN
reversible count. Build the root context and initially cleared pawn retention
as in EVAL-RETAINED-SEQUENCE. Perform a full evaluation of this initial state
and publish its result before processing the first step.

The resulting positional subtotal and pawn-progress value are the initial
retained pair. Evaluation age starts at zero after that full evaluation.
Root material values, ownership, phase-dependent coefficients, square values,
draw preference and variation range remain fixed throughout this request.
Moves do not establish new root contexts.

## Ordinary move transition

Apply [POSITION-MOVE-SEQUENCE](move-sequence.md) to current state. Preserve
its chronology-sensitive piece order, captured-piece removal, promotion
append order, castling-rook movement, rights/target changes, placement
fingerprints, phase and modulo-256 reversible counter behavior.

The child inherits the parent's positional subtotal and pawn-progress value
unchanged. Neither capture nor pawn movement clears that pair. Its evaluation
age is `(parent evaluationAge + 1) modulo 256`, independently of whether the
reversible counter resets. This diagnostic continues along one child path;
sibling and backtracking behavior are separate.

The child's square balance must equal the current-position sum under the
unchanged root square-value context, with the current-phase king term and
pawn-only rule of [EVAL-FRESH-SUBTOTAL](evaluation-subtotal.md). Captures,
promotions, en passant and both king/rook castling movements all participate.
An implementation may maintain this incrementally or recompute the identical
sum; the specification does not require a particular storage technique.

## Null transition

Keep placement, piece order, castling rights, phase, placement fingerprints,
square contribution and the retained evaluation pair unchanged. Exchange the
side to move, clear the en-passant target and increment both reversible count
and evaluation age modulo 256. The null transition does not itself trigger a
full evaluation or alter pawn-cache selection.

## Evaluation and output

Before evaluating the new state, expose its inherited pair and age. Then
perform the requested full or fast evaluation using EVAL-RETAINED-SEQUENCE.
Full evaluation refreshes the pair and resets age to zero; fast evaluation
preserves the inherited pair and age. Current state produces pawn chronology,
reversible count, phase, check context and placement identity, rather than
accepting these as independent per-evaluation values.

Pawn retention persists across evaluations in this request. A move does not
itself select a pawn entry; a later full evaluation does. Fast evaluations
continue using the previously produced pair even after pawn or material
changes. Search's decision about whether this is an appropriate fast call
is a separate behavior.

Return `{results: [...]}`, containing the initial evaluation and one result
per step. Each result has the complete EVAL-RETAINED-SEQUENCE shape, plus:

- `state`: the POSITION-MOVE-SEQUENCE result for this position, including
  normalized/current rights, target, reversible count, chronological piece
  order, phase and fingerprints;
- `inherited`: `null` for the initial result; otherwise
  `{positionalSubtotal, pawnProgress, evaluationAge}` immediately after the
  transition and before its selected evaluation.

The `retained` member is observed after evaluation. In particular, inherited
age can be nonzero while retained age is zero after a full evaluation.
`relationQueries` counts that evaluation's relation charges, not a complete
search or elapsed-clock budget. The sequence does not stop automatically at
repetition, reversible-count draw thresholds or evaluation-age wraparound.
Those are search/terminal admission behaviors, not this diagnostic's policy.

Each request starts independently. No retained state crosses requests.

## Remaining connections

This establishes one forward path from normalized setup through actual move
state into evaluation. [EVAL-QUIESCENCE-ENTRY](quiescence-entry.md) separately
connects non-check quiescence full/fast selection. This contract does not define null
eligibility/reductions, undo/backtracking, sibling cache effects, repetition
admission, root reinitialization between searches or session clock scheduling.
Passing it is stronger than supplying per-position pawn order and retained
scores, but is not proof of a complete recursive search or played game.
