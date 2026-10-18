# Threat/shelter diagnostic transport handoff

Sender: /root/threat_shelter_transport. Recipient: /root (Imp2).
Prepared cold on 2026-10-18. Only this unique /tmp directory was written.
No builds, rustc, tests, engines, profilers or simulations were run. All shell/helper
commands were prefixed with taskset -c 0-5,8-13. No Herdr or subagents were used.
Requested Normal; runtime speed readback was unavailable.

`threat_shelter.rs` prepares evaluation.materialThreat, search.fastThreat and
(optionally) evaluation.kingShelter. It is not integrated. `identity.json` records
SHA-256 identities of this module, read references and the supplied native receipt.
Any test expectations in the module are unit-test assertions, never runtime data.
Only released specs/approved fixtures and native Rook2 diagnostic/engine sources
were inspected. No Rook/Imp1 source was read.

## Wiring

Copy the prepared module to diagnostic/src/threat_shelter.rs and add
`mod threat_shelter;` to diagnostic/src/main.rs. Add these dispatch arms:

```rust
"evaluation.materialThreat" | "search.fastThreat" => {
    threat_shelter::dispatch(operation, input)
}
#[cfg(feature = "king-shelter-components")]
"evaluation.kingShelter" => threat_shelter::dispatch(operation, input),
```

Declare this diagnostic-only Cargo feature (leave disabled for two-route integration):

```toml
[features]
king-shelter-components = []
```

With the feature disabled, neither imports, code nor tests refer to the new native
shelter accessor, so materialThreat and fastThreat are independently integrable
against the unchanged native API. Merely defining the feature does not enable it.
For all three routes, apply the native visibility delta below and enable the
feature in the later diagnostic build. Existing production artifact remains frozen.

## Exact proposed native API delta (not applied)

In src/shelter.rs, change only the visibility of the existing structure, its four
fields and the existing accessor function:

```diff
-struct Components {
-    ring: i32,
-    files: i32,
-    screen: i32,
-    shelter: i32,
+pub struct Components {
+    pub ring: i32,
+    pub files: i32,
+    pub screen: i32,
+    pub shelter: i32,
 }
```

```diff
-fn components(position: &Position, influence: &Influence, color: Color) -> Components {
+pub fn components(position: &Position, influence: &Influence, color: Color) -> Components {
```

This exposes copies of read-only diagnostics already calculated by the owner; it
introduces no formula or changed production calculation. The adapter obtains terms
and weighted output from existing shelter::compute and raw fields from components.
It currently repeats raw component computation for observation. Phase is derived
from current placement by compute and position.phase; no phase override is required
or admitted by EVAL-KING-SHELTER. Until this visibility change is accepted, the
third route and its feature must remain disabled.

## Admission and composition choices

- Exact object fields, integer-number admission and list bounds use the existing
  shared helpers. Placement uses positions::placement(..., true): one king per side,
  at most sixteen pieces/eight pawns per side, no pawn on rank one/eight, at most
  ten knights/bishops/rooks and nine queens. Attacked/adjacent kings are admitted.
- Material values are 0..10000 by absolute color/type. Adjustment entries are
  bounded to 768, distinct by color/type/square, non-king, -128..127, and their
  value plus material value must remain -10000..10000. All entries are validated,
  including entries for absent pieces, other colors, and entries behind closed
  cutoff gates. Omitted adjustments are reset to zero. No extra side reflection.
- Repetitions are 1..16; passed-pawn balance is -10000..10000. Standalone material
  observations invoke the native estimator for every repetition and sum its
  semantic charges. Fast observations invoke the gate, pressure predicate and
  estimator per repetition as admitted, reporting each call's charges separately.
  Reusing influence maps never removes relation charges.
- FastThreat checks searchPly 1..62, targetPly searchPly+1..64, staticScore
  -10000..10000, upperBound -9999..10000, strict booleans and non-null existing
  descriptor syntax. It uses previous destination occupancy/counts for native
  capture_exception. No candidate-source, legal-transition, derived-check or
  fast-entry restrictions are added; special kinds have no extra guard here.
- Native fast_cutoff_gate suppresses all later requests; native king_pressure uses
  CURRENT king board neighbors and evaluation Influence maps, and a true guard
  suppresses estimator work. Final signed adjusted-minus-threat comparison follows
  the existing search.fastCutoff transport's consumer composition. A queried zero
  differs from absence; final failure retains all estimator charges. Producing a
  promotion threat can be positive without a relation query.
- Shelter pressure/weights both admit 0..4096 per color, materialScore
  -100000..100000, 1..4096 independent queries. No phase, maps or classification
  input is accepted. Raw diagnostics survive closed phase/weight gates. Native
  compute retains floor rounding and intermediate weight rounds.

## Prepared checks (not run)

Eight unit tests are included: unused/independent-field admission behind a closed
gate; Black ownership and sixteen repetitions; favorable queried-zero charges vs
absence; positive promotion threat with no relation queries; failed final score
with retained per-call work and special-kind admission; CURRENT king selection and
evaluation transparency; previous-board capture facts; and feature-gated raw shelter
observations at closed phase/effective-weight gates with query-order preservation.

Parent must review/build/run these and the released material-threat-v1,
fast-threat-v1 and (when enabled) king-shelter-v1 conformance fixtures after the
active timing campaign permits it. No passing-test claim is made. The only
unresolved native API issue is the visibility exposure above.
