Completed independent own-PGO reconciliation: all70 normal native lifetimes,14 excluded warmups/56 measured, and all70 original checkReplay records passed. Actual2e130a/0; no engine reruns. Exact control6a5ce6e2 versus activity candidated5ee1f3f, each using its own-source profile.

| Case | Control median [min,max] CPU s | Candidate median [min,max] CPU s | Candidate/control median | Full ranges |
| --- | ---: | ---: | ---: | --- |
| profile-01 | 1.0148715 [1.006033, 1.018855] | 1.0001730 [0.998871, 1.007444] | 0.985516886 | overlap |
| profile-02 | 0.6696420 [0.666850, 0.673086] | 0.6651280 [0.662509, 0.669844] | 0.993259085 | overlap |
| profile-04 | 4.3042870 [4.290881, 4.387664] | 4.2604350 [4.238681, 4.274039] | 0.989812018 | candidate-below |
| profile-05 | 2.3765490 [2.366633, 2.385113] | 2.3245655 [2.322620, 2.328692] | 0.978126477 | candidate-below |
| profile-29 | 0.2294495 [0.228088, 0.229937] | 0.2303845 [0.227261, 0.231084] | 1.004074971 | overlap |
| profile-35 | 4.3889200 [4.368918, 4.421001] | 4.3312855 [4.315853, 4.350559] | 0.986868182 | candidate-below |
| profile-08 | 0.3606240 [0.360192, 0.361114] | 0.3576180 [0.356166, 0.360972] | 0.991664448 | overlap |

Sum of seven medians: control 13.3443430s, candidate 13.1695895s; ratio 0.9869043009461013, 1.309569905% lower. 6/7 case medians lower; worst case ratio 1.004074971. All four measured samples per variant/case were retained; displayed ranges include their full minima/maxima. Exact floating-point values and every sample are in independent-reconciliation.json.

Frozen execution-plan rule satisfied: Consider source integration only if sum-of-seven-medians candidate/baseline<=0.995, at least5of7 case ratios<1 and none>1.02. Preserve/reconcile every sample/range; no outlier removal or favorable-case reruns. A successful exploratory pilot supports further integration validation, never final qualification. This supports considering source integration and further validation; it is not automatic adoption or final qualification.

Whole-suite CPU15 tick deltas: [0, 0, 0, 14448, 0, 0, 0, 0, 0, 0]; nonidle excluding iowait=0, idle=14448, iowait=0. No per-variant attribution or continuous host/guest exclusivity follows.

Current scope: fixed custom cases01/02/04/05/29/35/08, direct whole-lifetime native wait4 CPU including the disclosed small Python child pre-exec prefix; protocol pipes inherited without relay. CPU14/image/single-task placement is a point observation. Independent source/artifact/tool/input hashes, every argv/normal exit, accounting arithmetic, repeated schedule, four-sample ranges/medians and exact frozen rule passed with stable dependencies. No outlier removal, confidence/significance, PMU, wall-ratio, generic timing/profile transfer, full54 CPU/full-game or final-qualification claim. This offline analysis launched no engine/build/profiler/timing/Git command.

Result SHA256: `99dd586c3cdf06fcb91420287af703c1c10c46de54c133c16ca3027e11991127`. Actual verification terminal:2e130a/0.

Historical preparation text (superseded status; preserved for provenance):

Prepared only. Neither helper has been parsed/imported/executed. Parent source review plus a NEW review-clearance.json must precede execution. That file must set parent_review_complete:true, pilot_actual_terminal:"e40bd2/0", and helpers:{absolute helper path:sha256} for these two scripts. Run only under taskset0-5,8-13 and HOME TMPDIR.

Mechanical adaptation from the accepted generic70 scripts is exposed completely in adaptation.patch. PRE is activity-value-inputs-pgo-cpu-plan-20261018-01. Immutable plan.json remains the original pretraining declaration; execution-plan.json is the actual runner plan bound by clearance.plan_sha256 and copied as RUN/plan.json. Both declaration and execution plan are checked for identical cases/schedule/gates/repeat/advance semantics, linked by frozen_declaration_sha256. The script's literal rule exactly matches execution-plan.advance_rule: consider source integration only if aggregate<=0.995, at least5of7lower, none>1.02. A passing rule supports further integration validation, never final qualification or automatic adoption.

Artifacts are distinct own-source PGO images: baseline6a5ce6e27b74490e623fbb705f70c770ec12ff7e88f761fb0c7119ca2aee4a50 and candidated5ee1f3f7258f152c0a9c50664855c46f6b631e611a85bdfdae07f509654decc. Pilot actual30708/4e51ca→e40bd2 exit0. No generic timing/profile/qualification transfer. Existing frozen PGO/source/compiler/profile proof is bound through the original launch-clearance dependencies.

All70 existing raw comparator records are rechecked through original checkReplay, with unchanged14warmups/56measured, all wait4 arithmetic/argv/exits/image/affinity/one-task checks, all four samples/ranges/medians, seven-case aggregate, whole-suite CPU15 ticks and repeat rules. The sole subprocess is offline Node importing checkReplay; no engine/build/profiler/timing/Git or new corpus work. Strict actual stdout/stderr and exits are retained; no separate stdin byte stream exists. One point observation is not continuous descendant/exclusivity proof. CPU15 has no per-variant attribution. No outliers removed, confidence/significance/PMU/wall-ratio/full54/full-game/final qualification claim. Failures preserve original attempts and stop output.
