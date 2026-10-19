# Current43 pawn score arithmetic: exclusive source-row context

The five requested source lines account for **7,919,968 simulated Ir in35 (0.0174905% of whole-program SELF)** and **32,455,541 in08 (0.8256256%)**. They are mixed source-expression contexts, not isolated signed-correction instructions or a removable-work estimate. Unknown attribution prevents treating this five-line sum as an upper bound for all correction instructions. No source trial is selected.

| Source expression |35 exclusive Ir|08 exclusive Ir|
|---|---:|---:|
| pawn_progress.rs:78 |3,561,107|14,534,038|
| pawn_progress.rs:80 |6,030|1,092,144|
| pawn_progress.rs:82 |33,810|705,306|
| pawn_progress.rs:141 |2,033,192|7,797,024|
| pawn_progress.rs:144 |2,285,829|8,327,029|
| **Disjoint five-line total** |**7,919,968**|**32,455,541**|

| Denominator / separate context |35|08|
|---|---:|---:|
| Whole-program exclusive SELF Ir |45,281,552,465|3,931,023,836|
| selected SELF, all inline file parts |762,134,260|585,953,636|
| selected / whole |1.683101%|14.905878%|
| Five-line context / selected SELF |1.039183%|5.538926%|
| Unknown line0, all selected file parts |116,011,007|82,863,156|
| Positive-line types.rs context, left unknown |43,082,759|111,715,764|
| Excluded top-two line174 |2,021,096|4,240,040|

## Inputs and exact ownership

These are the existing closed fresh43 own-PGO profiles35/08, image36251ecf and source72 graph e89dcb33. The collector6e7a77/0 and independent704fc5/0 had already closed; their provenance, verification, two profiles and frozen source/hash maps are bound in input-pins.json. No new profile, source annotation, native execution, compiler or binutils tool was run. No old25/40 cost transfers.

extract.py copies the accepted closed hot-cost analyze.py raw() parser verbatim and uses its physical-row convention: expand fl/fi/fe names and relative line positions; a cost row following calls= is an inclusive arc and excluded from SELF. All physical exclusive cost rows reconcile exactly to each profile summary/totals. The selected owner is exactly rook2::pawn_progress::selected in the36251ecf image object, including every inline file part. Its complete SELF and file partitions equal the closed function-ranking output. No alternative selected-name suffix was silently merged.

Each profile-*-rows.json preserves each targeted row’s raw file line number, literal compressed cost text, resolved source line, cost, object, exact function/name token and source expression. Distinct physical rows sharing a source line are summed once. For35, the five target lines contain28 physical rows; for08,24. The remaining selected SELF is partitioned disjointly into other positive pawn lines, positive types lines, line0 from all files, other positive inline contexts and separately excluded174. All partition row IDs are unique and their costs exactly sum selected SELF. Source-adjacent77/79/81/140/142/143/145 rows are retained as a non-added diagnostic subset. Outgoing call arcs are retained only under NOT_ADDED.

## Interpretation and limits

Line78 combines coefficient selection, indexing, clamp-dependent multiplication and division;80/82 combine bonus multiplication and division;141 includes raw result composition, multiplier/offset and division;144 includes king-distance factor multiplication and division. The parent’s independently inspected signed-correction sequences establish a compiler mechanism separately; DWARF line context alone cannot isolate those instructions. In particular, the shared80/82 lowering need not retain the spelling of each source expression on every instruction. A physical row count is neither an entry count nor a static-clone execution count.

Top-two174 is excluded because the actual backend already uses logical SHR and the parent explicitly excluded it as a target. No part of line0, types.rs, signed integer intrinsic overlays, other file parts or inclusive arcs is reassigned to corrections. Source grouping may hide or relocate some correction work while including required work on target lines. The five-line percentages therefore support only the exact mapped context stated above, not a hypothetical CPU gain, PMU claim, cost-per-candidate or a whole-function removable envelope. The numeric admitted-domain proof and any experiment decision remain parent-owned.

The mapped five-line pool is much smaller in35 than selected’s full cost; sparse08 has a larger context share. That contrast is disclosed without choosing a favorable case, inferring unmapped instruction counts or changing the fixed workload. Parent must combine the closed compiler evidence and these attribution limits before selecting any source trial.
