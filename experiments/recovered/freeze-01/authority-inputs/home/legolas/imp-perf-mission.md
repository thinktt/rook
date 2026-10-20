# Mission: High-Performance Rook Architecture
### Independent Implementation Team — Engineering Directive

## Objective

Design and implement a new, high-performance Rust chess engine that independently satisfies the released KingRE behavioral specification and approaches or exceeds the performance targets established in its approved performance companion.

The objective is not to optimize the existing Rook implementation. It is to engineer a substantially more efficient system from first principles, with correctness and computational performance treated as equally fundamental requirements.

## Team Structure and Responsibilities

The new effort will operate as an independent implementation team consisting of a principal architect/coordinator and implementation subagents.

The coordinator acts as a senior systems engineer specializing in performance-critical software, CPU microarchitecture, compiler behavior, memory organization, and efficient native binary design.

The coordinator owns the overall architecture, directs subagent investigations and implementation, reviews their work, and ensures their contributions form a coherent system rather than a collection of individually optimized components.

The existing Rook implementation team remains independent and serves as a **specification interpretation and conformance resource**, not an architectural advisor.

## Architectural Freedom

Develop the new engine from the specification rather than from the existing Rook implementation.

Choose representations, algorithms, state ownership, memory layouts, caching strategies, and subsystem boundaries based on the efficiency of the complete system.

Pay particular attention to:

- Compact representations and efficient memory access.
- Data locality, cache behavior, and branch prediction.
- Reducing unnecessary instructions, allocations, copies, and intermediate operations.
- Reusing derived information and avoiding redundant computation.
- Minimizing overhead across the complete search pipeline.

Treat computational efficiency as a foundational design requirement, not something to address after functional completion.

Do not preserve abstractions merely for elegance or familiarity. Likewise, do not assume low-level complexity is inherently faster. Measure the actual costs of architectural decisions.


### Independence and Collaboration

Imp2 is an independent implementation effort. It must develop its own architecture directly from the KingRE specification and performance companion, without examining or drawing upon Imp1's source code or architectural design.

Imp2 is expected to investigate and resolve its own implementation challenges. If it encounters a persistent specification or conformance problem, it may consult Imp1 for focused assistance, drawing on the original team's experience without adopting its implementation approach.

Imp2 retains full ownership of its architecture and engineering decisions. Genuine specification ambiguities or behavioral changes remain the responsibility of the specification authority.

## Performance Engineering

Use the approved performance companion to establish achievable computational costs for the specified behavior.

Measure:

- **Retired instructions** as the primary diagnostic of machine-code work.
- **CPU cycles and CPI/IPC** to assess execution efficiency.
- **CPU time** to establish actual performance.
- Logical work and conformance observations to verify equivalent behavior.

Evaluate both individual workloads and aggregate results across the established corpus, under controlled and reproducible measurement conditions.

Pipeline-level reference costs are diagnostic guidance, not mandatory ceilings. The architecture may redistribute work between subsystems whenever doing so improves overall performance.

The primary performance acceptance criterion is whole-engine execution approaching or exceeding Generic Rust KingRE-PGO, with exact behavioral conformance.

## Implementation Strategy

Begin with a coherent, performance-oriented architecture for the complete engine, then work progressively toward exact specification conformance. Treat architectural efficiency as the foundation of the implementation rather than something to optimize after achieving correctness.

Develop an integrated, measurable search early instead of perfecting isolated components. Establish performance baselines and use lightweight correctness checks to ensure measurements represent meaningful, comparable work.

Use profiling, targeted experiments and whole-search measurements to evaluate architectural decisions. Maintain a unified design while remaining willing to replace unsuccessful approaches rather than accumulate compatibility patches.

As the architecture demonstrates competitive performance, progressively tighten behavioral fidelity and expand conformance testing. Do not allow early conformance debugging to dictate the architecture or derail the performance effort.

Use the existing Rook binary and approved fixtures for behavioral validation where permitted, without examining or adopting the original implementation's architecture.

Preserve reproducible measurements, exact binary identities, build settings and evidence supporting major design decisions.

**The objective is to converge on both high performance and exact conformance, starting from an efficient architecture rather than optimizing a conformant but inefficient one.**

## Completion Criteria

The effort succeeds when it delivers a new Rust implementation that:

1. Satisfies the released KingRE behavioral specification and required conformance suite.
2. Demonstrates whole-search computational efficiency and execution speed approaching or exceeding the approved reference targets.
3. Maintains a coherent, independently developed architecture whose performance is supported by reproducible measurements.
4. Passes final behavioral and performance qualification under the established clean-room process.

Intermediate speedups, successful prototypes, and isolated optimizations are evidence of progress, not completion.

**The mission is to build a fundamentally efficient Rook, not merely a faster version of the existing one.**

## Performance measurement and hardware calibration

Use the released performance companion to evaluate whole-engine execution cost. Functional benchmarks, retired instructions and cycles guide optimization; they do not impose a particular architecture or independent subsystem ceilings.

A separate hardware-calibration memo identifies a fixed executable and supplies a workload that can be run unchanged on both the reference hardware and the implementation team's hardware, using an independently authorized opaque copy of that executable. The memo/tool packet does not include the binary. Comparing those measurements establishes empirical, workload-specific timing ratios between the machines. The executable is only a convenient calibration vehicle—not an engine-performance target, architectural example or behavioral authority.

Report per-case calibration ratios and their variation. Use them to interpret local measurements against the KingRE reference, with disclosed uncertainty; do not assume one ratio transfers perfectly across all workloads or implementations.

KingRE remains the performance reference, and final acceptance follows the released companion's measurement and qualification policy.
