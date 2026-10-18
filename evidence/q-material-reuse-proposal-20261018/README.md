# Q-only local material-endpoint reuse proposal

Status: cold, uncompiled and unexecuted. Parent selected this bounded trial, not production adoption. Isolated source: /tmp/imp2-q-material-endpoint-reuse79-20261018-mrdiwe1a. Baseline is the exact frozen79 source at /tmp/imp2-eval-pawn-observers-20261018, matched to the earlier census baseline43. Current root, another child's82 diagnostics, preparation/census evidence and prior reports were not edited.

Only src/quiescence.rs and src/quiescence_policy.rs differ. All other41 native/build identities, including ordinary.rs, ordinary_policy.rs, evaluator.rs, evaluation.rs, Position, Node/Retained/Evaluation ownership and root fields, are unchanged. No persistent field, heap allocation, protocol/diagnostic schema change, Node enlargement or ordinary/frontier reuse is introduced. The archive contains exactly43 native/build files plus the23 unchanged tools; every archived member was read back and hash-verified.

## New measured motivation, not a CPU prediction

The new verification independently reconciles54 strict cases. This preparation reread all54 original counts.json files and reconciled their Q totals with verification.json. Q has33,428,231 actual allowance calls,22,874,073 summed per-loop victim-tuple keys,16,210,786 nonempty and27,887,854 total candidate-inventory lifetimes. There are11,677,068 zero-call lifetimes, including6,924,502 checked Q inventories.

Original Q endpoints total66,856,462. The local lazy model totals39,084,859 (one current endpoint per nonempty loop plus each distinct after endpoint). The difference27,771,603 is41.5391% of Q endpoint source demands and16.9770% of all measured search-segment material source demands. It splits into17,217,445 repeated current endpoints and10,554,158 repeated after endpoints. These are actual source-selection opportunities, not emitted calls, retired instructions or CPU gain. Root preparation is outside the census segment. The old8d simulated instruction profile is not attribution for this new trial.

## Representation and exact lazy scope

Q declares a stack-local Option<AllowanceMaterial> after candidate ordering and the existing empty/mate-return gates. It starts None. The original non-check, late-screened, !special/nonempty allowance branch alone calls get_or_insert_with. Special still means promotion or EP. Therefore A0 and checked Q never invoke the cache constructor, request any material endpoint or initialize the after-score array at source level. The Option discriminant/frame can still have a cost even on those paths; compiler output must establish its placement.

The first admitted request creates a cache with before:i16, after:[i16;10] initialized to zero, and seen:u16. Constructor requests complete current-parent root.material once. At each original allowance site, actual occupied destination victim color/type maps to color*5+kind, with bits0..9 for White P/N/B/R/Q then Black P/N/B/R/Q. On first use of that tuple, the code copies the original parent Position, decrements exactly that victim's actual count and computes/stores complete adjusted/clipped after material. On repeated use, only this pure endpoint calculation/copy is omitted. A separate valid bit allows an actual stored zero score; no sentinel score is used. Ten slots retain explicit color ownership rather than assuming a pawn or inferring a tag from move spelling.

The cache stores only numbers, not borrows of evaluator/root/Position. Its sole production owner is that Q stack invocation and one immutable parent inventory. It survives child recursion/suffix candidate processing on that parent and is discarded on return, break or error propagation. Recursive Q invocations have separate locals. RootContext values/counts/root side/averageDepth remain fixed during that invocation; child pawn-cache/learning/history changes do not affect material. A cache must never be reused after mutating the parent/root or across another invocation. No fingerprint/shared lookup or persistence implements that reuse.

## Endpoint and finishing proof

RootContext::material reads current counts with fixed root context and always returns a fully adjusted/clipped score in[-7000,7000]. Every cached endpoint is therefore exactly representable in i16. Endpoints widen back to i32 before subtraction; difference is within[-14000,14000]. The full allowance remains i32 and is not narrowed. Material's signed floor rounds, actual non-pawn presence including zero-valued pieces, average-depth adjustment, sign selection, advantage caps and final clipping are computed by the unchanged original material function at every miss.

For a fixed parent/root, removing any actual victim of the same color/type produces exactly the same count-only state regardless of destination/source or physical victim identity. This is the cache key proof. The count-only hypothetical never becomes a played child, never updates board/lists/fingerprints, and never changes base influence or retained pawn state. Promotions and actual joined-EP victims remain handled by the original Q special route and never enter this ordinary allowance cache. Checked Q also never enters it.

Public allowance retains its signature and uncached current/after calculation, so direct count-only diagnostic/ordinary-frontier callers remain valid. It now delegates the remaining arithmetic to one private finish_allowance kernel. The cached method calls that same kernel on every request. The old suffix from victim sign through gain, retained pawn-versus-positional selection,50 addition and capture_exception800 addition is byte-identical to that kernel's suffix; source-proof.json records its common hash. This is a native extraction, not an adapter-formula clone.

Each call still rereads its actual victim, chooses its sign, selects current retained inputs and runs capture_exception after endpoint acquisition at the original allowance site. Changing retained arguments on a repeated key is deliberately not cached. Standing score addition, moving-value/support selection, optimistic best/threshold updates, initial eligibility, check/reply probes, king safety, recursion and semantic N/R selection/order are unchanged. Pure material performs no relation charge or pawn-cache effect, so omitting its duplicate calculations changes no semantic charge. No final-score/retained value substitutes for current material.

