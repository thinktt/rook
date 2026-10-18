# Optimized production instruction simulation

Frozen PGO ordinary artifact
`3660fecfa0c4a681e6a7152009417199d91706fa9acf0508e073c76427e18438`
passed the unchanged public profile-01 replay while running under the same
locally extracted public Valgrind3.24.0 tool used for the earlier baseline.
`provenance.json` re-verifies the package/tool identities and binds the launch,
oracle and annotated source.

The whole lifetime reports13,607,144,696 simulated `Ir`, versus the previous
baseline's20,083,250,913. Both source optimization and compiler PGO changed
between these artifacts; this is not an isolated PGO instruction result.
These are simulated instructions, not PMU retired instructions or CPU cycles.
The actual four-case CPU experiments remain separate.

PGO inlined attack finding into its callers, changing attribution labels.
Comparing function-table rows directly with the older binary would misattribute
work. `movegen-lines.txt` retains source-line annotation matching the frozen
native source to inspect those costs. Activity and influence construction are
prominent remaining simulated-cost rows. Those observations motivate future
whole-pipeline experiments, not exclusive CPU shares or guaranteed removable
cost. This run makes no qualified cross-host or final performance claim.
