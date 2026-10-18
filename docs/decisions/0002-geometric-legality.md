# Generation-local geometric king safety

Date: 2026-10-18. Owner: Imp2. Status: adopt the combined local-summary/evasion variant after balanced CPU comparison.

The full mailbox projection remains the admission oracle. The Callgrind
profile-01 diagnostic attributes roughly one-third of simulated instructions to
geometric attack finding, including uses outside candidate admission. That is a
reason to investigate reuse, not a claim that one-third can be removed.
A single-case native CPU pilot found no benefit for direct piece-code matching
alone and a provisional4.5% lower median for precomputed attack rays/leaps.

## Alternatives and ownership

The experiment compares the unchanged ordinary baseline, precomputed geometric
attack tables, an unchecked-node pin summary, and that summary plus a necessary
check-evasion screen. All use the same Position/Node layout, copied-child
restoration, search policy, logical charges and retained state ownership.
Each summary belongs to one immutable original position in one generation call.
It is never cached by fingerprint or reused for a played child.

A persistent board/occupancy representation could also reduce attack work, but
would add transition/restoration and duplicated-state maintenance. The local
summary is a smaller experiment with a direct differential oracle. Representation
and restoration alternatives remain open until whole-pipeline evidence selects
them. No production layout winner follows from isolated attack costs.

## Unchecked-node sufficient condition

After normal candidate geometry, destination admission and king-capture rejection,
only ordinary moves and promotions can use the shortcut. The moving king stays
fixed, the source becomes empty, and the destination becomes/remains occupied by
an own piece. The original king must be geometrically safe. Vacating the source
can expose a surviving enemy slider only when that source was the sole occupied
blocker between king and matching enemy slider. Other enemy pieces cannot acquire
a new attack on a stationary king through this change.

Scan each original king ray. Mark a source only if its first occupied square is
own and its next occupied square is a matching enemy bishop/rook/queen. An
intervening piece stops the scan. Geometric enemy attacks still count if the
attacker is pinned to its own king. A marked source falls back to projection;
it is not rejected, since moving along the pin ray or capturing the pinner may
be legal. An unmarked eligible source can be admitted without projection.

King moves, castling and EP retain full projection. EP can remove another square,
including a non-pawn on unusual admitted geometry, defeating the proof. The
summary assumes nothing about safety of the nonmoving king or legal history.

## Checked-node necessary condition

Checked nodes do not construct pins. For a nonking ordinary move or promotion,
a lone geometric checker must be captured at its square or have its current
slider ray blocked. Destinations outside those squares can be rejected before
projection. With two existing checking routes, one destination cannot resolve
both: current geometric routes cannot share a blocked ray square, and a checker's
occupied square cannot already lie between another slider and the king.

This is only a rejection screen. Admitted destinations still use full projection
to detect new source exposure. EP bypasses the screen; the joined double-check
EP evasion can remove one checker and block another. King moves keep projection.

## Evidence and critique

The independent advisor reviewed the unchecked geometric premise and emphasized
explicit ordinary/promotion eligibility and the checked quiescence caller's zero
opportunity for unchecked reuse. Imp2 incorporated those corrections. The later
necessary-evasion screen is Imp2's separate incremental experiment; it does not
have advisor approval or require it.

Each summary variant passed ordered full-inventory equality against the old full
projection route on10,000 independently constructed admitted positions, plus
joined-EP, promotion, pin-ray and pinned-attacker witnesses. Tests also check the
bounded reply count against min(2, complete count), retaining exact lists below2.
These positions intentionally include attacked nonmoving/adjacent kings and
promoted material rather than only legal-game histories. The oracle switch is
thread-local test-only state and compiles out of production.

Both variants independently passed the unchanged released all54 profiling replay
checker. Full gameplay/mandatory diagnostics and performance acceptance remain
open. Frozen builds and verified sources:

| Variant | Artifact SHA256 |
| --- | --- |
| Unchecked pin summary | a0916607823621ea0a3119ba17f5c069339c26d2bf0cc53614ed137c2b13bf0f |
| Pin summary and necessary evasion screen | aff147eeaa5cf19b5cd34a00637c3b2dcd91ea06d1c6ca73cf54435861c9e0f3 |

The four-case CPU pilot fixes opening, middlegame and sparse endgame workloads
before launch, uses the unchanged strict oracle on each repetition, and accounts
for whole native user+system CPU lifetime. It is a local decision experiment;
it is not either complete reference collection or a qualified cross-host ratio.

## Decision from measured evidence

The four-case experiment completed all80 strict-oracle lifetimes. The combined
variant had the lowest median in every case. Relative to the unchanged baseline,
its individual median reductions were about9.5–23%; the sum of four case medians
was12.3% lower (11.2444805s versus12.8260115s). `evidence/generation-cpu-pilot-20261018/`
retains all samples, paired differences, range/median spreads and context.

Adopt that algorithm in `src/movegen.rs`, retaining the full projection oracle
and test-only differential route. Rebuild and regress the integrated artifact
under its own identity. This selects an incremental algorithm with measured
whole-search benefit; it does not close representation/restoration comparisons,
complete-corpus performance collection, calibration or final qualification.

Integrated artifact `670b965a29c063e1849eb0d790ba33dfb792fff2a13370b467f1235acf0d66a2`
passed all54 strict replays,130 native unit tests and the eight wire interruption
fixtures under its own retained build/check receipts. It has not inherited
the older baseline's full focused-game result or the prototype's CPU samples.
