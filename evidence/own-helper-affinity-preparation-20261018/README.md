# Scoped own-helper affinity correction

The source is prepared and syntax-parsed only; no affinity has changed yet.
After the original collector handle37105 is authoritatively terminal,
`limit_ancestors.py --output evidence/owned-helper-affinity-20261018` checks that
the old collector and named native image are gone. It constrains only the two
previously observed Codex ancestors of its own process, rechecking ancestry,
UID, process start ticks and executable identity. It records every observed
thread affinity before/after and checks convergence as threads start/exit.

The target is the lead/client process pair, not other agents or guest tasks.
Only their thread scheduler affinities change to0-5,8-13. No host/global
isolation, cpuset, kernel, security or privilege setting changes. Existing
engine accounting explicitly assigns each future native child to14; inherited
helper affinity is not a cpuset restriction. This point correction does not
establish continuous exclusive CPU14/15 ownership or quantify prior interference.
The already running collection retains its original conditions and limitation.
