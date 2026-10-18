# Coordinate-oracle differential check

The release-optimized native test executable compares the geometry-table
prototype with our own prior coordinate-loop influence and activity code.
`oracle/` retains the exact pre-test-module prefixes of the baseline sources;
their original whole-source hashes and all actual prefix/driver hashes are
bound by `receipt.json`. These are independent prior algorithms, not fixture
answers or other-engine code.

All10,000 constructed placements passed normalized128-byte influence equality,
per-color activity/pressure scores, weighted score and semantic relation-query
count equality. Placement generation includes promoted material, adjacent/
attacked kings, varied turns and full effective-weight range. The test binary
was hashed before/after actual execution, and source/driver maps remained fixed.
The harness is release optimized with panic unwinding; it is not a production
CPU measurement. Production build, all54 replay and balanced CPU experiments
have separate identities.
