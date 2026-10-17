# Native composed evaluation and root checks

All 1,352 generated native cases pass: 1,333 evaluator cases containing 201,374
queries, ten first-root iterations and nine ordinary fixed-iteration searches
(six neutral and three selected personalities). The fixture inventory and
operation counts are in `receipt.json`. Expected data remains in an external
test crate; none is embedded in the engine.

The evaluator checks cover central influence, board patterns, pawn progress,
candidate order, pawn/queen endings, pawn race geometry, fresh pawn subtotal,
pawnless material potential, minor mate geometry, material blends, fortress
and race bounds, endgame adjustment, final score and composed fresh scores.
Native root checks compare move descriptors including kinds, initial and
carryover candidates, every root window, score/best/second, child/root PVs,
iteration results and cumulative SearchID/N/R work. Native settings cover
the supplied complete 30-field profiles with rnd 0; random/session binding is
still pending. These finite tests do not prove every possible search tree.

`tools/check_evaluation.py` prepares data files and a small test dispatcher;
`tools/evaluation_probe.rs` reads valid fixture data and calls actual native
computation. It never supplies expected answers to engine code or branches
on fixture identifiers. The probe is a checker, not the production parser.

The verified compressed test archive retains every generated Rust/JSON file,
the manifest and lockfile. Receipt hashes bind released fixtures, checker,
runner, engine sources, data and raw results; pre/post checks confirm stable
engine, generated source and expected data. Generated copies are ignored in
Git because their exact bytes are preserved in the archive.

This is native semantic evidence. Strict DIAG validation/transport, complete
quiescence/evaluation-stage traces, ordinary session lifecycle, gameplay and
whole-engine performance qualification remain outstanding. No mandatory
conformance or performance acceptance claim is made.
