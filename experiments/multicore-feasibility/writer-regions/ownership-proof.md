# Eight concrete transport regions, original protocol

Retained Q source68; original unconditional SC-RMW latch, not the parked fence
variant. The one Shared/Arc contains request, Packet, white/black output+done,
packed lifecycle, latch, cold waits and Control regions. Explicit C layout and
64-byte alignment define the sole candidate. Numerical body, both owner hooks,
spins4096, sample512, all observation operations and every atomic order remain.

Keep the existing private unsafe Sync for Cells only. It contains the same three
concrete UnsafeCell payloads, now in aligned Packet/Side regions; the two actual
done atomics sit outside UnsafeCell alongside their own payloads. No generic
payload Sync, new allocation, raw pointer table or whole-Shared/whole-slot mutable
reference is introduced. Initialization of fields and atomics precedes sharing.
During execution only Packet/SideOutput payload cells are written, never an entire
slot containing a live atomic. SideOutput Copy reads do not include done.

Coordinator owns input under Control and Flight::None, derived from both matching
done Acquires and ended output reads, or both actual quiet/exited readers. Request
Release/Acquire still publishes initialized Packet. Each reader's lexical Packet
borrow ends before its own SideOutput write and original done Release. The owner
still requires both actual done Acquires AND Published under Control before
reading either output. Copy reads end before Flight::None; the next request
Release/Acquire carries the reverse edge before either output is overwritten.
Co-locating done does not grant any new payload access or retirement authority.

Failure/close/startup/exhaustion and concurrent final guards retain original
Control/Flight::Discarding and actual park/join ownership. Lifecycle state/failed
metadata move but retain their publication order. Stop remains monotone. The
single cold waiter and every normal/terminal publisher retain exactly the old
SC-RMW chain; no fences or weaker loads replace it. Wake still waits on Control;
completed still waits on Sleep; no Control/Sleep nesting changes.

A source comparison reverses only the concrete field-path renaming and finds
26 operational bodies byte-identical, including dispatch, kernel, done/wake,
consumption, registration, terminal, park/close and shutdown. Packet, SideOutput,
Metadata, Flight, Control, Metric and Readiness declarations are unchanged. The
constructor solely initializes the same concrete values in their new regions;
no runtime relocation is performed. The source and normalized body pins are in
preparation.json. Affected original24 worker tests plus one layout control run;
35 unaffected numerical/owner/Q controls are reused.

Cold projection is opt-in CLI plumbing through Session/Evaluator to the actual
ColorsWorker instance. It requires initial generation0, no scopes/closing/flight,
no terminal and both real readers PARKED under Control. It reports actual
production type sizes/alignments/offsets and Shared address phase; its flag is off
in all timing lives. A cfg(test) projection is explicitly marked testBuild=true
and cannot satisfy the external admission. The extra test checks shared alignment,
slot offsets and startup-only availability, without treating test Shared as the
production size. No JSON/counters/layout inspection enter the hot search path.

Before timing, one actual production cold process must report testBuild=false,
parked=true, eight ordered disjoint 64-aligned rounded regions, two64-byte slots
with56-byte output and8-byte done, and actual Shared address modulo64=0. Shared
size and regions are facts from that candidate; Arc header/allocator extent are
not introspected and remain estimated. A contradiction stops before timing and
is reported rather than changing topology or sweeping padding. Runtime controls
supplement this unchanged ownership proof; no broader qualification follows.
