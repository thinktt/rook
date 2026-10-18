# Static piece-kind activity kernels

Date:2026-10-18. Owner:Imp2. Status:adopt the exact measured specialization;
canonical artifact/profile verification remains separate.

The current instruction simulation identifies activity as a substantial source
cost. A private arithmetic-width experiment is essentially flat and remains
parked. This experiment instead exposes the already-known piece kind to the
compiler throughout destination traversal and piece scoring.

`compute` visits White then Black, and Knight/Bishop/Rook/Queen in the same
order as before. Four private const instantiations consume the same typed
chronological lists. Arithmetic remainsi64/u64. Targets, transparency, capture
preference, mark order, rounding and every semantic relation charge stay at
their existing owners. No cache, root/context change, retained-state extension
or Position/Node change is introduced. Test-only dispatch wrappers exercise
the same instantiations through existing private probes.

The main tradeoff is additional code: in generic builds, activity compute grows
from4890 to8975 bytes and total text grows4120 bytes. This is static size
evidence, not a performance prediction. All134 native tests,10,000 placements
against our prior independent coordinate implementation, and54 strict replays
pass for genericc946104a. The identical generic controle7168491 reuses its
already-completed strict replay, with that provenance explicitly recorded.

The fixed six-case generic pilot independently reconciles60 native lifetimes:
15.0116965s versus14.605204s in summed case medians, ratio0.972921615
(2.707839% lower). All six medians are lower; four finite observed ranges are
disjoint, with profile02/29 overlapping. This motivates an independently trained
PGO comparison rather than transferring the generic timing.

Own-profile PGOb8cee321 passes54 strict replays and eight interruption fixtures.
Its profile is produced by54 unchanged public training replays with all raw
profile/source/merge inputs independently verified. Against canonical8c4619a7,
the separate60-lifetime pilot sums13.7566335s control versus13.453188s candidate,
ratio0.977941878 (2.205812% lower). All six medians are lower; five observed
ranges are disjoint and profile29 overlaps. The ranges are finite observations,
not confidence or acceptance intervals. Original raw samples and actual terminal
receipts are retained in `evidence/pgo-activity-specialization-cpu-pilot-20261018/`.

Adopt only the exact measured `src/activity.rs`. The guarded integration records
all43 before/after native identities and establishes that this is the sole
changed source file. Rebuild/test the repository source, relink the diagnostic
adapter, train a fresh canonical profile and collect its own cost evidence.
The earlier8c complete54 CPU/focused results remain attached to that binary;
prototype timing, full12 costs or final qualification do not transfer.

Fresh canonical8d9dddc5 now owns verified54-case profile0da6d3b5,134 native
tests,54 strict replays/eight interruptions and the identical57-operation
adapter relink e31263ac(2868 cases/42 units). Its balanced60-lifetime pilot
gives2.052997% lower summed CPU medians than8c, with profile29 slightly higher
and overlapping. Its complete54 CPU collection independently reconciles216
lifetimes and sums81.131004s,0.852305% below previous8c;41 medians decrease and
13 increase. This supports the local adoption while leaving substantial whole-
engine performance and final qualification work. Prior gameplay is not transferred.
