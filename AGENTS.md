# Rook2 implementation instructions

## Mission and authority

Build an independent high-performance Rust implementation of KingRE. The guiding
mission is `/home/legolas/imp-perf-mission.md`; behavioral authority is the released
package at `/home/legolas/king-spec`. Revisit the mission at major milestones or
when the owner changes it, rather than on every task.

Start from a coherent efficient architecture and measurable integrated search.
Progressively tighten fidelity and conformance. Prototype timings must identify
omitted behavior; approximate search is not a qualified KingRE comparison.
Vic's local qualification scope is exact mandatory conformance, production
review and the regular12-game pre-gate. The owner assigned the full3288-game
gate to an external system with more resources; do not run that gate on Vic.
Prepare the exact artifact/evidence handoff for that external gate. Performance
work and the released measurement/qualification policies remain applicable.

## Independence

Do not inspect or adopt Imp1/Rook implementation source, architecture, or private
source-derived performance findings. Study released specifications and approved
handoff materials. An independently authorized opaque binary may be used only
for its approved behavioral or calibration purpose. Keep fixtures outside the
engine and never use expected answers as a runtime answer database.

## Ownership and collaboration

The owner-approved [last-mile working agreement](docs/leadership-working-agreement-last-mile.md)
governs the current phase. `imp2-lead` owns technical strategy and architecture,
including deep investigation and original design work. Imp2 owns implementation
and experimental execution within that agenda and makes routine engineering
decisions independently. Challenge proposed directions and raise significant
architectural tradeoffs, unexpected evidence and scope changes. Keep
coordination lightweight; routine execution does not require approval.

Top-level agents use Herdr native prompts to other Herdr agents with their
centrally assigned sender identity. Follow the standard local AGENTS.md
identity and memo-size rules; do not infer a name from a role or tab label.
Subagents must use their supplied collaboration tools and must not use Herdr
for identity or communication.

Imp2 uses GPT-6.1 Sol xhigh at normal speed. Implementation subagents use
GPT-6.1 Sol at an appropriate reasoning level and normal speed. Imp2-lead may
use at most one Astra subagent at a time for difficult analysis, independent
challenge, or demanding implementation when useful; Imp2's team remains the
default. The owner's
latest `/fast off` supersedes the temporary fast-subagent request. The current
collaboration controls expose model/effort but no speed setting: do not claim
that updating this policy switches or verifies a live runtime.
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

## Commit attribution

Use `Tobias Toland <github@thinktt.e4ward.com>` as both the primary author and
committer of commits in this repository. The repository-local `user.name` and
`user.email` must use that identity; do not override it with an agent identity.
Keep Codex attribution in the required co-author trailers below.

Every commit created for this repository must end with the following commit
trailers in this order:

```text
Co-authored-by: Codex GPT-<current Sol model version> Sol <codex@openai.com>
Co-authored-by: Codex GPT-6 Astra <codex@openai.com>
Directed-by: Tobias Toland <github@thinktt.e4ward.com>
```

These trailers are required on every commit, regardless of which agent performs
the implementation, review, testing, documentation, or commit operation.

For the first trailer, replace `<current Sol model version>` with the model
version running the Sol implementation owner when the commit is created. Use
the active session's model information or an explicit model assignment from the
user; do not infer the model from the agent name or tab label. If the model
cannot be established, ask the user rather than copying a previous commit's
version. For example, when running GPT-6.1, use:

```text
Co-authored-by: Codex GPT-6.1 Sol <codex@openai.com>
```

The Sol model version is dynamic. Keep the Sol name and email, the Astra
trailer, the director trailer, and their order exactly as shown. Place all
three trailers at the end of the commit message, after the summary and any
explanatory body.

Use this commit-message structure:

```text
<short imperative summary>

<optional explanatory body>

Co-authored-by: Codex GPT-<current Sol model version> Sol <codex@openai.com>
Co-authored-by: Codex GPT-6 Astra <codex@openai.com>
Directed-by: Tobias Toland <github@thinktt.e4ward.com>
```

Before completing a commit, verify that all three trailers are present at the
end of the message in the required order, with the Sol model version matching
the active model at commit time.

## Evidence storage

Keep code history, reproducible experiment setups and concise outcome reports in
this repository. Store raw runs, binaries, profiles, intermediate build products
and packed checkpoints in `/home/legolas/rook2-experiments`. The complete original
worktree/history is preserved there. Read `docs/evidence-layout.md` for relocated
paths and commit mapping, and update `docs/performance-experiments.md` with brief
idea/result entries (label untried proposals explicitly). Do not automatically
commit new evidence trees or replace old immutable records to fix their paths.
