# Pawn forward-scan fusion: isolated source prototype

Concrete uncompiled source proposal; no adoption or performance claim. Only this new evidence directory is changed. The activity-value-input candidate is not composed.

## Basis and proposed code

`base-src/pawn_progress.rs` is copied from the exact69-file own-PGO117 archive at `evidence/complete117-pgo-use-build-20261018/source-before/src/pawn_progress.rs`. Its canonical receipt binds source SHA `0bca6bb9678657b2efadc023c07d1ffcc9ff91c1c97553b84e2131c6ce30d9dc` to image `6a5ce6e27b74490e623fbb705f70c770ec12ff7e88f761fb0c7119ca2aee4a50`. Fresh actual `cmp` bf6f6c exited0; no fresh full-tree hash/archive verification is claimed.

`proposed-src/pawn_progress.rs` adds one shared private `raw_and_path<const WITH_PATH: bool>` producer returning `(raw, path, protected)`. Public `raw` retains its original scalar signature and selects false. `candidates` selects true and consumes the resulting path/protection/raw scalar. The shared producer retains the original backward scan and raw arithmetic, adding path accumulation alongside its existing forward traversal. The previous separate candidate forward loop disappears. There is one production raw algorithm body; the prior body is duplicated only under cfg(test) as an independent transformation reference.

`proposal.patch`, `inverse.patch`, literal `prepare_source.py`, `scope-proof.json` and `derivation-verification.json` record the exact change. Independent unified-text application verifies both patch endpoints; deleting only the collector and tuple projection restores the entire old raw body byte for byte. All original source from `aligned` through `weighted`, including current-candidate filtering, descriptor order, endings, fallback and weighting, is byte-identical. Candidate composition is otherwise byte-identical apart from binding the shared scan and using its raw operand.

## Domain and equivalence argument

The released `spec/pawn-candidates.md`, Diagnostic interfaces, expressly requires each color's supplied list to name unique **present pawns of that color**, on the bounded no-terminal-rank-pawn placement domain. Production `current_candidates` also includes a retained descriptor only if its current square contains `Piece::new(side, Pawn)`. Thus raw's board-derived pawn color and candidates' supplied side agree at every admitted call. No new assertion, rejection, fallback or narrower position domain is added. Arbitrary internal calls violating this precondition are not a new supported diagnostic domain.

For such a pawn, both old forward loops enumerate the identical fixed file from its next forward square through promotion, without stopping at occupied squares. At each square the fused loop reuses the raw loop's same immutable board piece and own influence byte. Its path increment is the original empty1/occupied2 expression; its protection conjunction is the original own-king-or-nonzero-own-influence predicate. Induction on the visited prefix gives identical path sum and conjunction; protection is an order-independent boolean conjunction, while the production fused traversal retains the original forward direction. The own-king shortcut changes no relation charge: raw already reads that own byte independently, and neither path nor progress performs a tested-piece relation query.

The nearest occupied backward square still stops that scan, so a nearer nonrook still masks a farther rook/queen. Raw measure updates remain in their original order: backward contribution; then each forward rook contribution and influence/occupancy branch; lower clamp; coefficient multiplication/division; current-pawn influence bonus, otherwise immediate-front bonus. The immediately-forward occupancy penalty remains conditional on the same ordinal-influence branch. No division is combined, moved across a multiply, or replaced. All raw/path values remain i32, and downstream two-stage candidate rounding is unchanged.

The raw scan now runs before the candidate's adjusted-path/relation arithmetic rather than after it. These operations inspect immutable local inputs, have no clock/cache/retained effect, and perform no R queries; on the admitted bounded domain this reordering has no observable state or error boundary. Supplied pawn order, strict path tie selection, top-two candidate scoring and all later composition remain unchanged. No pawn-cache activity, retained state, public layout, allocation or R charge is added or removed.

## Meaningful unrun unit witness

Pawn-progress declarations change0→1; the new unit is unrun. It compares the fused tuple against the entire prior raw implementation (test-only, no calls to the new helper) plus a separate coordinate-indexed path oracle. It also checks public raw's false specialization against that prior raw scalar.

Seven synthetic placements cover both colors, relative ranks2/4/7, immediate promotion, occupied forward squares including both rook colors and an own king, and a nearer backward knight hiding a rook. Each uses its actual placement-derived Influence and256 additional internal normalized-byte maps to exercise ordinal comparisons, equality and current/front pawn bits. Those constructed maps are pure-producer unit inputs, not claims that every such map arises from an admitted placement. They are not fixture-derived answers. No unrelated behavior or new runtime adapter is introduced.

## Cost rationale and remaining gates

The closed current35/08 profile review attributes threshold-limited exclusive displayed owner rows of737,032,118 /584,170,242 simulated Ir to `pawn_progress::selected` (1.5120% /14.0317%). There is no closed pawn_progress source-line allocation proving what fraction belongs to the duplicate walks, and no gain percentage is inferred. This experiment removes a visible repeated traversal with O(1) existing-demand locals rather than a persistent cache or material hint.

The private helper and tuple can change inlining, raw-only return lowering, caller spills, code size and frame use. Public raw's unchanged scalar signature does **not** prove that tuple/path storage or an extra call disappears. Although the false const branch semantically performs no path accumulation, its local constants/aggregate may survive in emitted code. Fresh default backend review must inspect both false raw callers and true selected/candidate consumers before timing; no layout/ABI neutrality is asserted. Full native/strict54/eight-wire and any diagnostic/oracle checks, followed by a matched CPU experiment, require later parent authorization. Nothing compiled or executed here.

## Actual closure

Initial source checkpoint54a416 exited0 before the quiet CPU window; all tools then stopped. After explicit release, exact base comparisonbf6f6c/0, final text derivation4bf132/0 and independent forward/inverse/raw-body verificationad2f87/0 completed. Manual indentation cleanup only affected the test-reference declaration. All helpers ran on0–5,8–13 and returned actual terminal results. Zero owned processes remain. No engine, build, Rust parser/formatter, test, profiler, timing, Git or archive command ran; no shared/root/frozen source changed.
