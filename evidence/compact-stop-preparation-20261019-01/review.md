# Experiment34: current25 compact recursive stop source proposal

Source-only, unparsed/unformatted/unbuilt/unrun. No execution authority is granted. The prepared current25 trial is frozen at source69 graph `7cd62441a19950f20ba5bdc136bb5d4b558dbcbb02b1ededb69b13cf76f2cf34`. Changed files are exactly `src/{engine,ordinary,quiescence}.rs`; other66 members, including tools23, are byte-identical to retained25. Production remains25.

The historical proposal supplied the design and19 uniquely anchored changed hunks, not replacement files. Engine and Q historical bases exactly equal current25. Historical ordinary differs only at the two adopted projected-bit checks; both current hunks are retained. `historical-hunk-rebase.json` records every old/new hunk hash and unique current anchor. No26–33 source, cache, field or numerical optimization is composed.

## Representation and actual owners

Public Stopped remains text-exact, including NodeLimit(u64), every distinct stop reason and HostIo(std::io::ErrorKind). Public Search/Q/ordinary-facing signatures and ordinary Error remain unchanged. A crate-private InternalStop removes only the redundant internal NodeLimit payload. It retains native ErrorKind without encoding/truncation and keeps WorkPoll, IIO, HostStop and HostAbort distinct. It introduces no Search, Node, Position, Host or retained field.

The actual shared `work_clock::charge_search_unit` is unchanged. New `charge_node_compact` calls it with the same `&mut self.stats.nodes,self.limits.nodes`, then invokes the unchanged work_poll only after a credited positive4096 boundary. The two rich-to-compact conversions exist only at these calls. No limit/increment/poll arithmetic is cloned. The generic primitive still accepts arbitrary counters; units5/limit3 returns public NodeLimit3 without changing5.

NodeLimit can originate only in that primitive with the current configured Some limit. work_poll returns WorkPoll, HostStop, HostAbort or the full native HostIo kind; it cannot produce a different budget. begin_sequence installs Search.limits before traversal. Recursive visits, history pop, scout retry, IIO and Host clock/post commands do not change it. Therefore every outward compact NodeLimit is reconstructed with **self.limits.nodes.expect(...)**, never stats.nodes or a guessed fallback. A new future producer tied to another budget owner would violate this invariant and must not be added silently. This private conversion is not offered as a replacement for the generic primitive's broader contract.

## Complete recursion and boundaries

| Shared worker / boundary | Carrier and preservation |
|---|---|
| `visit_ordinary_compact<ALLOW_IIO>` | All null/main/scout/retry calls stay compact with the same const. Both ordinary-to-Q handoff and shallow mate/frontier use visit_q_compact. |
| `ordering_phase_compact<ALLOW_IIO>` | Both initial and tail calls, and all IIO children, stay compact. False capability increments its original phase counter then returns the same IIO reason before passes/children. |
| `visit_q_impl_compact<O>` / visit_q_compact | Observed and no-observer child recursion stay compact; the same shared body retains entry/leave guards, current scratch, prepared/lazy child timing, charges and history pops. |
| `visit_ordinary_impl<ALLOW_IIO>` | Existing root/fixed/timed callers receive rich Stopped after one outward mapping. Default visit_ordinary still selects true IIO. |
| `visit_q`, continue_subtree | Standalone/public Q receives rich Stopped through the existing wrapper. |
| `search_subtree_observed` | Maps compact failure at the outer observed boundary; stopped traversals still produce no invented successful leave/output. |
| charge_node and ordering_phase | Old test-facing rich-error wrapper signatures remain; their production workers use compact directly. |

The same code is generic over DIAGNOSTICS; no false-mode shortcut changes enforcement. Timed/session/first-iteration files are unchanged. ActualEffects still receives the public stop and treats only WorkPoll/HostStop/HostAbort as graceful; NodeLimit and HostIo remain errors. Existing Result cleanup and public formatting remain unchanged. A rich seed/start/publication io::Error channel is separate and is not converted by this patch.

`source-proof.json` verifies exact whole ordinary, IIO and Q worker bodies after reversing only worker/charge names and the one IIO carrier spelling. Thus arithmetic, windows, remembered policies, candidate order, current25 projections, successful-only scout retry, pop-before-error propagation and observer semantics are literally preserved. Search's field definition is text-exact; public Stopped is text-exact; work_clock and all other owners are byte-identical.

## Meaningful unrun falsifiers

The two historical test bodies are retained exactly, with only `compact_stop_` prefixed to their names for focused selection:

- `compact_stop_public_stop_recovers_configured_budget_even_when_counter_is_already_over`: first checks the independent shared units5/limit3 contract. Then actual selected/continued Q in D=true and D=false starts with configured3 and internal count5, requires repeated public NodeLimit3 and exact Debug form, no new work/history change, and the rich charge wrapper's same result. It would reject reconstructing the current counter.
- `compact_stop_timed_poll_io_kind_survives_compact_recursion_and_unwinds`: actual START timed ordinary/Q recursion with a Host command failure, separately PermissionDenied and ConnectionReset in both diagnostic modes. The first command Err happens before work_poll's Session-control unwrap. It requires one command read at charged4096, exact outward HostIo(kind), root history restoration and timing=None. Large clock bounds avoid the normal elapsed stop;8192 budget exceeds4096 and iteration capacity6 is intended to permit reaching that poll. Actual reachability remains to be checked by execution, not assumed passed.

No conversion-table mirror or extra arithmetic test was added. Existing178 bodies are byte-identical, including observer-resource error, initial/tail false-IIO, diagnostics parity, interrupted history and timed cleanup witnesses. Q's entire old test module is recovered by removing exactly the two new declarations; ordinary's old module is intact; every other test owner is unchanged. Expected declarations are180 total (178lib+2dev), not180 executed tests. Parent can filter `compact_stop_` before timing.

## Risks and next gate

This is a representation hypothesis. It does not prove a smaller Result, register return, sret removal, fewer instructions, spill/frame neutrality or CPU improvement. ErrorKind's actual layout, success/error tag packing, conversion at the unchanged rich charge seam, wrapper inlining and false/observer monomorphs need actual generic WireHost backend inspection. Keeping the existing test-facing rich charge_node and ordering_phase wrappers can produce non-test dead-code warnings now that production bypasses them; no warning-suppression or cfg/API change was introduced speculatively. Parent may review that explicitly before a separate source revision or build.

The parent proposal permits source review first, then separately selected generic/backend and focused checks. No helper/parser/compiler/native/profile/binutils/Git/archive action occurred here. The missing historical review.md source read failed74e0cf/1 and was corrected by reading its actual rationale/parent review, without source mutation. Initial metadata freeze d1a5d2/1 rejected an ambiguous let-p/target anchor before writing final freeze outputs; the retry scoped it inside the unique worker and passed31d4b6/0 without source changes. Both failures are retained. Runtime speed control/readback is unavailable; no verified-speed claim is made.
