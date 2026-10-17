# External native policy checks

All884 generated Rust test cases passed, with11,136 supplied queries inside
the selective-depth cases. The engine library performs every chess/policy
calculation. Fixture expected values compile only into an external test crate;
they are not engine source or a runtime answer database.

| Operation | Source cases |
| --- | ---: |
| Selective depth | 178 |
| Priority permutation | 26 |
| Capture preference | 50 |
| Ordinary candidate order | 120 |
| Material threat | 164 |
| Move extensions | 288 |
| Cutoff memory | 58 |

The checker emits controlled native calls from the released data, comparing
the supplied expectations. It does not recompute the chess rules in Python.
Profile packing and move-descriptor conversion are representation bridges.
Capture equality groups and preferred flags are projections of native computed
magnitudes. Candidate-order tests use actual placement influence and supplied
root value/square tables. Extension tests replay legal history and compare the
generated order and every extension. Threat tests repeat actual calls and
compare their accumulated relation charges. Memory tests compare each full
history/killer snapshot, including reduction and reset.

Eight influence-operation cases in the source files are explicitly unsupported
by this policy checker. The run does not qualify transport/input validation,
all diagnostic output fields, consumer call placement, whole-search equality,
timing, gameplay or final conformance. The current search evaluator is partial.

`receipt.json` records fixture, generator, generated test and engine-source
hashes, case mapping, compiler, command, status and unmodified-source checks.
`verified-test-source.tar.gz` preserves exact tested Cargo/source bytes, checked
after archiving; raw test output is retained. The policy, ordering, influence,
position, types and root-material helper source hashes still match the frozen
ordinary build. One later native tail-ordering regression changes only its
test module. Earlier generator attempts remain local: the first failed to
compile because a generated closure shadowed its move helper; no engine policy
change was required for the subsequent884 passes.

Reproduce in a fresh directory with:

```sh
taskset -c 0-5,8-13 python3 tools/check_policies.py --output evidence/new-policy-check
```
