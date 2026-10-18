# Pressure-value-only cold proposal

Date: 2026-10-18. Parent owns implementation acceptance and any later comparison.

Isolated source: `/tmp/imp2-pressure-value-only-native43-20261018-q0bjhzdd`.

The current root native43 matches all 43 source/build hashes in the activity-specialization profile provenance. Only `src/activity.rs` changes in the new tree. `src/influence.rs` retains the original arithmetic profile_sum helper; this proposal is separate from the profile-sum candidate. The prior review/proposal directory is unchanged and its file identities are recorded in proposal.json.

## Exact production change and ownership

A private `const PRESSURE_VALUES: [u8; 256]` generates the complete original pressure_value mapping at compile time. The existing private `pressure_value(mark: u8) -> i32` performs a table lookup and widens the u8 entry to i32. There is no runtime table construction, persistent placement/search state, cache, unsafe code, alignment change or layout change in source. Actual machine-code payload and cost are unverified until the parent compiles the proposal.

For bits 0 through 7, the original formula has weights `[16,24,8,16,8,16,8,16]`: 0x54 selects bits2/4/6 with weight8; 0xa8 selects bits3/5/7 with weight16. Thus every mark maps to a nonnegative value no larger than 112, safely stored in u8 and exactly widened to i32. The generator uses the original weighted-popcount formula only at compile time. Indexing an input u8 into all256 entries is in bounds for the full helper domain.

All other production source bytes are identical. Existing callers still apply their 0xf0 orthogonal, 0xcc diagonal and3 knight masks before calling the helper. Presence mark writes, repeated OR behavior, weak/strong coexistence, direct versus additional-ray selection, fresh marks per compute invocation, absent-piece gates, occupancy admission, geometry traversal, pressure accumulation, subtraction12/clamp, relation charge sites and outer scoring arithmetic remain untouched. The new table does not encode influence or relation classes.

## Independent helper coverage added, not executed

The existing pressure-mark/own-blocker test exercises only selected marks; it lacks full256 helper-domain coverage. The new test enumerates every u8 mark, decodes each bit by repeated `% 2` and `/ 2`, and adds independent per-bit weights `[16,24,8,16,8,16,8,16]`. It compares this sum to pressure_value. It uses neither the generator's popcounts/masks nor table entries as its oracle. No existing test source is altered. This finite-domain helper test is appropriate for checking that the compact payload and cast preserve all values, including unmasked inputs not ordinarily passed by current callers.

The test has not been compiled or run. Existing coordinate-oracle complete-activity checks and strict work replays remain separate integration validation under the parent's control.

## Measured target versus hypothesis

The retained canonical profile01 is whole-lifetime 11,603,840,314 **simulated Ir**, with cache/branch simulation disabled. It is not PMU instructions, cycles or native CPU timing. activity.rs:389-392 attributes 65,704,375 Ir (0.5662% of the lifetime) directly to the old scalar weighted-bit expression. Intrinsic work can be attributed elsewhere, so this is the identified source-row envelope rather than a hard total-cost ceiling for the helper or a predicted gain. The additional activity::compute uint_macros.rs rows are not all attributable to this helper; the old review explicitly leaves their mapping uncertain. Do not add their whole function-file row to the opportunity.

The code hypothesis is that one small immutable lookup saves enough arithmetic/popcount work to beat its address/dependent-load cost. Constant caller masks may already simplify portions of the original expression. No native benefit, emitted payload count, generic/PGO result or interaction with the profile-sum proposal is claimed. Pressure-value remains a separate candidate; parent reports about another candidate do not validate this one.

## Downstream checks owned by parent

Inspect compiled payload/code and verify the table is immutable and free of runtime preparation. Run the new full-domain independent test and relevant existing native/coordinate-oracle activity tests, then exact strict54/wire/diagnostic checks as appropriate. Any later balanced generic pilot should use this isolated source against its exact source-matched control and preserve original raw samples, logical work, artifacts and interference context. If the result is flat or noisy, park this bounded change; this proposal supplies no reason to expand optimization scope. PGO or combination requires separate authorization and evidence.

## Identity records

`proposal.json` contains all43 baseline/candidate hashes, the sole changed-file identity, root HEAD, old-evidence identities and patch hash. `pressure-value-only.patch` is the complete edit. The record below binds the files most relevant to this semantic review. Paths are relative to /home/legolas/rook2 unless absolute.

```text
07d1b062f5ce6a4ffb66bd57eb3570f9221f42d7105b1df1f11e3039caf93c38  src/activity.rs
05b402b7e0137720d5fb4d2f062601ebf5abf61411fe648531cdc94e2959843e  src/influence.rs
2a202da079b16b3becb6651427701ec8e40aed88bd19550854c800b842b22feb  src/types.rs
9990111619222e74aee3e5d944cd08d7f3a6182eb0ef7c3c1c04d742f52e281a  evidence/callgrind-activity-specialization-20261018/provenance.json
f512b4dc32493ee906694e2593fabaa309f7a0bafba300f9a24c5be341842495  evidence/callgrind-activity-specialization-20261018/profile-01.callgrind
95ff89f216228faeab64b9187a19e018e9439af721f555b6d91da787f665b065  evidence/callgrind-activity-specialization-20261018/activity-lines.stdout
fcdc2472609d076b6eba7023ccb5b469a3c2a6b100eeff5a087f6908bafc192c  /home/legolas/king-spec/spec/activity.md
e11c98c390f539435874a9463232d86e9f26802bae2140e6abb2199ac705a9a6  /tmp/imp2-pressure-value-only-native43-20261018-q0bjhzdd/src/activity.rs
7ca5351f3e935c4b726fb370f2cbf86b1de49882177cd31c86c06ccb1560dfa8  pressure-value-only.patch
```
