# Preserve the failed name check and continue the fixed schedule

Preparation at a5922503 passed38 focused tests, both generic builds,13 CLI
controls and two unmeasured original08 affinity/liveness controls. Its source,
images and build receipts remain unchanged.

The collection completed its first three excluded35 warmups (preserved2,
inline1,current2). At the first colors3 startup, the external supervisor observed
main14 /white6 /black4 correctly, but compared Linux `/proc/.../comm` fields with
16-byte Rust thread names. Linux exposed their15-byte truncations:
`rook2-eval-whit` and `rook2-eval-blac`. The strict full-name assertion failed;
the input gate timed out and the unverified native startup was killed (exit-9).
No readiness/input-release receipt exists for this attempt. The tap recorded421
**attempted** setup bytes before calling the blocked gate; those bytes are not
proof of delivery. Stdout/native stderr are empty. This is a placement metadata
failure before protocol release, not an engine output or numerical mismatch.

All raw bytes remain at
`/home/legolas/rook2-experiments/colors-three-20261026-01`.
The original pipeline/preparation/collection records are unchanged. Before repair,
32 original tooling/dependency/record files were preserved and hash-verified in
`01/frozen-tools/manifest.json` (SHA256
`d6d07eac600f6740034f432c4abb8531b4b572812d2d9acd820bab561d08944d`).
The failed native/supervisor are terminal and selected housekeeping was restored.

Repair only the expected comm representation, including the independent placement
check. Actual thread IDs/CPUs/engine options and numeric code are unchanged. A
separate completion setup audits/adopts the three existing warmups under their
original frozen tool bindings, executes only45 uncompleted schedule entries plus
four idle probes, then independently reconciles the complete fixed48+4 schedule.
It reuses the original3600s pipeline and1800s collection monotonic starts/caps.
No rebuild, repeated completed life, expanded measurement cap, PGO or new variant.
