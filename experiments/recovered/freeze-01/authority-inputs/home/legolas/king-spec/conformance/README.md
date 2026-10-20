# KingRE conformance kit — version 2.5.0

This kit is not a complete gameplay test suite. It contains only semantic
fixtures and independent test machinery. It does not contain an implementation
of the specified engine behavior.

Version2.5.0 adds a separate [performance companion](../performance/README.md).
Its23functional benchmark projections and optional offline observation checker
are not additional fixture operations, production commands or part of the
7739-case runner. The existing117fixtures, case IDs, inputs/answers, focused
gameplay and continuity collectors are unchanged. Numerical performance limits
and measurement qualification are separate from functional conformance; neither
this kit nor passing supplied projection files establishes a timing pass.
Reference measurements retain their exact artifact, scope and historical limits;
no new full-suite/gameplay/downstream qualification is claimed by publication.
Retained version 2.4.2 adds established P-identities, original comparison case order and
[historical performance baselines](profiling/benchmark-results.md). Stable case
IDs/inputs/answers and component/gameplay fixtures are unchanged. Timing numbers
are informational, not conformance speeds; final presentation is offline-validated,
not freshly engine-executed or gameplay-qualified.
Retained version 2.4.1 expands the existing profiling kit to 54 fresh-position workloads
and an independently selectable correctness replay checker. Reference semantic
posts/work/moves are retained-observation expectations; final checker validation
is offline/mock, not a fresh engine/full-suite/gameplay pass. No speed threshold,
new engine interface or component/gameplay fixture change is introduced.
Retained version 2.4.0 adds six focused production-wire controls for the existing
fine-work post interface, plus six reusable profiling workloads and an optional
Linux host driver. The 7,739 component fixtures/answers are unchanged. Six
focused KingRE wire cases passed before final reporting-only corrections;
current reporting has offline/mock checks, not a fresh engine run. Timing
efficiency has no pass threshold. No full-suite/gameplay/downstream qualification
is claimed for this amendment.
The expanded [profiling correctness replay](profiling/README.md#observable-correctness-replay)
provides 54 independently schedulable fresh-position cases and semantic work/post/
move expectations, separate from the component and gameplay fixture inventories.
Its final checker has offline/mock controls, not a fresh engine qualification.
Retained version 2.3.1 clarifies the continuity runner's bounded host-wait option:
one-minute default, optional positive integer wait up to five minutes, recorded
and validated in receipts. Search inputs and all assertions remain unchanged.
Offline/mock controls pass; no fresh native continuity qualification is claimed,
and historical longer-wait diagnostics are not converted into native receipts.
Retained version 2.3.0 adds the separate continuous-process switching check:
four segments/eight searches in one process, with same-artifact collection
alongside independent-game coverage. The supporting KingRE draft passed8/8;
later collector/completion changes have offline mock controls, not a new engine
run. No fresh12/632/full-suite or integrated pass is claimed.
Retained v2.2.0 permits independently schedulable focused replay games, with one
persistent process per game and strict same-artifact complete collection.
All inputs and expected answers are unchanged; no fresh gameplay/full-suite
pass is claimed. Continuous-process switching coverage is separate.
Retained v2.1.0 clarifies shared quiescence evasion preferences and adds the explicit
local quiescence-ordering option to the existing candidate-production diagnostic.
The v2.0.1 null-reversal correction is retained unchanged; all existing requests,
case IDs and answers are preserved. The v2.1.0 release added to the previous 7,735 cases one
[quiet-evasion preferred-permutation case](fixtures/quiescence-evasion-permutation-v1.json),
and three [derived evasion-order cases](fixtures/quiescence-evasion-order-v1.json),
for 7,739 cases. The derived cases calculate legal candidates and preferences
from position/context/history through the explicit quiescence-ordering option
of the existing candidate-production operation; see their
[local composition and coverage limits](../spec/quiescence-evasion-priority-example.md).
The three derived cases passed focused native qualification, plus one unchanged
ordinary smoke; 14/14 offline controls passed. These are not a full 7,739-case
qualification or a claim of integrated search/gameplay closure.

The [acceptance statement](../spec/README.md#required-deliverable-and-acceptance-surface)
defines the mandatory adapter/fixture surface. All included fixture operations
are mandatory for package acceptance except `output.analysisCandidateReport`
and `search.analysisRootSequence`, which are optional supporting diagnostics.
The default runner includes both optional operations; use explicit fixture
selection for a mandatory-only run. Neither kind of run establishes complete
gameplay conformance.

The required production wire interface is
[KING-XBOARD-ORDINARY](../spec/ordinary-xboard-wire.md), not this JSON adapter.
The separate [focused accepted-game replay](gate-replay/README.md) uses the
ordinary executable with the opt-in
[gate seed command](../spec/gate-seed-command.md). It establishes gate-facing
interface/lifecycle readiness before the complete 3,288-game recorded-oracle
gate; it is not another JSON operation or a replacement for that final gate.
Its games may be run independently/in parallel with one persistent process
per game and exact complete coverage collected under the focused runner's
rules. This does not qualify cross-game continuous-process behavior or turn
failed/prefix-only records into completed-game passes.
The separate [continuous switching check](gate-replay/continuous-switching.md)
uses one process for four short segments/eight searches, then exits cleanly.
Complete focused qualification needs both results on the same artifact and
configuration; schedule independent games and this check separately.
Implementer acceptance also includes the specification-owner normative review
defined by the linked acceptance statement. Fixture results do not replace
that production review.

The separate [work-clock profiling controls and workload kit](profiling/README.md)
check the opt-in launch/formatter interface on a small production search.
Those wire controls are not JSON fixture operations and do not change the
7,739 component-case inventory. The six reusable benchmark workloads have no
timing expected answers or performance pass threshold; execution efficiency
and wall throughput are measured results, not normative speed requirements.

The current ordinary-play route is `search.ordinaryJoinedSearch`, specified by
[ordinary-play ingress](../spec/ordinary-play-ingress.md),
[joined search](../spec/ordinary-joined-search.md), and the
[persistent session/reset contract](../spec/ordinary-session-lifecycle.md). Its
fixtures connect fresh position/history, a complete numeric personality,
game-clock allocation, natural seed acquisition, recursive search, work-clock
stopping, public posts and a selected move, or the specified fatal zero-root
outcome. The persistent-session fixtures
exercise reset and cross-search lifetimes separately. Component fixtures below
remain useful diagnostics for the rules composed by that route; their supplied
inputs and smaller resource domains do not narrow the ordinary-play target.

First-iteration fixtures require searching every generated legal root from
setup/history. They compare child windows/results, evolving ranking/PV and
cumulative work, without supplying those results as inputs. See
[complete first iteration](../spec/first-iteration.md).

Ordinary-iteration fixtures continue actual recursive search through two to
four complete unrestricted iterations. They compare the retained ordering,
remembered-result and evaluation-state effects through every root result, PV
and cumulative-work boundary. The requests use fixed completion and do not
supply child answers; see
[completed ordinary iterations](../spec/ordinary-iterations.md).

Two existing cases also check caller-context rules. In
`ordinary-iterations-start-depth3`, the `e2e4` step retains the tactical
`d8d1 e1d1` suffix at iteration depth three. In
`ordinary-iterations-selected-b-opening-depth2`, the `f6g4` step retains score
441 under the below-six null-child depth rule. The corresponding expected PV,
score and work fields remain unchanged.

### Quiet-rook work accounting

The `ordinary-iterations-quiet-rook-depth4` request starts from
`r3k3/8/8/8/2n5/8/8/RN2K3 w - - 0 1`. Its second iteration ends at
**117 search units / 185 relation queries**. In iteration three, the first
root `a1a8` visits the legal reply `e8d7` and, among White's later candidates,
`a8c8`. These are explored moves, not necessarily the final PV. At the
`a8c8` ordinary node, ply 3 and remaining depth 1, the below-six null rule
enters a no-preceding-move child at ply 4, remaining depth -2. Its tactical
target is 2 and its inherited iteration depth is 3, so the non-recapture
`c8c4` passes the `ply <= target + iterationDepth` screen (4 <= 5).

The null child's window is [506,507]. Its standing score is 500, best is 500,
and lower bound is 506 before `c8c4`. The captured Black knight gives material
balances 615 before and 950 after, hence gain 335. The retained positional
contribution is 1 from White's perspective and adds no captured-color margin;
the low-material exception adds 800. The capture allowance is therefore
`335 + 50 + 0 + 800 = 1185` and its initial estimate is `500 + 1185 = 1685`.
The attacker is a White rook of value 500. The capture-policy threshold is
`max(500,506) = 506`; after subtracting the attacker value, 1185 still exceeds
506, so destination support is not consulted. The estimate forces search.
King safety does not reject this move.

The following cumulative checkpoints make its work ownership explicit.
Search and relation columns are the two *cumulative* charged-work values,
not independent costs to add to the fixture step:

| Point in the specified iteration-three traversal | Search | Relations |
| --- | ---: | ---: |
| End of iteration two; start of the next root | 117 | 185 |
| After the `a1a8` child's entry and full evaluation | 118 | 188 |
| After the `e8d7` branch's `a8b8` candidate | 218 | 227 |
| After full evaluation at the `a8c8` ordinary node, before its null child | 219 | 230 |
| After the null child's `c8c4` search and return | 221 | 233 |
| After the ordinary `a8c8` candidate finishes | 222 | 233 |
| After the full `e8d7` branch finishes | 241 | 239 |
| After the `e8f7` branch finishes | 256 | 245 |
| After the `e8e7` branch and the root step finish | 271 | 251 |

The null subtree spans **219/230 to 221/233**, charging two search units and
three relation queries in total. Its own full evaluation charges the three
relations on c3, c2 and c1 beyond the knight blocker on c4. The `c8c4` child
charges **one search unit and zero additional relation queries**: after the
capture there is no pawn work or further additional-ray relation, and direct
adjusted relations are uncharged. The child returns -798, so the null parent
returns 798. Negating the null result gives -798, below the ordinary parent's
upper bound -506; the shallow cutoff fails and ordinary search continues.

At the root-step level, the increment from 117/185 to 271/251 is **154/66**:
the root child's entry/evaluation contributes 1/3, then the `e8d7`, `e8f7`
and `e8e7` branches contribute 123/51, 15/6 and 15/6. The `e8d7` branch's
123/51 already contains the 2/3 null subtree, which already contains the
`c8c4` child. Adding another 1/4 to the final 271/251 would count visited
work twice and would assign four relation queries to a child that charges
none. The final PV `a1a8 e8d7 b1d2 c4e3` does not list every explored
candidate; it is not a work ledger. This worked example clarifies the
existing fixture and rules; it does not supply child answers as request inputs
or change the fixture's expected output.

Seeded-iteration fixtures add an explicit retained seed, comparing both
randomized child windows and adjusted root scores through complete searches.
They include bounded defaults and three exact selected personality vectors
with their nonzero randomness. They supply no child results or activity totals; see
[seeded ordinary iterations](../spec/seeded-ordinary-iterations.md).

Seeded-timed fixtures continue actual recursive work until computed clock
expiry. They compare completed and interrupted roots, retained capture versus
stopping work, and semantic public posts/move, without supplying clock samples
or child answers; see [seeded timed search](../spec/seeded-timed-search.md).

Quiescence-tree fixtures require actual recursive search from setup/history and
a selected legal root move. No child results, candidate lists, evaluation
choices or work counts are supplied as inputs. See
[composed quiescence](../spec/quiescence-tree.md).

Capture-policy fixtures qualify depth and score boundaries, conditional support
consultation and optimistic best updates from supplied estimates and support
answers; see [capture policy](../spec/quiescence-capture-policy.md).

Capture-defense fixtures connect normalized influence and actual board geometry
to the quiescence destination-support predicate, independently of the caller's
depth/score thresholds; see [capture defense](../spec/quiescence-capture-defense.md).

Ordinary-capture allowance fixtures test material change and signed retained
terms across both colors, piece types, sparse/dense material and asymmetric
value contexts. These are component inputs, not complete searched positions;
see [capture allowance](../spec/quiescence-capture-allowance.md).

Quiescence-entry fixtures connect actual setup and forward state with search's
non-check full/fast evaluation choice, including strict window endpoints and
parent-position capture exceptions. They do not supply the final static score
or evaluation kind; see [quiescence entry](../spec/quiescence-entry.md).

Fresh-score fixtures extend the subtotal through actual placement identity,
root preference/variation and full endgame/final score and bounds. They require
fresh recomputation, not ordinary cache clearing or retained evaluation;
see [fresh score](../spec/fresh-score.md).

Fresh-subtotal fixtures connect root/current placement and personality settings
to all component terms, tempo, retained subtotal, base score and relation work.
Only semantic pawn order remains supplied at that boundary; fresh-score
composition adds final adjustment, while retained/fast evaluation remains
separate. See
[evaluation subtotal](../spec/evaluation-subtotal.md).

Activity fixtures produce general piece scores, pressure on kings, and charged
relation counts, then verify the resulting shelter composition. They no longer
supply the king-pressure input used by the lower-level shelter diagnostic.
Effective weights and material still have a supplied-input boundary; see
[activity](../spec/activity.md).

King-shelter fixtures derive phase and influence from placement and compare
the raw geometric contributions, side terms and weighted composition. Activity
pressure, material score and effective weights are supplied diagnostic inputs;
see [king shelter](../spec/king-shelter.md) for this boundary.

Work-timed root fixtures connect counted activity to clock observations,
ordinary polls and retained results after interruption. They supply child
scores and activity runs, not elapsed time; see
[work-timed root sequences](../spec/work-timed-root-sequence.md).

Post-lifecycle fixtures compare immediate versus deferred reports, retained
capture-time metadata and replacement of earlier PVs. They supply qualifying
captures and a successful ordinary finish; see [post lifecycle](../spec/post-lifecycle.md).

PV-line fixtures compare included complete tokens and byte length, with
controlled prefix widths and notation; see [PV line output](../spec/pv-line.md).

Analysis candidate-report fixtures cover score normalization and nonempty or
shortened child lines. They do not qualify overlength lines or complete public
post timing; see [candidate reports](../spec/analysis-candidate-report.md).

Fixed-analysis root sequences compare Nth-ranked windows, stable score prefixes
and report admission. Their controlled report booleans are not complete protocol
posts; see [analysis root sequences](../spec/analysis-root-sequence.md).

Restricted root sequences exercise work-based exploration, per-candidate
responses through reordered identities, retries, ranking penalties and carried
work. They use controlled children, not full searches; see
[restricted root sequences](../spec/restricted-root-sequence.md).

Unrestricted root-sequence fixtures compare every produced ranked prefix,
following window, carried work and next-iteration schedule. Child results/work
are controlled inputs, not actual chess searches; see
[unrestricted root sequences](../spec/unrestricted-root-sequence.md).

Root-work fixtures connect the ordinary SearchID threshold to stable tail
exploration order, retaining the first candidate and label/work binding.
They supply earlier work rather than executing earlier iterations; see
[root work scheduling](../spec/root-work-schedule.md).

Root-aspiration fixtures supply controlled child results and check the initial
window, optional retry and ranking penalty. They do not run the child search or
define full root scheduling; see [root aspiration](../spec/root-aspiration.md).

Output-score fixtures distinguish root ranking scores from reported integers,
including phase-scaled draw preference and mate/sentinel boundaries. They do
not cover result/PV copying or all formatting; see
[reported score](../spec/output-score.md).

Clock-seeded sessions freeze only system seconds, leaving KingRE work time
and seed acquisition active. They compare actual seeds, selected moves and
complete semantic posts across persistent searches and fresh/prefix controls;
see [seed lifetime](../spec/seed-lifetime.md).

Root-randomization fixtures use algebraic endpoints, move kind, promotion and
an explicit seed; no native move encoding is supplied. They check adjustment,
transformed search bounds and ranking scores, not complete root searches.
See [root randomization](../spec/root-randomization.md).

Position-setup fixtures derive starting order and normalize requested rights
and en-passant targets. Setup-to-history fixtures then advance actual moves
without supplied ordering. These differ from the lower raw-initial-state move
diagnostic; see [position setup](../spec/position-setup.md).

Move-sequence fixtures check actual history transitions, including preserved
piece order, promotions, castling/en-passant/count state and placement
fingerprints. They supply the initial order and expect the initial state plus
every resulting state; see [move sequences](../spec/move-sequence.md).

Fixed-root pawn sequences build context from the first position and personality
settings, then retain pawn information across later evaluations. They include
all 188 parameter sets with both root colors and active-piece collision cases.
They are explicit evaluation sequences, not full legal game histories; see
[the contract](../spec/search-pawn-sequence.md).

Public search-session fixtures contain setup commands, work-clock allowances,
selected moves and semantic post trails only. They preserve one engine session
between searches; some intentionally omit `new`. No memory snapshots, hashes
of internal state, debugger controls or contamination are included. See
[ordinary search pawn lifetime](../spec/search-pawn-lifetime.md).

Retained-subtotal fixtures extend stateful checks through current penalties,
piece activity, fallback and weighting. Each step supplies its own effective
context; retained pawn information persists unless explicitly cleared.
See [retained pawn subtotals](../spec/retained-pawn-subtotals.md).

Retained-candidate fixtures follow saved structural order into current-position
candidate progress and raw ending scores. Full-identity-collision fixtures use
different pawn arrangements with the same identity, not injected keys. Both
are stateful sequences: do not clear between steps unless requested. See
[retained pawn candidates](../spec/retained-pawn-candidates.md).

Identity/retention fixtures include stateful sequences with natural pawn-group
collisions. Do not reset the tested state between steps of a retained-structure
request; honor only the request's initial state and explicit diagnostic clears.

Context-pawn fixtures compose root and current positions with personality
settings through fresh pawn and central contributions; see
[the contract](../spec/context-pawn-subtotals.md). They do not specify retained
cache behavior or infer a legal history between the two positions.

Personality-weight fixtures connect explicit percentages and root color to
effective coefficients and central evaluation contributions; see
[the contract](../spec/personality-evaluation-weights.md). Extreme direct
percentage cases do not extend the input domain of downstream operations.

From the package root (`spec/package/` in the recovery repository), run against
an implementation-provided adapter:

```sh
node conformance/run.mjs -- /absolute/path/to/adapter optional-arguments
```

To select one fixture file:

```sh
node conformance/run.mjs --fixtures conformance/fixtures/time-allowance-v1.json -- /absolute/path/to/adapter
```

The [diagnostic transport](../spec/diagnostic-interface.md) defines requests.
The runner sends semantic inputs only and compares full response outputs.
It exits nonzero on any mismatch or adapter failure and emits a JSON report
with fixture hashes and individual results. Standard error can be retained
locally by a test harness; it is not part of expected behavioral output.

The runner sets a 1 MiB subprocess-output capture ceiling (`maxBuffer:1048576`
for stdout/stderr).
This transport ceiling is not an operation's result-size admission or an
engine limit. A valid larger response requires a harness with adequate capture
capacity; the bundled runner reports overflow as a resource failure.

The current fixtures cover schedule/allowance, idle clock-state composition,
work-clock ledger arithmetic, root phase/material values, descendant material
balance, evaluation influence/relations (including adjusted contribution
exclusion), tactical capture preferences, priority/tie ordering, composed
ordinary non-root search ordering, phase-specific square values and positional
composition, threatened-material estimation and its relation charging,
stateful cutoff-memory updates, explicit learned-state reset and their ordering effects,
repetition-query/admission boundaries and next-ply clearing, short move-reversal
recognition, composed early-draw/search-mode handoff behavior, mate-leaf
decisions and bounded actual-position terminal composition, remembered-result
retention/query/clear sequences and their mate-depth effects, actual search
admission/cache composition with follow-up state observations, phase-adjusted
selective-depth arithmetic and its node/root consumers, post-evaluation bound
suppression and cutoff decisions, uncapped king-neighborhood pressure and its
increase guard, promotion/destination capture exceptions and crowded-material
normalization, composed fast shallow-cutoff decisions and query suppression,
fast-entry admission and actual retained-result/query composition, board-derived
pressure/threat production and charged cutoff work, late-endgame pawn-span,
pawnless-material and bishop-and-knight geometry contributions, their selected-side
composition with pawn-plus-minor and equal-material blends, selected rook-fortress
geometry and score reductions against one rook or opposing pawns, bishop/pawn
and queen/pawn bound geometry and tightening, king/pawn race classification
and turn-sensitive support/opposition, selected multi-pawn bound consumers and
complete endgame adjustment/assignment/selection/clipping, ordinary-phase final score
finishing and its complete late-phase composition with preference, variation,
clipping, reversible-count rounding and independent score/bound orientation,
root-phase/personality production of effective draw preference and nonlinear
variation range, their final-score composition, placement-derived root/current
phase consumption with promotion-carry boundaries, fresh influence-derived pawn
classification and support/doubled-pawn base scores, pawn progress/path/king-distance
effects and ordered candidate score/terminal composition, selected pawn-only
and queen-pawn ending rules with actual material/candidate composition,
pawn-count fallback and material-adjusted, separately rounded structural/progress
weighting with candidate/ending composition,
fresh structural/piece-to-candidate/ending/subtotal production with explicit
pawn ordering and composed relation work,
central evaluation-influence comparison, spatial/nonlinear aggregation and
phase/personality weighting, with actual placement influence composition,
raw pawn-related piece
contributions and their relation work, actual phase gating/scaling composed
with fresh structure and supplied or placement-derived phase, local pawn pressure and
rook-line adjustment, selected structural penalties/subtotals and their
candidate/relation-work observations, and personality-command contracts.
They are not a
complete engine test suite, do not replace game parity, and do not prove
strength calibration. The fixture requests and expected values are
self-contained.
