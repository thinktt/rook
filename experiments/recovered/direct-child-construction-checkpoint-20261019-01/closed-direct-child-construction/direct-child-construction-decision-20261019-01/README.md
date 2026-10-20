# Experiment28: direct child construction

Rejected before native tests or timings. Candidate25 remains retained.
Only Node::child was rewritten to initialize a complete local child before
applying the unchanged transition primitive. Source formulas, Retained values,
null child, public APIs and the existing 178 tests remain unchanged.

The generic build d8a7c802 succeeds with exact source69 graph d69955c6. Actual
compiler output retains the required parent-to-child 160-byte copy, then
transfers a whole 176-byte Node after application. The control's second transfer
is 160 bytes. Local stack reservation increases 168→184 bytes; child body grows
937→942 bytes. The same apply primitive remains. Actual generic ordinary and Q
call the outlined child owner, so the failed construction is on their path.

This does not establish a CPU regression; it disproves the intended copy-removal
mechanism and adds a concrete static cost. The frozen backend-first gate therefore
stops this trial. No native tests, strict replay, diagnostic, CPU pilot, own-PGO
or gameplay run follows. No source is promoted, and the failed source is not
combined with another trial.

Actual build 14553:df8ecf→a036ed/0; scoped code capture 8a2aec/0; existing-text
resolution baa22d/0; final backend report 30fb6a/0. Raw captures, exact source
and source review preserve all claims and limits; no whole-program layout or
copy neutrality is asserted.
