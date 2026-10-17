# Imp2 measurement and fidelity design

Date: 2026-10-17. Status: a proposed local engineering procedure, **not a
performance qualification**. This investigation ran no engine or calibration
workload. The later recorder validation used only a tiny native synthetic
helper, as detailed below. The design reads the mission, released KingRE v2.5.0 performance
and profiling contracts, and approved performance handoff. No Imp1 engine
source or private architectural findings were consulted.

## Acceptance obligations

The mission starts with an efficient integrated search and progressively
tightens fidelity. A fast partial implementation is useful evidence, but the
finished engine must satisfy the behavioral specification and its required
qualification routes as well as the performance decision policy. Record three
independent dispositions for every study: **behavior**, **measurement validity**,
and **performance**. A mismatch does not disappear because a sample is fast.

The approved reference is generic x86-64 KingRE-PGO candidate v1.1.1, executable
SHA256 `bf71485c48e780e29f32813219e4283cc54c04015abce0bccda62c190e2ba080`.
It is private; this design does not assert possession, execution, or full
gameplay qualification of that artifact. Its 54 production inputs also served
as PGO training inputs. Native targeting, another generic build, an observation
adapter, and an opaque calibration executable are different artifacts.

The primary acceptance cost is **whole-lifetime owned engine user+system CPU**,
including setup, allocations, output and normal destruction. With all required
cases present, compatible accounting and observations on the same hardware
under comparable resource/observer profiles, use:

`R_cpu = sum(candidate case medians) / sum(reference case medians)`.

| Collection | Optimization target | Accepted aggregate limit | Individual guardrail |
| --- | --- | --- | --- |
| All 54 fresh-process production searches | <= 1.00 | <= 1.10 | Every case <= 1.25 |
| All 12 complete selected game units | <= 1.00 | <= 1.10 | Every game unit <= 1.25 |

All four conditions must hold separately. Do not blend collections, omit a
failed case, change weights, or let a favorable aggregate offset an individual
regression. Twenty-three functional units and retired instructions/cycles are
diagnostics; they impose no subsystem ceilings or mandatory internal layout.

The released policy leaves final repeatability tolerance, uncertainty method,
confidence level, near-boundary handling and maximum follow-up budget unset.
These and the comparison resource/observation profile must be frozen and
validated before a formal performance decision. Until then use `reported-only`.
An interval crossing a limit is inconclusive. Neither measured noise nor
calibration adds an extra allowance to 1.10 or 1.25. Finite benchmark agreement,
full behavioral qualification, performance acceptance and publication are
separate decisions.

## Fidelity ladder: make useful work measurable early

Each stage records implemented rules, deliberate omissions and exact tests
executed. Advance architecture experiments without requiring every later stage
to be complete. Stage labels describe evidence, not an automatic certificate.

| Stage | Practical experiment and minimum behavior evidence | Permitted interpretation |
| --- | --- | --- |
| F0: integrated search prototype | Real recursive search through candidate production, apply/restore, evaluation, ordering and tactical frontier; legal selected move, restored root state, finite completion, deterministic result under the same declared internal inputs. Check representative special moves/history and root legality. | Local cost of this prototype and task only. No KingRE speed ratio, equivalent-work claim, or production conformance claim. |
| F1: frozen internal workload | A small diverse position/history set and fixed completed-search request. Freeze search/evaluation policy and stopping rule for an A/B experiment. Record score, depth, PV, selected move, semantic work and known differences. | Same-policy architecture comparison when work/results agree. Changed search policy gets its own baseline and a changed-work label. |
| F2: released semantic anchors | Implement selected public functional sequences and the three composed controlled searches; check exact projections and required reset/retention lifetime. Add targeted conformance for rules actually used by measured searches. | A same-sequence diagnostic comparison, with scope and missing rules disclosed. Not an exclusive pipeline timer or full-engine parity. |
| F3: natural production searches | Use all 54 public inputs, original stored order, full settings/history, natural acquisition with rnd=0, natural stopping, complete expected posts/move/results/stderr/normal exit, exact work-post behavior. | Whole-search reporting against published references, with local hardware and endpoint caveats. A subset remains a named pilot. |
| F4: persistent ordinary behavior | All 12 complete selected game units, preserving within-game state, changing settings/clocks, explicit seed assertions and shutdown. Run required component/ordinary/continuity and full gameplay qualification separately. | Both published whole-engine collections can be evaluated once behavior, ownership and comparison procedures are qualified. |

