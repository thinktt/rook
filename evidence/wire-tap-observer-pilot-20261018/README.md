# Controller byte-tap overhead: balanced complete-game pilot

Latest production PGO1dc996b2 ran the complete unchanged main-0168 unit24
searches per lifetime. Plain and tapped modes each have one excluded warmup,
then four alternating AB/BA measured repetitions:10 lifetimes/240 searches.
All strict game assertions, native normal exits, artifact/tool identities and
original byte/record reconciliations passed. Every result/file hash was then
independently rechecked. The tap retains120 external search intervals; zero
CPU tick deltas are explicitly unresolved, with no reciprocal rate.

`analysis.json` retains both CPU and wall sample sets and median ratios. The
observed median difference is small relative to overlapping ranges. This is a
development observer control supporting the reported-only game collection,
not a final observer tolerance, confidence interval or cross-host qualification.
Native wait4 includes a small child pre-exec prefix; the quantized go/move
intervals remain external boundaries and do not expose terminal N/R or PMU.
