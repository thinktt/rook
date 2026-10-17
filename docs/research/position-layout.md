# Compact position layout receipt

The standalone [microexperiment](../../experiments/position-layout/main.rs) independently checked the proposed compact mailbox/type-grouped layout using only the released specification. It is not an engine crate, legal generator or conformance adapter. [Recorded results](../../experiments/position-layout/results.json) passed before timing.

Rust 1.85.1, `#[repr(C)]`, generic x86-64 optimized compilation produced:

| Fields | Bytes |
| --- | ---: |
| Mailbox | 64 |
| Six type groups sharing sixteen square slots per color | 32 |
| Twelve type counts | 12 |
| Primary, secondary and pawn fingerprints | 12 |
| Side, rights, EP sentinel and reversible count | 4 |
| Raw starting-square occupancy measure | 1 |
| Tail padding | 3 |
| **Position size / alignment** | **128 / 4** |

Fingerprint fields begin at byte108, rules at120, raw starting measure at124. Adding an `i32` square balance gives132 bytes. Adding square balance, two retained `i32` evaluation terms and an age byte gives144 bytes. The128-byte result therefore describes the position fields above, not every branch/evaluation field. Reading padding as part of an output digest is avoided.

Each color's count sum is at most16; per-type counts can reach15 for non-pawns. Four constructed capacity controls checked king plus fifteen knights, bishops, rooks or queens. This follows [setup](../../../king-spec/spec/position-setup.md), rather than imposing narrower nine-queen/ten-other-piece diagnostic bounds. A promotion removes the pawn before inserting the promoted type, so total occupancy needs no extra seventeenth slot. Type boundary16 is a valid end index, not an on-board square.

The proposed raw starting measure must remain occupancy-derived even below the phase material gate. [Phase](../../../king-spec/spec/root-material-context.md#eval-phase) substitutes effective U=0 when M<=32; a later promotion can cross that gate. Keeping only gated U and applying local deltas would lose contributions from unchanged home pieces. Kings contribute no raw U. Phase material normalization must use actual type totals and its specified carries rather than saturating or replacing material counts.

The experiment applies selected quiet/capture/promotion/castling/EP/null transitions to this one representation. A separate reference uses per-type vectors and recomputes fingerprints/raw U. Before timing, every child matched all state fields, compact counts/lists matched the mailbox, derived fields matched recomputation, all inactive list slots retained their sentinel, and reverse edits restored the full parent. Controls include middle-list removal, promotion append, both-color castling/EP, reversible-count wrap, double-push EP presence/absence, and joined EP with a rook behind the target. Move geometry/king safety are not generated or independently qualified here.

The mutation record is40 bytes in this experiment: prior fingerprints/rules/raw U, up to four overwritten mailbox cells, and up to three reversible list edits. It restores capture victims at their original chronology index and undoes promotion insertion/removal in reverse order. Castling changes two squares in their existing type slots. EP removes the actual behind-target victim. Null changes only side/EP/counter in this state-only scope; its evaluation-age behavior belongs to the enclosing frame. These follow [move transitions](../../../king-spec/spec/move-sequence.md) and [null transition](../../../king-spec/spec/evaluation-moves.md#null-transition).

Compilation used helper affinity `0-5,8-13`; the single short execution used CPU14. This work launched nothing on CPU15. Build and execution used well below the requested five-second total CPU budget by observed duration. Compilation command:

```sh
taskset -c 0-5,8-13 rustc --edition=2021 -O -C target-cpu=x86-64 experiments/position-layout/main.rs -o experiments/position-layout/layout-micro
taskset -c 14 experiments/position-layout/layout-micro
```

One512-repeat warmup per route preceded three4096-repeat samples, with12 transitions per repetition. Sample order alternated copy/delta. Every child and restored parent had all semantic fields consumed into the same matching fold. Timed intervals include transitions, result consumption and restoration, plus common loop bookkeeping; input construction and correctness controls are outside those intervals.

| Sample | Copy-child route, ns | Delta restoration route, ns |
| --- | ---: | ---: |
| 1 | 12,920,979 | 12,528,327 |
| 2 | 12,934,175 | 12,309,392 |
| 3 | 13,005,394 | 17,454,523 |

These are monotonic wall observations from a very short, repeated-input microexperiment. No PMU/CPU timer or noise diagnosis was collected, and output consumption is substantial. The third delta sample remains in the receipt. The observations do not select a restoration strategy or establish whole-engine speed. Keep copy-child as the simple production baseline; revisit delta only through integrated meaningful search with identical behavior and appropriate measurement boundaries.
