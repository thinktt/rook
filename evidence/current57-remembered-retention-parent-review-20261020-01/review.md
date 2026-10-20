# Retained-result numerical owner: bounded source crosswalk

This read-only review compares released SEARCH-REMEMBERED-RESULTS with the actual canonical57 src/remembered.rs owner. The exact two native files also match candidate62's source-bound build receipt. It closes the algorithm under the component's own admitted numerical/descriptor context, and the same owner under explicitly imported native capacity/index/identity premises. It does not certify every production caller, diagnose hash-collision reachability or prove arbitrary public library calls are admitted. No engine/test/build/profiler/binutils/Git action occurred.

## Preconditions and representation

For the direct component: ply P in0..63, target T in0..64, raw score/window endpoints in[-10000,10000] with strict lower<upper, well-formed source/destination descriptors and valid abstract group/identity mappings. Required T-P lies[-63,64]; Record's i16 is exact. Mate normalization is computed in i64 from the raw i32, adding P for S>=9000, subtracting P for S<=-9000, unchanged otherwise. Thus the admitted normalized range is[-10063,10063], exactly representable by i16. Query decoding widens the stored score to i32 before its bounded ply adjustment. The inclusive normalized +/-9000 tests match the contract, including the distinction between normalized classification and adjusted cutoff value.

Record::from_store derives LOWER exactly from raw S>lower and UPPER exactly from raw S<upper, before normalization. Strict component windows ensure at least one permission, while an interior score has both. The bound decoder gives Lower/Upper/Exact for flag1/2/3; its None case is an implementation fallback, not a new admission for collapsed diagnostic windows. Independent quiet-checked and marked-depth bits do not affect permissions.

Move::new encodes source in bits0..5, destination in6..11 and kind/promotion above them. from_store keeps only low12bits and exports Move(endpoints). The zero sentinel cannot erase an admitted non-null descriptor: endpoints zero means source=destination=a1, but SEARCH-CANDIDATE-ORDER explicitly requires different endpoints. This relies on descriptor admission, not arbitrary Move(pub u16) construction. No returned hint is certified legal or assigned a moving type here.

## Deterministic retention

Only group.records[0..3] participate in store identity matching, through current-generation AND identity equality. Their first match uses .position; the recent slot is excluded. A shallower matching store replaces only recent; an equal/deeper store replaces the retained record at the same physical priority and leaves recent unchanged. This preserves fixed tie precedence, including a possibly older recent duplicate of the identity.

For a new retained identity, the first generation-invalid priority is filled before all signed depths, and recent is reset to the all-invalid default. With all three priorities valid, least begins at0 and updates only on strictly smaller depth: first priority wins every tie. New depth>=least displaces the exact least record to recent and replaces that same priority; otherwise only recent changes. This matches negative depths and equality boundaries; no insertion age or sorting is substituted.

clear's logical generation change makes every old record ineligible. Filling after clear therefore recreates first-empty precedence, regardless of old physical depth contents. Before reusing generation1 after255, physical Group::default clearing removes all old byte epochs. This restates the already closed generation-lifecycle fact; it does not claim new cross-go runtime evidence or answer same-search collision composition.

## Query and mutation order

ProbeResult::default starts None score/bound/hint/marked depth and false quiet check. probe considers a matching recent first and returns immediately only if consider supplies a score. Otherwise it considers the first matching retained priority and stops scanning. Native store/clear rules maintain at most one valid retained record per identity, so this chooses the abstract retained result; manually forged record arrays are private and outside this induction.

Each consider first replaces bound with this record's kind, replaces hint only when endpoints nonzero, ORs quiet check, and max-combines marked depths for marked records. Consequently no-score recent metadata can survive a retained null-hint, quiet flags combine, marked depth is a maximum, and the LAST considered record owns bound. Permissions are not unioned across records. A usable recent prevents any retained observation.

The score is decoded using the normalized sign/threshold. Lower cutoff uses LOWER and decoded score>=query.upper; upper cutoff uses UPPER and decoded score<=query.lower. The early mate route requires normalized>=9000 plus lower cutoff, or normalized<=-9000 plus upper cutoff, with no stored-depth requirement. It raises this record's depth to max(old,required) and returns its adjusted score. Metadata was collected BEFORE that mutation, so marked depth reflects the old value on this query and can reflect the raised depth later. Both recent and retained are actual mutable records, so later storage comparisons observe the mutation.

The remaining route requires stored depth>=required and at least one cutoff. Exact scores strictly inside the window provide metadata but no score. Boundary equality cuts off. No branch in store/probe/consider calls search or relation charging; the owner imports only Position/types and maintains table state. This establishes zero direct semantic charge, not zero CPU work or unchanged downstream search work.

## Explicit remaining scope

This is source reasoning about the shared numerical table owner. Diagnostic label interning/validation/serialization, identity/hash/group construction, allocation/resource bounds, native score/depth producer ranges, optional bounds-only invalidation and full search lifecycle are separate owners. Native remaining-depth and normalized-score capacity rely on their separately bound proofs. Arbitrary Query or Store outside those domains may panic or differ and is not admitted by this memo.

In particular this review neither legalizes remembered endpoints nor supplies the absent moving-color/type rule for an empty-source cutoff completion. The uncertified-hint composed-call question remains unresolved without an admitted public witness or exclusion proof. Full cached-admission/window/TT/IIO/interruption compositions are not inferred from this local crosswalk. Finite test passes are not relabeled a universal production theorem. No source, build flags, current measurement inputs or artifacts were changed.
