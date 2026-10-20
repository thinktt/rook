# Pressure presence: compiler discriminator closed

The numerical mechanism survives this discriminator. Recommend the existing
ordinary generic screen to arbitrate a mixed cost tradeoff. No engine performance
measurement, PGO, source adoption or production promotion ran in this stage.

All200 library tests pass, including seven new pressure tests and eight existing
Activity controls. The new tests compare the complete Activity/shelter outputs and
relation charges against the independent original byte producer/consumer, with
duplicate/coexisting labels, category zero, lane boundaries, blockers/family gates,
all inventories, supplied maps, repeated calls and stale private planes. The
generic release build succeeds without source repairs.

## Exact identities

- Candidate: `34083ebb796d88940d8eb210c18966edd1759eeb9eb12a564de5070f7cb85b2a`,
  7,063,744bytes, mode0555, external `build/rook2-exact`.
- Admitted generic control: `5d10b2fa6b75b1eead79a444c5eaccd13f5e8b959e1d0469075be1ebabba27e6`,
  7,060,840bytes. Its recorded native51 files exactly match retained62 source;
  compiler hashes, Cargo profile, generic flags and empty Cargo config match.
  The older helper predates profile-only ExtTSP support; its actual generic
  compiler arguments establish reuse. It was read, not rebuilt or executed.
- Source52/tool24 graph:
  `ed163c28ce60d9d6e468c04ac9f9dabb4686cde0223f1b8efa56fa8c730191ef`.
  Base `e2301c04352cd21eb923b4c20982c2e31c55669f`; only activity.rs and the new
  test module differ. The complete patch is adjacent, SHA256
  `97ea2041febe9801c65d84a863d486683fc20004843a188fa397acc327137077`.

Build: Rust1.85.1/LLVM19.1.7, x86_64-unknown-linux-gnu, generic x86-64,
O3/thinLTO/one codegen unit, panic abort/debug1, no profile. Tests, build and
binutils captures ran on0–5,8–13. Actual outer completions: tests `373c74/0`,
build `7b09a9/0`, capture `b728ef/0`, inventory `f1287e/0`. Frozen source/archive
checks and canonical/retained62 identity checks pass; checked-slider source
remains unchanged and unbuilt.

## Actual backend

Complete Activity callers and both consumed pressure helpers were captured and
reviewed, including normal calls and cold error tails. Values are decimal bytes.

| Actual owner or property | Control | Candidate |
| --- | ---: | ---: |
| compute code | 7,884 | 9,287 |
| pressure helper code | 1,235 | 1,035 |
| combined Activity code | 9,119 | 10,322 (+13.19%) |
| entire ELF .text section | 500,251 | 501,451 |
| compute local reservation | 456 | 392 |
| compute saved registers | 6 ×8 | 6 ×8 |
| helper reservation/saves | 72 +6 ×8 | 0 +1 ×8 |
| max normal Activity-chain stack displacement from compute entry | 632 | 456 |
| lexical RSP memory sites: compute / helper | 198 /10 | 254 /0 |

The last row is an address-bounded inventory excluding LEA/NOP; it omits aliased
stack operands and is neither a spill count nor dynamic traffic. RBP is a general
register here, not a frame pointer. An initial exploratory count incorrectly
included18 control RBP data references; the committed inventory uses RSP only.
Smaller frame/scratch does not establish lower memory traffic.

Production byte marks, the256B PRESSURE_VALUES symbol and its old king_pressure
lookup consumer are gone. Eleven static byte-OR producer sites become eleven
indexed64-bit stack OR sites at the shared pair `[rsp+0x30]`, with destination
shifts and real memory dependencies (for example18bf0–18c11). The presence pair
is not promoted to two permanently resident registers. Pressure partial sums
and retained family masks also have real stack traffic: partial sum store19134,
load/store1967c/19686; diagonal mask store19619 and queen reuse1a859.

Four inlined paired reductions use PSRLW/PAND/PSUBB/PADDB/PSADBW and scalar
16/24 or8/16 weighting, e.g190d3–19131. Complete mnemonic review shows only
baseline integer/SSE2 instructions; no POPCNT, BMI, AVX, SSSE3 or population
helper. Kind-count branches bypass each absent kind's16B clear, destination
work, visibility and reduction. Queen reuses B/R masks at1a850–1a882 and computes
only missing families. Normal helper calls are0–2 per color, each admitted
slider family once; the old consumer was called twice per compute. There is no
unconditional kind-call chain. The remaining indirect calls resolve to existing
slice/bounds/panic error owners, not successful-path arithmetic helpers.

Setup is only partly gated: three16B mask loads at189d2/189da/189e2 are
unconditional, including when all Activity kinds are absent. Constants reload
after visibility calls (15 static load sites total; up to15 loads on the fully
populated normal path). Each present kind clears16B; eight groups still write
128B, matching the old clear volume despite the smaller scratch footprint.
Most scalar king geometry remains, with bit insertion replacing mark/table
consumption. Code growth, indexed RMWs, sum/mask spills and constant reloads are
the reasons to measure rather than forecast a gain.

The lead independently selected one fixed70 generic screen after reviewing these
same artifacts. That is a subsequent stage with its own frozen plan and unchanged
gates. This compiler result itself makes no speed or qualification claim.

Raw evidence, complete disassembly/rodata/relocations, source archive and images:
`/home/legolas/rook2-experiments/pressure-presence-compiler-20261020-01`.
See `closed-summary.json` for named support hashes. The scripts reproduce the
bounded setup; choose fresh external roots for a new instance and do not replace
the closed records.
