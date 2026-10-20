# Pressure presence experiment

`report.md` closes the build/test/compiler discriminator. `closed-summary.json`
pins the actual artifacts and named external support records. No production code
is adopted by this setup.

Reproduction starts from detached base `e2301c04352cd21eb923b4c20982c2e31c55669f`
in an isolated worktree, then applies `prototype.patch`. Check the exact two
changed file hashes and complete source/tool graph in `plan.json`. The selected
instance's raw artifacts live under
`/home/legolas/rook2-experiments/pressure-presence-compiler-20261020-01`.

Under housekeeping affinity0–5,8–13, PATH=/usr/bin:/bin,
TMPDIR=/home/legolas/rook2-build-tmp and PYTHONDONTWRITEBYTECODE=1:

1. `run_scope.py tests` runs the full library suite, including the seven new
   pressure controls and eight existing Activity controls.
2. `run_scope.py build` invokes the unchanged generic build helper, then freezes
   `build/rook2-exact` at mode0555 after source/flag checks.
3. `tools/archive_build.py EXTERNAL_BUILD` verifies and archives pre-build source.
4. `capture.py` captures both exact images' full disassembly, symbols and rodata.
5. `inventory.py` emits address-bounded static metrics, not dynamic traffic.

Readelf relocations resolve the remaining indirect Activity error calls; complete
captures and the resolution are external. The admitted historical generic control
was reused only after matching native source, compiler hashes/config and actual
flags. Its recorded helper predates profile-only ExtTSP support.

All stage directories must be fresh. A new independent reproduction must choose
fresh external roots in the setup, preserve failed outcomes, and bind its actual
outer tool completions separately. Do not overwrite the closed instance. Build
and test logs are retained files; the240s process-group bound is not a general
escaped-descendant supervisor or an output-volume cap.

The subsequent fixed70 generic screen is separately selected by the lead. Its
frozen plan, execution and result belong to this same experiment record, with
raw measurements external. No timing, PGO, retuning or adoption follows merely
from running the compiler-stage scripts.
