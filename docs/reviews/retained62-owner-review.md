# Retained62 specification-owner review map

Prepared by imp2-lead, 2026-10-20. **Specification-owner decision: pending.**
This is the current entry point for production review; the
[historical ownership map](../production-map.md) retains the detailed chronology.
An internal scoped acceptance below is supporting evidence, not the
specification owner's acceptance of the deliverable. The owner may identify
further concrete obligations during review.

## Deliverable and authority

The released [acceptance contract](/home/legolas/king-spec/spec/README.md#required-deliverable-and-acceptance-surface)
requires exact mandatory fixtures and a requirement-to-implementation/test
review of ordinary production behavior. It covers interfaces, admitted domains,
state/reset lifetimes, numerical rules, production producers, stopping and output.
It expressly does not demand an exhaustive equivalence theorem. Any actual
discrepancy needs correction or a versioned specification amendment.

The [retained62 handoff](../../experiments/retained62-game-handoff/README.md)
and its [manifest](../../experiments/retained62-game-handoff/manifest.json)
bind source, build, executables and existing receipts. The ordinary SHA256 is
`01237e6dfe89822e540d0f07c7b70f7227537a846ce8c69ea9e91167b759e98d`;
the separate diagnostic SHA256 is
`eda652abd182cb536736dd758d330f779e94b1e7ad0e779ff7792c2235fffde2`.
The 117-file source graph is
`32f3da5d7713aa588b170322a9bea828975c07a79804764b0e919f08e18ebdb7`.
Native/diagnostic source is unchanged from57;62 changes only the build helper
to select profiled ExtTSP at profile use. It explicitly reuses own57 profile
`b4806420…`. See the [exact recipe](../production-build.md).

Scope is the released ordinary, nonpondering native profile and the mandatory
external diagnostic adapter. Diagnostic supplied state does not replace native
state producers. Controlled component domains, arbitrary public library mutations,
custom Host callbacks and panic recovery do not broaden the ordinary contract.
Conversely, a bounded diagnostic limit does not silently restrict production.
The 62-iteration ceiling is supported by
[terminal stopping](/home/legolas/king-spec/spec/iteration-terminal-stop.md),
not an extra personality limit.

## Requirement, owner and evidence crosswalk

All rows await the specification owner's disposition. The linked acceptances
preserve their named premises and finite evidence; none certifies all inputs.
The mandatory fixture bundle supplies component coverage throughout the table:
7,673 cases,117 operations,115 files, with195 native and209 diagnostic tests.
Those are inherited unchanged-source/exact-DIAG results, not fresh62 executions.

| Normative family and admitted domain | Actual producer → consumer / test surface | Current support and premises |
| --- | --- | --- |
| [Ordinary ingress](/home/legolas/king-spec/spec/ordinary-play-ingress.md), [setup](/home/legolas/king-spec/spec/position-setup.md), move sequence, history and repetition | [Session](../../src/session.rs), [Position](../../src/position.rs), [identity](../../src/identity.rs), [history](../../src/history.rs) → root and generated/null descendants; diagnostic positions/joined-search adapters and ordinary game replays | [Placement/phase acceptance](../../evidence/current57-placement-admission-review-20261020-01/parent-acceptance.json) closes named native arithmetic domain and structural preservation. Exceptional EP king-victim continuation fails before evaluation. Structural coherence is not a claim of unrestricted chess legality; admitted setup/history contracts still govern. |
| [Candidate production](/home/legolas/king-spec/spec/search-candidate-production.md), order, tactical candidates, attacks and [relations](/home/legolas/king-spec/spec/evaluation-relations.md) | [Movegen](../../src/movegen.rs), [attacks](../../src/attacks.rs), [tactical](../../src/tactical.rs), [Influence](../../src/influence.rs), [relation table](../../src/relation_table.rs) → ordinary/Q/evaluation; generation/relations/order adapters | [Coherence review](../../evidence/production-source-audit-parent-review-20261019-01/decision.json), [retained pin-summary review](../../evidence/bitplane-pin-summary-production-review-20261020-01/review.md) and [wrapping Influence proof](../../evidence/influence-bitsliced-sum-production-review-20261019-01/review.md). Native permission requires owned coherent placement; public supplied routes retain their specified authority. Ordered inventories and semantic charges remain part of the contracts. |
| [Personality](/home/legolas/king-spec/spec/personality-configuration.md), fixed root context, material/phase, full/fast evaluation and retained pawn state | [Parameters](../../src/parameters.rs) → [root material/phase](../../src/evaluation.rs), [Evaluator/Node](../../src/evaluator.rs) and pawn/activity/shelter/positional/endgame owners; fresh/retained/context/score adapters | [Retained origin](../../evidence/current57-retained-origin-review-20261020-01/parent-acceptance.json), [capacity](../../evidence/current57-evaluator-capacity-review-20261020-01/parent-acceptance.json), [selection/consumer crosswalk](../../evidence/current57-evaluation-window-review-20261020-01/parent-acceptance.json), [shelter arithmetic](../../evidence/current57-shelter-arithmetic-domain-review-20261020-01/parent-acceptance.json) and [race producer](../../evidence/current62-race-producer-parent-review-20261020-01/acceptance.json). These import actual root, cache-origin and placement premises; normal Result restoration does not promise arbitrary unwind recovery. |
| [Learned lifetime](/home/legolas/king-spec/spec/learned-state-lifetime.md), [remembered results](/home/legolas/king-spec/spec/remembered-results.md), [cutoff memory](/home/legolas/king-spec/spec/cutoff-memory.md) | Session/root preparation → [remembered table](../../src/remembered.rs), [Learning](../../src/ordinary_policy.rs), four ordinary store sites; learned/cached adapters | [Learned-state acceptance](../../evidence/current62-learned-remembered-parent-acceptance-20261020-01/acceptance.json), [numeric identity/collision](../../evidence/current62-remembered-collision-parent-review-20261020-01/acceptance.json), [store clauses](../../evidence/current62-remembered-store-parent-review-20261020-01/acceptance.json), [window forwarding](../../evidence/current62-tt-window-transform-parent-review-20261020-01/acceptance.json). Collisions intentionally need no board-equality certificate. Directional score proof closes the first-half inherited-hint route; **Q1 below remains**. |
| [Ordinary recursion/IIO](/home/legolas/king-spec/spec/ordinary-iterations.md), extensions, null/scout/retry, [Q tree](/home/legolas/king-spec/spec/quiescence-tree.md) and pruning | [Ordinary](../../src/ordinary.rs), [ordinary policy](../../src/ordinary_policy.rs), [Q](../../src/quiescence.rs), [Q policy](../../src/quiescence_policy.rs) → actual descendants and returns; bounded ordinary/Q traces | [Extension/flag transport](../../evidence/current51-extension-parent-review-20261020-01/acceptance.json), [IIO eligibility/sequence ledger](../../evidence/current51-iio-eligibility-parent-review-20261020-01/acceptance.json) and [native capability entry](../../evidence/current51-iio-entry-source-review-20261020-01/README.md). Fresh depth and accumulated flags have distinct owners; tail uses original window and saved entry metadata. [Directional scores and weak window ordering](../research/permission-sensitive-search-bounds.md) narrow **Q2 below to equality**. Explicit bounded diagnostic IIO exclusions are not a production omission. |
| [Root schedule](/home/legolas/king-spec/spec/root-work-schedule.md), [randomization](/home/legolas/king-spec/spec/root-randomization.md), aspiration, clocks and terminal stop | [Root schedule](../../src/root_schedule.rs), [timed sequence](../../src/timed_sequence.rs), [timed](../../src/timed.rs), [timing](../../src/timing.rs), [clock](../../src/clock.rs), [work clock](../../src/work_clock.rs) → ranked roots, allowances, work polls and completion; root/timed/work adapters,54 replay | Production drives its own scores, counts and clocks. Same-move adjustment is applied to both endpoints; clamping may preserve only weak order. Work-clock wrap, rounding and host lifetime use the released arithmetic domains. [Q2](#q2-first-main-cutoff-at-an-equal-window) isolates the remaining specific control join; performance accounting is separate. |
| [Persistent session](/home/legolas/king-spec/spec/persistent-ordinary-session.md), [seed lifetime](/home/legolas/king-spec/spec/seed-lifetime.md), [gate seed](/home/legolas/king-spec/spec/gate-seed-command.md) and resets | [Session](../../src/session.rs), [CLI](../../src/bin/rook2.rs) → placement/history, parameters, clocks, evaluating-search preparation and gate override; persistent/clock adapters,12 games and seed/reset controls | Native production seed source remains distinct from opt-in gate override. Fresh [exact62 continuity8/seed11/persistence3](../../experiments/retained62-focused-closure/README.md) now passes, separately from the historical57 receipts. Reviewed equivalence binds the existing62 independent games to the same actual native image/configuration. |
| [Ordinary wire](/home/legolas/king-spec/spec/ordinary-xboard-wire.md), [interruption](/home/legolas/king-spec/spec/interrupted-sessions.md), [post lifecycle](/home/legolas/king-spec/spec/post-lifecycle.md), PV/status/fatal output and opt-in work formatter | Single [CLI Input](../../src/bin/rook2.rs)/[wire](../../src/wire.rs) → [Host](../../src/host.rs)/timed poll → [capture lifecycle](../../src/post_lifecycle.rs)/[output](../../src/output.rs)/Session; wire controls and output adapters | [Framing/FIFO source disposition](../../evidence/production-wire-framing-parent-review-20261019-01/decision.json), [four directed43 CLI witnesses](../../evidence/production-wire-directed-parent-review-20261019-01/acceptance.json), fresh [62 wire8/24](../../evidence/exttsp-profiled-wire-parent-review-20261020-01/acceptance.json). The directed runtime work is already accepted; its earlier future-work wording is superseded. Record/token, search-time command and ordinary stderr exclusions remain exactly those in the wire profile. |
| [Diagnostic transport and admission](/home/legolas/king-spec/spec/diagnostic-interface.md), mandatory fixture surface and independence | Separate [diagnostic dispatcher](../../diagnostic/src/main.rs) and admission modules → native owners; immutable external fixture inputs/comparators | All mandatory operations are covered; the two analysis operations are optional. Source/build maps bind the ordinary and adapter partition. Review must confirm native producers and the absence of fixture-answer substitution; component-supplied inputs are not evidence that production generated them. Exact fixture success is necessary and finite. |

## Two explicit source questions

### Q1: second-half inherited hint at normal learning

After FULL evaluation, a second-half effective lower can exceed incoming L.
If no main candidate replaces the entry hint, normal completion may still
exceed L and call cutoff learning. The remembered hint is not a legality
certificate; [Learning's empty-source guard](../../src/ordinary_policy.rs#L413)
has no independently specified skip semantics. The direct cutoff diagnostic
imports occupied-source candidate admission, so a synthetic empty-source event
there is not an admitted counterexample.

The [completion note](../research/uncertified-hint-completion.md) and
[directional proof](../research/permission-sensitive-search-bounds.md) exclude
inherited, unreplaced hints at every native **first-half** normal completion.
Two completed four-piece key enumerations exclude only their proposed sibling
recipes. No actual public second-half violating prefix is established.

**Needed disposition:** establish exclusion at this remaining native consumer,
or exhibit an admitted public prefix and obtain specification-authority behavior
clarification. Do not invent a moving piece, skip rule or fallback. Existing
conditional arithmetic and enumeration results should be reused.

### Q2: first-main cutoff at an equal window

The [IIO contract](/home/legolas/king-spec/spec/ordinary-iterations.md#internal-iterative-ordering)
says a first main result reaching U ends candidate processing. The later main
rule and [actual code](../../src/ordinary.rs#L1069) nest cutoff inside strict
best and running-lower improvement. The accepted local IIO proof used L<U.
The new [native ordering proof](../research/permission-sensitive-search-bounds.md#native-weak-window-ordering-and-the-remaining-cutoff-question)
establishes L<=U for actual root descendants. On surviving FULL bounds, a first
main result s>=U skips that cutoff **exactly when s=L=U**. Inverted windows
are excluded under those premises; universal strictness is neither assumed
nor required as a separate release rule.

The [released-contract consultation](/home/legolas/agent-memos/20261020-first-main-equality-released-reading.md)
reads the explicit first-main sentence as requiring immediate completion if the
joint state is admitted. It does not permit preference/PV changes at equality,
establish reachability or issue a specification amendment. No explicit numerical
composed L<U admission/rejection rule was identified in that bounded reading.

**Needed disposition:** exclude this joint equality event at the relevant
consumer, or establish that the implementation follows the prescribed composed
behavior. The isolated [first-main correction](../../experiments/first-main-cutoff-correction/README.md),
committed at `42d98f71`, now implements the latter condition and passes its bounded
correctness discriminator. Retained62 itself remains unchanged. The additive
guard runs after existing updates and before index advancement/tail dispatch;
strict cutoffs already leave through the old branch. At the new equality edge,
best becomes U without changing preference/PV or invoking parent normal learning;
normal storage retains the original query and grants neither score permission.
Prior child/quiet-mate effects remain, and child stops still propagate first.

**Lead disposition:** accept the isolated correction's source semantics and
finite discriminator. Identical actual-owner tests on old logic fail only the
equality regression, specifically by entering the disabled-IIO tail; the below-U
and strict-window controls pass. Corrected source passes all 196 library tests and
1,008 mandatory cases in 22 files/20 operations. These controlled TT/window
contexts are not admitted public equality witnesses. The accepted strict
recursion lemma applies to actual ordinary/Q entries; a strict requested root
window before transformation is a different premise.

Lead source/receipt check `3c9128/0` confirms 39 frozen pins, 117 unchanged canonical
files, both 118-file isolated snapshots, the exact guard inverse, artifact hashes
and absence of all 2,016 native/supervisor PIDs. Independent reconciliation binds
the original negative control and all raw fixture exchanges. Its SHA256 is
`8418a8e00533cec55ab3fd3261139e281ca7d5a99b6b7d9fd6cc3988ab272d76`.
The candidate DIAG is `68a1c304`; 1,007/1,008 post-exec observations exist, with the
one unavailable short-lived observation preserved explicitly. All 1,008 audited
exec/wait/exit0 chains remain. No repairs, timing or production promotion occurred.

The [same-image mandatory completion](../../experiments/first-main-cutoff-correction/mandatory-completion/README.md),
committed at `4978efc0`, now passes: 93 additional files/6,665 cases combine with
the preserved first report to cover all 115 mandatory files/7,673 unique cases/
117 operations. All 209 diagnostic and two development tests pass; the 196
library tests are reused. The lead accepts this finite union on unchanged
DIAG68a1c304 and corrected source. Check `50d630/0` verifies 141 frozen pins,
canonical/candidate source maps, both report hashes, exact disjoint coverage, and the actual
contents of the two excluded optional-operation files. Independent closure
SHA256 is `1cdedcbf2b6c867880e88d197670391519c8ec9b686fc102324755324d0c0b86`.
All 7,673 exec/wait/exit0 chains reconcile; two post-exec point observations are
unavailable and remain disclosed. No runtime repairs or diagnostic rebuild occurred.

One fresh own-source PGO production build and paired full54 comparison against
retained62 are selected next. This measures the correction's complete-search
cost without an optimization gain threshold; it does not promote the candidate.
Production gameplay receipts and specification-owner acceptance remain separate.
Tail execution in
the old implementation additionally needs an unconsumed suffix, D>=5 and entry
bound exactly Lower; endpoint clamping alone remains no witness. Existing
target, extension, metadata and stable-permutation proofs are unchanged.

## Separate qualification receipts and decisions

| Obligation | Current disposition |
| --- | --- |
| Exact mandatory adapter fixtures | Existing exact retained DIAG evidence:7,673 cases/117 operations/115 files. Reuse is labeled; no new run claimed. |
| Specification-owner production acceptance | **Pending for this map and Q1/Q2.** Internal acceptances and the bounded Q2 consultation are supporting evidence; no specification-owner acceptance is recorded. |
| Same-artifact focused gameplay | **Local evidence complete via reviewed equivalence**, [de478938](../../experiments/retained62-focused-closure/README.md): deterministic original repeat0 gives12/632/5,801 posts; fresh62 continuity1 process/4 segments/8 searches/90 posts, seed11 children and persistence3 pass. All48 original game lifetimes remain preserved. The custom evidence route is accepted internally below; no released `combine.mjs` pass or final qualification is claimed. |
| External full3,288-game gate | Local [handoff](../../experiments/retained62-game-handoff/README.md) complete. Full runner/corpus/schedule/checker, operator authority and receipts remain unresolved. Assigned off Vic; focused success cannot substitute. |
| Performance qualification and parity |62 whole54=67.640360 CPU s; whole12=675.156653 CPU s. Historical reference ratios1.066348/1.048017 span different hosts/windows and are descriptive. Compatible54/12 comparison profiles, uncertainty and resource conditions remain open. Released acceptance1.10 aggregate/1.25 each differs from parity1.00. |

Lead disposition of the focused evidence, 2026-10-20: accept the supplied
native-artifact/configuration equivalence and finite local coverage under the
released [prior-evidence rule](/home/legolas/king-spec/conformance/gate-replay/README.md#independent-games-and-parallel-collection).
Original reports identify Python and distinct accounting destinations, so they
are preserved rather than rewritten to satisfy literal collector fields.
The reviewed chain binds unchanged native ELF01237e6d, its actual arguments,
complete original inputs/events and clean exits to the new same-image controls.
The new controls have13 lifetimes: five exit0 and eight prescribed fatal exit1,
with11 total searches. Source review covered the supervisor, capture and offline
reconciler; the lead additionally checked29 report path/hash/size bindings,
38 frozen plan pins, all13 post-exec observations,12,331 raw bytes and absence
of all26 native/supervisor PIDs. No oracle or engine was rerun by that check.
Result SHA256 is `c809e3263c6c32e6aba8f009411ba8861738987da84e0aa9449267c5a54dcac2`.
This closes the missing exact62 local receipt work; specification-owner acceptance,
the full gate and performance qualification remain separate.

The [last-mile strategy](../last-mile-strategy.md) ends the current optimization
batch. The isolated Q2 correction is correctness work and is not promoted.
This map consolidates evidence for review now. It does not impose another general
proof campaign or require new runtime evidence merely because a historical note
says “all compositions.”
Any further source concern should name the relevant contract and missing premise.

Prepared from retained source, existing receipts and the
[implementation owner's bounded discriminator](/home/legolas/agent-memos/rook2-imp2-to-lead-production-review-discriminator-20261020T194906Z.md).
Raw historical paths resolve under
`/home/legolas/rook2-experiments/original-worktree/evidence/`; frozen bytes are
unchanged. The separate focused-control assignment does not alter these
source-review conclusions or grant external transfer/execution authority.
