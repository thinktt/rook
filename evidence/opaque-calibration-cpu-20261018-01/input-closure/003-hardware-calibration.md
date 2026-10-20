# Fixed-executable hardware calibration

## Purpose

This separate memo supplies reference-host observations and a reproducible
workload for interpreting timing differences between machines. The selected
opaque executable is a convenient fixed calibration vehicle. Its competitiveness
as a chess engine is irrelevant here: it is not the implementation team's speed
target, architectural example or behavioral authority. KingRE remains the
performance reference described by the specification's performance companion.

Run the identical executable and workload on the other machine, then compare
matching per-case observations. This produces empirical hardware/runtime ratios,
not a universal conversion factor or an independent performance qualification.
Only the reference host has been measured in this packet; no receiving-host
ratio or measurement is claimed in advance.

## Fixed artifact and workload

The calibration artifact is production Rook v1.0.0-rc.2-r3 / candidateV27:

- Delivery commit: `1fd4a3ae8f4949778841216a11cd2fa572dc1a4f`.
- Exact executable SHA256:
  `4f647377c176c9fe454f369b0698efa6c9f20d0324d4c54d5c5907189cbde370`.
- Linux x86-64; use a compatible runtime and ISA. No binary is included in this
  memo/tool packet. An already supplied opaque copy must match the exact hash.

Use all54 cases, in stored order, from the unchanged public profiling kit
included in KingRE Specification v2.5.0. These inputs/oracles are retained from
the v2.4.2 behavioral baseline:

- `conformance/profiling/workloads.json`, SHA256
  `5fd3117420ce7a9813268dc0db322f339739061868395324c36ff3cebce6126e`.
- `conformance/profiling/replay-oracle.json`, SHA256
  `6719db738383dae810d49db96575dc981e5d83b57bd52acf7c5a23c1b22e09dc`.
- `conformance/profiling/replay-check.mjs`, SHA256
  `f25d63ad547505d1b2ade6b294d0b4a4a3cdb7c29000634373521ca3dbaa88cd`.

Preserve every numerical setting, personalityP ID, history, clock, TT request,
setup acknowledgment, semantic post, work snapshot and selected move. Use the
existing `--work-clock=kingwcr --work-clock-post=work` options, natural seed
acquisition with `rnd=0`, and natural search completion. The public setup
records followed by `cm_parm rnd` supply readiness; no new engine interface
or explicit seed override is introduced.

Each case has one excluded complete fresh-process warmup and three measured
fresh-process repetitions. The reference collection completed216lifetimes:
54warmups and162measured searches, with2496semantic posts across all216.
The first case's four-lifetime pilot is included once, not extra or reused from
an earlier historical benchmark. A preceding zero-engine setup correction is
preserved separately and contributes no measurement sample.

## Reference-host observations

Collection window:2026-10-16T23:25:47.906Z through23:39:52.313Z, recorded elapsed
844.406783409seconds. This is the collection's elapsed duration, not a sum of
per-case medians or an ordinary continuous-game timing.

The named host profile is Linux x86-64 on AMD Ryzen7 5825U,16logical CPUs,
Linux6.12.111+deb13-amd64. Engines used CPU14 in a temporarily isolated14/15
physical-core partition with sibling15idle; helpers used0-13. The engine was
UID1000/capabilities0,1GiB/no swap/no CPU quota. The controller was separately
bounded to1GiB; the privileged read-only PMU collector was outside the engine
leaf with its own256MiB limit. Prior CPU masks were restored and owned groups
removed at terminal verification. Core isolation did not isolate shared cache,
memory, thermal/power or operating-system effects.

Governor metadata reports `powersave`; no turbo/governor/global PMU-security
setting was changed or fixed. Runtime inventory reports glibc2.41 and
Nodev22.22.3. Post-run library/runtime metadata is not a before/after per-launch
library closure or a guarantee of instantaneous frequency during every sample.
Record corresponding facts and differences on the receiving machine.

The data files retain all162measured rows and all54case summaries, with samples,
minima, medians, maxima and variation. The per-case references are in
`calibration/calibration-data.json`; the flat measured table is
`calibration/measured-162.csv`. Warmup and normal-exit/cleanup evidence remain
in the owner's private retained records rather than being disguised as extra
measured samples.

