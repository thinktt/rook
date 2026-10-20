# Remaining qualification work

Candidate62 is the retained production build, 2026-10-20. It adds an explicit
`--ext-tsp-profiled` profile-use-only option in `tools/build.py`. Native engine
and diagnostic source are unchanged from57. The exact ordinary image is
`01237e6dfe89822e540d0f07c7b70f7227537a846ce8c69ea9e91167b759e98d`;
the retained diagnostic is `eda652abd182cb536736dd758d330f779e94b1e7ad0e779ff7792c2235fffde2`.
The existing own57 profile `b4806420` is reused explicitly; no fresh training or
canonical-path rebuild is claimed. Source117 graph is `32f3da5d` and native/tools74
is `97292303`.

The new ordinary artifact passes the paired fixed70 comparison (1.043875178%
lower CPU,7/7 cases lower), full54 (216 fresh lifetimes,432 offline checks,
2496 posts), wire8/24 and regular12 (48 fresh lifetimes,2528 searches,23204 posts).
Whole54 costs **67.640360 CPU seconds**; whole12 costs **675.156653 CPU seconds**.
The separate57-window reductions are2.042965% and2.120477%, with54/54 and12/12
medians lower. These are descriptive comparisons. CPU15 recorded0 nonidle ticks
in54 and5 nonidle/1iowait ticks in12;294 measured per-search CPU values in12
remain null, without imputation.

Existing195 native tests,209 diagnostic tests and7673 mandatory cases across
117 operations/115 files are reused source/artifact evidence for unchanged
engine/diagnostic source and the same diagnostic companion. They were not
newly rerun for62. Original57 continuity8/seed11/persistence3 results are also
inherited evidence. New main-artifact coverage is stated separately above.

Final behavioral/performance qualification remains open. Raw historical-reference
ratios are1.066348 for54 and1.048017 for12, with maximum individual ratios
1.167576 and1.123680. Different hardware/windows, uncertainty and resource scope
prevent treating these as qualified acceptance. The external3288-game gate
belongs off Vic; no new Bee/export/READY grant follows.

See [source promotion](../evidence/exttsp-profiled-integration-20261020-01/source-promotion.json),
[whole54](../evidence/exttsp-profiled-standard54-results-20261020-01/README.md),
[whole12](../evidence/exttsp-profiled-games12-results-20261020-01/README.md),
[build recipe](production-build.md) and [decision0048](decisions/0048-exttsp-profiled-layout.md).

The [learned-state source acceptance](../evidence/current62-learned-remembered-parent-acceptance-20261020-01/acceptance.json)
accepts remembered numeric/metadata ownership, direct diagnostic transport,
direct cutoff history bounds10504/5636, and normal evaluating-lifetime retention
under stated premises. The later acceptance below closes prescribed numeric
TT collision/table association; uncertified-hint completion, full TT/window/IIO
joins and general lexical/framing behavior remain open.
Existing detailed ownership obligations below remain applicable where not
superseded by this explicitly scoped evidence.

The [remembered-collision acceptance](../evidence/current62-remembered-collision-parent-review-20261020-01/acceptance.json)
closes the prescribed numeric `(group, secondary)` identity, retained/recent
collision handling and saved-query association with the four syntactic store
sites. The released contract intentionally permits placement collisions; no board
equality or hash-injectivity premise is required. This does not certify the
admission or correctness of every stored score/hint/window, full TT/IIO/stop
composition, or uncertified/empty-source hint completion. No new runtime evidence
or source change supports this scoped closure.

The [local store-clause acceptance](../evidence/current62-remembered-store-parent-review-20261020-01/acceptance.json)
adds the four sites' operational gates, payloads and order under their imported
entry/producer/capacity premises: fast/shallow cutoff storage and return,
checking-mate update/storage followed by continued search, and clipping before
normal completion storage. Early returns/stops skip later completion without
rolling back prior or descendant effects. This does not prove full producer,
window, TT/IIO or uncertified-hint admission, and adds no runtime evidence.

