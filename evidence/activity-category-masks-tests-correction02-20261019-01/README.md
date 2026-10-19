# Experiment35 fixture correction02

The first focused run failed only while constructing the coordinate witness: the original Rd4/Qd3/pd1 FEN has a pawn on a promotion rank. Original source is preserved in `batch_tests-before.rs`; original preparation and failed native evidence remain unchanged.

This narrow correction translates that witness to Rd5/Qd4/pd2. The rook/queen/pawn south-ray distances and kind/color roles remain identical. Under all eight board symmetries the pawn is on rank2 or7/fileb org, so no transformed pawn reaches rank1 or8. No assertion, symmetry, oracle or test is removed. There are still eight new declarations; all178 prior test bodies and production files are untouched.

Source-only correction; no parsing/build/test/native execution by this owner. Parent owns the corrected focused run. `correction.patch` and `inverse.patch` preserve exact endpoints.
