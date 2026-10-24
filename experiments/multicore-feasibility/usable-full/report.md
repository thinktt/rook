# Practical FULL integration: gain retained, one-CPU policy still needed

**Retain this integration for the next bounded configuration fix.** The cleaned
two-thread mode is5.84% below cleaned inline search wall on this four-case study,
and0.43% above the preserved winning two-thread generic control. Its one-CPU
control is correct/live but takes55.61s; treat that as a usability defect before
PGO. No retune, profile campaign, adoption or qualification occurred here.

## Identity and changes

Source `e44b7c3b4d12a0d4c975a16763bc7c830f354dcf` explicitly restores5612's engine
and Cargo.toml, then adds practical thread configuration and waiting. Failed
reversal/inventory/census source is removed from the current normal path and
preserved in prior commits/reports. Accepted main and frozen a977/f9ee remain
unchanged. See [plan](plan.md), [restoration](source-restoration.json),
[results/ranges](results.json), [closure bindings](proof.json).

Frozen new generic image:
`/home/legolas/rook2-experiments/usable-full-20261024-01/rook2-generic`,
7,539,816 bytes, SHA256
`462f62249c2e236d541939110133504f9df61350f6eba593e48ec217a9761b54`.
Raw focused/build/measurement receipts are in that containing directory.
Same generic GNU recipe/compiler as preserved64e control: Debian Rust1.85.1 /
LLVM19.1.7, x86-64, O3/ThinLTO/one CGU/panic-abort/debug1, **no PGO**.

Default1 starts no helper; positive requests configure `min(requested,2)` and
expose requested/configured counts through library getters and explicit CLI
inspection. This image does not yet cap by the number of permitted CPUs.
No mandatory CPU number or wall deadline remains in the engine. Lifecycle and
completion waiters use their associated mutex/predicate; bounded spinning and
conditional completion notification preserve the usual transport path. Terminal
errors remain explicit, shutdown joins, and normal public/search/direct-FULL
returns check scope closure. The numerical producer/composition, coordinator
pawn-cache/retained/R ownership and prescribed Host polls remain shared.

## Matched generic result

48 original strict replay lives:12 excluded warmups and36 retained observations
(three rotated repeats/configuration/case), plus3 separate idle probes. All648
ordered posts pass. The unchanged raw replay auditor and scoped external-placement
audit reconcile streams, launch/exit, hashes, schedule, CPU, placement and ranges.
Every stage exits0; no failed native attempt, replacement sample or retune.

| Sum of four case medians | Frozen current2 | Cleaned1 | Cleaned2 |
|---|---:|---:|---:|
| Search wall seconds |11.855924|12.646141|11.907192|
| Whole native CPU seconds |23.714664|12.651381|23.816353|
| Whole lifetime wall seconds |11.892348|12.677494|11.943680|
| Maximum observed RSS KiB |19828|19548|19748|

Cleaned2 saves5.8433% wall versus cleaned1 with1.88251x its CPU. Versus frozen
current2 it costs0.4324% wall and0.4288% CPU. This is a two-thread generic control,
not accepted serial; the study cannot establish serial overhead relative to the
accepted production image or reproduce the earlier own-PGO54 gain.

| Case | Cleaned2 vs cleaned1 wall | Cleaned2 vs frozen current2 wall |
|---|---:|---:|
|35|−9.83%|+0.64%|
|08|−2.77%|−0.65%|
|04|−7.50%|+0.64%|
|43|+1.02%|+0.08%|

Cleaned2's retained ranges lie below cleaned1 in35/08/04 and above it in43.
Only04 has separated ranges versus frozen current2 (a loss). Preserve all cases;
no selector or overhead-only explanation follows. Full samples/ranges are in
results.json. All three250ms startup-idle probes register0 CPU ticks at10ms
resolution; this is not proof of literally zero cost or every idle interval.

The native inherits14/6, then the external supervisor pins/verifies main14 and
helper6 before an external gate releases the first setup write. Original pipes
and comparator are retained, with no protocol relay. Search wall is go-write to
move-data; wait4 CPU/RSS/lifetime includes all native threads, startup/placement,
parking/joined shutdown and a small Python pre-exec prefix. Builds/harness use
0–5,8–13; owned15/7 are unused. Point placement/guest ticks do not prove host
isolation. Captured stdin excludes end(data) cleanup; pinned runner/output/exit
retain that boundary. No PMU or current KingWCR comparison.

## Focused behavior and remaining work

20 distinct unit checks pass:8 worker protocol,7 numerical/cache/budget,
3 root/Host/public-Q/first-iteration lifecycle,1 explicitly selected delayed-helper
test and1 CLI parser. The11s control holds a test-only helper barrier before
computation; it does not suspend an OS thread. Completion-before-wait, terminal
wakes, abandoned requests, scope errors, root rebinding, supplied Influence,
retained values and relation charges are covered. Production panic-abort still
does not run unwind cleanup. Archived default-off features were not revalidated.

Nine native CLI controls verify default/1/2/8 inspection and invalid requests.
One separate original08 projected replay passes10 posts with both task masks
observed as CPU14 after startup, with no engine widening. It completes in55.61s
under the external180s cap. This is liveness evidence, **not acceptable single-CPU
performance**. The lead selected a subsequent source fix: when authoritative
permitted affinity contains exactly one CPU at configuration, retain the request
but configure one thread. That change is absent from this image and these results.

The measured multi-CPU gain survives this cleanup, with case43 and extra CPU still
material. Close this record unchanged; address the one-CPU configuration policy
next. Fresh PGO/full54 and exact-image behavioral adoption evidence remain later
decisions. No scaling beyond2, combined policy or external delivery is established.
