# Compact48 own-PGO: outlined store and allocation review

Scoped PASS: no stop condition found in these consumed owners. Root still owns complete inline-probe/store/caller review and timing admission. No speed/cache/traffic prediction, engine execution, fresh capture, or source change occurred here.

Control: `01237e6dfe89822e540d0f07c7b70f7227537a846ce8c69ea9e91167b759e98d`. Candidate: `e2b2d9ee1f725e7a0b96bb4513b3d3127160d68023e4c2a9910fe25f1d67dd5e`, its own profile3f7e3dfa… per root receipt. Reviewed complete captured store/from_tts/clear/Option<Search> drop pairs, then the actual finish_grow/extend_with/allocator and replacement branches from full.disassembly. Reviewed selected-owner hashes match capture/receipt.json. Actual GOT targets come from each side's resolved-calls.json and relocations.txt; there is no top-level resolved-calls.json.

## Outlined store survives with all five branches

Both are the actual owner27eb0: control642B, candidate573B. Candidate has only push RAX (8B temporary/alignment); control saves RBP/R14/RBX plus16B locals (40B total). No successful outcall exists in either owner. The three tail calls are bounds/checked-i16 conversion failures, resolved to panic_bounds_check and unwrap_failed. No vector, AVX/BMI or other new ISA is present on the changed store path.

Candidate27eb1–27eee preserves signed mate normalization (>=9000 adds ply, <=−9000 subtracts ply) and checked score/remaining-depth conversion.27efb–27f68 preserves strict original lower/upper flags, quiet/depth marker bits and12-bit endpoints, and packs endpoints/flags/generation into one DWORD. Group addressing27f6f–27f77 is48*index; identity slots are0/4/8/12, payloads16/24/32/40. No group/payload bulk copy or helper is inserted.

| Required storage case | Actual candidate evidence |
|---|---|
| Matching retained, shallower new depth -> recent | Retained identities tested in order27f7b/27f84/27f8d, then generation gates28033/28018/28028. Signed depth comparison2803f–28045 uses JG to2806f; writes recent identity+score/depth/packed remainder at2806f–2807b. |
| Matching retained, equal/deeper -> overwrite that retained slot | Same signed comparison falls through on equality to28047–28055; selected index preserved. Recent duplicate remains untouched. |
| No valid retained identity, first invalid slot -> fill and fully clear recent | Generation gates27f96–27fd6 select first invalid0/1/2, including identity0 normally.27f9e–27fac writes the selected full logical record, then27fb1 clears recent identity DWORD and27fb8 clears its whole8B payload. |
| All valid, new depth >= first least-depth slot -> displacement |27fd8–27ff6 uses signed SETL and CMOVGE: ties retain the first minimum.27ffa–28000 sends only strictly shallower new depth to recent.28002–2800d copies the SAME selected old identity DWORD and payload QWORD to recent before28047 overwrites that retained slot. |
| All valid, new depth below least -> recent only |28000 JG reaches2806f. All retained slots stay unchanged. |

Displacement preserves a logical identity/payload pair through one selected index; it does not introduce a hardware-atomic12B write or concurrency guarantee. Normal record writes remain12 logical bytes, now four stores (4+2+2+4) rather than six (4+2+2+2+1+1). Displacement remains4+8 bytes read/write for the old pair. Additional upfront identity comparisons/packing/address streams are real costs; smaller owner/frame is not a performance verdict. Ordinary uses this actual owner through GOTee9c0->27eb0, at candidate35d1a/36d12 versus control31bf5/354fc/36c22. Inlined cases are root's separate obligation.

## Constructor, initialization and allocation closure

Actual from_tts is control4bae0/candidate4bb60,746B each, four saves plus136B locals unchanged. Candidate4bb71–4bc89 retains the original /48 and descending-prime selection, including96-byte minimum.4bca8–4bce7 checked multiplication requests48G bytes; alignment argument changes4->16, with the corresponding maximum-allocation bound. Output metadata remains capacity/pointer/length at0/8/16 and generation at24 (4bd1f–4bd2e); no second array or enlarged table metadata is introduced.

The actual call4bce7 reaches finish_grow a590. Empty old capacity takes a5a6->a627. Size48G>=96 and alignment16 take a63a–a649->a684, then exactly one malloc viaa687/GOTee768. No posix_memalign/realloc/copy path is consumed by this constructor. Requested layout alignment16 is discharged by the supported Linux x86-64 malloc alignment contract, not by an observed runtime address or a VM cache-line assumption. The allocator's other alignment/reallocation branches exist but are not an extra allocation here.

Before actual initialization, capacity isG and length0. Therefore extend_with452b0's capacity test452b8–452c5 cannot enter grow_amortized at453c8 in this constructor. It copies the zero48B template to EVERY group: three16B stores,48-byte stride, original unrolled/remainder/final handling. Candidate uses aligned MOVAPS where control45230 uses MOVUPS; no higher ISA. This is full48G initialization, not sparse identity initialization. It performs no additional slab allocation. Generic growth code is present but unreachable under this exact reserve/resize path.

## Clear, replacement and destruction

Clear e640/105B is byte-identical. Ordinary clears increment generation without touching slab. Generation255 takes e65e–e69e: whole length-derived48G bytes passed to resolved memset ee5c8, then generation1 committed. The reciprocal arithmetic computes48*(G−1)+48, not a truncated/sparse span. Initialization and physical wrap invalidate all identities AND payload bytes; identity0 is not an empty sentinel.

Normal native run consumes from_tts at5024a (GOTeeac8->4bb60), moves all32B metadata at50291–502bb, and calls clear5041b (eec68->e640). Existing storage is reused only when budget matches53974–53982. Replacing a nonempty old table frees old pointer at538c4–538d5 before metadata commit; this is allocate-new/replace/free, not in-place TT reallocation or a permanent second slab.

Final Option<Search> destructor108c0/171B is identical: table capacity/niche checked at108fa–10906; pointer+178 freed once at10908–1090f through GOTee8a0/free. Other destructor frees are separate existing search buffers. No new TT drop scan, payload destructor or source-level allocation policy was introduced.

## Limits and actual review closure

This establishes emitted layout/write/initialization/allocation mechanisms for the actual owners, conditional on the existing scalar semantic domains and allocator contract. It does not independently reprove all native admission, PGO correctness, platform malloc internals, inline probe filtering, every whole-run temporary allocation, cache-line costs, or speed. Root binds the196-library and original54 training/remerge proofs separately; they were not rerun here.

Read-only actuals:2f1780/1 (metadata path assumption: absent top-level resolved-calls.json; no mutation/native work),4400d6/0,02cf96/0,25052d/0,0e7218/0,99a762/0. The latter reads use the actual per-side resolved files. All owned helper jobs terminal. This report is the sole written file; sources/captures unchanged. No build, engine, test, binutils, profile, archive, Git or Herdr command was invoked.