## Differential test inventory, not executed

Three new tests compare the cached path against the public uncached helper using the unchanged material calculation. The two paths share the finishing rule intentionally; the old rule's unchanged suffix proof and existing allowance tests independently protect that extraction. New comparisons target cache key/lifetime/narrowing behavior, rather than reproducing the cache algorithm as their oracle.

- All five actual victim types in both colors, both root sides, asymmetric generated root values, and averageDepth[-99,-1,0,1,99], with root/current population differences. All target routes in this group are clear queen captures from d4.20 cache lifetimes,800 comparisons if executed.
- Two different rook destinations and two knight destinations, reverse traversal, both root sides, zero-valued knights and queen values around sign/50-point boundaries. Repeated calls vary retained positional/progress terms to catch accidental whole-allowance caching.54 lifetimes,1728 comparisons if executed.
- Positive/negative final clamps (also activating the advantage cap), and a zero-valued last non-pawn capture that still changes material because the presence gate disappears. Three lifetimes,24 comparisons if executed.

All groups check parent preservation. These are component requests on bounded constructed placements, not a claim of natural ancestry or full legal-move completeness. Original public-helper tests remain present. The new test inventory totals77 local-cache lifetimes/2552 comparisons by static loop counting; none is a pass result. Root contexts in tests are fixed per cache; a new cache is created for every changed root/parent. Parent owns native/full54/wire/adapter validation.

## Code-generation and measurement caveats

The plain cache payload is24 bytes at source (eleven i16 values and a u16 mask). The Option requires validity representation and alignment; actual Rust layout, frame growth and emitted accesses are unverified. It reserves a function-local value even when never constructed, so A0/checked calls can still pay frame/discriminant/spill costs. At first use it initializes ten after slots even if only one tuple is ever used; these nominal20 zeroed bytes plus current/mask stores are paid once per nonempty loop. Key formation, valid-bit branches, endpoint loads/widening, register pressure and retention across recursive calls are additional work. The compiler may hoist zeroing or enlarge stores; source-level get_or_insert laziness does not prove exact machine initialization placement.

Conversely LLVM may elide portions of the old count-only Position copies or common-subexpressions. The source-request savings cannot be multiplied by a nominal per-call cost or old profile percentage. Extracting the shared finisher changes the public helper's compiled shape too, even though ordinary/frontier source and semantics are unchanged. A generic whole-search comparison must include all these effects. No inline/alignment/unsafe/layout tuning was added to rescue this proposal before evidence.

Parent should first compile and run the meaningful new/existing native tests, exact strict54/work and wire/diagnostic checks against this exact archive. Then inspect frame size, initialization placement and material/finisher code, and run the prospectively chosen balanced generic comparison against the same frozen79 baseline under each artifact's own receipt. No timing is inherited from the census, old8d, current81 root or other trials. Any PGO/combination/adoption requires a separate parent decision and fresh validation. This proposal has no measured CPU benefit and no production adoption claim.

## Exact identities

prepared.json binds all43 before/after native/build hashes and all66 archived files. source-proof.json binds raw census totals, the shared unchanged native suffix, and the unexecuted test inventory. Paths below bind the relevant source/spec/evidence anchors; native paths are relative to the frozen79 baseline.

~~~text
dddd6a260805a7a53ee61ceb74141cb52f9a3fdc899f2350412ffa86be439e33  src/quiescence.rs
07ed6db1af2d7fc21f093aa619f5a931aa32d594f4c1b435968ad95691b8bda4  src/quiescence_policy.rs
767b1ef83fea5d30d1b5a6edaa259fa718c666cfdb568fb9ad7b2aca2e9f33f7  src/evaluation.rs
68e44e7a7af1349934423679f4717c281fc437c050ee0ccb93f66b808296535e  src/evaluator.rs
446b518a5824a8a60b65666d1b841d959ab2964c995739a2bc44d27bd5a9c442  src/ordinary.rs
a79ec111e2d34bb9e4a3c2a7953c5b2a82b011016982fd2b63d6769da3036bf6  src/ordinary_policy.rs
749f9fa1e90684c4df670c115c3c7f7dbdb196cf62b5eb267900ba217143ce3a  src/position.rs
0d961686154deb4b9dfdd110588fe146300546dd2adbcfb031a78cfb40605610  /home/legolas/rook2/evidence/material-allowance-census-20261018/verification.json
bb6fca599055c06c84a52f8a5b1bc7f8dbc9cea704cdb146b641d5ce13356784  /home/legolas/rook2/evidence/material-allowance-census-20261018/summary.json
7e1c7f546e68cfafc636abfec52c21a0bb9258f908ccfb2adbd9dd840a309e10  /home/legolas/rook2/evidence/material-allowance-census-20261018/tool-terminal.json
6608d35bf643cca6880342193b63fa10961de424621bd9e44cb637b11c318220  /home/legolas/king-spec/spec/quiescence-capture-allowance.md
ec81afa0660683ccf12389df3eba8b6b7e5676fc7c8d1fd3a8fdc881df663666  /home/legolas/king-spec/spec/material-balance.md
~~~
