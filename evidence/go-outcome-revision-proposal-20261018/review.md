# goOutcome revised source proposal

Source `/home/legolas/rook2-work/imp2-go-outcome-revision-20261018-gejdcnbl` is a NEW generic110 clone. It copies exactly `src/host.rs`, `src/session.rs`, `src/bin/rook2.rs` from persistent113 revision02 `/home/legolas/rook2-work/imp2-persistent-session113-revision02-20261018-idpvozjm`, then changes ONLY `diagnostic/src/actual_timed.rs`. Frozen generic110/111, persistent113, root and prior audits remain unchanged. `native.patch`, `cold.patch`, `trial.patch` are reviewable text patches; no hashes/archive/freeze or full inventory were performed.

## Admission and native state

The Go parser retains exact top-level fields and60000 clocks. It eagerly validates the ENTIRE JSON command array, string types, ASCII/no embedded separators,1022payload/40token bounds and explicit sd/go/quit/hard fences before creating the setup Session. There is no command-count cap or fixture whitelist. Per parent clarification, native argument grammar and legality are checked during ONE actual setup, entirely before go: Session.idle owns ordered parameter/default/alias/query/unknown, move, reset, clock and protocol effects. No disposable preflight Session or command algorithm copy is added.

Native Action::Search/Quit and native Illegal move:/Error replies fail setup; valid parameter name=? and all other accepted non-search replies are ignored. Thus native unknown commands cannot become accepted merely because they return Reply, while unknown parameter names remain valid. Blank records and empty/bare cm_parm are permitted. Stored transient values are unrestricted by final-vector admission; native final effective settings decide qualification.

A cold boolean tracks only successful game-initial reset provenance: FEN6setboard qualifies the baseline, new/FEN4 clear it, later successfulFEN6 qualifies again. There is no exact setboard count. Native coordinate+undo/remove can restore empty active history on this same baseline. Actual native reset/adjudication/counter/position/chronology arithmetic remains authoritative. Explicit post/easy encounter is retained per parent interpretation, alongside final full neutralmd1/rnd0, enabledpost, disabledpondering, force mode and emptyhistory. Final time/otim60000 are sent through Session.idle after qualification. Independent actual full legal roots, checked-nonempty admission and first-iteration/resource checks remain unchanged.

## Late natural seed and actual publication

Cold GoHost uses the existing Host interface, no command queue, and actual Session.go_live. It samples SystemTime only inside acquire_seed, after native timed root/fresh-state preparation, calls the exact113shared native helper, records that acquisition and the actual started seed, and publishes actual native Records. The supplied seconds0 is only an ignored prepared placeholder. A successful nonempty result must have exactly one acquisition, actual entryclock and outcome seed agreement, and one started observation. rnd0 does not suppress acquisition.

Generated zero-root is independently tested, then only actual FatalEmptyRoot can select fatalExit. This path must have zero acquisitions/started callbacks/records. Generic failure cannot become fatal. Nonempty success projects actual ordered Records: posts before one selectedMove, optional adjudicatedResult only after it; unrelated status/abort/post-after-move/duplicateMove fail. The native retainedPV head must equal that selected move. Actual live publication/final_report/clone/rendering/move-application/error cleanup stay owned by native go_live; SearchResult.events is intentionally unused because live leaves it empty. No adapter search or publication recurrence is introduced.

## Exact native binding and default scope

Small byte comparisons prove the three copied native files equal revision02. Removing the one authorized host helper and reversing its two call substitutions restores each generic110 file exactly. Therefore no default Session/WireHost sample site, native state/layout/interface or search body was changed by this proposal. This does not claim byte-identical emitted code: the shared helper is a new public inline function, so fresh native/generic/strict+wire and scoped default/backend review are still required.

Source literal proof also preserves the seededTimed route, shared projection/validators, and all three existing seeded tests. Neither its explicit-seed controls nor generic110's const IIO capability entries change.

## Test declarations and limits

actual_timed still declares SEVEN tests in total: three seeded tests unchanged and four Go tests strengthened; the original parent phrase Go7 is interpreted as the file's seven existing declarations, not seven Go-specific tests. Declaration delta0; native declarations/routes/fixture cases/files/source-file counts delta0. Absolute union counts have not been recounted.

The four revised Go tests cover: native harmless noops/unknown/bare/emptyqueries/overwritten settings; entire-record fences/width/token/schema failures; repeated reset/FEN6 and FEN4/new provenance; actual legal c2c3+undo/remove restoring empty baseline; invalid late native argument/command/move/final state and missing encounters; actual live/offline native post+move equivalence and unchanged output under harmless setup; shared seed equation and native started observation; independent generated checkmate/stalemate zero roots with ZERO acquisition/publication. These are unparsed, uncompiled, unexecuted SOURCE declarations. The fixed c2c3 test is a legal blocking continuation from the authored checked test root by source inspection, not an oracle result claimed from execution.

No Rust parse/format, build/test/engine/codegen/profiler, archive/hash/inventory or performance work ran. The root source and frozen parents are untouched. Parent owns source acceptance, later freeze/inventory, fresh native/generic+strict54/eightwire24 and exact full cold raw/original/independent validation. No speed, parity or adoption claim.
