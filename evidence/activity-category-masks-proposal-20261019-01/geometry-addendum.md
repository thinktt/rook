# Owner geometry clarification for experiment35

This source-only clarification preserves the fixed API and supersedes the frontend proposal to walk every ATTACK_RAYS destination merely to form P/X. Use private immutable compile-time ray masks, constructed from the same DIRECTIONS and board coordinates inside activity.rs. geometry.rs is unchanged. There is no new persistent or mutable position representation.

For ray R, first occupancy blockers are R & !board.empty; activity-opaque blockers are computed from mailbox kind/color masks for the exact class, color and ray direction. The nearest blocker is the least set bit for positive linear steps and greatest set bit for negative steps. With one-bit blocker b, prefix-through is R & (b | b.wrapping_sub(1)) for positive steps and R & !b.wrapping_sub(1) for negative steps. No blocker returns R. Guard zero before first-bit extraction.

P is the first-occupancy prefix and X the first-opaque prefix. D=P minus friendly; A=(X minus P) minus friendly. Queen has X=P. Preserve per-piece cardinality/value/rounding and sparse V pass; rook vertical doubling changes T only. The independent coordinate oracle must not call this prefix machinery. Construction, bit scans, sparse V and mark flush are included in the actual complete frontend and later measured cost. No parse/build/test/engine execution is authorized by this clarification.
