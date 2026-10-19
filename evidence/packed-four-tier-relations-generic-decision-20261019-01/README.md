# Park packed relation experiment38

The frozen generic comparison sums 13.8680260s for retained37 versus 13.9646995s for38 in whole-native CPU case medians: **0.697096% higher**, with 1/7 lower medians and worst ratio 1.0127366397. Aggregate<=0.995 and>=5 lower both fail; worst<=1.02 passes. Park this exact decoder without retry, retuning, PGO, full186/117/54/wire/games or promotion. Production stays37.

Source72 graph66e553f1 changes only influence.rs and relation_table.rs from37; all old185 test bodies remain exact. Offline exhaustive pair/tier/exclusion proofs and two focused native controls pass. The other native tests were not run. The safe decoder preserves King dispatch before the opponent-zero shortcut; no unsafe conversion, state growth, charge change or consumer API edit is introduced. The source archive is reopened against all72 exact hashes.

Actual generic backend emits one65536-byte table instead of262144 bytes, with net rodata-196584B and text+368B. Observed activity/material/priority/full/ordinary/Q/root reservations stay equal. Numeric activity consumers add safe enum reconstruction with real conditional branches or conditional moves; predicate consumers specialize. This provides a plausible cost to investigate, not dynamic branch/cache attribution or proof of why this trial lost. No PMU was collected.

Generic image287f7d6b is6850880B/0555 and remains at the named local build path. The exact generic37 control isf8343eda. Both use thinLTO/O3/CGU1/defaultx86-64 with matching Cargo/tools/compiler/config; no PGO profile was used. No result is transferred to either production PGO image.

All70 fresh lifetimes pass strict live/original offline replay and independent native wait4/raw/PID/affinity/image checks:14 excluded warmups and56 measured samples, four alternating samples per variant/case. Pilot71423d/session77145→400c5d/0; independent reconciliation6bc6eb/0 invokes70 original checks and zero engines. All479 immutable inputs and both images stay exact. Helpers use0-5,8-13, engines14. All270 selected Herdr/Codex threads were already on housekeeping CPUs; zero changed. CPU15 whole-window counters record 0 nonidle/15083 idle/0 iowait ticks. Point observations do not establish continuous host exclusivity, statistical significance or final qualification.

|Case|37 generic median s|38 generic median s|38/37|
|---|---:|---:|---:|
|profile-01|1.0458410|1.0591615|1.0127366|
|profile-02|0.7325965|0.7297330|0.9960913|
|profile-04|4.4251405|4.4714080|1.0104556|
|profile-05|2.4754320|2.4839175|1.0034279|
|profile-29|0.2480745|0.2494670|1.0056132|
|profile-35|4.5511380|4.5806065|1.0064750|
|profile-08|0.3898035|0.3904060|1.0015457|

The mandatory117/12-game/full54 successes described elsewhere belong to retained37. This rejected38 trial did not run them. Its source, build archive, generated payload, bounded backend evidence and every original timing sample are preserved. Final37 performance/domain qualification and the external3288-game gate remain open.
