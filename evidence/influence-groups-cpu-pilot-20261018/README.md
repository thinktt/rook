# Generic typed-list influence comparison

Generic10634820 enumerates the existing typed piece lists while preserving
the exact native influence rays, contribution wrapping and lifetimes. It passes
134 native tests, including10,000 placements compared with both mailbox and
coordinate oracles before/after type-order reversal, all54 strict replays and
eight interruption fixtures/24 searches. Position160/Node176 is unchanged.

The matched six-case pilot against genericf28279c3 retains60 fresh native
lifetimes:12 excluded warmups and48 measured, four alternating AB/BA samples
per variant/case. Every strict oracle, normal exit, original native/comparator
hash, schedule, artifact/input identity and one-time CPU14/single-task/helper
placement observation reconciles independently. No sample failed, was dropped,
replaced or rerun. Session95713 actually returned0(chunk10071f).

Sum of case CPU medians:16.181479s baseline versus15.4118105s typed lists,
ratio0.952435219(4.756478% lower). All six observed candidate maxima are below
their baseline minima. These finite ranges do not establish a confidence
interval, universal benefit or acceptance allowance. All raw samples remain.

This supports testing the influence change together with the selected relation
lookup under a fresh PGO profile. No combined or standalone PGO gain is inferred
from these generic results. Production is unchanged. Direct wait4 includes
startup/destruction and a small Python pre-exec prefix, without protocol relay.
No owned builds/tests/other engines/profilers overlapped measurement. Final
PMU/resource/observer/uncertainty/calibration, full54/12 and gameplay obligations
remain separate.
