# SEARCH-CACHED-ADMISSION — early draws and remembered results

This contract composes search admission with remembered-result lookup. It
covers non-frontier ordinary search and interior mate search through either
an immediate return or continuation beyond a cache miss. It does not specify
the later evaluation, legal replies, move ordering or completed search.

## Ordered behavior

First perform [SEARCH-DRAW-BOUNDARY](draw-boundary.md), including historical
repetition, the analysis exception, next-ply preference clearing and the
upper-bound-dependent short-reversal decision. An early draw returns zero
without querying remembered results. Its clearing/retention behavior remains
exactly as defined by that earlier contract. In particular, an available
cached winning or losing score does not override an earlier draw.

If admission continues, query remembered results for the current position's
cache identity and conflict group, with the current search ply, absolute target
ply and unmodified lower/upper bounds. Apply all
[SEARCH-REMEMBERED-RESULTS](remembered-results.md) query rules, including hint and
marker combination and mate-depth mutation.

A usable cached score returns immediately as that score. Do not clamp it to
the window boundary or add another search unit. The next-ply preferences have
already been cleared. No later evaluation or reply-generation decision is
needed for this return. This applies to both supported search modes.

If the cache cannot supply a score, continue search with the query's move and
metadata observations available. A matching exact result inside the current
window is one such continuation, not an immediate exact-score return.
This contract does not imply that the hint is legal, that an interior mate
search orders by it, or that every later consumer uses all returned metadata.
Those consumers require their own contracts.

The admitted query can change a record's depth through a mate cutoff. An early
draw prevents that mutation because no query occurs. Follow-up probes in the
diagnostic observe the resulting table state immediately after this stage,
before any later search work. They are observations of stage composition,
not a claim that complete searches always stop at this boundary.

The entire stage charges one search work unit, including early draws, cache
hits and continuations. The query adds no direct search or relation work.
There are no pending host events or poll boundary in this diagnostic context.

## Diagnostic request

`search.cachedAdmission` input contains:

- `context`: all SEARCH-DRAW-BOUNDARY fields plus `lowerBound`;
- `setup`: 0..128 SEARCH-REMEMBERED-RESULTS store/probe/clear events;
- `group` and `identity`: the current cache conflict-group and identity labels;
- `followup`: 1..16 SEARCH-REMEMBERED-RESULTS probe events.

The context mode must be `full` or `mateInterior`. Search ply is 1..62 and
strictly below target ply; full mode additionally requires it to be strictly
below maximum depth. Target is at most 64. Lower and upper bounds are integers
−10000..10000, with lower strictly below upper. Other context fields retain the
draw-boundary domain, including history lengths, check/analysis states, move
descriptors and preferences. Quiescence and mate-leaf dispatch are excluded
here; their admission behavior is specified separately.

Start with an empty table and apply setup events in order. Setup probes may
change retained depth; their observations are not included in this operation's
output. Then execute the search-entry stage above and the follow-up probes.
Use at most sixteen distinct conflict-group labels across the entire request.
Store/probe arithmetic and label domains follow SEARCH-REMEMBERED-RESULTS.

The context's repetition identities and the table's cache identities/group
labels are distinct supplied equality relations. This operation composes their
consumers without defining how either relation is derived from a legal board
or complete history. Artificial component contexts are permitted; matching
these cases does not qualify position hashing or naturally reachable history.

## Diagnostic response

Output contains:

- `repetitionCount` and `isCycle`: auxiliary context-query observations;
- `outcome`: `draw`, `cached` or `continue`;
- `score`: zero for an early draw, the actual returned cached score for a cache
  return, or null on continuation;
- `cache`: null if no table query occurred, otherwise the query observation
  object defined by SEARCH-REMEMBERED-RESULTS;
- `followup`: ordered query observations after this stage;
- `chargedSearchUnits`: one;
- `chargedRelationQueries`: zero;
- `killers`: resulting nonempty preference pairs in increasing ply order.

Auxiliary repetition/reversal observations do not assert that a real search
executes those queries after an earlier return. Cache nullness, unlike those
auxiliary observations, distinguishes an actual skipped query from a query
that found no usable score. A zero cached score would still be `cached`, not
an admission draw. No internal sentinel or observation address is exported.

This is an opt-in diagnostic stage. It imposes no production interruption API,
subprocess model or implementation module boundaries. Subsequent search work,
table lifetimes, complete work-clock stopping and whole-game behavior remain
separate specification obligations.
