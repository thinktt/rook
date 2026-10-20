# Current25 pipeline ownership: a small concrete copy backup, no unmake redesign

The clearest removable owner is **the intermediate Position result inside Node::child**, not move application or parent restoration. Keep a direct mutable-Node-construction spelling as a separate small backup. The evidence does not establish a large material pipeline saving, and does not justify a Position/Node layout change, unmake design, or the broader entry-borrow refactor. Parent has selected the independent arithmetic-only pressure pair-sum as experiment27; this review authorizes no implementation or measurement.

Current production remains exact51529 (candidate25). Experiment26 phase sharing failed its advance rule and is parked. The Bee75.770s versus RustPGO63.277733s search-CPU gap is context only; the following two simulated lifetimes do not explain or convert that gap.

## Disjoint actual copy attribution

| Selected source/copy owner |35: copy leaf Ir + related exclusive caller rows |08: same | Share of whole simulated Ir35 /08 |
|---|---:|---:|---:|
| Ordinary entry snapshot, ordinary728 |48,209,397 +9,974,358 |12,658,355 +2,618,970 |0.127144% /0.385028% |
| Q entry snapshot, quiescence234 |60,449,050 +10,422,250 |5,151,328 +888,160 |0.154868% /0.152211% |
| Required parent→child Position initialization, position246 |113,339,743 +23,398,662 |21,702,585 +4,455,642 |0.298802% /0.659254% |
| **Intermediate Position→child transfer, position248** |**113,339,743 +15,616,088** |**21,702,585 +2,981,944** |**0.281795% /0.622113%** |

Entry snapshots together are129,055,055/21,316,813 known instructions (0.282012%/0.537238%). They occur on1,662,393+2,084,450 and436,495+177,632 **explicit calls=** respectively, not entries inferred from Ir. The two child-copy stages each occur on3,908,267/748,365 explicit calls in Node::child or its ordinary/Q inlined paths. Direct session/output played_unchecked uses are excluded from these Node-only groups. Each selected call copies160 bytes and its observed libc leaf executes29 simulated instructions. Logical copied bytes per child stage are625,322,720/119,738,400; these are not DRAM traffic, bandwidth, or cache-miss measurements.

The dynamically resolved libc function is raw `0x0000000000162880` under object2 `/usr/lib/x86_64-linux-gnu/libc.so.6`. The saved exact51529 Node::child assembly calls the real memcpy GOT slot at both corresponding sites. The raw helper confirms that target is a recorded leaf, and **all incoming arc Ir sums exactly to its exclusive self Ir**:491,144,601/70,963,320. Inclusive arcs therefore partition that leaf cost; they are never added again to its exclusive self rows. Caller source rows in the table are different exclusive instructions, and all four selected groups are disjoint by raw-row/arc IDs. Some caller rows include required result/setup transport; their full sum is not a guaranteed removable total or complete CPU upper bound. No unknown/line0 aggregate is assigned to copies.

`attribution.json` retains every selected raw line, function and arc. Function suffixes plain/`'2` are preserved without guessing generic parameters. The initial name-only exploratory files found only symbol-named memcpy entries, missing the resolved libc implementation; `profile-*-resolved-copy-arcs.json` and final attribution supersede that exploratory query without overwriting it. Raw exclusive totals reconcile to45,762,253,122/3,967,850,732. No old6a shares are transferred.

## Actual lowering and the narrow backup

At emitted Node::child0x14830, a168-byte frame holds a160-byte Position temporary. Normal/special move paths converge on:

-0x1497b–0x1498f: parent.position → `[rsp+8]`, length0xa0, memcpy throughr13.
-0x14992–0x14997: apply_unchecked on that local Position.
-0x1499d–0x149a9: local Position → returned Node.position at`[rbx+0x10]`, length0xa0, same memcpy.

Ordinary's inlined child path repeats this shape around0x34d65–0x34da0; Q has corresponding paths around0x2ca46–0x2ca82 and0x2cfe7–0x2d024. Thus the duplication survives optimization; it is not inferred from source Copy derives or frame size. The out-of-line child already writes retained values directly into the return object after that second Position transfer.

The proposed **source-only hypothesis**, if parent later selects it, is to keep all existing moving/victim/promoted/castling nonking arithmetic in place, initialize a mutable Self with `position:self.position` and exactly the original Retained inheritance, call `child.position.apply_unchecked(movement)`, then return child. This makes the final Node.position available as the mutation destination and could permit return-place construction with only required parent→child initialization. It does not require an into-uninitialized API, unsafe, fields, unmake, a second transition implementation or changes to the primitive.

The second transfer is not semantically mandated. But Rust need not construct the named local in the final sret destination: it may build a whole176-byte Node temporary and move that at return, merely relocating/increasing transport. Existing lowering supports the hypothesis, not erasure. An eventual cheap falsification gate is the **actual exact-source optimized default out-of-line and ordinary/Q inlined paths**: if160-byte transfer persists or becomes an equivalent176-byte return copy, drop without CPU timing. Also inspect frame/lifetime changes and actual helper calls. No such prototype, build or binary scan ran here.

