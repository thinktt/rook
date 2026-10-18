# Unusable clock-sampling attempts

These gprofng2.44 attempts are retained as failed diagnostic experiments.
The first wrapper used `-F off` and followed only its launching shell, yielding
no meaningful native samples. `-F on` followed the native executable and passed
the public profile-01 replay comparator, but the collector reported the timer
period changing from1000 to0 and explicitly marked its samples unreliable.
A direct native launch and a separate busy synthetic control reproduced that
warning. No percentage from these tables is used as hotspot evidence.

Raw `.er/` data remains local and ignored. `raw-experiment-files.json` binds its
retained bytes without publishing captured collector environment metadata.
Text reports, stderr, comparator results and launcher receipts are retained.
The first launcher's earlier source revision is not closed by the current tool
source; its launcher hash is recorded and its result is unusable regardless.
This experiment does not establish a working CPU-time sampler or PMU observer.
