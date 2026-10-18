Annotation-only B does not achieve the proposed constructor-relay or public-code restoration goal in the generic artifact. Both small source helpers were already inlined into their callers in A; neither has an emitted constructor/finisher symbol or a corresponding call transfer. Explicit inline(always) leaves the two material allowance functions byte-for-byte unchanged.

| Generic emitted property | source79 control | A | annotation-only B |
|---|---:|---:|---:|
| visit_q symbol bytes |7450|7727|7727|
| visit_q primary stack allocation bytes |1192|1288|1288|
| public uncached allowance bytes |410|459|459|
| public uncached allowance stack bytes |232|232|232|
| cached allowance bytes |absent|546|546|
| cached allowance stack bytes |absent|200|200|

A and B visit_q use the same addresses and function size. Only26 of its7727 instruction bytes differ: moving the Option-present word store at stack+0x206 before the unchanged20-byte cache-array zeroing, after the same material call. Both sequences then write the current endpoint and zero validity mask. All relevant Q/cached/public allowance call transfers are identical A/B (see resolved-material-call-transfers.json), including the first-use current-material call and cached helper call in Q, the miss-path material call and per-demand capture_exception call in cached allowance, and two material calls plus capture_exception in public allowance. This is a source-site audit, not an invocation count or timing estimate. Control Q's original allowance call is replaced by first-use material plus the cached helper in both variants; unrelated existing material call sites remain present.

The public helper still grows49 bytes versus control despite matching behavior. Annotation-only B does not recover that original emitted scope. Both A/B keep96 extra stack bytes on each entered Q frame, including checked/A0 calls. Static sizes establish these costs' existence, not runtime magnitude; no performance gain/loss is inferred and own-PGO may differ.

The whole .text sections are493291 bytes each and differ in448 bytes, so whole-program emitted identity is not claimed. The relevant functions above are compared by exact section slices, not anonymous LLVM comment labels. Complete inventories, raw sections, disassemblies and focused instruction diffs are retained. Because Q is not byte-identical, B receives the authorized full untimed regression; no redundant extra tests were added.
