# Rook2 implementation instructions

## Mission and authority

Build an independent high-performance Rust implementation of KingRE. The guiding
mission is `/home/legolas/imp-perf-mission.md`; behavioral authority is the released
package at `/home/legolas/king-spec`. Revisit the mission at major milestones or
when the owner changes it, rather than on every task.

Start from a coherent efficient architecture and measurable integrated search.
Progressively tighten fidelity and conformance. Prototype timings must identify
omitted behavior; approximate search is not a qualified KingRE comparison.
Completion requires exact mandatory conformance, production review, gameplay
qualification and performance qualification under the released policies.

## Independence

Do not inspect or adopt Imp1/Rook implementation source, architecture, or private
source-derived performance findings. Study released specifications and approved
handoff materials. An independently authorized opaque binary may be used only
for its approved behavioral or calibration purpose. Keep fixtures outside the
engine and never use expected answers as a runtime answer database.

## Ownership and collaboration

Imp2 owns architecture and engineering decisions. `imp2-lead` is an independent
architectural advisor. Obtain its critique of the initial design before
substantial implementation. Later consultations should be infrequent and bounded,
for consequential decisions, significant uncertainty or measured evidence that
challenges the fundamental direction. Supply a focused question, evidence,
alternatives and a preliminary judgment. Approval is not required.

The top-level agent uses Herdr native prompts to other Herdr agents with the
sender header `[imp2]:`. Follow the standard local AGENTS.md memo-size rule.
Subagents must use their supplied collaboration tools and must not use Herdr
for identity or communication.

The lead uses GPT-6.1 Sol xhigh at normal speed. Implementation subagents use
GPT-6.1 Sol at an appropriate reasoning level, with fast speed requested by the
owner. The current collaboration controls expose model/effort but no speed
setting: do not claim that updating this policy switches a live runtime.
Assign disjoint write ownership and integrate/review contributions centrally.

## Measurement environment

Vic is the clean-room KVM VM. Its vCPUs 0–15 are pinned one-to-one to Ryz host
CPUs 0–15. Use vCPU14 for engine measurements and keep sibling15 idle. Run build
and measurement helpers on `0-5,8-13`. Guest affinity alone does not exclude
other guest activity; verify conditions and disclose interference. Do not change
host/global isolation, security or privileged measurement setup without the
appropriate authorization. Do not infer actual cache geometry from duplicated
VM cache inventory.

Record exact artifact/spec identities, build settings, workload/fidelity,
logical work, retired instructions/cycles when available, CPU/wall boundaries,
repetitions and uncertainty. Separate development diagnostics from qualification.
Calibration ratios are per-case estimates, not universal host conversion factors.

## Engineering

Keep JSON/protocol parsing and diagnostic recording outside hot search state.
Prefer concrete compact types and measured improvements over speculative
complexity. Preserve specified rounding, overflow, ordering, reuse/collision,
reset and interruption semantics. Semantic work is independent of actual CPU work.
Run checks appropriate to each change; do not build a complete fixture adapter
before integrated search is measurable. Record architectural decisions and
evidence, and replace failed approaches instead of accumulating patches.
