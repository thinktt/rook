# Scoped ACCEPT: frozen named-vector parser02

Reviewed immutable parser `d4c59266…`, checks `886970dd…`, schema/proof and closed owner attempt19dc45/0/final7e401f/0. Source/current-tool semantics are acceptable for the explicitly frozen ASCII v1, complete single-part, line-only workflow. This is not a general Callgrind importer or recording authorization. No engine, profiler recording/model, build, disassembly, Git or owner-tree edit occurred in this review.

Primary authority is the installed Valgrind `html/cl-format.html`: sections3.1.1–3.1.6 define event ordering, omitted counters, exclusive cost lines, inclusive call associations, sequential string compression and relative positions;3.1.7/3.2 distinguish summary from totals and describe inline fi/fe and jump records. The local installed annotator source was also inspected, not executed again. Exact paths/hashes are in input-pins.json.

## Findings resolved before freeze

Three draft notes were sent to owner/root, not patched by this reviewer. First, Costs? in the format permits position-only rows with every counter omitted: final vector45–52 and row99 accept/pad these as zero. Second, compressed-looking malformed names must not silently become literals: resolve29–39 now rejects `(12`/`(1)name`. Third, compression IDs are string aliases, not physical function identities. Rank127–138 intentionally coalesces object/function NAMEs; final results/schema explicitly disclose possible same-name merging and preserve file partitions/raw rows/function tokens. This is honest NAME attribution, not unique owner/caller evidence. Do not later relabel it physical function cost.

## Frozen semantic audit

Events are parsed once by name and order; an explicit expected list validates the exact set, so header reordering is mapped correctly rather than assumed positional13. Cost vectors pad omitted trailing counters, including all omitted values. Ir=0 rows with Dr/Dw/branch/cache events remain in raw SELF and all sums/ranks; no positive-Ir filter exists. Counters and aggregate SELF totals are checked within u64; grouping is nonnegative partitioning of that sum.

File aliases are shared across fl/fi/fe/cfi/cfl, function aliases across fn/cfn, object aliases across ob/cob, with separate namespaces, forward-unresolved/redefined aliases rejected. Inline file changes remain attached to the current function name. Relative source positions use the preceding cost position, including call cost positions. Raw call target tokens remain tokens, not certified resolved addresses. Callee-object inheritance is explicitly unresolved when not established in the current function context; no physical provenance is inferred from stale names.

Exactly the next cost row following calls= is classified inclusive and kept separately. It updates compressed source position but is never added to SELF. A pending call cannot cross a name/header/EOF boundary without rejection. Comments/blank lines may intervene, as the format allows. SELF sums, full summary and totals must agree for EVERY event, and rank sums are checked likewise. Unknown/unidentified labels or source line0 are retained rather than assigned to engine work.

The general format permits summary>=SELF for partial attribution. Parser02 intentionally rejects unequal/short/missing vectors, multipart/thread-split/instruction-position/derived-event/jump inputs and malformed/overflowing rows. These restrictions are fail-closed workflow admission, not claims that the general format forbids them. Future collection must validate the exact schema rather than silently reclassify a rejected file. This audit does not demand support outside the frozen actual-tool domain.

Derived rates are Bcm/Bc and Bim/Bi only: integer counts remain exact, absent/zero denominator gives null, impossible misses>branches rejects. Ratios are floating diagnostic summaries, not exact rationals, PMU measurements, cycles, calibrated cost or CPU predictions. Other cache ratios are not asserted by this parser.

## Independent controls and historical agreement

Reviewer actual00f5fc/0 ran18 small hand-worked controls against the frozen parser: Ir0 secondary/short/all-zero vectors; cross-namespace aliases/inline files with huge inclusive arcs excluded; zero-rate denominators; and15 malformed/incomplete/schema/multipart/jump/count failures. All passed,0.003776s internal wall, no subprocess/engine/model/annotator from that helper. This remains far below the assigned60s cumulative offline-child/16MiB output envelope; source-only reads/design were separate. Own output inventory is in closure.json.

Owner's separately closed33 canaries and existing old57 Ir cross-check were inspected. Their source compares every22,091 SELF row and1,203 arc row/labels/positions/counters to the prior accepted result, and511 NAME-group/file partitions. That is compatibility regression evidence, not an independent oracle for future13-event cache/predictor semantics. The retained actual installed-annotator command/stdout/stderr hash/exit independently corroborate43,940,740,008 PROGRAM TOTALS on that same old57 file. PROGRAM TOTALS does not independently certify each source owner, each arc, or the new event columns. No old57 cost is transferred to current62.

No further blocker identified within the frozen domain. Scoped ACCEPT for root's prospective collector integration, contingent on preserving parser hash, expected schema, exact totals reconciliation, bounded resource supervision and raw inputs. Recording/model execution remains false and requires separate parent activation. No performance/candidate or broader qualification conclusion follows.
