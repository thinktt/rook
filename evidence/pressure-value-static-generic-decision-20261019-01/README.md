# Advance shared static pressure lookup40 to own PGO

Generic fixed70 independently sums13.9486585→13.8302790s in whole-native CPU case medians:0.848680%lower,6/7lower,worst1.000070128. The predeclared rule passes. All70 strict live/original offline replays and native wait4/image/affinity/raw checks pass;14warmups and56measured samples retained. No retry/outlier deletion. Native focused2 passes; full185/117/54/wire/games not run.

The complete actual pressure body uses a named256-byte static object and direct ray/knight lookup, no inner memcpy; frame0x58→0x48. The knight load remains a cost risk. Static code observations do not establish dynamic savings. Source72graph216c8f51 changes only activity.rs from retained37. Generic imageadbf66a3 remains7047048B/0555, archive d352485b verified72 files. Actual pilotd02dd4/session72513→90d6a4/0; independenta36e78/0 with70 original replays and zero additional engines.

Advance only to fresh source-matched PGO training/remerge/use and its separately frozen comparison against retained37 own-PGO54be6552. No generic gain transfers, no production adoption or broad qualification is authorized by this decision. Root stays37. All original samples and source/build/backend evidence remain intact.

CPU15 whole-window ticks: 0nonidle/15071idle/0iowait; no continuous host exclusivity or pervariant attribution. Engine14/helpers0-5,8-13. All434 input pins remain stable.

|Case|37generic median s|40generic median s|40/37|
|---|---:|---:|---:|
|profile-01|1.0537815|1.0449425|0.99161211|
|profile-02|0.7362450|0.7217300|0.98028510|
|profile-04|4.4418800|4.4421915|1.00007013|
|profile-05|2.5067080|2.4316130|0.97004238|
|profile-29|0.2486135|0.2448445|0.98483992|
|profile-35|4.5680270|4.5565965|0.99749772|
|profile-08|0.3934035|0.3883610|0.98718237|
