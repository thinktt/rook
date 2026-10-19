# Experiment28 generic copy gate: NO-GO

**The required copy erasure failed. Stop before native178/strict/DIAG/CPU stages.** Exact trial d8a7c8020caa40cf0d1e693122d3df55955fbfaee380f6e0dba5fbad4b47aedf still performs the mandatory first160-byte Position initialization, then copies a **176-byte whole Node** from the stack to the return place after apply. The removed source temporary was relocated and enlarged, not eliminated. No source repair or new variant is proposed.

Control is candidate25generic2940ae5c003fa396b31639749b4c3ba29e52e8aebabfc96a7dde565b6d9abd04; trial native69 graphd69955c6. identity.json binds both frozen images, original build receipts/source-before69, exact compiler/toolchain, x86-64 generic flags/noPGO and tools23. Only evaluator.rs differs. Parent observed build14553/df8ecf→a036ed/0; this review did not build or run either image. Source review proves the one-function delta, but no fresh functional success is inferred.

At standalone Node::child0x1ee30:

| Actual transfer | Control2940 | Triald8a7 |
| --- | --- | --- |
| Required parent Position initialization |1f109–1f111, memcpy160 into `[rsp+8]` |1f109–1f111, memcpy160 into `[rsp+0x18]` |
| Transition primitive |1f119 via GOTe1d60 |1f131 via same GOTe1d60 |
| Post-apply return transfer |1f11f–1f12b, memcpy160 to `[rbx+0x10]` |1f137–1f144, **memcpy176** from `[rsp+8]` to `rbx` |
| Local reservation, excluding6saved registers |0xa8=168 |0xb8=184 (**+16**) |
| Body bytes |937 |942 |

Both memcpy calls use r13 loaded from GLIBC memcpy GOTe1f68. The same Position::apply_unchecked address0x2e730 and all1696 actual machine bytes match. Trial Retained stores now go to stack offsets8/10/14 before apply, followed by the whole-Node copy; control stores go directly to return offsets0/8/c after its second Position copy. The source's values and wrap expression are unchanged, but their local lifetime grows with the176-byte temporary. This is emitted evidence, not a private-layout/source-size inference.

The **actual generic** ordinary0x3cf40 and Q0x38e60 bodies each have two call transfers through GOTe19f0→Node::child0x1ee30. They contain no independently inlined changed child construction to credit. caller-evidence.json binds all four actual call windows and relocations; both entire captured caller machine-byte sequences are identical, including the reservation operands. Their local reservations are1064/1224bytes respectively, unchanged; no broader spill/stack equivalence or dynamic call frequency is claimed. The prior own-PGO51529 inlined child paths are a different artifact and are not transferred to this generic gate.

This proof is sufficient NO-GO under the predeclared backend criterion regardless of total text dimensions. No engine, unit, replay, profiler, timing, probe, archive or Git action ran. Bounded nm/readelf/size and four requested-region objdump captures were read-only on housekeeping. Further investigation/PGO/timing is stopped. All owned tools actually terminated0; exact source and original artifacts remain unchanged.
