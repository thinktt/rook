# Tactical capture preference and priority ordering

These contracts describe a capture-preference stage and the
ordering of a supplied priority sequence. They do not define legal capture
generation, the complete search move order, quiescence order or selected moves.
Hash preferences, special queen moves, promotions outside this stage, killer
moves and history priorities participate elsewhere in the full ordering.

## ORDER-PRIORITY-SEQUENCE

Inputs are an ordered sequence of nonnegative integer priorities. Each item
is identified by its zero-based input index. Higher priority comes first.
The required tie behavior is the following mathematical permutation:

1. Partition the original index positions into six classes by index modulo
   six. Within each class, order the items by decreasing priority, retaining
   the class's original relative order on ties. Put each ordered class back
   into the positions belonging to that class.
2. Order the resulting combined sequence by decreasing priority, retaining
   its now-current relative order on ties.

This is a definition of the resulting permutation, not a required sorting
implementation. Equal priorities need not retain their original relative
order. For priorities `[1,1,1,1,1,1,2]`, the result is the index sequence
`[6,1,2,3,4,5,0]`. All-equal sequences retain their input order. For at most
six items, the result is ordinary stable decreasing-priority order.

Diagnostic `ordering.prioritySequence` accepts `priorities`, a list of 0..230
integers in 0..4294967295. Output is `orderedIndices` plus
`chargedRelationQueries: 0`. Empty input returns an empty sequence. The values
in this diagnostic are abstract comparison priorities, not an engine's
private move representation.

## TACTICS-CAPTURE-PREFERENCE

For each supplied capture description, the inputs are:

- `attacker`: pawn, knight, bishop, rook, queen or king;
- `side`: white or black;
- `attackerValue`: the attacker's root-context material value;
- `victimEffectiveValue`: the victim's material value plus its positional
  adjustment at the captured square;
- `own` and `opponent`: influence profiles at the destination before excluding
  the moving piece's contribution;
- `promotion`: none, knight, bishop, rook or queen; only pawns may promote.

Influence and material values are different inputs. Personality material
weights do not replace the fixed influence categories. A victim's positional
adjustment affects this stage; the attacker's positional adjustment does not.
No simulated exchange sequence is performed by this contract.

For a non-king attacker, apply EVAL-ADJUSTED-RELATIONS excluding one contribution:
pawn for a pawn, minor for a knight or bishop, rook for a rook, queen for a
queen. Inspect the resulting relation for the attacker type, treating knights
and bishops as minors. Let `V` be victimEffectiveValue and `A` attackerValue.
Define effective gain `G` as `V-A` for an unfavorable relation and `V` otherwise.
When `V > 600`, use `G = V` regardless of the relation. Exactly 600 does not
receive that override.

The following comparison magnitude completely defines this stage's preference.
It is a mathematical device for defining outputs; neither its storage nor
an integer-valued production interface is required. Let attacker penalties be
pawn 99, knight 24, bishop 25, rook 40, queen 72 and king 160. Promotion bonuses
are none 0, knight 256, bishop 512, rook 768 and queen 1024.

| Condition | Comparison magnitude before normalization |
| --- | --- |
| Attacker is king | `4096 V - 160` |
| Non-king, `(V >= 200 or G <= 0)` and `G >= 50` | `65536 G - penalty + promotionBonus` |
| Non-king, `(V >= 200 or G <= 0)` and `G < -50` | 0 |
| Other non-king cases | `4096 V - penalty + promotionBonus` |

Normalize the magnitude to its least nonnegative residue modulo 4294967296.
Compare the resulting values as nonnegative numbers. This matters even in
the diagnostic's bounded range: zero or negative effective victim values can
otherwise produce a negative magnitude. Do not silently clamp it to zero.

Magnitude zero means this capture does not receive preference from this stage.
It does **not** mean the move is illegal, discarded or necessarily tried last
in the complete search. Other ordering rules may still favor it. King captures
do not consult influence or attackerValue; their special formula applies
regardless of support. A losing promotion capture can receive zero here and
still receive promotion preference in a later ordering rule.

## Diagnostic outputs and bounds

`tactics.capturePreferenceOrder` accepts `candidates`, a list of 0..230 capture
descriptions. Each description has exactly the fields above. attackerValue
is an integer in 0..10000; victimEffectiveValue is in -10000..10000. Influence
counts follow EVAL-RELATIONS (each 0..31). These synthetic inputs can test
conditions without claiming a legal position or a physically possible capture.

Output contains:

- `capturePreferred`: one boolean per input, true exactly when its normalized
  comparison magnitude is nonzero;
- `equalPreferenceGroups`: input-index groups, highest magnitude first, with
  indices increasing within each equal-magnitude group;
- `orderedIndices`: ORDER-PRIORITY-SEQUENCE applied to these magnitudes;
- `chargedRelationQueries`: zero.

The grouped representation reports equality without imposing input-order
tie-breaking on orderedIndices. It does not expose private move encodings or
priority fields. All candidates remain present, including nonpreferred ones.
Calls are independent and do not retain state. Computing the capture preference
and ordering the resulting list charge no KingRE relation units.

The current contract takes effective values and profiles as inputs. Their
complete derivation from root context, positional evaluation and cached state,
and the final composition with all search ordering categories, remain required
separate contracts.
