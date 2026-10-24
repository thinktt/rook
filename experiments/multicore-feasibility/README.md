# First deterministic multicore feasibility probe

This standalone driver uses the unchanged rook2 numerical library. A persistent
worker computes Activity then Shelter from immutable Position, supplied Influence,
root material and neutral weights. The coordinator alone selects/replaces pawn
cache entries, computes pawn terms/progress and remaining components, joins,
derives tempo and calls the existing endgame finisher. It has no TT, learning,
work-clock or host-polling operations. The engine sources are unchanged.

Inputs are the54 released standard workloads' positions reconstructed from their
complete legal move histories; no expected answers enter the measured kernels.
Influence (public scalar producer), material and maintained nonking sum are
prepared before timing. One fixed neutral starting-position RootContext and
neutral evaluation weights are used, rather than each original personality.
This is representative numerical work, not an accepted search workload.

Verification compares162 sequential standalone FULL calls with the actual
Evaluator, including component fields, score/bounds, pawn reuse, relation counts
and retained outputs. It also compares full worker Activity/Shelter results with
direct results. Timed modes consume all component fields and verify equal
checksums. Fast/FULL selection, Influence preparation, node restoration, logical
charge publication, wire serving and complete search are outside this probe.

Only one simple transport is tested: a persistent spinning worker, release/acquire
sequence counters on separate cache lines, and a reusable mutex-protected output
vector. There is no allocation or thread spawning per job; no unsafe packet
sharing. Unsafe code is confined to Linux x86-64 affinity and process-clock FFI.
The synthetic empty row measures this protocol's round trip. Chain-only and
composed FULL rows compare direct execution with worker batches1/8/32. Batching
assumes already fixed independent packets; future evaluation calls are not known
to be available that way in serial search.

Each row has one excluded short warmup then three fixed172800-packet samples,
with no retiming or replacement. Elapsed time is measured inside the harness;
process CPU includes worker spinning. Direct modes have one thread and no idle
worker. Worker startup/shutdown and input construction are outside sample clocks.
A single supervisor enforces timeout and preserves failures.

Allocation: coordinator CPU14, worker CPU6, no owned work on sibling CPUs15/7;
build/launcher helpers CPUs0-5,8-13. This follows observed guest topology, not proof
of exclusive host resources. No reference performance qualification is claimed.
