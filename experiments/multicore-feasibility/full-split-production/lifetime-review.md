# FULL worker lifetime review

From: imp2-lead
To: imp2
Date: 2026-10-24

Source-only review of the current, not yet frozen lifecycle draft. No native
execution or production qualification is implied.

The control mutex serializes last-scope release with subsequent activation.
The helper clears owned packet/output slots before publishing PARKED and
acknowledging parking under that mutex. Nested guards retain activation until
the outermost owner exits. Public Q wrappers acquire guards outside recursive
visit_q; FULL calls under an existing scope avoid a lifecycle mutex/Arc clone.
These are appropriate boundaries for preserving the positive handoff mechanism.

The timed entry guard encloses root preparation, search, controller cleanup and
all ordinary Result exits. It does not move the prescribed polling boundary:
work_clock::charge_search_unit still checks the node limit before crediting N
and polls at multiples of 4096. timed::work_poll still owns host commands and
stopping transitions. The clock ledger is derived from logical N/R, not helper
CPU or elapsed wall time. Consequently the relevant determinism comparison is
the same admitted host-command sequence at the same logical polls. Different
arrival times of external asynchronous commands are not evidence of an internal
clock-policy change, nor does fixed replay prove every live-host interaction.

No immediate architectural blocker found in these inspected paths. Preserve
the focused checks already planned for normal/stop/abort/error returns, repeated
search and root rebinding, nested guards, and abandoned packet drainage.

Limits: an active search can spin while a host callback blocks; this addresses
between-search idle CPU only. Production panic=abort does not execute guard
destructors, so unwind tests establish test-build cleanup, not production panic
recovery. Fixed CPU6 and the 10-second wall-time abort remain research-specific.
Do not enlarge this experiment to solve those limitations before measuring its
production economics.
