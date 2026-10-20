# Pressure presence: parked after the fixed70 generic screen

The candidate misses the unchanged advancement gate. Summed case medians are
**13.392375s control /13.4497075s candidate**, ratio**1.004280981**: candidate
**0.4281% slower**. Three of seven case medians are lower; worst ratio1.007737654.
The aggregate≤0.995 and≥5lower-case gates fail; the≤1.02 worst-case gate passes.
Park this source. No second screen, retune, PGO rescue or adoption is selected.

All70 fresh native runs and all70 independent original replay checks pass.
Four measured CPU samples per variant/case are retained;14 separate warmups are
excluded by the frozen protocol. CPU is whole-native wait4 user+system, in seconds.

| Case | Control min / median / max | Candidate min / median / max | Candidate/control median |
| --- | ---: | ---: | ---: |
| profile-01 | 1.003081 / 1.005756 / 1.007473 | 1.011341 / 1.013371 / 1.019329 | 1.007572 |
| profile-02 | 0.707644 / 0.709620 / 0.712612 | 0.702031 / 0.709445 / 0.716272 | 0.999753 |
| profile-04 | 4.288096 / 4.301367 / 4.329578 | 4.295685 / 4.316079 / 4.348429 | 1.003420 |
| profile-05 | 2.362582 / 2.368030 / 2.380435 | 2.382285 / 2.386354 / 2.413516 | 1.007738 |
| profile-29 | 0.238852 / 0.240342 / 0.240988 | 0.237591 / 0.239284 / 0.240915 | 0.995600 |
| profile-35 | 4.361399 / 4.384495 / 4.386125 | 4.400560 / 4.407076 / 4.440293 | 1.005150 |
| profile-08 | 0.381226 / 0.382765 / 0.385164 | 0.376943 / 0.378099 / 0.378605 | 0.987808 |

The images remain the compiler-stage candidate
`34083ebb796d88940d8eb210c18966edd1759eeb9eb12a564de5070f7cb85b2a`
and admitted generic57 control
`5d10b2fa6b75b1eead79a444c5eaccd13f5e8b959e1d0469075be1ebabba27e6`.
Both are generic engineering artifacts, distinct from retained own-PGO62.
No build or source change occurred between compiler closure and this screen.

The existing three screen helpers are byte-identical to the earlier fixed70
method. The seven-case order and balanced warmup/BC,CB,BC,CB schedule were frozen
before the first native run. Post-run comparison confirms all70 schedule entries,
70 unique PIDs,56 measured samples, exact outputs, valid direct-owned accounting,
CPU14/single-task placement and unchanged186 input pins plus both ELF hashes.
The native76 source/tool map, canonical native51 and retained62 image also remain
unchanged. Checked-slider source is still unchanged and unbuilt.

Helpers ran on0–5,8–13; no owned work used15. CPU15 guest entry/exit snapshots
show1 user tick,1 system tick and14,620 idle ticks; these point observations do
not establish continuous sibling idleness or host exclusion. Raw contexts, all warmups and samples, process receipts and
complete original comparator outputs remain external. No outcomes were discarded
or replaced; no measured launch failed or was repeated. A metadata-only preparation
assertion about the explicit no-PGO receipt schema was corrected before plan
creation and is preserved separately; it did not execute native work.

Actual outer collection completion: `b2d4aa/0`; reconciliation: `3e17c2/0`.
The offline original checker reports70 checks and zero engine launches. Quiet
window closure was reported to the lead. Source-only/backend observations in
[the compiler report](report.md) do not isolate the cause of this small net loss;
there was no new profile, PMU collection or component timing. This is an engineering
pilot disposition, not full54, regular12 or final qualification.

Raw screen evidence:
`/home/legolas/rook2-experiments/pressure-presence-compiler-20261020-01/generic-screen`.
The activated plan/schedule and original preparation snapshots are beside it in
`screen-preparation`; `screen-closed-summary.json` pins named supports. Retain62.
