# Park whole-program fat LTO after own-PGO timing

Experiment36 changes only retained25 Cargo release lto="thin"→"fat". All44Rust
files,178 test bodies,23tools and generic target/compiler/other settings remain
exact. The public reference declares fatLTO; oneCGU already covers most library
code, so the distinct hypothesis was final crosscrate integration.

Generic fixed70 passes at2.541759%lower summed medians,7/7lower. Fresh own-fat
PGO then passes54original/raw/PID/remerge checks with profile6b29f4b7 and builds
use93f4666d. Actual own-PGO integration differs: activity stays outlined, Q grows
4258B, allfourhot reservations grow16B/root96B, although text shrinks12736B.
No generic gain is transferred or static saving inferred.

The separate own-PGO fixed70 passes strict live/original offline checks and
independent native accounting but sums12.7189200→12.7716685s:0.414725%higher,
3/7lower,worst1.00948206. Aggregate/lower-case rules fail. Park without retry,
retuning, full178/117/standaloneuse54/wire/games or promotion. Original metadata
read/extraction failures and bounded actual capture/provenance remain preserved.
Production/root and immutable delivery stay25; no PGO profile is reused.

See [generic staging](../../evidence/fat-lto-generic-decision-20261019-01/README.md)
and [final own-PGO decision](../../evidence/fat-lto-pgo-decision-20261019-01/README.md).
