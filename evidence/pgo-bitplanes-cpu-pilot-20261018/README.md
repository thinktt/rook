# Persistent bitplanes — independently trained PGO trial

The candidate f4a2f8bf1ca752f275b24c952c4529084d66ffb6ee7148c889a0be8b4b5f5a85 has its own54-case compiler profile, exact source archive, all54 strict replays and eight live interruption fixtures(24searches). No missing-function/profile warnings were emitted. A retained dead-code warning concerns the local-supply constructor, unused in this persistent production binary. Instrumentation timings are not performance samples.

All60 CPU lifetimes are independently reconciled:12 excluded warmups and48 measurements over six unchanged cases. Every native exit, strict comparator result, source/input/image hash, actual native PID/task/CPU14 observation and wait4 sample remains. Four samples per variant/case use alternating AB/BA order. Own lead/client/helpers are confined to0-5,8-13; CPU15 is unused by owned work. These are point observations with no continuous host/guest exclusivity claim.

| Case | Baseline1dc996b2 median CPU(s) | Persistent trial median CPU(s) | Trial/baseline |
| --- | ---: | ---: | ---: |
| profile-01 | 1.2467750 | 1.1893720 | 0.953959 |
| profile-02 | 0.9454175 | 0.7822500 | 0.827412 |
| profile-04 | 4.9714180 | 4.9164160 | 0.988936 |
| profile-05 | 2.7534725 | 2.7194675 | 0.987650 |
| profile-35 | 5.0603740 | 4.9278705 | 0.973815 |
| profile-29 | 0.3193140 | 0.2699280 | 0.845337 |

Sum of six medians: baseline15.2967710s, persistent14.8053040s; ratio0.967871193, 3.212881% lower. In all six cases, the observed trial maximum is below the observed baseline minimum. All samples remain; this finite observation is not a confidence interval or inferred noise tolerance.

Decision: select persistent Position160/Node176 for source integration, followed by integration checks and a canonical repository PGO build/training. The local generic counterexperiment and all source/ownership caveats remain in ../bitplanes-20261018/. This does not qualify whole54/12 cost, calibration, PMU, final resource/uncertainty profile or full gameplay. No universal speedup is inferred.