## Preserved ownership obligations and historical checkpoints

The following text records the preceding57 state. Artifact and timing claims
there are historical; unresolved normative obligations remain open. Exact prior
bytes are preserved in [qualification-gaps-history-20261020-03.md](qualification-gaps-history-20261020-03.md).


Current retained source is candidate57, native/tools graphb845e921 and combined
117-file grapha58e7cad. Ordinaryaf849f92 uses its own profileb4806420; diagnostic
eda652ab remains a separate companion. Exact source promotion claims no canonical
rebuild. See [source promotion](../evidence/bitplane-pin-summary-integration-20261020-01/source-promotion.json),
[current ownership map](production-map.md) and [decision0043](decisions/0043-bitplane-pin-summary.md).
The preceding qualification notes are preserved [byte for byte](qualification-gaps-history-20261020-02.md);
artifact-specific claims there remain historical.

## Closed local finite evidence

195 native tests (193library+2development),209 diagnostic tests, all7673 mandatory
cases across117operations/115wholefiles, optimized strict54/eight interruption
fixtures/24searches and regular12/632 plus continuity8/seed11/persistence3
independently pass. The functional archive preserves original inputs,
expected/raw/actual responses and process exits. Finite fixture success does
not prove every admitted input or close all production compositions.

Current57 standard54 independently closes216 fresh lifetimes (54warm/162measured)
and432 original offline checks at69.051049 whole-native CPU seconds,68.640 search.
Compared to51 in a separate window, the descriptive reduction is0.527456%,48/54
case medians lower. CPU15 shows53 nonidle guest ticks. See [whole54](../evidence/bitplane-pin-summary-standard54-results-20261020-01/README.md).

Current57 whole12 independently closes48 fresh lifetimes/2528searches and23204
semantic posts at689.783349 whole-native CPU seconds,1.246666%lower than51's
separate window,12/12game medians lower. CPU15 shows2nonidle/2iowait ticks;
285measured per-search CPU values remain null. See [whole12](../evidence/bitplane-pin-summary-games12-results-20261020-01/README.md).
The raw historical-reference ratios1.088588/1.070721 are report-only; no exclusive
host condition, universal hardware conversion or final qualification follows.

Experiments58,59,60 are parked after fixed generic comparisons; no retry, PGO
or adoption follows.60 passed195 library tests and70 original live/offline
replays but costs1.036641% more CPU,0/7lower. Production57 stays unchanged.

The [capacity disposition](../evidence/current51-capacity-parent-review-20261020-01/README.md)
closes remaining-depth i16, produced-target i32, history u32 and Activity capacity
under its named caller premises. Current57 [Shelter](../evidence/current57-shelter-arithmetic-domain-review-20261020-01/parent-acceptance.json)
and [joined evaluator capacity](../evidence/current57-evaluator-capacity-review-20261020-01/parent-acceptance.json)
close named arithmetic joins, and [native retained-origin induction](../evidence/current57-retained-origin-review-20261020-01/parent-acceptance.json)
closes normal evaluating-lifetime P/G and private cache-payload provenance under
imported producer premises. The [placement/phase acceptance](../evidence/current57-placement-admission-review-20261020-01/parent-acceptance.json)
now ties the named native arithmetic domain to actual root/descendant owners;
the [local evaluation-selection crosswalk](../evidence/current57-evaluation-window-review-20261020-01/parent-acceptance.json)
closes its named native-stage caller facts and immediate consumers. Collision
semantic identity, arbitrary public mutations, full window/TT/IIO/hint composition
and cumulative counters remain separate. Normal Result restoration is not general panic recovery.

## Remaining obligations