F0/F1 should expose the whole search early; do not spend the initial schedule
perfecting an isolated microbenchmark or exact post formatting. Conversely,
never accelerate a prototype by silently dropping checks and carry forward its
old fidelity label. A legal chess search need not perform the same KingRE work.
Equal depth or equal generic node count does not establish equivalence.

## Minimal early A/B experiment

This is a future experiment design; no such run was performed for this memo.

1. Build two immutable release executables before collection. Start with generic
   x86-64, a fixed optimization/LTO/codegen policy and no PGO. Record all choices;
   later native/PGO studies are separate profiles. Do not compile during timing.
2. Freeze a small workload with position/history, personality/evaluation policy,
   state lifetime, fixed completion criterion and result consumption. Choose
   cases covering quiet/tactical/check/evasion and different game phases. Avoid
   wall-duration stopping when the question is cost of identical completed work.
3. Pin each engine process and all its engine threads to CPU14. Place the driver,
   oracle, shells, builds and inventory helpers on CPUs0-5,8-13. Keep CPU15 idle;
   do not borrow CPUs6-7. Use only process-owned affinity changes. Verify actual
   task affinity before measuring; the current shell's 0-15 affinity is not an
   engine placement receipt. Preserve the existing host vCPU mapping and CPU
   isolation; do not alter masks globally.
4. Initially prefer a single process with one search worker and no engine helper
   processes. A parent recorder can use `wait4` for that known direct child's
   user/system CPU and monotonic fork-to-reap wall time. Child wrapper pre-exec
   CPU belongs to this boundary and must be disclosed. The recorder, oracle and
   compilation CPU do not belong to engine cost. Multiple children/threads or
   delegated workers need validated complete ownership and accounting; direct
   main-PID accounting cannot silently stand in for them.
5. For a cheap in-process loop, take process CPU and monotonic readings only
   outside the whole batch, not at every node. Execute complete sequences from
   the declared logical reset state and consume actual results. Retain a wider
   complete-lifetime measurement so setup outside the loop remains charged.
   Predeclare a bounded duration-estimation step if repetition counts need to
   increase; freeze one identical count for both variants before measured runs.
   Short unresolved intervals stay unavailable. Repeated inputs warm hardware
   caches even when logical state is reset.
6. For a modest A/B decision, propose one excluded complete warmup per artifact
   and case, then four measured pairs in `AB, BA, AB, BA` order, serially. This
   proposal is an internal paired schedule, not the released reference schedule.
   Retain all eight measurements, warmups and order. Show paired differences,
   raw totals, each variant's median/min/max and `(max-min)/median`. Four pairs
   establish no universal noise bound. If evidence is too noisy, retain an
   inconclusive decision rather than select favorable samples or keep repeating.
7. Check behavior/work records before interpreting a speedup. A representation
   change should retain the same task/results; if semantic work changes, show
   both total cost and changed work. Make a deliberate architectural decision
   from whole-search impact; do not add overlapping component medians.

Freeze finite run/search/aggregate deadlines and raw artifact caps in the
experiment manifest before launch. The released full recorder protocols have
their own bounds; do not copy a short prototype timeout into a full-corpus speed
criterion. Stop later launches on collection failure, retain its evidence and
record corrections as a new experiment. Forced cleanup is not normal completion.
No transparent retries, timeout changes, or missing-case replacement.

Start with boundary CPU clocks and lightweight work counts. Instrument detailed
events only in a separately identified diagnostic build or mode; compare its
result parity and cost against the normal artifact before using it to explain
production behavior. Sampling and exhaustive tracing can wait for a real
whole-search question. No unavailable instruction counter is replaced by a
static assembly instruction count, wall-time estimate or generic node count.

## Local availability and environmental limits

Read-only inventory: [measurement-environment-inventory.json](../../evidence/measurement-environment-inventory.json),
captured 2026-10-17T17:12:19 UTC, with subsequent disabled-open probes. The
snapshot records this tool session, not per-run engine conditions.

