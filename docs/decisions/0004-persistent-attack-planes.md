# Placement-owned attack planes

Status: adopted in source;133 native tests and25 adapter units/1214 external
cases pass after integration. Canonical PGO build/timing qualification is pending.
Date:2026-10-18. Imp2 owns this decision. The bounded independent critique in
`evidence/bitplane-preparation-20261018/archive.json` identified the required
constructor audit and matched storage comparison; it was not an approval gate.

The Position now owns four exact Piece-tag u64 planes alongside its mailbox and
chronological lists. Position grows128to160 bytes, alignment4to8; Node grows
144to176. Copy-child ownership, retained evaluation and all logical identities,
ordering, work charges, root/context and shared-state lifetimes remain unchanged.
The planes provide a Boolean geometric attack/projection kernel for current
in_check and ordinary generation safety fallbacks.

The unchanged ordered find_attackers<2>/check_routes still owns capped checker
identities. Quiescence keeps its existing projected-mailbox reuse for check
classification and own-king safety. No second projection is introduced there,
and no universal64to32-byte projection saving is claimed. Persistent maintenance
and extra copies apply to all placements, including temporary/reply/null,
protocol/history and count-only material hypotheticals, not just searched children.

Construction/recompute establishes plane/mailbox coherence after direct board
construction. The existing placement setter XORs actual old/new tag differences,
including captures, promotion, castling and joined EP non-pawn/king victims.
Null preserves absolute piece colors. Independent validation decodes each tag
against the mailbox; it does not reuse the updater. The terminal king-victim
path does not acquire a new normal king lookup. Geometric attacks still include
pinned enemies and ordinary blockers; evaluation influence remains separate.

Both supply strategies use the identical query/projection kernel and consumer
scope. The local variant builds from chronological lists on demand, lazily
reuses a view within one immutable generation, and builds fresh singleton
in_check/EP/castling views. Both pass131 library+2 CLI tests and all54 strict
replays. Checks cover all13 tags/replacements,10000 broad constructed placements,
Boolean queries, projections/actual children/null and special/joined transitions.
The forced-projection oracle keeps the old mailbox safety kernel but shares
the pseudo-candidate producer; it does not independently prove completeness.

| Complete generic six-case pilot | Sum of case CPU medians(s) | Ratio to baseline |
| --- | ---: | ---: |
| Mailbox baseline128/144 |16.7270585|1.000000000|
| Persistent160/176 |16.3704720|0.978682056|
| Local128/144 |16.8066150|1.004756156|

All90 lifetimes are independently reconciled. This parks the explicit local
strategy tested here; it does not rank every local implementation or an
untested local PGO build. Persistent then received its own54-case instrumented
training and profile-use build. Trial artifactf4a2f8bf passes54 strict replays
and eight interruption fixtures/24 searches, with zero missing-profile warnings.

The matched PGO pilot retains60 independent lifetimes,12 excluded warmups and
four measured samples per variant/case. Baseline1dc996b2 sums15.296771s;
persistent sums14.805304s, ratio0.967871193(3.212881% lower). All six observed
trial maxima are below their respective baseline minima. This is a finite
observation, not a confidence interval or universal noise allowance. Exact
samples, source/build/profile identities and independent raw reconciliation
are in `evidence/pgo-bitplanes-cpu-pilot-20261018/`.

This evidence supports source integration and canonical validation. The canonical
repository will train/build its own PGO artifact at its declared crate path;
trial timings do not transfer to a different binary hash. Complete54/12 cost
qualification, current-artifact focused/continuity/full3288 gameplay, remaining
mandatory diagnostics, production audit and resource/observer/uncertainty/
calibration/PMU obligations remain open. A different measured kernel/layout can
replace this choice later; the unimplemented counts-guided mailbox control is
recorded separately without an inferred benefit.
