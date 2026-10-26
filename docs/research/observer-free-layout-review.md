# Observer-free layout: a useful counterfactual, no established cache cause

Recommend one future **old-layout, observer-free counterfactual** before changing
this graph: retain the original concrete shared field types/storage and remove
only observation operations. Verify its compiled offsets against the old image
before interpreting a comparison. This is a recommendation, not selection of a
build, padding variant, alignment sweep or run. Keep the exact lean trial parked
and preserve 67d011/profile948747.

The representation changed substantially; no unique cause of the common3 regression is established. The closed 48-run record remains at c0417762. This review uses existing source/images only.

## What is compiled

Old inventory4 is SHA256
`36c40aee75f8a93c773bc450f440ac14a2a94d8faa1057549805659ea4092e5f`;
lean is `6da55696941e4197edd1c82499eb233d2da520630868722776da06492221e6c7`.
Paths/source/build bindings are in the
[closed report](../../experiments/multicore-feasibility/observer-free-inventory/report.md).
Debug1 has no private structure/member DIEs. These offsets are reconstructed
from constructor, publication, helper and consumption instructions, cross-checked
against source; Rust declaration order was not used to infer them.

Let **B be the Arc allocation address**, with refcounts at B+0/B+8 and Shared
at B+0x10. All offsets/sizes in this table are hexadecimal bytes.

| Storage/field | Old | Lean | Relevant ownership |
|---|---:|---:|---|
| Allocation size / requested alignment | 3ce0 / 10 | 6b8 / 8 | 15,584 / 1,720 bytes; allocation failure arguments encode alignment |
| Cells span | 5d0 | 580 | Private input and disjoint producer outputs |
| Input start / Packet size | 10 / 138 | 50 / 128 | Owner writes; admitted helpers borrow |
| White / black output starts; each size | 148 / 180; 38 | 10 / 30; 20 | One writer per color; owner reads after done |
| Inventory output start / size | 1b8 / 428 | 178 / 418 | Third helper writes; owner copies used slice/length |
| request / inventory_request | 3c30 / 3c38 | 590 / 598 | Owner publishes; helpers acquire |
| Reader0/1/2 done | 3c40 / 3c58 / 3c70 | 5a0 / 5b8 / 5d0 | Each helper publishes; owner acquires |
| Reader0/1/2 state | 3c50 / 3c68 / 3c80 | 5b0 / 5c8 / 5e0 | Parking/terminal traffic |
| active_scopes | 3cb8 | 5f0 | Activation/close publication |
| Control mutex / Control data / scopes | 5e0 / 5f0 / 3c20 | 5f8 / 600 / 690 | Owner dispatch/completion; lifecycle locks |
| Sleep mutex / wake / completed | 3cc0 / 3cc8 / 3ccc | 6a0 / 6a8 / 6ac | Cold waits/notifications |
| stop / waiting | 3cd0 / 3cd1 | 6b0 / 6b1 | Stop polling; unconditional helper SC exchanges |

Reader size/stride stays 0x18, done/failed/state offsets 0/8/0x10. Mutex<Control>
shrinks 0x3650→0xa8, Control0x3640→0xa0. Removing u128 histogram storage removes
its 16-byte alignment requirement. The color outputs shrink 56→32 bytes; Cells
reorders input and outputs, and Packet also reorders generation/Position.
## What this supports and what it excludes

- Request-to-done distances and Reader stride were already compact. The
  Sleep/wake/completed/stop/waiting cluster keeps its internal geometry. Cold
  observations did not separate every coordinator/helper writer previously.
- Color output packing, header adjacency, packet field phase and allocation
  size/alignment all change. Old 56-byte outputs could already share a line;
  shrinkage alone does not prove a new conflict or a higher conflict rate.
- Under a 64-byte-line model, lean Reader1.done and Control mutex are exactly
  64 bytes apart and cannot share one line. Reader1.state is 48 bytes before the
  mutex, but state writes are parking/terminal traffic. The newly close
  third-reader/control pairing can concern mode4; it cannot alone explain mode3.
- Control.scopes is 33 bytes before waiting (previously177), potentially sharing
  a line, but scopes changes on activation/close. Per-FULL Flight storage is
  old B+5f0..63f and lean B+600..62f, more than 128 bytes from lean waiting6b1.
  That per-FULL Flight/waiting same-line explanation is excluded.
- Heap B modulo64 and actual line traffic are unavailable. Requested
  alignment16/8 is not line alignment. Wall/CPU totals establish no cache-miss,
  coherence-traffic or instruction-time attribution.

The native generator keeps the same address/RIP/comment-normalized instruction
shape: 0x151d bytes /1214 instructions in both images (old2ca90, lean2c0a0).
This weakens a generator code-shape explanation, while caller costs, inlined
color/control lowering and global code placement remain alternatives.

The proposed counterfactual would keep the old concrete Packet/outputs/Metadata/
Control/production-storage/Shared types, safely initialized without hot observation
updates. Keep the zero-lease marker, original demand/charges and synchronization.
Check compiled offsets rather than trusting source order. This tests a specific
representation confound across matching3/4; even a positive result would not prove
cache misses caused the regression. No padding sweep or queue change is justified.

Narrow reproducible anchors use `nm -S -C IMAGE`, `readelf -rW IMAGE` and
`llvm-objdump-19 -d --demangle --no-show-raw-insn --start-address=... --stop-address=... IMAGE`:
allocation anchors old423a9..42428 and43736..43746,
lean417c8..41837 and425aa..425ba; old helper stores18ca2..18ce1 versus
lean1851f..18542; old publication44010..441d9 versus lean42e73..42f5b;
old waiting476b0..47728 versus lean44160..441d8. These inspect existing bytes.
The bounded extraction memo is
`/home/legolas/agent-memos/imp2-observer-free-existing-layout-20261026.md`.
No engine source/image bytes changed and no further execution is selected.
