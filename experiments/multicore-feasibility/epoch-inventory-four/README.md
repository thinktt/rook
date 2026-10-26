# Epoch colors plus conditional ordinary inventory4

Selected integration and fixed generic discriminator; preparation is in progress.
The accepted [source design](../../../docs/research/after-epoch-fourth-worker-choice.md)
and [eager-generation domain argument](generation-domain.md) guide the implementation.
This experiment preserves the positive epoch3 source/images/profiles and adds a
conditional third input reader only at confirmed ordinary FULL calls.

Scope: five configurations on original35/08/43, one warmup plus three fixed
rotations each (60 successful replay lives), five idle probes, no PGO/tuning or
qualification/adoption. Source/control/build admission precedes timing. Coordinator14,
colors6/4, inventory2; housekeeping0–1,8–13; siblings15/7/5/3 unassigned by us.
All native stages share one persisted3600s ceiling; collection1800s, per-life180s.
Raw products belong outside Git under `/home/legolas/rook2-experiments`.

`source.patch` is the complete isolated code delta from the exact64-file epoch
base; apply with `git apply --unidiff-zero` only after verifying that base map in
preparation.json. It uses zero context to keep patch artifact whitespace distinct
from code. The final build snapshots independently bind all candidate source files.
