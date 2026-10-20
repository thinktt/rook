# Compact48 TT: bounded own-PGO trial

**PARK.** The one own-PGO fixed70 screen is 0.292952% lower in
aggregate, below the required 0.5%: ratio 0.9970704781,
6/7 lower, worst 1.0011708050. Summed medians are
11.8722445s retained62 and 11.8374645s compact48. No repeat,
retune, rescue or adoption. Retained62 remains unchanged at whole54
67.640360 CPU seconds and regular12 games 675.156653 CPU seconds on Vic.

All 196 library tests, fresh 54-case training/independent replay/remerge checks,
the actual backend gate, and 70 live + 70 independent screen replays pass.
All 70 native PIDs are unique; 14 warmups are excluded and 56 measured samples
retained. All 201 immutable pins and live 76-file source maps close unchanged.
The final native stage closed at 795.906/1800 elapsed seconds.
Collection 286506/0; independent reconciliation fef40e/0; all owned jobs terminal.

| Case | Control range / median CPU s | Compact48 range / median CPU s | Ratio |
| --- | --- | --- | ---: |
| profile-01 | 0.890912–0.900248 / 0.893236 | 0.889583–0.896487 / 0.891077 | 0.997582387 |
| profile-02 | 0.597870–0.604354 / 0.601608 | 0.594913–0.602127 / 0.596238 | 0.991073929 |
| profile-04 | 3.774789–3.809304 / 3.793922 | 3.784975–3.872242 / 3.791825 | 0.999447142 |
| profile-05 | 2.115086–2.127195 / 2.119909 | 2.104437–2.136081 / 2.122391 | 1.001170805 |
| profile-29 | 0.200977–0.204551 / 0.203225 | 0.201894–0.205410 / 0.202248 | 0.995192532 |
| profile-35 | 3.926542–3.952445 / 3.929983 | 3.884956–3.915646 / 3.904931 | 0.993625419 |
| profile-08 | 0.328892–0.331192 / 0.330359 | 0.325869–0.330918 / 0.328753 | 0.995138622 |

CPU15 interval tick deltas: `[1, 0, 0, 13039, 0, 0, 0, 0, 0, 0]`. No owned CPU15 workload was run;
these point observations do not prove continuous isolation. No sample was
deleted. Whole-image GOT scans confirm only the two candidate outlined-store
calls (versus three control sites) identified in the actual backend review.

The layout keeps one 48G allocation and original primeG/modulo, placing four full
32-bit identities at offsets 0/4/8/12 before four 8-byte payloads, with 16-byte group
alignment. No census instrumentation, public behavior, second slab, sparse clear,
explicit SIMD, padded group or alternative design was introduced.

Three new differential controls compare results AND complete logical slot state
with an independent frozen copy of the old table: collisions/recent duplicates,
all five replacement branches, normal/mate/signed/window metadata, stale entries,
identity 0, 255-step generation wrap and deterministic mixed sequences. The 196
library tests passed once; the two development tests were outside this library
command. The only warning was an unused test-only old-oracle helper. Source
remained unchanged through both builds/training and the timing screen.

The exact own-PGO-first method trained the one instrumented image on every
original 54 case once (54 unique native PIDs/raw files), then independently
checked original replays, raw/PID/source associations and a byte-identical merge.
One own-profile use build applied ExtTSP to profiled functions only. The use-step
receipt's `fresh_training:false` describes that code-layout step, which itself
runs no training; it does not mean this pipeline borrowed an old profile.
Generic x86-64, Rust1.85.1/LLVM19.1.7, O3/thinLTO/one CGU/panic abort/debug 1 were
retained. There was no generic timing lane.

| Identity | SHA256 | Bytes |
| --- | --- | ---: |
| Retained62 control | 01237e6dfe89822e540d0f07c7b70f7227537a846ce8c69ea9e91167b759e98d | 7118376 |
| Instrumented compact48 | a4a21e110ff69ad15032e412d30a9f9525786a6e8636a8f87959c3e0d9e937bf | 7666480 |
| Own-profile compact48 | e2b2d9ee1f725e7a0b96bb4513b3d3127160d68023e4c2a9910fe25f1d67dd5e | 7119752 |
| Fresh merged profile | 3f7e3dfaafc08fbe4b940eaa571de8be047536115f03e744f306521fde44fb22 | — |
| Native53/tool23 source graph | 182e3bcfa32816aa0b7121e7322b07efb4fcca9d3addae02667402a34b58518f | — |

The complete actual inline probe excludes payload loads on full identity misses.
All recent/retained metadata, mate writes, five inline/outlined store branches,
constructor/init/clear/drop and actual caller paths were reviewed. Same 48G,
one allocation and 32B metadata survive. Whole ordinary grows 199B, separate
store shrinks 69B, combined grows 130B; ELF .text grows 128B. Ordinary keeps its
0x568 local frame and six saves; outlined store stack including saves falls 40B
to 8B. Static ordinary call sites 114->113 and RSP references 1185->1162 are not
dynamic traffic or spill counts. New records use four scalar writes rather
than six; displacement keeps the same 12-byte identity/payload association.
These compiler changes establish the intended mechanism, not a speed claim.
See the two backend reviews for exact addresses and limits.

One 1800-second monotonic native-lane ceiling began immediately before the first
tests, including all intervening analysis gaps; stricter stage, memory and output
caps remained active. No native stage was retried, source retuned or second
layout prepared. One source-only resolver preparation AST error was corrected
before its first execution; both texts and the failure are external. Read-only
inspection path/format corrections did not replace executed stages. Effective
PGO helpers relocate paths and pin the exact archival-only 24th canonical tool;
training order, raw-model/replay code, merge and build recipe are unchanged.

The fixed70 screen uses cases 01/02/04/05/29/35/08; warmBC then measuredBC/CB/BC/CB,
14 excluded warmups and 56 measured lifetimes. Direct wait4 accounts whole native
process CPU, including startup/table initialization, not prepared-loop or isolated
TT time. Helpers stay on 0–5,8–13; natives use 14; no owned CPU15 job. Guest snapshots
are point observations, not exclusive-host or continuous-idleness evidence.
No PMU is available. The fixed rule requires summed-median ratio<=.995, at least
5/7 cases lower, worst<=1.02 and all live+independent original replay checks.

The archived setup and bounded results cannot qualify performance, settle cache
traffic, establish a full 54/game speedup or discharge unresolved conformance
obligations. No promotion, repeat/retune, alternate layout, broader 54/12 run or
external work is authorized by this trial. Raw data, binaries/profiles, complete
assembly and build products remain under
`/home/legolas/rook2-experiments/compact48-tt-20261020-01`.
