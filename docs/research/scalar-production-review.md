# Scalar work/history production review

Reviewed2026-10-18 against the exact source of production artifact1dc996b2.
`evidence/scalar-review-20261018/receipt.json` binds every reviewed native and
released-contract file; native hashes match that build's source map. This is
source/algebraic review. No new engine, build, profiling or native test workload
ran during the live game collection. It does not close mandatory DIAG transport
or the complete production review.

## WC-LEDGER and profiling numerator

| Requirement | Native owner and review |
| --- | --- |
| Effective K equals N through2147483647, then2147483648 | `Work::effective_search_count` takes the minimum of raw u64 N and2147483648. This is identical at the inclusive boundary and above it. |
| Combine weighted activity before integer rounding | `Ledger::observe` casts operands to u128, computes3806*K+770*R once, then divides by30000000. There is no per-event rounding or floating-point accumulator. |
| Intermediate capacity covers admitted counts | K is at most2^31 and R at most2^64-1. Their maximum numerator is below2^74; every multiplication and addition is in u128. The bound calculation is retained in the review receipt. |
| Saturate the segment before adding origin | The divided increment is capped at2147483647, converted to u32, then added to origin with wrapping addition. It does not saturate the carried sum. |
| Observe absolute segment work | Each call replaces numerator and last from origin plus current T. It does not add T to the previous last or accumulate repeated observations. Replacing diagnostic supplied work with a lower count can accordingly lower last within the segment. |
| Reset carries only the last observation | `reset` copies last to origin and clears the numerator; it does not read newer Work. It leaves last unchanged, so repeated resets do not advance it and fractional remainders do not carry. |
| Fresh ledger starts at zero | Derived Default initializes origin/last/numerator to zero. Nonzero `with_origin` is an explicit internal carry boundary. |
| Fine post reads the most recent B | `fine_post` divides stored numerator by1000 and caps at2147483647. It neither observes work nor adds carried origin. Reset clears B. |
| Publication uses its current snapshot | Immediate publication sets the third field from the current timing ledger before rendering. Deferred session publication uses the current finished ledger. Capture objects do not own B. The fallback branch renders default zero fields. |

The reviewed session search-entry path observes prior segment work, computes
allowance/seed context, resets the ledger and clears its Work. The timed clock
starts with that observed origin and zero segment work. Search finish copies
the outcome ledger/work and makes its specified finish observation. These are
identified call sites, not a completed proof that every possible ordinary
observation/reset or interrupted host path is placed correctly.

The native ledger returns an unsigned clock word. The mandatory diagnostic
adapter still needs explicit signed-word serialization and schema/domain
acceptance for clock.workSequence. Normal elapsed-time consumer wrap rules and
profiling launch persistence are separate review obligations. Existing all54
strict fine-work replay observations remain attached to their frozen artifact;
they do not substitute for the complete scalar transport or lifecycle audit.

## Historical repetition and endpoint reversal

| Requirement | Native owner and review |
| --- | --- |
| H<4 returns0 | `SearchHistory::repetition_count` returns before any scan. |
| H>100 or H==100 outside check returns50 | The explicit numeric sentinel is preserved. H==100 in check continues to the scan. |
| Scan distances4,6,... through available H | The loop starts at4, steps by2, and ends at min(H,currentIndex). Distance2 is excluded; unavailable earlier states are excluded. |
| Exact supplied repetition equality | Boundary equality uses primary identity, moving side, rights and EP only. Secondary identity, mailbox geometry, chronology and halfmove do not strengthen that predicate. Upstream identity derivation is a separate obligation. |
| Return M+1 only after at least one match | A zero match count returns0; positive matches add the current occurrence. At H<=100 at most49 earlier distances are examined, so the counted result fits u32 and can equal50. |
| Root split does not discard eligible history | `mark_root` records an index without truncation. The scan uses the whole boundary sequence. Search reset removes only the recursive tail. Vec capacity is a reservation, not an admission/truncation ceiling. |
| Signed nonzero ana has the same exception | `repetition_draw` tests ana==0, ply>=3 or count>=3 after requiring positive count. It does not order negative and positive nonzero ana. |
| Reversal requires current/prior same-side endpoints and flags | `short_reversal` requires search ply>=3 and H>=3, current and two-plies-earlier arrivals present, reversed endpoints and rights/EP equal to the three-plies-earlier boundary. It does not strengthen with secondary identity or placement equality. |
| Null arrival is absent | `push` filters the absent-move sentinel to None; either compared endpoint arrival being None rejects reversal. A null intermediate arrival is not itself one of those two compared moves. |

Ordinary entry charges its node, tests repetition, clears next-ply killers only
on continuation, then applies the upper-bound-dependent reversal rule before
remembered lookup. This identifies the reviewed ordinary placement. Frontier,
mate-leaf, quiescence, host interruption and all charged-event placements still
need their own composed review. The external nodeAdmission/history/reversal
transports and upstream position/history production remain separate acceptance
work; finite native tests and supplied labels do not prove natural reachability
of every diagnostic context.
