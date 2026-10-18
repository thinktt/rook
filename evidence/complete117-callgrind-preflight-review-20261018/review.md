# Bounded source-only Callgrind preflight

Reviewed 2026-10-18 while parent CPU12 session 96272/PID 480262 remained live. Only small source/text reads and this new memo were performed, pinned to CPUs 0-5,8-13. Shared preparation files were not edited. No scripts were parsed/imported or executed; no engine, profiler, tool/version process, hash, archive, Git, build, binary or annotation scan was run.

## One concrete launch blocker

`complete117-callgrind-preparation-20261018/profile.py:44` passes `callgrind_annotate --version` to the ordinary success-only `run`. That function asserts return code zero at line 39 and returns stdout at line 40. The installed public Perl source `/home/legolas/.local/imp2-tools/valgrind/usr/bin/callgrind_annotate:248-250` handles this option as:

```perl
if ($arg =~ /^--version$/) {
    die("callgrind_annotate-$version\n");
```

Its version is declared as `3.24.0` at line 199. Thus the informational version string goes to stderr and termination is nonzero; the current driver fails before the first case at line 48. The recipe cannot reach fixed35 then08 unchanged. This conclusion is from tool source, not an executed version probe.

Parent selected the following narrow correction; this review does not apply it:

1. Extend `run(argv, stem, cwd=source, expected_exit=0, output_stream="stdout")`. Record `stem`, declared `expected_exit`, actual return code and actual child-return observation; assert actual equals declared.
2. Keep every normal command at expected zero. Only the named `annotate-version` call declares expected 255 and selects stderr. Require empty stdout and exactly `callgrind_annotate-3.24.0\n` on stderr.
3. In `verify.py:11`, permit only that named version command to have declared/actual 255; every other command must have declared/actual zero. Do not introduce a generic nonzero waiver.

Exit 255 is the selected Perl informational-probe expectation, not an observed runtime result. If the later actual probe differs, preserve its failure before any bounded repair. Its exception must not make either engine or annotation-generation errors admissible.

## Released-schema and closure checks

No second definite launch/schema blocker was found in the bounded text review.

- Released `replay-check.mjs:61-64` accepts exactly the constructed `--case ID -- COMMAND...` form. Its `:29-30` appends the oracle mode to the command, so the Valgrind wrapper receives the released work-clock arguments without the adapter recreating them. The retained oracle header specifies `--work-clock=kingwcr` and `--work-clock-post=work`. Both selected IDs exist in released workloads (08 at line 311, 35 at line 6671) and oracle (08 at 273, 35 at 3181).
- Released rows use `case`, `pid`, `stdout`, `stderr`, `exit`, `error`, `complete`, `truncated`, and `discardedObservedBytes` (`replay-check.mjs:29-30,41,55-59`). The driver uses those names correctly at `profile.py:50-56,64`; no invented call count or obsolete schema was found. Reports expose `selectedCases` and `results` at released `:69-73`, matching both scripts.
- `recheck.mjs:4,7-9` imports and calls the released `checkReplay`, rather than copying its post/work oracle. The checker verifies ordered acknowledgments, posts/work, selected move and complete shutdown records at released `:13-24`. The imported `benchmark.mjs` contributes `parsePost` and imports only Node builtins. The plan pins both JavaScript files and both JSON inputs at `plan.json:89-94`.
- The driver additionally compares collected raw bytes to the current exact own-PGO strict reference (`profile.py:51-55`), and the independent verifier repeats the comparison against saved raw files (`verify.py:16-18`) before running the original checker offline (`:25-28`). The offline checker never calls `runReplay` or launches an engine.
- Parent source correction at `profile.py:17,20-24,65-66` binds archived AND actual compilation-root source/tool bytes before/after. This addresses absolute DWARF paths without claiming the annotator exclusively opened the archived tree. The comment at line 60 is stale shorthand; the receipt and parent-source-review correctly disclose both roots. No runtime code change is required for that comment.
- Source archive membership, exact build/image/reference pins and actual tool/preload identities are checked only at later authorized runtime. They were not independently hashed or opened as archives now. `parent-source-review.md` already requires post-window syntax and runtime admission checks.

## One limited derived-output closure gap

`profile.py:39` records argv/exit but no output names or digests for annotation commands. `:64` binds only each raw profile and log; `verify.py:19-23` independently validates those files, but never reads or binds `*-functions.stdout` or the four `*-lines.stdout` outputs. Consequently the current independent pass establishes raw/profile/source closure, not unchanged derived annotation text. The memo/receipt must not describe those annotations as independently reconciled.

This does not prevent either simulation or raw/profile verification. If the intended provenance includes saved annotation bytes, the minimal addition is to record each command stem and stdout/stderr SHA256 after close, then have the verifier rehash those exact outputs (including the version probe outputs). No second annotation execution is necessary. Confirming that focused source rows actually carry useful attribution still requires later inspection of the resulting saved text; source-only review cannot establish that now. Threshold99 function output is explicitly incomplete, not an exhaustive hot-path census.

## Deferred boundaries

The fixed once-only case order and no-repeat policy are present in `plan.json:3-6,131` and the driver loop. Released finite guards remain 30s setup/900s search/5s cleanup (`replay-check.mjs:27,71`); source review cannot guarantee these cases finish under simulation. Profile size is checked only after return (`profile.py:57`), as already disclosed. Whole-lifetime `Ir` is simulated attribution, not PMU retirement or CPU timing. Function totals and source/inlining rows overlap and cannot be added as independent costs.

All owned tool calls for this review were ordinary bounded text reads and one memo write. No owned long-running process was created. Actual final write terminal is reported separately to parent; all owned work is closed.

## Corrected source follow-up

After this memo was drafted, parent applied the version contract source-only (reported actual f6644d/0), preserving both original files as `*-before-version-contract.py`. I read the corrected small scopes, without parsing or executing them: read terminals ca6a73/0 (`profile.py`), 46a5fd/0 (`verify.py`), bfd468/0 (parent correction note). The wrapper now records stem and expected exit, selects stderr for the version call, and requires exact version bytes/empty stdout. The verifier requires exactly one named version command, exact annotator/option argv suffix, declared/actual255 only there, and declared/actual0 everywhere else. No concrete new defect was found in those corrected scopes. The inferred255 expectation remains runtime-unverified; the earlier launch blocker is addressed by source, not yet demonstrated by execution. The limited annotation-output closure observation above remains unchanged and is not a second launch blocker.
