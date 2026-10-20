# Quiet-promotion evasion ordering — local worked example

This example illustrates the shared [quiescence preference rule](quiescence-candidates.md#quiescence-preference-value)
on the ordinary legal evasions imported by [QUIESCENCE-TREE](quiescence-tree.md).
It is a local component composition, not a full-search input, a claim of
incoming search-state equality, or an extension of the narrower non-check
`search.quiescenceCandidates` admission domain.

Use position `K6r/p1P5/1p6/8/3k4/8/8/8 w - - 1 1` with fresh setup piece
chronology. White is checked along rank eight. [Ordinary candidate production](search-candidate-production.md)
and king safety yield, in generated order:
`c7c8q`, `c7c8r`, `c7c8b`, `c7c8n`, `a8b7`, `a8a7`.
The four c8 moves are empty-destination promotions, block the check, and do
not directly check the Black king. The a7 move captures a pawn; b7 is quiet.

For the capture's numerical context use both sides' material percentages 100,
`averageDepth=0`, `cfd=0`, `sop=100`, and this same position as root.
The [root phase](root-material-context.md) is wholly endgame. The a7 victim's
effective value is 98; the king attacker value is 1500, giving preference
`0xd0000000 + 65536*98 - 1500 = 3496016420`.

| Generated index | Move | Preference with omitted history |
| --- | --- | --- |
| 0 | c7c8q | 3758097408 |
| 1 | c7c8r | 3758097152 |
| 2 | c7c8b | 3758096896 |
| 3 | c7c8n | 3758096640 |
| 4 | a8b7 | 0 |
| 5 | a8a7 | 3496016420 |

Repeat with the single history entry
`{side:"white",piece:"pawn",square:"c8",value:2}`, every other key omitted.
All six preferences remain exactly the same: each quiet promotion takes its
promotion preference before the history fallback is considered. No promoted
piece key or pawn key is consulted for these four moves.

In both cases the preferred subsequence, collected in reverse generated
order, is `a8a7, c7c8n, c7c8b, c7c8r, c7c8q`. Applying
[ORDER-PRIORITY-SEQUENCE](tactical-capture-order.md#order-priority-sequence)
returns its indices `[4,3,2,1,0]`. Append the deferred `a8b7`:
`c7c8q, c7c8r, c7c8b, c7c8n, a8a7, a8b7`.

For contrast, an entry keyed by `white/king/b7` is used by `a8b7`.
Value 1 remains deferred; value 2 becomes preferred. The pawn/c8 entry does
not affect that move. These values describe local ordering, not how history
values are learned or retained by a complete search.

The accompanying [conformance case](../conformance/fixtures/quiescence-evasion-permutation-v1.json)
exercises the existing abstract permutation operation on the five preferred
values. It does **not** independently test priority calculation, legal
evasion production, or history lookup.
The composed local priorities and order were separately checked against the
maintained engine's actual component functions and a functional model.
Neither observation establishes a causal explanation of any full-search
work or returned-score discrepancy.

The [derived evasion cases](../conformance/fixtures/quiescence-evasion-order-v1.json)
add that missing executable coverage through the explicit
`orderingMode: "quiescence"` option of
[search.produceAndOrderCandidates](search-candidate-production.md#explicit-quiescence-evasion-ordering).
Both requested history inputs supply the FEN and numeric material/adjustment
context, never the generated list or computed preferences. Their outputs must
derive all six legal evasions and the complete order shown above. A third case
uses `white/king/b7=4294967295`, requiring `a8b7` first, and distinguishes ignoring
quiet-evasion history or using the wrong source-piece/side/destination key.
The supplied context material values are pawn 100, knight/bishop 300, rook 500,
queen 890 on each side; the only square adjustment is Black pawn/a7 = -2.
This interface supplies those context operands rather than claiming to derive
the full search's evaluator/history state. No recursive result or work total is
an expected output of these local cases.
