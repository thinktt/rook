# Candidate57 opaque binary delivery draft

Prepared locally; new external execution/export remains subject to Toby's approval.
Behavioral reference KingRE v2.5.0 released commit `1c89c21a4645ec85adf28285616d822b3cd91f73`.
This draft is not a READY signal or a performance/gameplay qualification claim.

- Candidate: `candidate57`.
- Implementation revision identifier only: `4435523e2da8ed89a596c744f6504b50816a5589`.
- Binary-only delivery root commit: `e01d49e5faf5c7fdc69d84238fd4b33d186c2ef2`.
- Annotated tag: `rook2-candidate57-binaries-20261020`.
- Tag object: `5c0c9e4b5a930fb9e45a31c4406e2a55d018d926`.
- Bundle: `/home/legolas/benchmark-handoff/rook2-candidate57-20261020.bundle`.
- Bundle size: `4944294` bytes.
- Bundle SHA256: `9a32c784de1571bd08f16d50c57c3292152fabc928845d182d0112a1c05801b7`.
- Sole advertised ref: `refs/tags/rook2-candidate57-binaries-20261020`.

Independent empty-repository import verifies one root commit, one annotated tag,
one tree and exactly two executable blobs, no prerequisites or branch refs.
No source, other implementation history or internal traces are included.

| File | Role | Bytes | SHA256 |
| --- | --- | ---: | --- |
| `rook2` | Benchmark executable | 7125520 | `af849f920897ec1f174b16718be5d6886158913ee4819f84273f15bd8c23e5b8` |
| `rook2-diag` | Diagnostic companion | 14038464 | `eda652abd182cb536736dd758d330f779e94b1e7ad0e779ff7792c2235fffde2` |

Individual immutable files are `/home/legolas/benchmark-handoff/candidate57/rook2`
and `/home/legolas/benchmark-handoff/candidate57/rook2-diag`; this directory
contains only those two files. Git mode100755; individual filesystem mode0555.
Bundled blob bytes match the named files exactly.

Both are Linux x86-64 ELF executables using `/lib64/ld-linux-x86-64.so.2`,
`libgcc_s.so.1`, `libm.so.6` and `libc.so.6`; required runtime versions include
GLIBC_2.34 and GCC_4.2.0. Benchmark invocation:

```text
./rook2 --work-clock=kingwcr --work-clock-post=work
```

`rook2-diag` is the separately identified diagnostic adapter, without extra args.

Proposed scope: the existing standard Bee pinned-CPU54 benchmark, binding returned
results to these exact identities, through cleanroom-gate's audited opaque intake
and safe-report process. No reference binary transfer, source inspection,
game-gate launch or performance qualification follows. Authorization is pending;
no external delivery or execution has been requested and READY is untouched.
