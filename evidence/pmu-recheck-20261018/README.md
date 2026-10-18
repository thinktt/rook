# Read-only PMU capability recheck

The probe attempted only disabled, self-scoped perf_event_open calls for
instructions, cycles and task-clock, excluded kernel/hypervisor activity, and
closed every successful descriptor without enabling it. `result.json` binds
the script, UID/capabilities, current paranoid/seccomp state and syscall results.

All three calls returned EACCES with UID1000, zero effective capabilities,
perf_event_paranoid3 and seccomp0. No security, isolation, affinity, or global
kernel setting was changed. PMU counters remain unavailable through this route;
that does not block ordinary correctness or local CPU-time experiments.
