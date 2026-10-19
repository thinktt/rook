# Park experiment32 after its own-PGO timing test

Retain candidate25 unchanged. Generic table traversal passed its first timing gate, but its independently trained PGO image does not improve on retained25 PGO in the frozen seven-case comparison. Sum of case medians12.7554505→12.7859410s is0.239039% higher, with4/7 lower case medians and worst ratio1.011352. This fails the pretraining-declared aggregate<=.995 AND>=5 lower cases AND worst<=1.02 rule. No retry, sample exclusion beyond the14 declared warmups, full use54/eight-wire/full117/pre-gate, promotion or new external benchmark is selected.

Own-PGO32 d2fac478bb7ba45019421f082cca31a03b4b1516bb4a553fbacb4294e3a1a212 is compared only with own-PGO25 51529cebf24ad91b0cf86e4ae497bc32bb7ad7a819f8b300f8b86028326b254a. The32 source graph is3c8aeee3b726aa6de3edc1c2e7dde4fcc784c44b06616753ff83992b5d802e6a. Its fresh54 training passes both original live and independent offline replay;54 PID-bound raw profiles independently remerge byte-identically to89cd873f3b1b4f049571a28809ebb50c6885179548b819bcd95bf032959512e3. Use build records no selected missing/stale profile warning. Backend confirms the intended table traversal in both actual inlined pressure colors, with added code/register/check costs.179 same-source native tests pass separately; this is not a full117 claim.

All70 normal native lifetimes pass the original strict comparator, including14 excluded warmups and56 measured lifetimes. Independent reconciliation reproduces wait4 user+system arithmetic, single-taskCPU14 identity, hashes/inputs, schedule and all70 original offline replay checks. Preserve every four-sample range and median; no statistical-confidence or PMU claim follows. Helpers ran on0-5,8-13 and conflicting owned jobs were closed before the pilot. Point guest context does not establish exclusive host isolation.

|Case|25 medianCPU s|32 medianCPU s|32 vs25|Four-sample ranges|
|---|---:|---:|---:|---|
|profile-01|0.9658305|0.9767950|+1.1352%|separate,32 higher|
|profile-02|0.6346020|0.6298495|-0.7489%|overlap|
|profile-04|4.1191350|4.1300260|+0.2644%|separate,32 higher|
|profile-05|2.2866795|2.2852110|-0.0642%|overlap|
|profile-29|0.2141225|0.2121455|-0.9233%|overlap|
|profile-35|4.1910425|4.2124795|+0.5115%|overlap|
|profile-08|0.3440385|0.3394345|-1.3382%|separate,32 lower|

The isolated generic pilot's0.832364% improvement remains valid within its own window/build phase; it does not predict this own-PGO result or a whole54 speedup. Neither pilot establishes performance qualification. The exact25 external package and root69 production sources remain preserved. Actual pilotc7430d/session54398→54fb55/0; independent reconciliation8a4c50/0.
