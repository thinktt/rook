# Fixed-executable hardware calibration — private export candidate

Status: transfer authorized by Toby; the original handoff was delivered to Vic.
The former HARD TRANSFER HOLD is superseded. The export-adapted tools have
offline/mock checks only and have NOT been live-qualified on Vic. This is a
measurement-validity limitation, not a delivery restriction.
This is not specification supplement content, an engine-speed target, or a
replacement for KingRE performance authority. The opaque Rook executable is a
fixed hardware-calibration workload; no binary is included.

## Contents and evidence boundaries

`calibration-data.json` contains the completed 54-case reference measurements,
including three measured repetitions per case, ranges and host metadata.
`measured-162.csv` is the corresponding numerical table. One warmup per case
is excluded from those 162 measured rows. All 216 lifetimes and 2,496 posts
passed their retained public replay checks. The first four lifetimes were the
pilot and are included once, not rerun. Actual collection took 844.406783409s.

`templates/` are **export-adapted sources**, NOT the historical measured sources.
They add receiver-selected topology, ownership-gated cleanup and root-owned
PMU spooling. Those changes have pure/mock/syntax/render controls only; no
engine, privileged setup or counter collection was rerun with them. Original
measured sources and raw evidence remain private and unchanged. Do not attribute
their live qualification to the adapted export. Templates use neutral path
placeholders; `rebind.mjs` renders fresh local paths without launching anything.

## Receiver configuration

Requires Linux x86_64, engine UID1000 with zero capabilities, cgroup v2
cpuset/cpu/memory/pids, root-authorized external observer, Node, Python3,
taskset, sudo and systemd system/user managers. Root installation of the
reviewed observer is an explicit operator action; the engine never runs as root.
Counter groups must supply paired user instructions/cycles without scaling,
multiplexing or loss. Unsupported topology/PMU/ownership fails, not zero-fills.

Select an engine CPU, its **entire actual physical sibling set**, and a nonempty
helper CPU mask with no sibling overlap. Masks are checked against online CPUs
and actual sysfs topology at render and setup/run time. The engine uses one
CPU; all physical siblings are reserved, with unused siblings idle. Helpers
may be a subset of the other CPUs; host effective masks exclude the reserved
siblings. Existing isolation or namespace/unit collisions reject admission.
No global perf security, governor, turbo or frequency setting is changed.

Provide the already staged opaque binary with SHA256
`4f647377c176c9fe454f369b0698efa6c9f20d0324d4c54d5c5907189cbde370`,
the released package directory containing `conformance/profiling`, and a fresh
absent output directory **outside this export's containing directory**. This
last restriction protects adjacent retained measurement material. Every output
ancestor must be a real directory, not a symlink; the renderer rejects escapes
before writes. The renderer verifies the opaque binary's SHA256; it does not
inspect its implementation or bundle the binary.

Example generation only; it does not authorize execution:

```
node rebind.mjs --output /fresh/profile-root --spec /path/to/king-spec --engine /path/to/staged/rook --name fixed-calibration-unique --cpu 14 --siblings 14-15 --helpers 0-13
```

Pure/mock and render/syntax controls (the example CPU masks must fit the host):

```
node test-safety.mjs
PYTHONDONTWRITEBYTECODE=1 python3 test-safe-spool.py
node check-export.mjs /fresh/control-receipt.json /fresh/render-control /path/to/king-spec /path/to/staged/rook 14 14-15 0-13
```

`check-export` does not execute setup, the engine, or the PMU collector. It only
executes the rendered cleanup's **no-marker/no-action** branch. Mock controls
exercise wrong token/resource/snapshot, namespace collision/no-marker behavior,
symlink destination rejection and privileged writer rejection before any write.

## Separately authorized deployment

The rendered entrypoints are `prepare.mjs`, `setup.mjs`, `runner.mjs`, and
`cleanup.mjs` as controller ExecStopPost. Controller: helpers affinity, 1GiB RAM,
no swap, Node heap1GiB, 6h aggregate bound; engine: 1GiB/no swap/no quota;
collector: separate256MiB/no swap/helpers affinity. Setup30s, search300s,
cleanup5s; raw8MiB per engine lifetime, PMU256KiB per collector, engine raw512MiB
aggregate, artifact2GiB checked between lifetimes. These are retained source
guard scopes, not a hard aggregate filesystem quota. A receiver must retain
effective cgroup limits, direct exits and cleanup evidence on its own run.

Setup claims a fresh root-owned runtime namespace and records matching random
ownership tokens, resource device/inode/UID identities, and the restoration
snapshot digest. Cleanup verifies those proofs **before any kill or teardown**.
No marker means no destructive action; incomplete/mismatched proofs stop for
manual owner review rather than guessing ownership. An interrupted partial
setup may therefore leave its own resources for explicit inspection.

The privileged observer writes bounded reports only to an anchored root-owned,
non-user-writable spool. It rejects unsafe targets before writes, uses
exclusive/no-follow temporary creation and directory-relative atomic replace.
The unprivileged client copies the completed report with exclusive destination
creation. No privileged write follows a user-owned report/tmp symlink.

## Interpretation and limitations

Use the exact fixed executable and 54 public workloads in original order:
one excluded fresh warmup plus three measured fresh lifetimes per case.
SEARCH CPU/wall covers GO-write-request through received move. Whole-lifetime
CPU uses native wait4; PMU starts after the pre-exec attach stop and covers the
remaining prefix/native lifetime. The attach pause affects lifetime wall time.
SEARCH PMU brackets the CPU/wall interval with explicit overhang; endpoints
are not simultaneous. Per-post PMU is unavailable. Work efficiency is not
move latency. CPU sample resolution is10ms; PMU counter scope excludes kernel
and hypervisor execution. Ratios vary with workload/runtime/host/frequency.

Measured direct native/wrapper exits and collector service completion are
retained. Later unloaded-controller status is **not** an independent historical
controller-exit receipt; that direct controller code is unavailable. Post-run
library metadata is not launch-time library closure or in-search frequency
tracking. This packet establishes no universal hardware conversion, other
engine speed requirement, gameplay qualification or new reference-engine run.
