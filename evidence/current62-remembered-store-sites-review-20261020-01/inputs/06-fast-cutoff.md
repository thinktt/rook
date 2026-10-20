# SEARCH-FAST-CUTOFF — guarded shallow score cutoff

This contract combines the depth/score gate, prior-move capture exception,
king-neighborhood pressure guard and threatened-material result. It describes
the decision **when this candidate cutoff is attempted**, not the earlier
conditions that select this attempt or the whole search procedure.

Let d be target ply minus search ply. The candidate is unavailable when d
exceeds two. Its margin is 100 for d=1 and 150 for d=2. Let S be static score
minus that margin and B the upper search bound.

The candidate is rejected before checking king pressure if any of these holds:

- S is less than B;
- either the current position or its predecessor is in check;
- the prior move satisfies [SEARCH-CAPTURE-EXCEPTION](capture-exception.md).

If none holds, apply [SEARCH-KING-PRESSURE](king-pressure.md) to the supplied
previous/current influence profiles. A true pressure guard rejects the candidate
without requesting threatened material. Otherwise request threatened material
T and let R=S−T. The cutoff score is R when R is at least B; otherwise there
is no cutoff. Equality is accepted at both score comparisons. The returned
score is the adjusted score, not B. Zero is a valid returned score.

This ordering is observable through whether pressure and threatened material
are requested. A rejected depth, score, check or capture condition suppresses
both requests; a true pressure guard suppresses only the latter. Supplying
the same threatened-material result does not authorize requesting it when a
guard suppresses that work.

All subtraction within the diagnostic domain below has its ordinary signed
integer meaning; no overflow occurs. The absolute ply numbers affect this
contract only through their difference. There is no retained state between
diagnostic queries. Selecting and preparing the supplied contexts in a real
search remains a separate composition requirement.

## Diagnostic

The opt-in operation `search.fastCutoff` accepts `queries`, an ordered array
of 1..4096 objects. Each object has exactly:

- `searchPly`: integer 1..62;
- `targetPly`: integer greater than `searchPly`, at most 64;
- `staticScore`: integer −10000..10000;
- `upperBound`: integer −9999..10000;
- `currentCheck` and `previousCheck`: booleans;
- `capture`: one query object from `search.captureException`;
- `pressure`: one query object from `search.kingPressure`;
- `materialThreat`: integer 0..20000, supplied as the result if requested.

Output contains `results`, one object per query with `cutoffScore` (integer
or null), `pressureChecked` (boolean) and `materialThreatQueried` (boolean).
Null means no cutoff; it is distinct from zero or any negative cutoff score.
The upper-bound range intentionally excludes −10000; behavior outside this
diagnostic domain is not established by these tests. The threatened-material
range bounds the test surface, not every possible personality evaluation.

Capture and pressure inputs follow their component contracts, including
normalization, color ownership, selected-neighbor rules and independent
supplied facts. Check status, capture facts and influence profiles need not
describe one reachable board. An implementation may calculate this diagnostic
without using the research engine's internal structure.

## Composition limits

These tests supply the threatened-material result; they do not run its
estimator inside the cutoff. [EVAL-MATERIAL-THREAT](material-threat.md) separately
specifies that estimator and its relation-query charges.
[SEARCH-FAST-THREAT](fast-threat.md) supplies its candidate-production and
charged-work composition with this consumer. The
query flags here are observations, not complete SearchID or virtual-clock
charges. They establish that the estimator is or is not requested.

[SEARCH-FAST-ENTRY](fast-entry.md) adds admission and retained-result caller
composition with controlled evaluator responses. It distinguishes the helper's
broad diagnostic domain from combinations admitted by the normal fast entry.
[SEARCH-FAST-THREAT](fast-threat.md) separately connects actual board-derived
pressure and threatened-material production/charges to this consumer.

Earlier attempt eligibility, generation of the static score and influence
profiles, ordinary shallow/null-search alternatives, remembered-result writes,
search stopping and complete engine behavior are not established here.
In particular, diagnostic capture/pressure combinations are not assertions
that the complete engine reaches them through its normal entry conditions.
