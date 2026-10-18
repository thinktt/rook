# Pure evaluation-input prototype replay

Frozen generic artifact3cc6dda6 passes all54 unchanged released strict
profiling replays. `profile-all.json` retains each full native stdout/stderr and
exit result; `identity.json` binds the actual native image and build receipt.
This isolated prototype does not add persistent node state. Its adjacent
six-case CPU pilot remains a generic-only experiment, with no production
adoption or inferred PGO benefit.
