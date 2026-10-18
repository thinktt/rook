# Selected and full endgame-bound transport

Exact adapter:
`f8e0b7b0d73b1024984731e60fe44fbd958762db034e7e7de8b02d44da80cf12`.
All42 unit tests and2868 unique external cases pass across57 operations.
The declared corpus contains47 complete files plus25 unchanged selected cases
from two partial files. Four new routes add372 cases:

- `evaluation.pawnRaceBounds` selects pawns against a bare king and preserves
  the supplied score while native classification updates endpoints.
- `evaluation.endgameAdjust` calls the complete native material/bound/rule
  stage with independently supplied score, phase, check and pawn contribution.
- `evaluation.fortressBounds` validates selected bishop/pawn or queen/pawn
  material and calls native geometry without clipping or replacing score.
- `evaluation.rookFortress` validates its distinct rook/pawn modes and calls
  native signed score reductions with supplied turn/check context.

All endpoints remain independently White-relative, including contradictory
input intervals. No legal ancestry, score-favor, check or phase inference narrows
the component domains. Unknown fields and ignored-but-invalid fields are errors.

The18-file adapter source/preparation archive, actual frozen unit image,
canonical native43 reference, build/source closure, before/after dependencies
and every original normal external exit are retained. The adapter calls native
owners and never reads fixture answers at runtime. Native ordinary source
remains unchanged. [identity.json](identity.json) independently reconciles the
complete original report and all declared cases; `terminal.json` binds the
actual successful verifier observation.

This expands finite mandatory transport coverage. Other mandatory operations,
the production audit and full engine/gameplay/performance qualification remain
open. These component tests do not supply a global production score-range proof.
