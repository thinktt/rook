# Checked-slider compiler/tests result

Recommend one ordinary generic screen if the strategy lead selects it. The
mask test actually skips traversal before coordinate construction or mailbox
loads, and unchecked directions acquire no ray-mask test. The tradeoff remains
uncertain: generation code grows, the full generator reserves another16 bytes,
and checked loops retain stack traffic. This stage contains no timing, own-PGO,
source adoption or performance claim. Retained62 remains production.

All196 library tests pass after one test-fixture repair. The original attempt
passed195 and panicked in the appended all-rays fixture before comparing
generators: the southwest target b2 had no two-square perpendicular continuation
in either direction. Moving its interposition checker one square past the target
keeps all eight fixtures on board and preserves the intended capture/blocker
checks. Production code and the inherited test prefix are byte-identical before
and after this repair. The failed run and original patch remain preserved.

The three new test groups compare full ordered inventories and exact bounded
witnesses with the old unpruned enumeration plus mailbox safety projection.
Coverage includes both colors, eight ray signs, B/R/Q, capture/interposition,
prior friendly blockers, edges, promoted inventories/reversed source chronology,
joined EP, castling/promotion controls, zero/one/two bounded replies, sole
non-king replies and double-check zero evasion masks. Below two replies, the
complete reusable list is compared. These finite checks are not final
conformance or gameplay qualification.

## Identities and execution

- Candidate generic image: `0cde6b78b95a3b99840560c52ae315b5813815810f44099948c14a9bb36b7ead`,
  7,066,128 bytes, mode0555, external `build/rook2-exact`.
- Admitted generic control: `5d10b2fa6b75b1eead79a444c5eaccd13f5e8b959e1d0469075be1ebabba27e6`,
  7,060,840 bytes. Its native51 map matches retained62; compiler hashes, Cargo
  profile, empty Cargo configuration and actual generic flags match. Its older
  build helper predates profile-only ExtTSP support; no control rebuild was
  needed. This is the generic source control, not the retained PGO62 image.
- Original patch: `cfc7b78342db83768c7acbb76bf5e26b5a8dae5fc1e1e2043243000ee0f7df06`.
  Test repair: `0505efb5ce07e6a09c82f26e0ae5feea4101e4e49432bf45d577625e4d155ff2`.
- Built movegen.rs: `5e3abd5104fa78b126928e206a77c157232910bfbcfbf736e1660ed41a0f2ec1`.
  Repaired native51/tool24 graph:
  `54e90c138807e704937e241e5d11c692b59bb92e35f34d2d5305759df096701a`.
- One generic release build: Rust1.85.1/LLVM19.1.7, generic x86-64, O3,
  thinLTO/one codegen unit, panic abort/debug1, no profile. Tests, compiler and
  capture helpers ran on0–5,8–13; no CPU14 measurement or owned CPU15 job.

Actual outer completions: initial tests `c63c70/1` (native cargo101), repaired
tests `b09611/0`, build `ee3b26/0`, capture `1aca87/0`, source archive `c530a8/0`.
Repaired tests and build each observed child exit0 and stable input maps.
The verified75-file pre-build archive is external, SHA256
`c7bf315c6cd8cdfa04503361a2e11c4a314d10e315797dc8e14ea247de50cc9c`.

## Complete compiled owners

Full ELF disassembly, symbols, sections, rodata and relocations were captured
for both images. The full512 path inlines `pieces` and `checked_sliders` into
`generate_legal`; the bounded2 path calls the sole outlined `pieces`, which
contains its inlined checked walk. There is no separate new helper call.
Values below are decimal bytes; local reservations exclude saved registers.

| Owner/property | Control | Candidate |
| --- | ---: | ---: |
| full generate_legal code | 5,405 | 6,575 |
| bounded legal_replies_up_to_two code | 3,338 | 3,338 |
| bounded pieces code | 2,300 | 3,475 |
| all emitted movegen owners | 17,895 | 20,240 |
| movegen + ordinary visit/order + Q visit code | 36,380 | 38,725 |
| entire ELF .text section | 500,251 | 502,603 |
| full generator locals / saved registers | 264 /48 | 280 /48 |
| bounded wrapper locals / saved registers | 232 /48 | 232 /48 |
| bounded pieces locals / saved registers | 184 /48 | 184 /48 |
| ordinary / Q / ordering locals | 1,064 /1,224 /504 | 1,064 /1,224 /504 |
| lexical RSP memory sites: full / bounded / pieces | 251 /153 /101 | 300 /153 /151 |

Lexical sites exclude LEA/NOP and omit aliased stack operands; these are not
spill counts, dynamic traffic or CPU savings. RBP is a general register here.
The two changed owners add2,345 bytes; alignment makes the entire .text increase
2,352 bytes. The remaining movegen owners keep their sizes and frames. Whole
ordinary/Q/ordering bodies keep their instruction shape, calls, branches and
stack operands after relocation/comment normalization; retained raw differences
include renamed/moved anonymous constants and jump tables. This is not a claim
of byte-identical ELFs or a substitute for checking data references.

ELF call-slot resolution confirms ordinary consumes full generation; Q consumes
both full and bounded generation. The same full/bounded consumers also remain
in output, session adjudication/coordination and the top-level runner. Complete
consumer bodies are in `full.disassembly`; ordinary/Q and all movegen owners
also have separate captures. Existing attack, pawn and pawn-prefix helpers are
retained; cold indirect calls resolve to existing panic/slice owners. The
unchanged pawn-prefix memmove calls include register-indirect r12/r15 calls
loaded from its existing memmove GOT slot; no new successful-path helper was
introduced.

In the candidate full owner, kind/check dispatch at25c53–25c7c reaches the old
walk at260e0 when unchecked/non-slider. Only the checked branch forms the MASKS
ray base at25d34–25d49. Tests25dbe and25f6e jump directly to the next direction
before step construction and mailbox loads at25e0e/25fbe. The bounded helper
has the same structure: dispatch23634–23657, checked MASKS base23760, and
tests237de/2396e before mailbox loads2382e/239be. Its old route starts23acf.
Thus unchecked code pays entry dispatch and changed register allocation, but
no new per-direction mask work. It is not asserted to have identical cost.

Checked evasion/source-king variants duplicate inner walks in both owners.
Mask pointers, evasion masks and coordinates are kept on the stack (e.g full
25d49/25dae/25db6 and bounded23770/237d1/237d6), and surviving candidates still
copy their32-byte attack projection before `legal_after_bits`. Old unchecked
and checked destination/pin admission loops remain present. No second bitplane
view, ray construction, new cache/coherence state or wider ISA was introduced.

The test-only FORCE_PROJECTION branch bypasses the new dispatch and returns
the original mailbox projection before optimized admission. It therefore
enumerates every old direction independently of the new mask intersection.
King-first bounded witnesses, EP-before-safety handling, pawn ordering and
original blocker/near-to-far order are retained. EP is not pruned by this path.

The opportunity census already rejected off-mask candidates before safety
projection. Any possible gain here is avoided traversal/construction, not those
already avoided projections; average visited squares per attempted slider
direction are only about0.9–2.1 in the04/35 census. Entry costs, extra checked
mask loads, duplication and the larger full frame must be paid by an integrated
measurement. Recommend one unchanged-gate generic screen, without a speed
forecast; no such screen or later work is selected by this report.