| Item | Observed locally |
| --- | --- |
| System | `vic`, KVM guest, Linux `6.12.107+deb13-cloud-amd64`, x86-64 |
| Exposed CPU | AMD Ryzen 7 5825U, 16 online logical CPUs, guest microcode `0xa500011`, CPU14/15 sibling set `14-15` |
| Rust | `/usr/bin/rustc` 1.85.1 (`4eb161250e340c8f48f66e2b929ef4a5bed7c181`), host `x86_64-unknown-linux-gnu`, LLVM 19.1.7; cargo 1.85.1 |
| LLVM utilities | `llvm-profdata-19`, `llvm-cov-19`, `llvm-objdump-19`, `llvm-readobj-19`: 19.1.7. Unversioned profdata/cov absent. Instrumentation/PGO execution not tested. |
| Native tools | GCC 14.2.0, GNU ld/objdump/readelf 2.44; taskset util-linux 2.41.5; sha256sum coreutils 9.7 |
| Runtime/recorder | Python 3.13.5, Node v20.19.2, glibc 2.41; `/proc` CLK_TCK=100 (10ms CPU ticks) |
| Missing commands | `perf`, `rustup`, `valgrind`, `/usr/bin/time` absent from inspected locations/PATH |
| Counter policy visible here | perf_event_paranoid=3; effective and bounding capabilities zero; seccomp filter active |
| PMU metadata | CPU PMU type4, instructions `event=0xc0`, cycles `event=0x76`, max_precise=0; additional branch/cache aliases visible. Metadata is not successful collection. |
| Disabled self-event opens | Instructions, cycles and software task-clock each returned EACCES; no event enabled or read. The coordinator repeated the identical disabled-open probe outside the tool sandbox through approved execution and reported the same three EACCES results. This establishes unavailable counter access for this unprivileged account outside the sandbox too; it does not prove absent PMU hardware or lack of support for a separately authorized observer. |
| Resource view | Current session and visible user ancestors report cpu.max=`max 100000`, memory.max=`max`, memory.swap.max=`max`; no study-specific limits established. Current tool affinity0-15. |
| Frequency | Guest CPU14 cpufreq governor/driver/current-frequency files unavailable. `/proc/cpuinfo` MHz is guest metadata, not a run-frequency measurement. |

The user-supplied deployment fact is that guest vCPUs0-15 are pinned to the
same-numbered host Ryz CPUs. This was not independently reverified from the
guest. Virtualized cache-size reports should not be treated as physical cache
ownership. Guest sibling topology and pinned affinity do not eliminate shared
cache/RAM/power/thermal effects, host scheduling, guest interrupts or steal.
Host-level load/frequency/isolation observations remain unavailable unless
separately supplied. Preserve guest `/proc/stat` steal/context information if
collected later, but do not subtract it from engine CPU to invent native costs.

The reference used native Linux, Node22.22.3, a different kernel, bounded
engine/driver memory and no swap, and a scoped privileged read-only PMU
observer. The current guest/runtime/resource profile is different. This task
does not authorize administrative setup, installation, downloading tools,
global perf/security/governor changes, or calibrator execution. CPU/work-only
local experiments remain useful and explicitly lack I/C/IPC.

For reproducibility, the exact disabled-open probe was:

```python
import ctypes, os, struct
libc = ctypes.CDLL(None, use_errno=True)
for name, typ, config in [('instructions_user', 0, 1),
                          ('cycles_user', 0, 0),
                          ('task_clock_software', 1, 1)]:
    attr = bytearray(128)
    struct.pack_into('IIQQQQQ', attr, 0, typ, 128, config, 0, 0, 3,
                     1 | 32 | 64)  # disabled, exclude_kernel, exclude_hv
    buf = (ctypes.c_char * len(attr)).from_buffer(attr)
    ctypes.set_errno(0)
    fd = libc.syscall(298, ctypes.byref(buf), 0, -1, -1, 0)  # x86-64
    error = ctypes.get_errno()
    print(name, 'opened' if fd >= 0 else f'errno={error}: {os.strerror(error)}')
    if fd >= 0:
        os.close(fd)
```

