# Balanced whole-native CPU pilot

This is a reported-only local optimization experiment on public `profile-01`,
not either complete performance collection or a qualified reference comparison.
The unchanged released comparator asserted every post and selected move.

The frozen schedule was one warmup per variant followed by four measured rounds,
alternating variant order ABC/CBA/ABC/CBA. All15 runs passed. Engine processes
ran on CPU14; the comparator/accounting supervisors used housekeeping CPUs.
No owned build or other engine collection was active during this pilot. The
context snapshot was taken during collection and is named accordingly; it is
not a pre-collection observation or proof of exclusive host ownership.

| Variant | Artifact SHA256 | Median native CPU seconds | Measured range |
| --- | --- | ---: | ---: |
| Baseline | da82041f29091ed8db54f2cd2ffd0c338da5ae5216cae3caea6130974573e648 | 1.7741975 | 1.756293–1.781602 |
| Direct piece codes | 7e00a926c8346006b50c3be2ddb9f5263c0700cbf4d68442a44a426450f7e103 | 1.7817825 | 1.777684–1.795331 |
| Precomputed attack geometry | a78874670cd6a52d117b76c1ace893cb8ae8f417fa40a02b76f1164cbce24282 | 1.6939465 | 1.674495–1.698565 |

Direct codes have no established benefit here. Geometry's median is about4.5%
lower, but one workload cannot select a production layout or qualify a global
speedup. Both variants independently passed all54 public replay cases before
this collection. Their build folders contain exact verified source archives.

`manifest.json` binds the schedule, artifacts, recorder, comparator and inputs.
Every run retains direct native wait4 user+system CPU, parent wall boundary,
post-exec placement observation, hashes, exact comparator stdout/stderr and
exit status. Native CPU includes the small child pre-exec launcher prefix;
it excludes comparator/supervisor CPU. This known single-process engine uses
no worker processes or native threads. The one-time task observation is not a
continuous descendant monitor. `summary.json` retains all measured samples;
startup/shutdown are included, and no timer endpoint cuts off work at selection.

The approved reference's whole-life profile-01 companion value is0.894001s,
but hardware calibration and the measurement/uncertainty profile remain open.
No qualified cross-host ratio is claimed.
