# Retained62: local external3,288-game handoff

**Local bindings only.** Retain candidate62. This directory identifies the exact
existing payload and evidence for a future off-Vic gameplay gate. It creates no
execution, transfer or READY authority. The full gate has not run. General
behavioral and performance qualification remain open.

The machine-readable [manifest](manifest.json) binds every named artifact,
receipt, released checker and policy document by path, SHA256 and size. Null
external fields are unresolved, not defaults or completed checks.

## Existing payload and provenance

Reuse the already prepared comparison payload, without rebuilding, stripping,
repacking or making another binary copy:

`/home/legolas/rook2-experiments/retained62-external-comparison-preparation-20261020-01/payload/`

| Existing file | SHA256 | Bytes / mode |
| --- | --- | --- |
| `rook2` — ordinary gate executable | `01237e6dfe89822e540d0f07c7b70f7227537a846ce8c69ea9e91167b759e98d` | 7118376 / 0555 |
| `rook2-diag` — separate JSON companion | `eda652abd182cb536736dd758d330f779e94b1e7ad0e779ff7792c2235fffde2` | 14038464 / 0555 |

Payload and original-image hashes/sizes/modes were rechecked without executing
them. All 117 files in the retained source map still match. Its graph is
`32f3da5d7713aa588b170322a9bea828975c07a79804764b0e919f08e18ebdb7`;
74 native/tool files have graph
`9729230374cb947d3e469140f634b670edf4df6ae87d9af4ab394f5bbc4e9cd0`.
These maps identify engine/diagnostic/build inputs, not the evolving entire repo.
Existing ordinary and diagnostic source archives were hash-checked in place.

The ordinary image was built with Rust1.85.1/LLVM19.1.7, generic x86-64 GNU/Linux,
O3/thinLTO/one codegen unit/panic-abort/debug1, existing own57 profile
`b4806420937681c8228903507018233d7176be0333ef98881a73d34c66df3a5c`
and profiled-only use-stage ExtTSP. Native engine and diagnostic source are
unchanged from57; only the build helper changed for62. DIAG is the exact57
generic non-PGO companion. No fresh62 training or canonical-path rebuild is
claimed. Default builds do not select62 automatically. External loader/library,
launcher and Node/runtime identities still need binding on the execution host.

## Existing finite evidence

| Evidence | Scope preserved |
| --- | --- |
| Mandatory conformance and units | Reused 195 native and 209 diagnostic tests; 7673 mandatory cases/117 operations/115 files on the exact retained DIAG and unchanged source. Not new62 executions. |
| Full54 | Exact62:216 fresh lifetimes,2496 posts,432 offline checks;67.640360 whole-native CPU s on Vic. |
| Wire | Exact62:8 original interruption fixtures/24 searches, complete streams,8 normal exits and independent reconciliation. |
| Regular12 | Exact62:48 fresh lifetimes,2528 searches/23204 posts;675.156653 whole-native CPU s.294 measured external-search CPU intervals remain null. |
| Continuity/seed controls | Prior exact57 ordinary `af849f92…`:12/632 plus continuity8,seed11,persistence3; inherited source evidence. Its executable hash differs from62. |

The manifest links exact reports, plans, raw-evidence roots and independent
receipts. Frozen records may describe their then-pending promotion; their scopes
and bytes remain unchanged. Resolve old `/home/legolas/rook2/evidence/...` raw
paths under `/home/legolas/rook2-experiments/original-worktree/evidence/...`.
Do not combine57's continuity receipt with62 receipts and label that a released
same-artifact focused pass. Same-artifact continuity disposition remains explicit.

## Released invocation and checker boundary

Authority: KingRE v2.5.0, commit
`1c89c21a4645ec85adf28285616d822b3cd91f73`. Ordinary gameplay replay requires
`--diagnostic-seed-command`. Before every search, the gate sends decimal
`king_seed N`, waits for `king_seed N`, then checks actual
`KING_SEARCH_SEED seed=N` consumption on stderr, every semantic post/move and
required terminal result. Preserve ordered inputs, reset/override lifetimes,
complete output and clean exits. Use the ordinary executable, not DIAG.

The released kit supplies only the focused 12-game and short continuity tools.
These are **reference commands, unexecuted here**:

```sh
node /home/legolas/king-spec/conformance/gate-replay/run.mjs \
  --report /fresh/path/games12.json -- /ABS/BOUND/rook2
node /home/legolas/king-spec/conformance/gate-replay/continuous.mjs \
  --report /fresh/path/continuous.json -- /ABS/BOUND/rook2
node /home/legolas/king-spec/conformance/gate-replay/combine.mjs \
  --report /fresh/path/focused.json --continuous /fresh/path/continuous.json \
  /fresh/path/games12.json
```

The first command covers all 12 games in one report. If collecting separate
per-game reports instead, supply complete coverage of all 12 IDs exactly once.
The runners append the diagnostic-seed option. This gate profile has ordinary
posts; the comparison payload's separate54-case work-post flags/schedule do not
supply a gameplay invocation or full-gate schedule. Released seed command and
seed persistence controls are separate required checks; their hashes are bound.

Focused waits: independent default/max 300000ms, continuity default 60000ms/max 300000ms
via `--timeout-ms`; independent streams retain the32MiB cap, continuity the8MiB
cap and five-second quit/cleanup handling. Focused
completion covers 12/632 plus 8 continuity searches and always leaves
`completeGameplayQualification:false`.

**No full 3,288-game corpus, runner command or completion checker is supplied by
this focused kit.** Those manifest fields remain null. The external operator
must identify the actual immutable full oracle and prescribed continuous-process
schedule. Independent-game parallel scheduling permission for12 does not redefine
that full schedule. No invented `--full` option or12-to3,288 substitution applies.

## Required external receipts and unresolved decisions

Before any separately authorized execution, bind receiver/operator authority,
full runner/checker/corpus hashes and dependencies, exact argv, host/runtime,
continuous process/reset boundaries, expected coverage, finite resource/output/
timeout limits and failure/retry policy. Preserve every attempt and failure.

Return native ELF identities before/after and actual exec arguments; launcher
hash alone is insufficient. Receipts must associate every prescribed game/search
with its process, complete raw input/stdout/stderr, seed acknowledgments and
consumption, posts/moves/results, normal exit or failure, and confirmed owned
cleanup. Require independent raw/artifact/coverage reconciliation, exact 3,288
completion and the qualification authority's explicit decision. These are
handoff requirements, not a fabricated released full-gate receipt schema.

Production-owner review remains open for the documented TT/window/IIO/stop/hint
compositions, remaining admitted caller/arithmetic and command/publication
obligations. The bounded zero-match capture proof does not close the general gap.

Report behavior, measurement validity and performance separately. Historical
cross-host totals are descriptive. Formal 54/12 performance still needs a fixed
same-hardware/resource/observation profile, repetitions/repeatability, uncertainty/
confidence, near-boundary follow-up budget, private-memory and no-swap policy.
The released 54/12 limits do not define a 3,288-game timing threshold. All current
performance/full-game qualification fields remain false or unresolved.

Preparation performed only reads/hashes and this local README/manifest update.
No engine/diagnostic run, build, profile, binutils, new timing, binary/archive
copy, external contact/transfer or READY signal occurred. Strategy and
qualification documents remain owned by imp2-lead and were not edited here.
