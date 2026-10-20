# SEARCH-REMEMBERED-RESULTS — retained search results

This contract defines how remembered results compete for retention and how a
new search query interprets them. It includes mutations caused by a successful
mate lookup. It does not define position identities, their conflict groups,
memory-size selection, or when a complete search stores or clears results.
The early search-entry/query/return composition is defined separately in
[SEARCH-CACHED-ADMISSION](cached-admission.md).
The initially empty fast-path cutoff/store/follow-up composition is defined
in [SEARCH-FAST-ENTRY](fast-entry.md).

## Semantic context

Each result belongs to a conflict group and a position identity. Only records
in the selected group compete for retention. Identity equality selects which
retained results a query may use. Diagnostic labels supply both relations;
neither a board encoding nor a private hash value is part of this interface.

A stored result contains a score, a remaining search depth, a possible move
hint, lower/upper-bound permissions, a quiet-mate-check marker and a marked-depth
marker. The last two are independent. The first records prior quiet-mate
consideration, not proof of mate; the second makes the record's depth available
as a separate observation. Their search-side setting and consumption require
additional caller contracts.

For storage at search ply P and target ply T, remaining depth is `T − P`.
Negative remaining depths are permitted. A score S gives lower-bound permission
exactly when S is strictly greater than the supplied lower window bound, and
upper-bound permission exactly when S is strictly less than the upper bound.
Thus equality with the lower bound stores upper-only, equality with the upper
bound stores lower-only, and an interior score stores both permissions.

Normalize mate-distance scores for later queries: add P when S is at least
9000; subtract P when S is at most −9000; leave other scores unchanged. These
thresholds are inclusive. Only the source and destination of a move hint are
retained. Promotion choice, en-passant designation and castling designation do
not survive as part of the hint. A query does not certify its legality.

## Retention and deterministic tie precedence

Each group has a depth-retained collection of up to three results and one
additional recent/displaced result. This is a behavioral capacity and priority
rule, not a required array, object layout or physical storage scheme.

The three retained priorities are fixed in precedence order. The first new
identity fills the first empty priority, the next fills the second, and the
next fills the third. Replacement preserves that priority's tie precedence;
it does not assign a new insertion age. Empty priorities are less valuable
than every depth in this diagnostic domain.

For an identity already in the retained collection, compare the new remaining
depth with its retained depth. A shallower result becomes the recent result,
leaving the deeper retained result intact. An equal or deeper result replaces
the retained result, preserving its priority and leaving the recent result
unchanged. Therefore an older recent result of the same identity can still be
queried first after a retained replacement.

For a new retained identity, select the least-depth retained priority, choosing
the first priority in a depth tie. If the new depth is at least that depth,
move the displaced result into the recent role and retain the new result at
the selected priority. Displacing an empty priority empties the recent role.
Otherwise only the recent result changes. The recent role is not searched
for identity matching during storage. It may duplicate a retained identity.

Clearing discards all groups' results and their precedence state. A later
store behaves as in a fresh context. This operation alone does not describe
a full engine reset or the lifecycle of the table between real searches.

## Query interpretation and effects

A query starts with no score, no bound, no move, no marked depth, and a false
quiet-mate-check observation. It first considers a matching recent result.
If that produces no usable score, it considers the matching retained result,
if any. A usable recent result ends the query without consulting retained state.

For each considered record, expose its bound permissions as `upper`, `lower`
or `exact` (both). A non-null move replaces the query's hint; a null move leaves
any earlier hint intact. Quiet-mate-check observations combine by logical OR.
For records with the marked-depth marker, report the greatest depth observed
so far. These observations are retained even when the record cannot supply a
score. Consequently a query can combine metadata from recent and retained
results rather than returning the fields of one record.

The exported bound kind is the kind of the **last considered matching
record**, whether or not that record supplies a usable score. Considering a
matching retained record therefore replaces the bound kind previously exposed
by a no-score recent record; bound kinds do not combine. Thus recent `lower`
followed by retained `upper` exports `upper`, while recent `upper` followed by
retained `lower` exports `lower`. If there is no matching retained record, the
considered recent record's kind remains. A usable recent result still ends the
query before retained state is considered. Consumers which require a particular
kind use this final exported observation, not the union of permissions from all
considered records.

Adjust the normalized score for the query's current ply P: subtract P from
values at least 9000; add P to values at most −9000. Ordinary values do not
change. Required remaining depth is query target minus current ply.

A normalized positive mate score with lower permission is immediately usable
when its adjusted value is at least the query's upper bound. A normalized
negative mate score with upper permission is immediately usable when its
adjusted value is at most the query's lower bound. Neither requires sufficient
stored depth. Such a result raises its retained depth to the required depth
if necessary. This mutation affects subsequent queries and replacement.
The marked-depth observation for this record precedes that increase: a later
query can report a greater marked depth than the query that raised it.

Otherwise a score is usable only when the record's depth is sufficient and
at least one permitted bound cuts off the new window: lower permission with
score at or above the upper bound, or upper permission with score at or below
the lower bound. Equality qualifies. An exact result strictly inside the new
window supplies **no score**, although it can still supply a move and metadata.

These table operations add no search-visit or relation-query work. They can
change how much subsequent searching occurs; zero direct charge does not mean
they are behaviorally irrelevant.

## Diagnostic sequence

`search.rememberedResults` input has `events`, an ordered list of 1..256 events,
containing at least one probe. Start with empty remembered results. Events are:

- `{kind: "clear"}`;
- a `store` with `group`, `identity`, `searchPly`, `targetPly`, `lowerBound`,
  `upperBound`, `score`, `move`, `quietMateChecked` and `markDepth`;
- a `probe` with `group`, `identity`, `searchPly`, `targetPly`, `lowerBound`
  and `upperBound`.

Group and identity labels are case-sensitive strings of 1..32 ASCII letters,
digits, underscores or hyphens. Up to sixteen different groups are supported
per request. Identity labels may be reused across groups. Labels are opaque:
consistent renaming does not change behavior.

Ply is integer 0..63 and target is integer 0..64. Scores and window bounds are
integers −10000..10000; the lower bound must be strictly below the upper bound.
Markers are booleans. The supplied move is null or a
[SEARCH-CUTOFF-MEMORY](cutoff-memory.md) move descriptor; it need not be legal in
a board position because this diagnostic does not supply a board.

Output has `observations`, one per probe in sequence order, and total
`chargedSearchUnits` and `chargedRelationQueries` (both zero). Each observation
contains `score` (integer or null), `bound` (`none`, `upper`, `exact`, `lower`),
`markedDepth` (integer or null), `move` (four-character source/destination or
null), and boolean `quietMateChecked`. Null score means no usable cutoff score,
not necessarily absence of a matching record. No numeric miss sentinel or
private record contents are exposed.

The diagnostic excludes identity collisions, group selection from positions,
allocation/reinitialization, optional bounds-only invalidation, arithmetic
outside the stated ranges, and complete search/session composition. Those
remain explicit specification dependencies, not freedoms to substitute an
arbitrary production table policy.
