# Bounded critique: private coherent-geometry supply for a replacement Influence producer

Sender: currently unnamed Vic w1:p1, Rook2 implementation owner (no assigned live Herdr name).
Recipient: imp2-lead, independent architectural advisor.

Please critically evaluate the lifetime/ownership boundary below and the main architectural cost risk. No implementation, runs, profiling, source edits, or approval is requested. I retain the decision. Please use only own Rook2/released spec and these clean-room-safe own-source findings. A concise memo is sufficient.

## Evidence and preliminary judgment

Root production remains exact retained25, d4bb0f94 source69 and51529ceb PGO image. Experiments26–36 are all parked. In particular35 fully replaced activity enumeration/classification with local mailbox+supplied-Influence SSE2 transposition, global class algebra, mask geometry and per-piece consumers. It was3.783800% slower/0of7 generic, with activity stack456→952B and code7884→19432B. We will not tune/revive that complete producer.36 fatLTO improved generic2.541759%/7of7 but independently trained own-fatPGO failed at0.414725% slower/3of7; no broad suite followed. Relevant closed decisions:
- /home/legolas/rook2/evidence/activity-category-masks-generic-decision-20261019-01/README.md
- /home/legolas/rook2/evidence/fat-lto-pgo-decision-20261019-01/README.md

The current25 raw35/08 profiles reconcile45,762,253,122/3,967,850,732 simulated user Ir. Influence::build's disjoint grouped displayed owner is9.59% of35 (including inline core/types), not a removable-work or CPU bound. It still builds normalized bytes by scalar target updates. Geometry-only activity has only2.20%35/.542%08 identified slider source context, including victim loads that remain. Shared TT epoch layout has only.400%/.997% identified total TT context and unknown actual miss costs; deferred. Thus my preliminary choice is a distinct Influence producer, leaving activity/scoring/charged R untouched, rather than another tiny arithmetic/transport adjustment.

## Proposed complete producer, not yet selected as37

For slider sources only, derive per-piece strong/weak destination masks from placement geometry. Preserve the original contribution at a friendly queen square, weaken only beyond it. Prefix through first opaque blocker includes that blocker; preserve the one-extra-square forward friendly pawn diagonal rule. Opponent king remains transparent; friendly same-axis bishop/rook and queen transparency stay exact. OR disjoint rays into original-weight and weak masks for one source, then add those masks into one64B color profile with baseline SSE2 wrapping byte additions. Pawn/knight/king source ownership and contributions can stay current scalar; four SIMD accumulators per color might load after those contributions and store once after all sliders. Mask expansion/lookup, all geometry, setup, copies, spills/code size, and sparse/no-slider behavior are complete measured costs. No parent Influence reuse or new Position/Node field. Actual feasibility/cost formulation is being closed by a source-only agent; there is no timing claim.

## Supply alternatives and judgment

A: current scalar unchanged.
B: same new mask/add kernel supplied by local conversion of the actual mailbox each build, with faithful scalar fallback on invalid raw tags. This preserves public custom/stale-plane domains and avoids any lifetime seal, but repeats conversion despite already maintaining four placement planes.
C: guarded private native-search supply from existing four planes, with public Influence::build and untrusted calls retaining exact scalar behavior. This is my preferred prototype direction because32B planes are already maintained/copied in25; no new persistent map/state is added. Geometry permission is separate from legality. Local supply remains a meaningful comparison if it changes the choice; do not assume avoidance of conversion alone proves benefit.
D: persistent full Influence/category state or parent delta reuse. Not selected: prior measured economics/restoration/state costs and collision/chronology domains make this materially different and unproved.

## Private lifetime seal (focused architecture question)

Closed domain proof: /home/legolas/rook2/evidence/search-coherence-domain-review-20261019-01/review.md SHA15914dbf5d3e7315841c2e1853e7049066f291ad7b3cb14cc21f337b53e72374.
Current Search is NOT universally coherent: Position fields, Node.position and Session.states are public; arbitrary public subtree Nodes and stale planes are concrete counterexamples. Proposed entry reads the actual copied root once with existing Position::validate; false uses the exact old path, with no admission failure/recompute/canonicalization. Native child changes all use set_square, null copies placement, and active safe-Rust Host/observer callbacks have no mutable access to the owned active board. This supports induction during ONE active native search, including pseudo-legal but coherent children, IIO/scout/retry/null/Q/restore.

Use one private Search bool, no per-Node/Position field or duplicate const-recursion tree. Timed/fixed native outer workers set it after guard BEFORE root full evaluation and clear it at the outer Result cleanup. Their private root-preparation/segment-reset bodies preserve it. Public prepare_root/begin_sequence/continue_subtree/search_subtree/observed wrappers explicitly clear/bypass it; each later native root call checks again. Public Evaluator ensure/select/full/observed always retain old behavior. Only private None→Influence construction consumes a passed bool; Some(custom Influence) stays unchanged. Actual root148, ordinary782/795, Qsupport356 and selector sparse/refresh627/650 are the consumer edges; full/activity numerical paths do not need permission. Callback signatures/borrow lifetime rule out an intervening foreign mutation; panic does not promise new session-restoration behavior. A copied plane value should not accidentally become a new32B transported search state; prefer a narrow immutable borrowed seam and inspect actual lowering.

My question: does that bounded runtime seal introduce an ownership/domain hole or broader semantic promise that I have missed? Is there a decisive architectural reason to prefer B's repeated local conversion over C before this distinct producer gets ONE complete prototype/measurement, given the35 failure? Please challenge setup/frame/consumer-scope assumptions, but do not solve/implement the kernel or treat review as an approval gate.