Successful opens alone would still not validate grouping, enabled/running time,
inheritance or virtualized event meaning. If a separately authorized collector
becomes available, validate grouped task-scoped user instructions/cycles on
the actual engine interval, retain encodings/enabled/running/scaling/loss and
all task ownership. Compute IPC=`I/C`, CPI=`C/I` only for compatible paired
counts; aggregate by total I/total C. Unsupported/zero denominators are null,
not zero work. Never compare user-only PMU as though it includes the system
CPU charged by whole-lifetime accounting.

## Three endpoint views and semantic work

Keep E2E, SEARCH and POST independent. E2E includes all owned engine work through
normal completion. SEARCH is the external go-write request to received move,
with separately bracketed process CPU reads; pending setup, buffering and tail
work can overlap it. POST pairs a particular received work snapshot with its
own CPU/wall observations. Record request, write completion, receipt and read
timestamps separately where available; none establishes an internal instant.
Ten-millisecond `/proc` zero deltas are unresolved, not zero-cost work.

KingRE work is a behavioral denominator, not machine instructions. Search
charges N and relation charges R have specified admission/lifetime semantics:
`K(N)=N` through 2147483647 and 2147483648 above that boundary. The last ordinary
clock observation sets segment `B=3806*K(N)+770*R`. A normal profiling post
prints `min(2147483647, floor(B/1000))`; reset clears B and the carried clock
origin is excluded. Publishing must not introduce an extra observation or
charge. Deferred posts can combine a captured result with a later snapshot.
The before-first-root fallback retains zero reporting fields.

Before saturation, `field/3000000` gives quantized virtual work seconds. Divide
by that same post's resolved CPU/wall interval only. A last post is not exact
terminal work, and does not recover separate N/R. SearchID, normal post
centiseconds, candidate inventory, generated moves and consumed attempts are
different observations. Per-post PMU is absent from the published production
reference. Do not attach after-move counters to an earlier post or interpolate
terminal work. Long PV truncation can differ when the profiling prefix changes.

Early internal counters must each define domain, increment location
(attempt/admission/completion), recursion and retry treatment, rejected and
interrupted handling, reset/retention lifetime, warmup inclusion, observation
artifact and overhead. Report total cost and total count before cost/count.
Only label counters KingRE N/R once their released charging rules are actually
implemented and tested. Fused/avoided work can make narrow operation counts
noncomparable; use the larger completed responsibility instead of emulating
reference calls.

## Published corpus and calibration boundaries

The 54-case schedule is one excluded complete fresh-process warmup and three
measured fresh-process searches per case: 216 lifetimes, 162 measured. Preserve
stored corpus order, all numerical settings/history/TT/clocks, setup replies,
natural acquisition with rnd=0 (not an explicit seed0), every semantic post,
selected move, expected result records, full framing/stderr and normal exit.
The public replay checker is a behavioral checker; the optional benchmark
driver checks repeat consistency and main-PID CPU, not oracle correctness or
complete descendants. Do not upgrade that driver into E2E ownership evidence.

The 12-game schedule is one complete warmup and three measured independent
fresh-process lifetimes per published game unit: 48 lifetimes/2528 searches,
including 36 measured lifetimes/1896 searches. Keep fixture commands and
explicit seed rules. Within-game persistence is essential; independent game
units do not establish cross-game continuity. Its reference has CPU/wall,
no PMU or terminal N/R; 281 measured per-search CPU intervals are unresolved.
No reciprocal rates can be manufactured for them.

The 23 optional functional units mean complete semantic sequences, not private
call counts. Preserve reset/retention and consume real outputs. Before/after
projection equality alone does not prove timed work occurred. Include actual
copy/reset/normalization/consumption cost, and retain E2E setup guards.
Reference functional drivers are separate artifacts and their counters have
wider boundaries than local CPU clocks. Synthetic consumption controls are
never subtracted. The reference's roughly21.9% mixed-null spread is observed
variation, not an adopted tolerance. Neither inclusive search nor the historical
profile35 sample shares are exclusive pipeline costs, CPU-time shares or
regional IPC. Instruction and cycle sample distributions stay separate.

The approved calibrator is opaque candidateV27, SHA256
`4f647377c176c9fe454f369b0698efa6c9f20d0324d4c54d5c5907189cbde370`.
It is not the engine target or behavioral authority. The handoff contains only
reference-host calibration observations and a deployment tool packet; no
receiving-host ratio follows from possession of the data. No calibrator was
run for this design. A future separately authorized deployment must preserve
existing topology and local ownership controls rather than replay historical
privileged setup blindly.

