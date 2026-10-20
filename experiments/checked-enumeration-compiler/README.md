# Checked-slider compiler discriminator

The [report](report.md) closes the selected generic build, library/differential
checks and complete caller/helper capture. No timing, PGO or adoption occurred.
Retained62 and canonical engine source are unchanged.

`prototype.patch` is the original source-only prototype. Apply it to native
source at `e2301c04352cd21eb923b4c20982c2e31c55669f`, then apply
`fixture-repair.patch`. The repair changes only an appended test fixture;
`fixture-repair.json` preserves the initial failure and exact repaired identity.
`plan.json` identifies the original pre-repair graph, not the built graph.

`run_scope.py` runs the finite tests/build; `capture.py`, `inventory.py` and
`resolve_calls.py` retain full machine code, owner inventories and resolved ELF
call slots. They use fixed external roots and exclusive stage outputs: choose
fresh roots and prepare/admit source/tool maps before reproducing this closed
instance. Nothing here automatically authorizes another build or run.

Raw evidence, both test attempts, stable pre-build source archive, complete
disassembly and images are outside the repository at
`/home/legolas/rook2-experiments/checked-enumeration-compiler-20261020-01`.
See `closed-summary.json` for the exact images and named supports.
