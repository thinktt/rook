# Matched bitplane storage trial — generic development evidence

Both variants pass131 library tests plus two development-CLI tests and all54 strict public replays. The query/projection kernel and Boolean consumer scope are identical; ordered checker identities and quiescence mailbox reuse retain their original code. Root native source is unchanged.

Persistent Position160/Node176 artifact: dc26cf6dcf8a65dc5ecab82bed34bfdb54dedf1448324cd54f12fb8a2d407422.
Local Position128/Node144 artifact: 6d4d6e865f094f9993135b473c9d2822c98baa4f9a3fce402051b50225f70ca6.
Baseline generic artifact: e734494836337f86d84fe166ae4952d192f3dc07346d482d5ecbb3a22831260c.

All90 lifetimes are independently reconciled:18 excluded warmups and72 measurements, with four samples per variant/case. Exact native wait4 receipts, strict comparator reports, source/build archives, before/after input hashes and all samples remain. Helpers, including verified own lead/client threads, use0-5,8-13; native measured children use14. No owned build, other engine or profiler overlapped the CPU pilot. Point observations do not establish continuous exclusive guest/host ownership.

| Case | Baseline median CPU(s) | Persistent median CPU(s) | Persistent/base | Local median CPU(s) | Local/base |
| --- | ---: | ---: | ---: | ---: | ---: |
| profile-01 | 1.3445090 | 1.2966695 | 0.964419 | 1.3468640 | 1.001752 |
| profile-02 | 1.0362165 | 0.8953785 | 0.864084 | 0.9251340 | 0.892800 |
| profile-04 | 5.4755250 | 5.4613715 | 0.997415 | 5.5916920 | 1.021216 |
| profile-05 | 3.0129430 | 2.9842780 | 0.990486 | 3.0624200 | 1.016421 |
| profile-35 | 5.5099125 | 5.4314785 | 0.985765 | 5.5670885 | 1.010377 |
| profile-29 | 0.3479525 | 0.3012960 | 0.865911 | 0.3134165 | 0.900745 |

Sum of case medians: baseline16.7270585s, persistent16.3704720s, local16.8066150s. Persistent/base=0.978682056 (2.131794% lower); local/base=1.004756156 (0.475616% higher); persistent/local=0.974049325. All six persistent case medians are lower; profile04 ranges overlap substantially and profile05 nearly touches. No sample is discarded and no confidence/noise tolerance is inferred.

Decision: advance persistent to its own compiler-PGO training/build/regression and matched PGO CPU trial against1dc996b2. Park this explicit local-supply strategy. No production representation change is adopted from these generic samples alone. This is not a claim about every possible local strategy or a qualified54/12 reference comparison. Final resource/observer/uncertainty/calibration and PMU limitations remain.
