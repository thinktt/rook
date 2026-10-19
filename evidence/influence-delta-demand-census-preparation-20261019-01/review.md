# Diagnostic influence demand census (not candidate31)

Exact parked30 source71 is preserved; new source71 graph `09a7cc641ae1c413d5bf8f37f31d6a1e7adf24547e0fbaa07fe0bd7fc3154038` changes only influence.rs, ordinary.rs, timed.rs and bin/rook2.rs.67 other files and all182 test bodies are unchanged. This diagnostic copy is never a production candidate or CPU/layout-neutral instrument.

Separate zero-initialized AtomicU64 counters use Relaxed fetch_add at every actual Influence::build entry, every actual unit update_ordinary entry, every ordinary empty-scratch fill (origin×eligible), and every fill call finding an already-ready scratch. Counter return values are ignored. Loads, sums, formatting, environment access and file I/O occur only in the reporter after run() returns. No count affects core decisions, N/R, ordinary Stats, retained/cache effects or branch eligibility. Ready hits mean reused fill calls, not all getter/map reads.

| Role tag | All production source owners |
| --- | --- |
|0 raw |unlinked remains the default for supplied/direct probes; its constructor cannot attest a link. Existing native tests stay raw unless they explicitly use a main factory. |
|1 root |fixed/seeded run_iterations_inner root predecessor and timed ActualEffects::execute root predecessor use the root wrapper. Both wrappers retain false eligibility. |
|2 current-null |the current context passed into the existing null recursion; same original position/map/checked/None data and false bit. |
|3 IIO |ordering_phase child predecessor, retaining its exact inputs and false bit. |
|4 main |the existing main_child factory, with ordinary_child still exactly movement.kind()==Ordinary. Special main moves therefore classify main/unlinked. |

Role wrappers only call the old unlinked factory and overwrite the census-only tag. No new trust source exists. Counting occurs inside the actual None fill, immediately before its unchanged fresh-vs-update branch; ready counting is the else arm. The shared completed-fill event remains once after the branch. Q is untouched. Global fresh entries include actual root/Q/other fresh callers; the remaining fresh count is unclassified, not inferred from old profiles.

Reporter write_influence_demand_census uses OpenOptions write/create_new and writes one JSON object plus newline. bin main preserves the exact original run() match ExitCode and original stdout/stderr, then checks ROOK2_INFLUENCE_CENSUS_PATH and attempts the report. It does not change the exit or streams even on report I/O failure: collector MUST require the bound path initially absent and a complete valid new report. Missing/partial/stale/unparseable reports are census failures, never silent successful observations.

Schema influence-delta-demand-census-v1 has fresh_build_entries, update_entries, ordinary_first_fill_by_origin (five ordered rows origin0..4, role, unlinked, eligible), ready_hits, ordinary_first_fill_total, ordinary_eligible_first_fill_total and ordinary_unlinked_first_fill_total. One fresh native process per original case gives whole-process scope with no reset. Expected accounting obligations are update_entries==sum(eligible), sum(unlinked)<=fresh_build_entries, row totals equal reported totals, and eligible rows0..3==0. Do not equate global fresh entries with ordinary first fills or import old-profile totals.

Parent plans exactly original strict cases35 and08 via released replay-check.mjs→root account_native.py→frozen census image, with explicit per-case report/native-accounting paths. Original inputs/bytes/protocol/known-single-process accounting remain the verification owners. No build/collection is authorized by this preparation, and no timings from this atomic/layout-modified image may be interpreted as performance. Whole-source/compiler/input/artifact binding and actual two strict replays are later parent-owned gates.

Source proof strips all instrumentation/role plumbing and recovers all four exact30 files bytewise; source30 is rehashed unchanged. Existing provenance, map arithmetic, lazy demand and fill-event semantics remain conditional on30's established source invariants. Native execution is still unrun for this copy. No Rust parsing/formatter, compiler/tests/engine, binutils/profiler/timing, Git or archive ran.

Preparation history: first source writer8b6476/1 found two generic closing blocks in binmain and stopped before writing that file; partial sources and exact failure are retained. Retry0075ba/0 used the unique main anchor. Final source/hash/stripping freeze b54987/0. This was a text-preparation correction, not an observed native failure.
