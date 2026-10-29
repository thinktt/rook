# Strong completion epoch: parked generic trial

[Report](report.md), [results](results.json), [all ranges](case-ranges.csv),
[concise closure](closure.json), [saved lowering](lowering.json),
[actual layout](production-layout.json), [plan](plan.md), [policy](policy.json),
[ownership/source proof](ownership-proof.md).

Park unchanged per imp2-lead. New3 sums7.365883s versus d71 mode3 7.342935s
(+0.3125%); all three medians lose,43 ranges separated,35/08 overlap. Inline
improves0.1787%, with all ranges overlapping.32affected/43reuse/14CLI2fallback/
actual832/lowering/48replay560posts+4idle pass first attempt. No PGO or retune.
Provisional c242/profile1a81, genericd71 and all predecessors stay preserved.

Normal done lowers to memory xchg then flag mov; terminal exchange stays.
The new normal notification body is inline, versus an old helper call; stack/
register/code changes count with the complete variant. Seven stages exit0;
52 comparison/idle receipts plus separate layout are terminal. Original pipeline
310.436s, terminal audit343.026s; no repeat/reset or source repair. Quiet window
released; native execution stopped. No adoption/qualification or extra lane.

Source: /home/legolas/rook2-experiments/workspaces/completion-epoch-20261029-01.
Raw builds/runs: /home/legolas/rook2-experiments/completion-epoch-20261029-01.
Preserve c242/profile1a81/d71 and all predecessors. source.patch is zero-context;
restore against exactbase with git apply --unidiff-zero.
