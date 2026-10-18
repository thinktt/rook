# Clock setup, synchronization and allowance composition

Status: bounded pre-search sequence contract. This joins protocol commands,
retained clock state, personality settings and the allowance calculation.
This diagnostic does not cover active search or pondering. Ordinary active
measurement is specified by the linked session contract below.

## TC-SESSION-SETUP — effective allowance after an idle sequence

Relevant abstract state consists of the effective time schedule, game half-move
count, the initial position's side to move, a selected clock color, the signed
clock adjustment in centiseconds, search optimism and pondering selection.
The initial side and the **current** side to move are different facts; playing
a move changes the latter but does not change the former.

For these forced, non-searching setup sequences:

- `new` establishes the standard starting position, initial side White,
  selected clock color Black, zero game half-move count, and zero adjustment.
  It retains an already selected time schedule and personality parameters.
- `setboard` establishes a new initial position and zero game half-move count
  and adjustment. It retains the time schedule. The supplied FEN's full-move
  and half-move numbers do not set the allowance's game half-move count.
- Replayed moves increase the game half-move count. `undo` and `remove` rewind
  one and two plies respectively without refunding or clearing the adjustment.
- `white` selects Black as the clock color; `black` selects White. These are
  the observed legacy command conventions, not instructions to flip the board
  or change its side to move. `force` keeps setup moves from starting searches.
- `easy` and `hard` select the normal and pondering allowance branches.
  `cm_parm sop=...` supplies optimism; `cm_parm default` restores optimism to
  100 without clearing the adjustment.

The ordinary command lifetimes and active-search measurement connection are
specified in [ordinary session/reset lifecycle](ordinary-session-lifecycle.md). This
diagnostic remains a bounded idle-setup observation, not a new-search reset.

### Schedule selection

For the valid `level` forms, each triple gives a move count, a base
time in minutes or `minutes:seconds`, and a per-move increment in seconds.
The effective schedule is defined by TC-SCHEDULE. A zero move count selects a
999-move repeating stage. `level` replaces the effective schedule but does
**not** recompute the adjustment previously established by `time`.
The production grammar and bounded numeric domain, including up to ten stages,
are defined by [KING-XBOARD-ORDINARY](ordinary-xboard-wire.md#clock-grammar-and-numeric-admission).
This component's smaller fixture domain does not reduce that production
requirement. Malformed text, excessive stages and out-of-profile arithmetic
remain excluded; examples do not define them by extrapolation.

### Synchronizing a remaining-time message

Let `p` be the game half-move count and let `b` equal 1 when the selected clock
color matches the **initial** side to move, otherwise 0. Define

`n = floor((p+b)/2)`.

For an inactive measurement, `time r` establishes

`adjustmentCs = 100 S(n) - r`.

Here `r` is the signed remaining-time value in centiseconds. Negative values
are accepted, not ignored or clamped to zero. The current fixtures remain
within the signed integer range throughout the calculation; wrapped-overflow
cases and numeric text outside ordinary decimal integers still need testing.
A later `time` replaces the effective adjustment using the then-current
schedule and move index; it is not an incremental subtraction from the prior
remaining-time message.

Use the resulting adjustment, game half-move count, optimism and pondering
selection with TC-ALLOWANCE to obtain the next normal search's average and
maximum allowances. Its own move index is `floor(p/2)`, not the synchronization
index `n`.

### Distinguishing examples

With the initial five-minute schedule, `time 1000` establishes adjustment
29000. Replacing the schedule with ten minutes afterwards leaves 29000 in
place, giving the allocator 310 seconds relative to its schedule. Reversing
those two commands establishes adjustment 59000, leaving ten seconds. These
sequences are intentionally not equivalent.

With a 40-move, five-minute, two-second-increment schedule, after one move
from the standard start, `white; time 30000` establishes adjustment zero;
`black; time 30000` establishes adjustment 200. After two moves both use the
same schedule index. Starting from a Black-to-move initial position reverses
the odd-ply selection. This is why current side to move cannot replace initial
side in the synchronization rule.

## Diagnostic observation and coverage limits

`session.timeSetup` receives ordered setup commands. After them, observe the
effective schedule, game half-move count, adjustment and allowances that the
next normal search would use, before it consumes search time. The adapter may
provide this observation without executing the search. Output is semantic;
no internal representation is prescribed.

The fixtures in `clock-session-setup-v1.json` use valid short histories,
at most two stages, controlled forced setup and no previous searches. They
cover ordering, resets, signed remaining time, increments, odd/even plies,
both initial sides, rewind, optimism and pondering selection. They do not
prove active-measurement synchronization, search-to-search work-clock reset,
arbitrary malformed commands or wraparound behavior. Those remain explicit
requirements to characterize, not assumptions about a fresh process.
