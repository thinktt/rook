# Ordinary depth and learned-history range review

Reviewed2026-10-18 against the unchanged native source bound to production
1dc996b2. This is source/algebraic review, with no engine execution, build,
profiling or new native test during the live full12 CPU collection.
`evidence/depth-range-review-20261018/receipt.json` binds the reviewed files.

## Recursive depth and table metadata

The normal work-timed entry accepts at most62 entered root iterations. Its
completed-iteration terminal rule stops at iteration depth greater than61;
personality `md` can stop earlier. The separate fixed-iteration library entry
accepts1..8 iterations. The root child starts at ply1 and remaining depth
`iteration-1`, at most61. This does not treat the personality's default md999
as999 entered iterations.

The ordinary entry delegates to quiescence before table operations when depth
is nonpositive, ply is63, or the personality depth has been reached. Ordinary
table queries and stores therefore use plies1..62 and positive remaining depth.
Fresh extension flags lie in0..7 under the released contract; the implementation
actually produces at most6, and accumulated OR flags can reach7. Use the looser
contract bound7 here. A main child can increase remaining depth by at most6.
IIO subtracts an offset of at least2 before the same fresh extension; a null
trial subtracts3 or4. Scout retries repeat an existing child request rather
than increasing its depth. Every recursive child increases ply by one.

Thus at ordinary ply P the conservative positive-depth bound is
`D <= 61 + 6*(P-1)`. At P62, D is at most427 and target P+D at most489.
An ordinary-produced boundary child at P63 has D at most433 and tactical target
at most496. Mate probes use target P+1 and cannot increase these maxima. These
are capacity bounds, not claims that the maxima are naturally reachable.

The native remembered table stores signed remaining depth in i16. Both this
ordinary production bound and the direct component domain(-63..64) fit. A mate
lookup raises depth only to a supplied required depth, so it preserves the
same bound within each admitted context. This review does not close score
normalization capacity, all table lifecycle callers, solve mode or the full
remembered-result production audit.

## Learned-history arithmetic

Fresh ordinary search clears history and its total. A continuing ordinary
learning event uses positive D<=427, so its increment8*(D+1) is at most3424.
Assuming the pre-event total is at most10000, the unreduced total and every
individual entry are at most13424. If that exceeds10000, per-entry ceiling
halving over at most768 keys gives a recomputed total no larger than
`(13424+768)/2 = 7096`. If no reduction occurs, the total remains at most10000.
This establishes the invariant by induction and keeps the native u32 entry,
increment and recomputed-total arithmetic far below overflow.

The direct cutoff component permits initial total10000 and D0..62. Its
increment is at most504, unreduced total at most10504, and the analogous
post-reduction bound is5636. Repeated identical events still reduce after each
increment; their repetition count does not become one large unchecked sum.

These arithmetic statements are conditional on an eligible event with an
identified moving piece. They do not supply a rule for an uncertified retained
hint with an empty source. That separate composed-call question remains open
in `uncertified-hint-completion.md`; the diagnostic candidate domain does not
admit such a direct event. This review neither validates skipping the update
nor infers a moving color/type. Entry/clear ordering and eligibility remain
separate behavioral obligations.
