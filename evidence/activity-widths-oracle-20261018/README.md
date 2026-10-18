# Independent coordinate comparison for activity widths

The release test harness compares10,000 deterministic broad constructed
placements against our own earlier coordinate-based activity/influence source.
The oracle modules are copied byte for byte from the prior retained experiment;
`oracle-origin.json` records that origin. No other engine source or fixture
answers are used by this harness.

Every placement has one king per color, up to15 nonking pieces per color,
up to8 pawns and no pawns on terminal ranks. Moving side, material and weights
vary. Complete influence bytes, activity piece/pressure/weighted fields and
semantic relation-query counts agree. The oracle shares the native relation
primitive, which has a separate exhaustive formula check; this comparison is
not an independent relation-formula proof.

`freeze_run.py` freezes the actual test executable before running it and binds
its image, oracle/input/source bytes before and after execution. `receipt.json`
records normal success with stable inputs. This is finite constructed-domain
correctness evidence; the test harness is not a production timing artifact.