For identical calibrator bytes/settings/case and compatible endpoints,
`H_cpu = median(local CPU) / median(reference CPU)`. Report every per-case ratio,
all repetitions and variation; wall ratios are separate. A casewise scaled
KingRE time is a planning estimate with transfer uncertainty, not observed
KingRE speed or same-hardware qualification. KVM and runtime differences can
affect two engines differently. The measured reference calibration's attach
pause affects E2E wall; user PMU excludes kernel/hypervisor and brackets SEARCH
with overhang. Do not divide its wider I/C by narrower CPU and call it frequency.

## Required evidence per experiment

Use a fresh immutable study directory and a manifest written before measurement.
Store exact machine-readable numbers and nulls, not only a rounded table.

- **Identity/config:** source commit and dirty-tree patch/hash, Cargo.lock and
  manifest hashes, executable SHA256 before/after collection, compiler/linker
  versions, complete build command/profile/RUSTFLAGS, CPU target features, LTO,
  codegen units, panic/overflow/debug settings, PGO status/profile/training
  identities, linked runtime, production versus diagnostic adapter partitions.
- **Input/semantics:** spec release and packet identities; workload, fixture,
  oracle and checker hashes; exact case order/settings/history/commands and
  lifetime; fidelity label and omitted rules; stopping/seed policy; completed
  semantic count definitions; actual score/depth/PV/move/work projections.
- **Environment:** host/guest facts and provenance, topology, effective per-task
  affinity, helper placement and idle sibling, inherited quotas/memory/swap,
  concurrency/load and available frequency/thermal metadata. Unverified
  host-side facts stay labeled as supplied, not observed.
- **Attempt records:** unique run ID, warmup/measured and A/B order, monotonic
  boundary times, separate user/system CPU and exact scope, raw bounded
  stdout/stderr before validation, executed checker/assertion results, direct
  child exit/signal/timeout, owned completion and cleanup outcomes. Missing,
  failed, partial and discarded-byte observations remain explicit.
- **Metrics/decision:** all repetitions and min/median/max, semantic denominators,
  sample matching and unavailable reasons, any counter group metadata, selected
  aggregate formula, worst per-case regressions, changed-work explanations,
  predeclared bounded follow-up rule and the three independent dispositions.

## Development runner supplied with this design

`tools/measure.py` implements a small direct-process CPU/wall recorder for a
noninteractive command with a known single-process workload. It cannot drive
the production wire protocol, implement an oracle, compare KingRE, account
delegated processes or attest full engine completion. `--known-single-process`
is the caller's assertion, not a discovered property. If the command is an
interpreter, hash its script and data using `--input-file`; its executable hash
alone identifies only the interpreter. Supply a build metadata file through
`--build-record` to bind compiler/settings/source evidence.

Example **plan inspection only**, with no child launch or affinity changes:

```sh
python3 tools/measure.py --output /tmp/fresh-rook2-study \
  --label prototype-baseline --fidelity F1 --known-single-process \
  --semantic-description 'Fixed completed task; declare reset, seed and omissions here' \
  --build-record /absolute/build-record.json \
  --input-file /absolute/workload.json --dry-run -- /absolute/benchmark task.json
```

Removing `--dry-run` performs the declared serial schedule; default one excluded
warmup and three measured invocations are the small single-artifact schedule,
not the four-pair A/B proposal above. Arrange A/B order explicitly in the
experiment plan; never compare separate run blocks as though they were
interleaved. Stdin is `/dev/null`. The runner pins itself to helper CPUs and
sets CPU14 in the child before exec, records that placement acknowledgment,
then restores its own inherited affinity. It does not verify that the command
keeps its affinity after exec or that CPU15/host siblings remain idle. Those
are experiment preconditions. A recorder started with the housekeeping mask
can request CPU14 independently in the child; the kernel and the child's
placement acknowledgment determine whether that request succeeds. An initial
preflight check incorrectly required CPU14 in the recorder's own mask; the
live-control investigation reproduced that rejection and corrected it.