- Qualify performance with a compatible comparison, repeatability/uncertainty,
  resource/private-memory/no-swap scope and finite follow-up procedure before
  applying the released aggregate1.10/every-case1.25 limits independently to
  whole54 and whole12. Historical Rust-PGO reference totals are63.431779 whole54
  and644.222971 whole12 CPU seconds. Different hardware/windows and accounting
  must be resolved as prescribed; raw ratios are reported only. PMU is unavailable
  on Vic. No privileged deployment or new external run is authorized here.
- Finish individual normative production obligations in the ownership map:
  remaining evaluator/endpoints/intermediate arithmetic and admitted caller premises; composed TT score,
  depth, age and lifecycle semantics; remembered-hint composition; natural IIO
  tail/multipass/extension/interruption; command/framing/poll/publication behavior;
  and all admitted diagnostic/schema combinations beyond finite fixtures.
  Existing scalar/normalized-score capacity10063 induction is conditional on its
  imported producer premises. Preserve those scopes rather than treating broad
  green fixtures as proof.
- Resolve the [uncertified-hint completion question](research/uncertified-hint-completion.md)
  through a justified production exclusion proof or public reachable input and
  specification-authority clarification. No admitted witness is established.
  Empty-source descriptors are outside the direct cutoffMemory diagnostic domain;
  do not infer a moving color/type, skip rule or fallback from that component.
- Prepare exact source/build/artifact/evidence handoff for the external3288-game
  gate. The owner assigned it off Vic; do not run it here. Local12 success does
  not establish the full gate. No new Bee benchmark/export grant follows from
  these local results.

Normal production IIO is enabled: timed and ordinary entries pass the true
capability through recursive owners. The explicitly bounded generic diagnostic
entry passes false and can reject at actual IIO entry. This is a source-level
boundary fact, not closure of all IIO semantics. See the [current entry review](../evidence/current51-iio-entry-source-review-20261020-01/README.md)
and the earlier [diagnostic-domain review](../evidence/current25-iio-diagnostic-domain-20261019-01/review.md).

The [window-composition source review](../evidence/current51-window-admission-review-20261020-01/review.md)
proves recursive strictness conditionally. Root numeric contracts explicitly
permit clamping collapse, so universal strictness is not imposed as a new
requirement. The supplied algebra examples do not establish public production
reachability or a defect; actual composed-domain behavior remains open.

## Reference and calibration limits

KingRE Rust v1.1.1 generic PGO bf71485c is the performance reference. Supplied
GCC/Clang historical columns are not that reference. The authorized opaque Rook
executable is only a calibration vehicle; its per-case Vic/reference ratios
0.906–0.972 (summed-median ratio0.938863) are program/case-specific evidence,
not a universal VM conversion or KingRE acceptance.

Only candidate25 completed the audited Bee round trip. Its same-artifact standard54
search totals are75.770s on Bee and72.630s on Vic; the4.323%difference is
window/accounting-specific and does not isolate VM overhead. Functional packet
22/23 coverage and unavailable sibling-restoration composition retain their
[documented scope](../evidence/candidate25-functional-coverage-review-20261018-01/review.md).
Final qualification remains open; intermediate speedups and local gates are
progress rather than mission completion.


## Current62 consumed late endpoints — verified reuse

The earlier numerical crosswalk's directional pawn-race FULL proof transfers
to current62 under the accepted placement, fixed-root and cache-origin premises.
The updated winning-race endpoint has magnitude at most7477; the opposite
endpoint may remain10000. This is not an unconditional bound on every emitted
FAST endpoint: sparse native race positions force FULL before bound consumption,
and terminal-Q FAST returns score only. Native consumed endpoints remain within
±10000. This closes that producer/caller premise; composed TT/window/IIO/hint
semantics remain open. The preceding coarse review is preserved and its overlooked
stronger existing proof is explicitly corrected by the follow-up.
See [parent acceptance](../evidence/current62-race-producer-parent-review-20261020-01/README.md)
and [current-source crosswalk](../evidence/current62-race-producer-correlation-review-20261020-01/review.md).
