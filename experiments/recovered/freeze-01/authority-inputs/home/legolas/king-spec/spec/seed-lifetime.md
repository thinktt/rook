# RANDOM-SEED-LIFETIME — ordinary searches and clock-derived seeds

For the ordinary searches covered here, acquire one seed when beginning the
first search depth. Let S be the sampled system time in seconds and C the
sampled engine clock in centiseconds. The seed is `(S + C) mod 2^32`, expressed
as an integer from 0 through 4294967295. The engine clock in the target profile
is [KingRE work time](work-clock.md), not host CPU or wall-clock duration.

For natural production acquisition, S is whole POSIX wall-clock seconds since
1970-01-01 00:00:00 UTC, reduced modulo 2^32 to an unsigned value. Discard the
fractional second before reduction. This is not process uptime, monotonic
uptime, local civil time or a timezone-adjusted count. Use a successfully
obtained nonnegative epoch time; host-clock acquisition failures and
pre-epoch operation are outside this profile. An abstract host time source
is equivalent only if it supplies this value.

Sample once during ordinary search preparation, after the reached root and
fresh search state have been established and before the first recursive
search work. The reference to beginning the first depth denotes this
acquisition boundary, not an additional resampling inside that depth. Reduce
the sampled work-clock value C modulo 2^32 before the modular sum as well.
Wall-clock adjustments may affect later acquisitions; do not impose a
monotonic-seed rule or timezone correction. Diagnostic supplied seconds replace
this time-source value only when that diagnostic control is selected.

Retain that seed across the search's moves, completed depths and repeated
root-move processing. A new ordinary search acquires a new seed even when no
`new` command intervenes, the position is restored with `undo`, the personality
changes, or randomness is zero. Zero randomness disables the adjustment, not
ordinary seed acquisition.

The seed is not advanced for each root move. Apply the deterministic
[root-randomization rule](root-randomization.md) using the retained seed and
that move's attributes. A subsequent search may obtain the same numeric seed:
acquisition is an event, not a promise that its value must differ.

Freezing S alone does not imply identical seeds across searches. KingRE
preserves its elapsed work-clock epoch across searches; later sampled C can
therefore differ. Starting a fresh engine session is different from clearing
the chess game in an existing session. Do not reset that epoch just because
`new` or a position-setup command was sent.

## SESSION-CLOCK-SEEDED-SEARCHES — composed diagnostic

`session.clockSeededSearches` accepts exactly `{systemSeconds, searches}`.
`systemSeconds` is an integer in 0..4294967295. It fixes the system-seconds
source for the entire diagnostic session; it does not directly set the search
seed or freeze/replace the work clock.

`searches` contains 1..16 sequential ordinary searches. Each has exactly
`commands` and `allowanceCs`, following the command/setup and allowance domain
of [session.searches](search-pawn-lifetime.md), except explicit `rnd` settings
may be any integer 0..1000. Every search still requires an explicit final
randomness setting and maximum depth 1..4 after any `default` reset. All
supplied randomness assignments must lie in that domain.

Use a fresh engine session with the target's default KingRE work clock and
token-independent behavior. Execute each command list, supply its allowance,
and begin an ordinary search. Await its selected move before processing the
next command list. Preserve engine/game/work-clock state between these searches
unless a supplied command changes the relevant state. Each completed selected
move has the normal session effect, so `undo` can restore its prior position.

Return `{results: [...]}`, with each entry containing exactly `seed`, `move`
and `posts`. The move and complete semantic post trail use the same schema as
`session.searches`; `seed` is the actual acquired unsigned value. Do not merely
echo `systemSeconds` as the seed. Post depth, score, SearchID, PV and virtual
elapsed time remain part of conformance.

Only completed ordinary searches with at least one root move are in this
diagnostic's current domain. This does not define seed behavior for terminal
positions, aborted preparations, solve, pondering or analysis. Command
validation does not replace the larger missing legality/protocol specification.
Errors, timeouts, nonzero or signaled exits are not matches.

This is an opt-in test control. Normal production behavior continues to acquire
system time naturally; a production fixed-seconds setting is not required.
Explicitly fixing the seed itself is a different diagnostic capability.

## Test composition and limits

Fixtures compare complete real searches under zero, an ordinary nonzero value,
the high-bit value and all-ones seconds. They cover repeated/deeper/shallower
searches, `undo`, game reset, personality changes, both root colors, middlegame
history and a sparse ending. Prefix and fresh-session controls distinguish
prior activity from position alone. All-ones seconds plus accumulated work
exercise unsigned wrap to a small seed.

Original-side observations establish one acquisition per covered search and
seed retention through every observed root mixer use, alongside exact moves
and complete post trails. This is not universal lifecycle coverage: additional
search modes, interrupted searches, empty roots and fallback acquisition paths
remain open. Neither frozen-seconds nor fixed-seed tests claim anything about
the real-world distribution of seeds, clock-source resolution, or playing
strength.
