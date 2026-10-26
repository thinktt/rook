# Eager tactical producer totality on the admitted domain

The exact producer bytes are bound in preparation.json's candidateSource map and
must equal the exact66 base for tactical.rs, tactical/check_masks.rs, movegen.rs,
position.rs and engine.rs. Independent source review is recorded in
[the source recommendation](../../../docs/research/q-owner-local-tactical-overlap.md).
This proof is separate from ordinary generate_bounded; tactical pushes are not
runtime capped before MoveList::push's512 assertion.

Private validated ancestry has at most16 own pieces including exactly one king,
valid unique list squares/mailbox agreement and coherent attack planes. At most
15 nonkings each contribute<=27 destinations: knight8,bishop13,rook14,queen27;
pawn main loop<=3. The sole king contributes<=8 captures. Global EP and quiet pawn
checking prefixes have two file iterations each, adding<=4 even if a prefix item
duplicates another emission. Thus15*27+8+4=417<512 for every admitted placement.
No orthodox reachability, safe-opposite-king or legal-EP-victim-type premise is used.

In check_masks::sliders, quiets are a subset of one empty movement-ray prefix;
a capture can use only that ray's separate nearest occupied endpoint. The union
is a subset of the ray, and movement rays are disjoint. Extending a checking mask
never extends the movement ray. Pawn quiet promotion and quiet ordinary paths are
mutually exclusive; two capture-file iterations emit one choice each, including
queen-only promotion. Joined EP's actual nonpawn victim is allowed but kings are
excluded. Every other capture arm also excludes kings. No child is constructed.

Validated king/source squares and offset results are in0..63. Nonzero guards
precede leading/trailing-zero extraction/shifts. A first blocker is occupied in
coherent planes, hence nonempty in the mailbox before color/kind access. A source
classified as a king-ray blocker lies on that ray and differs from its origin,
excluding quiet_targets' direction fallback. quiet.unwrap follows is_some_and.
Fixed kinds/directions and distinct endpoints satisfy Move::new's preconditions.
All loops are finite over bounded lists/rays.

Generation reads Position only and changes destination MoveList only; it does not
consult FULL score, Influence, root weights, pawn cache, learning, work or host
state. A FULL evaluation return which formerly skipped generation therefore does
not protect an admitted position from an overflow/index/kind failure. Public/
noncoherent routes stay at original scalar demand; this proof does not expand
their domain. No runtime validation, capacity/opposite-king probe or bounded
producer variant is needed or added. Focused ordering/special/empty/selection
controls complement the source proof, not a corpus-only capacity assumption.