## Keep measurement scopes separate

- Whole-lifetime CPU is kernel wait4 user+system accounting of owned native
  execution, including a small Python child pre-exec prefix. Its wall boundary
  includes the stopped-child attachment and coordination pauses: it is not
  ordinary user launch latency. The wrapper/collector is not engine CPU.
- Search CPU/wall spans external GO-write request through first received move.
  `/proc` CPU resolution is10ms; unresolved intervals are unavailable, not zero
  work. Pending input and publication/receipt delays are not internal search
  entry/exit timestamps.
- Paired grouped user-space instructions/cycles bracket their own read
  observations. SEARCH counters extend before the GO observation and after
  MOVE receipt; this disclosed overhang does not become an exactly simultaneous
  CPU/counter boundary. Whole-lifetime counters include the remaining child
  pre-exec suffix/native execution through completion.
- Groups were unscaled, nonmultiplexed and lossless under the recorded guards.
  Counters exclude kernel/hypervisor work; CPU includes user+system. IPC uses
  compatible paired I/C only. Do not infer frequency or an instruction rate by
  dividing a wider counter interval by narrower CPU time.
- Per-post PMU and exact separate terminal N/R are unavailable. Published work
  remains that post's quantized/saturated snapshot, not an invented terminal
  ledger. The independent strict oracle verifies expected observable behavior.

Native normal wait4 exits, wrapper/controller outcomes and collector completion
are separate evidence. Collector termination is supported by retained
`systemd-run --wait` outcome plus its terminal sidecar, not a separate historical
per-run service-status query. The later unloaded-controller status query is not
an independent retained historical controller-exit receipt; that independent
exit fact is unavailable. Completed output and owned cleanup remain distinct
supporting observations. Numerical/export reviews do not create additional
independent execution attestations or erase those limits.

## Measuring on another machine

The separate `calibration/README.md` and generator describe deployment inputs,
dependencies, safety checks and limitations. Use a fresh destination, compatible
Linux/cgroup/PMU facilities and a valid declared topology/resource profile.
Do not execute a historical configuration against its original paths. Never
run the engine as root or change global security settings to obtain counters.
Any administrative setup requires local authorization; inspect the measurement
tool, not the opaque engine's implementation.

The provided deployment generator is an adaptation of the measured recorder,
not a second live-qualified run. Its pure/mock controls do not establish PMU
support, topology correctness or containment on another host. Validate those
prerequisites and actual recording on that host before relying on its numbers.
Record source/config/executable hashes, actual counts/assertions, raw streams,
counter scope/enabled/running/loss, independent exits and owned cleanup.
Missing/failed cases or lost/unsupported counters must remain explicit; no
successful subset or forced cleanup creates a complete passing calibration.

## Forming and interpreting hardware ratios

For each case and compatible endpoint:

`H_cpu = median(CPU_other_host) / median(CPU_reference_host)`

The numerator and denominator must come from the SAME calibration executable,
settings, case, lifetime and recording method. A value1.20 means20% more CPU
time on the other machine for that fixed workload. Show all per-case ratios,
repetition variation and unresolved measurements; do not lead with one average.
Whole-lifetime CPU can resolve costs that10ms search ticks do not. Form wall
ratios separately with their own disclosed collector/receipt boundaries.

Instructions/cycles/IPC can help interpret changes, provided event meaning and
scope agree. They are not universal time units. Host/runtime/ISA, frequency,
cache/memory and scheduling differences can affect programs differently.
Ratios that vary substantially by case argue against one aggregate correction.

For planning, a case-specific ratio can inform an estimated KingRE target on
the other host. Label the estimate and its uncertainty: it is not an observed
KingRE timing and need not transfer exactly to another architecture. There is
no speed threshold for this calibrator, no claim it matches KingRE efficiency,
no new same-window engine comparison and no gameplay/conformance qualification
of another artifact. Final acceptance remains governed by the released KingRE
companion's policy and a fixed validated measurement/uncertainty procedure.