Each attempt has bounded raw stdout/stderr and a `record.json`; the study keeps
its prelaunch `manifest.json` and final `summary.json`. `wait4` user/system CPU
includes the small child preexec setup. Wall is parent fork-to-reap and includes
observer polling/scheduling latency (poll interval20ms), not an internal exit
timestamp or a reliable tiny-command latency. Kernel CPU accounting reported
as float seconds does not acquire nanosecond precision from conversion.
CPU and wall min/median/max plus range/median are emitted only for a complete
valid declared schedule. No reciprocal rate is invented for zero CPU.

The recorder stops after the first timeout, cap, failed placement/identity or
nonzero exit, retaining failed records. It uses bounded cleanup of its unreaped
direct child/session group; after the direct child is reaped it does not signal
a potentially reused PID. Pipes left open after main-process exit invalidate
the record, and unsupported descendant/escaped work is not magically contained
or accounted. This is a development tool, not an adversarial supervisor or a
qualification recorder. Every report says behavior unchecked/performance
reported-only, and I/C/IPC are null.

Validation executed for this delivery: seven mocked fork/wait4/preflight controls covering
raw retention and separate CPU fields, missing placement, stream cap,
nonzero exit, timeout despite later zero exit, zero CPU statistics, and a
housekeeping-pinned recorder admitting the independent engine affinity request.
`python3 -m unittest discover -s tools -p test_measure.py -v` passed.
A `--dry-run` plan for `/bin/true` also passed; `/bin/true` was not executed.

The subsequent live validation used `tools/runner-control.c`, compiled with
the installed GCC on housekeeping CPUs. This native helper has no chess code,
threads, subprocesses or PMU. Its own `sched_getaffinity` check requires exactly
CPU14. Evidence is retained under
[runner-controls](../../evidence/runner-controls/receipt.json), including source
and executable hashes, compiler command/output, the controller's source and
per-case raw streams, manifests, records and summaries.

| Live synthetic control | Retained result |
| --- | --- |
| Normal output plus30ms process-CPU loop | One excluded warmup plus three measured lifetimes; native helper observed CPU14, stdout/stderr exact, every direct exit0 and positive kernel CPU |
| Nonzero exit | Native exit7; invalid record retained; later two scheduled launches stopped; no partial performance summary |
| Deadline |120ms run deadline, native SIGKILL(-9); invalid record retained; later launches stopped |
| Output cap |1024-byte stdout bound respected, discarded bytes recorded, native SIGKILL(-9); invalid record retained; later launches stopped |

All four controls and compilation completed in0.47298 seconds total; each
controller invocation was under0.17 seconds and the compilation took0.060
seconds, within the2-second individual and15-second total budgets. The normal
measured CPU samples were0.031509,0.031450 and0.031542 seconds. They validate
positive accounting and summary retention for this synthetic workload; their
spread is not a general precision or repeatability guarantee.

Every recorder reported its housekeeping mask during collection and restored
that inherited mask afterward. The outer control driver stayed on housekeeping
CPUs while compiling/running controls and restored its original0-15 affinity
at completion. No global affinity, isolation, PMU or administrative setting
changed. Seven native synthetic lifetimes were launched; no engine or
calibrator ran. These controls validate a bounded live single-process path and
its retained failures, not descendant coverage, an interactive protocol,
oracle correctness or performance qualification.

The initial document/input identity snapshot is
[measurement-input-identities.json](../../evidence/measurement-input-identities.json).
It includes SHA256s of the approved policy, workloads/oracles/checkers and
calibration memo/data; it is not a full release verification or an execution
attestation. The three profiling workload/oracle/checker hashes match the
approved handoff. Rebind identities for every future actual study. No artifact
hash, self-written completion field, or sample count substitutes for executed
assertions and independently observed normal exits.

Primary local sources: `king-spec/performance/acceptance-policy.md`,
`measurement-policy.md`, `owner-choices.md`, `statistics.md`,
`functional-benchmark-guide.md`, `functional-metrics.md`,
`selected-games-protocol.md`, `operation-definitions.md`,
`sampling-profile-35.md`, `spec/work-clock*.md`,
`conformance/profiling/README.md`, and the approved
`spec-issues/v2.5.0/2026-10-16-performance-handoff/hardware-calibration.md`.
