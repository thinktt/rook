# Uncertified endpoint hint at ordinary completion

Status: unresolved conditional composition/admission gap,2026-10-18. This is not
a demonstrated reachable engine defect or an admitted direct diagnostic case.
The exact released-contract and own-source review hashes plus specification-only
consultation are in `evidence/spec-empty-source-hint-20261018/`.

SEARCH-ORDINARY-ITERATIONS initializes best from the saved effective lower
bound and preferred from the remembered endpoint hint. A strict child best
improvement above running lower replaces preferred. Normal completion caps
best by the effective upper bound, then invokes SEARCH-CUTOFF-MEMORY when the
result exceeds incoming L, using the final preferred move. This control flow
is represented in `ordinary.rs`.

A conditional state worth resolving has L < effectiveLower < U, no usable
cached score, a non-null uncertified hint, no replacing quiet-mate preference,
and no main candidate score strictly above the initial best. If completion
still has capped best > L, the existing hint can reach the learned-state
consumer without having matched a generated legal move. A hash identity/group
collision is one possible concern; no public reachable witness establishing
all these premises together has been produced.

A later source proof narrows this condition. If effectiveLower <= L, any
completion learned update with final best > L must first have crossed L through
a strict improvement by a generated candidate, replacing the inherited hint.
A preceding quiet-mate replacement is also generated. Thus the empty-source
inherited hint is excluded in that region. In first-half nodes the effective
lower is -10000, so this exclusion applies conditional on incoming L >= -10000;
the wider normalized-score bound alone does not prove that caller-window premise.
In second-half nodes the quiet-mate probe is automatically disabled. The open
branch therefore requires effectiveLower > L and every consumed candidate score
<= effectiveLower, along with an actually reachable uncertified empty-source
hint and the earlier admission gates. Recent/retained metadata can carry a
nonnull hint without a usable score even at sufficient marked depth; metadata
does not supply a provenance proof. See the [bounded reduction](../../evidence/uncertified-hint117-reduction-review-20261018-score-context/review.md).

SEARCH-REMEMBERED-RESULTS explicitly does not certify hint legality.
SEARCH-CUTOFF-MEMORY states that a non-null move with empty destination updates
killers/history, with history keyed by the moving piece's color/type. It gives
no moving-piece interpretation for an empty source. Its direct diagnostic
inherits SEARCH-CANDIDATE-ORDER's candidate source occupancy/side condition;
remembered hash/killer descriptors can fail that condition. Therefore an
empty-source cutoff event is outside the direct cutoffMemory diagnostic domain,
and creating such a component test would not resolve composed-call admission.

The current native empty-source guard prevents indexing an absent piece. It
is not evidence that skipping every update is the specified composed behavior.
No pawn/color fallback, legality certification, suppressed update or other new
rule was inferred or adopted in this review. Imp1's consultation used only the
released contracts and public domains, with no implementation/source findings
or engine runs; it confirmed this interpretation gap without proving reachability.

Closure requires either a public reachable input producing the composed state
and authority clarification of its behavior, or a justified proof that this
state is excluded by the full production contract/invariants. Keep the
production review obligation open. Existing finite replay success and direct
component eligibility tests do not close it.
