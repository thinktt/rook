# Current candidate25 instruction attribution

The exact delivered production binary `51529ceb` completed one fixed profile-35 and one profile-08 under Callgrind 3.24.0. Both match the unchanged released strict oracle and the complete stdout/stderr bytes of this same artifact's earlier strict54 run. Independent offline verification rechecked every pinned source, profile, tool and public input, raw output, tool exit and both original checkReplay calls. There were no retries or new builds.

Profile-35:45,762,253,122 simulated user Ir. Profile-08:3,967,850,732 simulated user Ir. These cover complete simulated process lifetimes, including startup and shutdown. They are not hardware PMU retired instructions, cycles, CPI/IPC or native CPU timings.

Engine simulation used CPU14; helpers used0-5,8-13, with no owned sibling15 work or claim of exclusive host ownership. point-placement.json records one live descendant/image/affinity observation. Build/native46/tools23 source is bound to the exact production receipt at both archived and absolute compilation roots. The immutable handoff executable remains unchanged.

Function tables use exclusive attribution and threshold99. displayed-function-contexts.json groups only the disjoint displayed file/function contexts and retains the unshown remainder. Inlining can attribute several conceptual operations to one machine owner; source subsets must not be added again to their enclosing owner. Actual call counts are not inferred from instruction counts.

The inherited driver's relative src/* annotations returned exit0 but no collected source information. Those original16 outputs remain unchanged. The raw profiles and function tables are valid. Separate absolute-source annotations at ../candidate25-callgrind-absolute-annotation-20261018-01/ correct only offline source matching; all16 have actual source rows, exit0/empty stderr and stable pinned source/profile/tool bytes. That receipt explicitly records the original no-data reports. No native profile was rerun.

The largest grouped displayed owner in the heavy case is activity::compute (about21.90% of simulated instructions); move generation and recursive ordinary search are also material. This is prioritization evidence, not an estimate of removable work or native speedup. A separate focused checker-prefix review will decide whether the known-unchecked full-generation hypothesis warrants experiment26. Evaluation-basis sharing and compact stop propagation remain unselected alternatives.

Reproduce with the pinned driver/plan in ../candidate25-callgrind-preparation-20261018-01/. Preparation verification requires the actual completed Vic54 terminal and same immutable engine/build/source identity. This is diagnostic evidence only, not whole-corpus performance or gameplay qualification.
