# One writer-region layout counterfactual

Recommend one later generic preserved/new inline1/mode3 comparison of the layout
below. Use retained Q source 68 and its **original SC-RMW completion protocol**;
preserve f8b829/profilebbb858. Keep numerical bodies, both owner-local hooks,
thread modes, spin4096/sample512 and every observation unchanged.
This is a source-only recommendation, with no
implementation, build, native run, padding sweep or automatic PGO selection.

The rationale survives review, with a correction: the retained generic image
already separates request from Packet filling. Do not count that separation as
new saved work. The stronger concrete exposures are packed helper completions,
adjacent outputs, and the request/stop/latch tail beside the second output.

## Existing evidence and actual access ownership

The saved control disassembly from the [closed fence study](../../experiments/multicore-feasibility/completion-fence/report.md)
is exact generic d2dd0ade, not the parked fence image or a newly inspected binary.
Let B be its Arc allocation base. Constructor/refcount/deref and producer/consumer
instructions give these bounded anchors; this is manual reading of already saved
assembly, not DWARF type information or a complete layout reconstruction.

| Anchor | B-relative bytes, hexadecimal |
|---|---:|
| Allocation size / requested alignment | 1b40 / 10 |
| Shared data start | 10 |
| Reader done0 / done1 | 10 / 28 |
| Control mutex | 40 |
| Packet start | 1970 |
| White / black output starts | 1aa8 / 1ae0 |
| Request | 1b18 |
| Stop / waiting | 1b38 / 1b39 |

Packet occupies 312 bytes before the first output; output stride is 56. Request
therefore follows Packet by 112 bytes of output storage: under a 64-byte model,
Packet filling and request polling are already separate. In contrast, two done
fields are 24 bytes apart; helper outputs are 56 bytes apart; request starts 56
bytes after black output. Stop and the hot multiwriter latch are adjacent.
Unknown B modulo 64 prevents claiming actual line collisions or traffic, but
these distances expose competing writers/pollers to possible shared lines.
The map applies to generic d2dd, not an inferred private layout of PGO f8.

Source ownership is precise. Coordinator dispatch writes Packet and Release
request; both helpers Acquire-poll request and borrow the immutable Packet.
Helper i writes only output_i, then Release done_i. Coordinator polls done,
then reads both outputs under Control. Stop is cold-written but hot-polled;
active_scopes is repeatedly read while helpers have no new request. Reader
state/failure fields change on parking/terminal paths. Control is ordinarily
coordinator-owned, but parking/failure handlers and independent scope guards
also acquire it. The latch is genuinely multiwriter on every completion.

## Select exactly eight regions

Use private concrete `repr(C, align(64))` regions, embedded in one Shared/Arc;
use explicit outer field order. 64 is an experimental layout hypothesis, not a
hardware conclusion from guest cache enumeration. No per-call allocation,
pointer table, additional Arc or generic padded-payload abstraction is needed.

| Region | Contents and decision |
|---|---|
| Request | Atomic request alone; make isolation from all other writers explicit. |
| Packet | Existing concrete UnsafeCell<Packet>, rounded to 64; both helpers read. |
| White completion | Existing UnsafeCell<SideOutput> followed by its AtomicU64 done. |
| Black completion | Same concrete slot, separately aligned; no cross-helper output/done line. |
| Lifecycle | Both readers' state/failed_generation plus stop/active_scopes, packed together. |
| Latch | Existing waiting atomic alone; all original SC exchanges remain. |
| Cold waits | Existing Sleep mutex and wake/completed condvars together. |
| Control | Existing Mutex<Control>, including Flight, failures and every observation. |

Choose output+done co-location prospectively: 56-byte output plus 8-byte done is
expected to fit one 64-byte slot. It lets consumption acquire the payload's line
with its completion. The downside is concrete: polling done can reacquire that
line while its helper is still writing payload. Separating them would instead
require another payload-line transfer. Do not sweep these choices after data.

Pack lifecycle fields rather than padding each reader's cold state. They have no
steady-search writes; their hot reads warrant separation from the latch and
Control, not separate lines for every flag. Keep mutex and Control metadata
together: their ownership is already serialized. A bounded Sol challenge supports
the output/done and polling tradeoffs; the final packing above is the selected
parent recommendation.

## Cost, safety and a cheap admission

Let R(x) round to 64, P=size(Packet), S=size(SideOutput), M=size(Mutex<Control>).
Expected Shared storage is `64 + R(P) + 2*R(S+8) + 3*64 + R(M)` on this target,
provided lifecycle/cold-wait groups each fit 64. With P=312/S=56 and the apparent
6448-byte Control-mutex span in the existing image, that is 7168 bytes. A64-aligned
Arc may need 64 bytes before data rather than the observed 16: approximately 7232
allocation bytes versus 6976, about 256 extra bytes. These are prospective size
estimates, not measured candidate geometry; actual standard-library layouts and
Arc data offset must be verified. No RSS or cache benefit follows from this sum.

Extra regions increase polling footprint: done polling now reaches two lines,
and stop/request/latch are distinct. The latch's true sharing remains, as do
necessary request/Packet and output transfers. Alignment may change allocator
and startup costs, Arc-header padding, address encodings and global code layout.
The earlier fixed-layout result establishes representation sensitivity, not
cache causation or a performance forecast for this grouping. Both owner hooks
remain readiness-conditional: changed completion timing can alter eager work
and waste despite identical semantic charges. Price the complete mechanism,
without adding a census or attributing net savings to cache traffic.

Keep one narrow concrete `unsafe impl Sync for Cells`: place aligned Packet and
the two output+done slots inside Cells. Atomic done requires no new unsafe
payload contract. Update only field paths and that existing proof's locations;
never form a mutable reference to Cells, a whole completion slot or Shared while
peers can access an atomic field. Write/read only the concrete UnsafeCell payload;
never copy/clear the enclosing slot across a live done atomic. The unchanged
request Acquire/Release, both real done Acquires, Control/Flight ownership,
output reverse edge, Discarding and actual park/join retirements remain authority.
No blanket Sync for generic payloads or new acknowledgment is needed. Physical
grouping does not change wake↔Control or completed↔Sleep pairing or lock order.

An eventual candidate should expose one cold projection of its **actual
production types and actual Shared instance**, before protocol input while
helpers are parked: size/align/offset_of, region spans, side stride, and Shared
address modulo 64. Assert 64 alignment, disjoint rounded regions and one-line
output+done slots before timing. A cfg(test) surrogate is insufficient because
TestHooks changes Shared. This needs no new introspection framework, hot counter
or extra synchronization. Retain existing lifecycle/SC controls and unchanged
numerical/Q evidence. If selected, use one preserved/new generic1/3 discriminator
with both hooks on; report serial drift and total costs without cache attribution.

Source pins: retained colors_worker.rs SHA256
`d6d87823839d064f4283c0c9f9626576ea191b3bbf53a59a5cf1cf14ad5b8f16`;
full 68 maps are in the [Q PGO record](../../experiments/multicore-feasibility/q-owner-local-own-pgo/preparation.json).
Saved control.objdump.stdout SHA256
`e28669ceba26226c742d1690d90e8516d80cd653624f7fd35f783696d80f0ad3`,
under `/home/legolas/rook2-experiments/completion-fence-20261026-01/lowering/`.
Anchors: constructor 42443/43221, dispatch 43764/43768/43af1/43c60,
complete 443a1/44775/447b4, signal 45c2a. No engine, compiler, test, collector or binutils execution, or engine edits,
were performed for this design. Wider execution remains a separate question.