Constructing Retained before apply would only move pure reads/arithmetic relative to a private local mutation; parent remains shared/immutable. Preserve all calculations and panic/error admission, including the explicit king-victim assertion. No user observer, charge or host call may move. Broad same-Position+Retained differential tests and actual protocol/strict checks would remain necessary if selected; source spelling alone proves no backend saving.

## Why application, restore and entry borrowing are different

Position::apply_unchecked269–345 performs required piece-list chronology, capture removal, promotion append, castle rook movement, placement identities, starting-credit/AttackBits maintenance, rights, joined EP eligibility, reversible count and side updates. Its1,792,523,759/274,643,353 exclusive Ir across all inline-source partitions is **not** an avoidable-copy envelope. Node::child38–80 additionally computes the exact root-derived nonking square delta, inherits positional/pawn retained values and advances age modulo256. Neither owner can be replaced by “just update a board.”

Ordinary/Q already leave their parent Node intact and recurse into independent child Nodes. `history.push`/`pop` restores path history, not a mutated parent Position. There is no hot whole-parent Position restore to eliminate. Ordinary821/null,896/shallow-Q,990/main and1135/IIO preserve these lifetimes. Main1020–1054 retains one child through scout and full-window retry, including refreshed child Retained. Recreating the child before retry would change behavior. Q392–427 intentionally retains a prepared reply-probe child and reuses it after history pop and final safety admission. Do not fuse/move those sites or reopen the parked projected-plane-child trial.

Released ordinary-iterations.md244–264/350–356/396–416 and quiescence-tree.md54–66/150–178 require exact child inheritance, parent preservation, retry reuse and chronological shared effects. Move-sequence.md remains authority for ordered transitions. These are semantic constraints on any ownership change, not requirements to retain a redundant temporary buffer.

Entry snapshots are also real: ordinary0x2fc39 and Q0x2ad84 memcpy160 from Node.position to local stack storage after charge/pv admission and before evaluation. Fixed frames are1320/1480 bytes plus48 bytes of saved-register pushes; those large frames are not removable-copy volumes. The immutable Position snapshot survives while evaluator fast/full/select accepts &mut whole Node and mutates only Retained plus evaluator-owned caches. A future internal `(&Position,&mut Retained)` split could permit a long-lived borrow and remove that snapshot without unmake. But it affects several evaluation wrappers/observers for only the0.282%/0.537% known instruction component.

Important current-source correction: ordering_phase1083 already accepts **&Node**, not &mut Node. It constructs separate child Nodes. It is not itself an additional mut-whole-Node blocker. Ordinary's Predecessor805 retains the same parent Position and Influence across null/main/scout/retry; a borrow refactor must preserve that lifetime and current Retained chronology. It must not refresh the Influence, reconstruct from descendants, or reset learning/pawn/cache effects. This broader seam is currently deprioritized.

## Recursive return packing and next evidence

Existing exact51529 returns use outward result pointers. Ordinary's normal tail0x354a2–0x354ae writes the score at+4 and Ok tag6 at+0. Q's common tail0x2d48c–0x2d4a3 writes fields spanning16 bytes, then restores its frame. This is concrete packing/transport, but does not show that compacting Stopped would eliminate a frame, sret, or many instructions on the real hot paths. Public Stopped retains configured NodeLimit(u64) and exact HostIo(ErrorKind), plus the IIO/host/poll reasons; errors must unwind history before propagation. Mapped core/result.rs costs8,685,796/1,270,580 under recursion are neither the complete packing cost nor an avoidable upper bound; normal/error/line0 ownership remains mixed. There is no defensible material return-ABI gain from these reports alone, so no compact-stop implementation is selected here.

Judgment: do not make an architecture/layout/unmake change to chase the entire apply/recursive owner. The **one-function direct Node initialization** is the best concrete backup because the duplicated transport is observed and the semantic boundary is narrow. Its measured component is still small; no claim is made that it closes a material fraction of the19.74% Bee gap or even passes the0.5% CPU advancement rule. Parent's smaller arithmetic trial can proceed independently. If this backup is later selected, first prove erasure rather than relocation in the actual matched backend, then run unchanged functional and predeclared matched CPU gates. No new census is needed to establish the duplicate.

Exact image51529cebf24ad91b0cf86e4ae497bc32bb7ad7a819f8b300f8b86028326b254a and saved function hashes are checked against existing identity/function-capture records. Frozen compiled source for six audited native owners equals its image's source-before and current root at review time. `input-pins.json` includes exact raw profiles/provenance, parser, source/spec and assembly hashes. All original inputs were rechecked unchanged. All work was offline source/saved-text/raw interpretation on housekeeping0-5,8-13; no binutils, builds, engines, tests, profiles, timing, Git or archive ran. Final analysis ACTUAL22ea05/0; all owned jobs terminal.
