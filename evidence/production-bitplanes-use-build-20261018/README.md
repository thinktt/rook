# Canonical persistent attack-plane PGO artifact

The immutable ordinary artifact is
`915f83e4c93bbb1b378c9a7d4250f93981347a4a75760db1510330ee395277fd`.
The canonical `/home/legolas/rook2` crate uses generic x86-64, opt3, thinLTO,
one codegen unit, panic abort and debug1 under Rust1.85.1/LLVM19. The build receipt
and verified source archive bind the exact sources, tools, settings and inputs.

Its own instrumented artifact086ccd5a trained on all54 unchanged strict public
replays. All54 independent raw profiles and their merge are verified under
`../production-bitplanes-training-20261018/`; merged profile SHA256 is
`5efa60756cf2677c7aea5f7587ed29ac596c2b19d2a7e9a361f275053f2481ef`.
No profile from the earlier isolated prototype was reused. There are zero
missing-profile/function warnings. The unused local-view constructor warning
is retained in the original build stream.

All54 strict replays and eight wire interruption fixtures/24 searches pass on
this exact ordinary binary. Its own independently reconciled60-lifetime CPU
pilot gives3.127329% lower summed case medians than prior1dc996b2, with one case's
sample ranges overlapping. These finite component and local timing observations
do not complete mandatory diagnostics, whole-production review, gameplay or
final performance qualification.
